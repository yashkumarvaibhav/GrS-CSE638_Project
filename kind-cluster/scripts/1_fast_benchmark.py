#!/usr/bin/env python3
# 1_fast_benchmark.py
# runs the benchmark test matrix for a given CNI plugin
# we use 10s durations to keep things reasonably fast
#
# usage: python3 1_fast_benchmark.py <cni> <baseline|policy|wireguard|kpr>
#
# TODO: maybe add a --dry-run flag at some point

import subprocess, json, csv, os, sys, time, signal
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")
KUBECTL     = os.path.expanduser("~/bin/kubectl")
CLUSTER     = "cni-bench"
W1 = f"{CLUSTER}-worker"
W2 = f"{CLUSTER}-worker2"

# pinned images - using sha digests so we always get the same version
IMG_IPERF3 = "networkstatic/iperf3@sha256:07dcca91c0e47d82d83d91de8c3d46b840eef4180499456b4fa8d6dadb46b6c8"
IMG_NETPERF = "networkstatic/netperf@sha256:f42eb5f94f31db407dd02cc65a4467e462e75d2619f7c8aad74dfebbdfae1a62"
IMG_FORTIO = "fortio/fortio@sha256:7cd60e11e59d2c109c360c1d63c76e48294ebccf1b147cd4c5c32fccdad02d46"
IMG_BUSYBOX = "busybox@sha256:b3255e7dfbcd10cb367af0d409747d511aeb66dfac98cf30e97e87e4207dd76f"
DUR = 10   # secs per test - might bump to 30 for final runs but 10 is enough
os.makedirs(DATA_DIR, exist_ok=True)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)  # line bufferd output


def cmd(c, timeout=120):
    """run a shell comand and return stdout + returncode"""
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", 1
    except:
        return "",1

def kc(args, timeout=120):
    """shortcut for kubectl commands"""
    return cmd(f"{KUBECTL} {args}",timeout)

def pod_ip(name, ns="benchmark"):
    o,_ = kc(f"get pod {name} -n {ns} -o jsonpath='{{.status.podIP}}'")
    return o.strip("'")

def cleanup():
    """delete all pods and svcs in benchmark ns"""
    kc("delete pod --all -n benchmark --force --grace-period=0", 30)
    kc("delete svc --all -n benchmark --force",30)
    time.sleep(2)
    # print("  [cleanup done]")  # uncomment for debugging


def deploy(tool, node):
    """deploy a server pod + clusterIP service for the given benchamrk tool"""
    cfgs = {
        "iperf3":  (IMG_IPERF3, '["iperf3","-s"]', 5201),
        "netperf": (IMG_NETPERF, '["netserver","-D"]', 12865),
        "fortio":  (IMG_FORTIO, '["fortio","server"]', 8080),
    }
    img, cmd_str, port = cfgs[tool]

    # build the yaml inline - probably should use jinja2 or something but
    # this works fine for now and keeping seperate template files is annoying
    manifest = f"""apiVersion: v1
kind: Pod
metadata:
  name: {tool}-server
  namespace: benchmark
  labels:
    app: {tool}-server
spec:
  nodeSelector:
    kubernetes.io/hostname: {node}
  containers:
  - name: {tool}
    image: {img}
    imagePullPolicy: IfNotPresent
    command: {cmd_str}
    ports:
    - containerPort: {port}
  terminationGracePeriodSeconds: 0
---
apiVersion: v1
kind: Service
metadata:
  name: {tool}-server
  namespace: benchmark
spec:
  selector:
    app: {tool}-server
  ports:
  - port: {port}
    targetPort: {port}
"""
    with open(f"/tmp/{tool}_m.yaml","w") as f:
        f.write(manifest)
    kc(f"apply -f /tmp/{tool}_m.yaml")
    kc(f"wait --for=condition=Ready pod/{tool}-server -n benchmark --timeout=60s",70)
    time.sleep(1)


# ---------- docker stats collector ----------
# we collect container resource usage while benchmarks run
# runs as a seperate python process in the background

statsProc = None

def start_stats(label, cni):
    global statsProc
    sf = os.path.join(DATA_DIR, f"1_{cni}_stats_{label}.csv")
    # yeah this inline script is ugly but it works
    script = f'''
import subprocess,time
with open("{sf}","w") as f:
    f.write("ts,container,cpu,mem_use,mem_pct\\n")
    for _ in range(999):
        try:
            r=subprocess.run(["docker","stats","--no-stream","--format","{{{{.Name}}}},{{{{.CPUPerc}}}},{{{{.MemUsage}}}},{{{{.MemPerc}}}}"],capture_output=True,text=True,timeout=10)
            t=int(time.time())
            for l in r.stdout.strip().split("\\n"):
                if "{CLUSTER}" in l: f.write(f"{{t}},{{l}}\\n")
            f.flush()
        except: pass
        time.sleep(1)
'''
    statsProc = subprocess.Popen(["python3","-c",script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_stats():
    global statsProc
    if statsProc:
        statsProc.terminate()
        try: statsProc.wait(5)
        except: statsProc.kill()
        statsProc = None


# ---------- iperf3 benchmark ----------
def run_iperf3(tgt, clientNode, cni, tag, sz, szLabel, co, rep):
    ov = json.dumps({"spec":{"nodeSelector":{"kubernetes.io/hostname": clientNode}}})
    out,_ = cmd(
        f"{KUBECTL} run iperf3-c --rm -i --restart=Never -n benchmark "
        f"--image={IMG_IPERF3} --overrides='{ov}' -- "
        f"iperf3 -c {tgt} -t {DUR} -P {co} -l {sz} -J", DUR+45)
    tcp = "FAIL"
    try:
        d = json.loads(out[out.index('{'):out.rindex('}')+1])
        tcp = round(d['end']['sum_sent']['bits_per_second']/1e9, 4)
    except:
        print(f"  WARNING: iperf3 TCP parse failed for {tag} {szLabel} P={co} r{rep}")

    # only run UDP for smaller msg sizes - large ones just timeout or give
    # garbage results, not worth the time
    udp=jit=loss = "N/A"
    if sz<=4096:
        out2,_ = cmd(
            f"{KUBECTL} run iperf3-u --rm -i --restart=Never -n benchmark "
            f"--image={IMG_IPERF3} --overrides='{ov}' -- "
            f"iperf3 -c {tgt} -u -t {DUR} -P {co} -l {sz} -b 0 -J", DUR+45)
        try:
            d2 = json.loads(out2[out2.index('{'):out2.rindex('}')+1])
            s = d2['end']['sum']
            udp = round(s.get('bits_per_second',0)/1e9,4)
            jit = round(s.get('jitter_ms',0),4)
            loss = round(s.get('lost_percent',0),2)
        except:
            udp=jit=loss="FAIL"
            print(f"  WARNING: iperf3 UDP parse failed for {tag} {szLabel} P={co} r{rep}")

    print(f"  iperf3 {tag} {szLabel} P={co} r{rep} -> TCP:{tcp}G UDP:{udp}G")
    return [cni, tag, szLabel, co, rep, "tcp", tcp, udp, jit, loss]


# ---------- helper: deploy a client pod and wait for it ----------
# some images need special idle commands bc they dont have /bin/sh
CLIENT_IDLE_CMDS = {
    IMG_NETPERF: "/bin/sh -c 'sleep 600'",
    IMG_FORTIO:  "fortio server -http-port 0",
}

def deployClient(name, image, targetNode, sleepCmd=None):
    ov = json.dumps({"spec":{"nodeSelector":{"kubernetes.io/hostname":targetNode}}})
    kc(f"delete pod {name} -n benchmark --force --grace-period=0 2>/dev/null",10)
    time.sleep(1)
    idle = sleepCmd or CLIENT_IDLE_CMDS.get(image, "sleep 600")
    kc(f"run {name} -n benchmark --image={image} --restart=Never "
       f"--overrides='{ov}' --command -- {idle}")
    kc(f"wait --for=condition=Ready pod/{name} -n benchmark --timeout=60s",70)
    time.sleep(1)


# ---------- netperf benchmark ----------
def run_netperf(tgt, clientNode, cni, tag, sz, szLabel, co, rep):
    deployClient("np-client", IMG_NETPERF, clientNode)

    # TCP_RR - measures req/resp latency
    out_rr, _ = cmd(
        f"{KUBECTL} exec -n benchmark np-client -- "
        f"netperf -H {tgt} -t TCP_RR -l {DUR} -- -r {sz},{sz}", DUR+45)

    trans = mean_lat = "FAIL"
    try:
        for line in reversed(out_rr.split('\n')):
            parts = line.strip().split()
            if len(parts)>=6:
                try:
                    val = float(parts[-1])
                    # sanity check - should be a transaction rate between 0 and 10M
                    if 0 < val < 10000000:
                        trans = val
                        mean_lat = round(1e6/trans, 2)
                        break
                except ValueError:
                    continue
    except: pass
    if trans=="FAIL":
        print(f"  WARNING: netperf TCP_RR parse failed for {tag} {szLabel} r{rep}")

    # TCP_STREAM - bulk throughput
    out_st,_ = cmd(
        f"{KUBECTL} exec -n benchmark np-client -- "
        f"netperf -H {tgt} -t TCP_STREAM -l {DUR} -- -m {sz}", DUR+45)

    stream = "FAIL"
    try:
        for line in reversed(out_st.split('\n')):
            parts = line.strip().split()
            if len(parts)>=5:
                try:
                    val = float(parts[-1])
                    if val>0.1:
                        stream = val
                        break
                except ValueError:
                    continue
    except: pass
    if stream=="FAIL":
        print(f"  WARNING: netperf TCP_STREAM parse failed for {tag} {szLabel} r{rep}")

    kc("delete pod np-client -n benchmark --force --grace-period=0",10)

    print(f"  netperf {tag} {szLabel} r{rep} -> lat:{mean_lat}us trans:{trans}/s stream:{stream}Mbps")
    return [cni, tag, szLabel, co, rep, mean_lat, 0, 0, 0, trans, stream]


# ---------- fortio benchmark ----------
def run_fortio(tgt, clientNode, cni, tag, sz, szLabel, co, rep):
    deployClient("fort-client", IMG_FORTIO, clientNode)

    out,_ = cmd(
        f"{KUBECTL} exec -n benchmark fort-client -- "
        f"fortio load -qps 0 -c {co} -t {DUR}s -payload-size {sz} -json - "
        f"http://{tgt}:8080/echo", DUR+45)

    qps = p50 = p75 = p90 = p99 = p999 = "FAIL"
    try:
        d = json.loads(out[out.index('{'):out.rindex('}')+1])
        qps = round(d.get('ActualQPS',0),2)
        # pull out the percentile values from fortio's json output
        pcts = {p['Percentile']:p['Value'] for p in d.get('DurationHistogram',{}).get('Percentiles',[])}
        p50 = round(pcts.get(50,0)*1000,4)
        p75 = round(pcts.get(75,0)*1000,4)
        p90 = round(pcts.get(90,0)*1000,4)
        p99 = round(pcts.get(99,0)*1000,4)
        p999 = round(pcts.get(99.9,0)*1000,4)
    except:
        print(f"  WARNING: fortio parse failed for {tag} {szLabel} c={co} r{rep}")

    kc("delete pod fort-client -n benchmark --force --grace-period=0",10)

    print(f"  fortio {tag} {szLabel} c={co} r{rep} -> QPS:{qps} p99:{p99}ms")
    return [cni, tag, szLabel, co, rep, qps, p50, p75, p90, p99, p999]


# ---------- pod startup time measurement ----------
def pod_startup(cni, iters=10):
    results = []
    print(f"\n  Pod network reachability ({iters} iters)...")
    for i in range(1, iters+1):
        t0 = time.time()
        ov = json.dumps({"spec": {"nodeSelector": {"kubernetes.io/hostname":W2}}})
        kc(f"run st-{i} -n benchmark --image={IMG_BUSYBOX} --restart=Never --overrides='{ov}' -- sleep 300")
        kc(f"wait --for=condition=Ready pod/st-{i} -n benchmark --timeout=60s",70)
        elapsed = round(time.time()-t0,3)
        print(f"    iter {i}: {elapsed}s")
        results.append([cni, i, elapsed])
        kc(f"delete pod st-{i} -n benchmark --force --grace-period=0",15)
    return results


# ---------- run a single scenario (topology) ----------
def run_scenario(cni, tag, serverNode, clientNode, mode, sizes, sizeLabels, concs, reps):
    print(f"\n{'='*50}")
    print(f"  {tag} server={serverNode} client={clientNode} mode={mode}")
    print(f"{'='*50}")
    iperf_rows, netperf_rows, fortio_rows = [], [], []
    for sz, szLabel in zip(sizes, sizeLabels):
        for co in concs:
            for rep in range(1, reps+1):
                print(f"\n  --- {tag} {szLabel} P={co} rep {rep}/{reps} ---")
                start_stats(f"{tag}_{szLabel}_P{co}_r{rep}", cni)

                # run iperf3
                cleanup(); deploy("iperf3", serverNode)
                tgt = f"iperf3-server.benchmark.svc.cluster.local" if mode=="service" else pod_ip("iperf3-server")
                iperf_rows.append(run_iperf3(tgt, clientNode, cni, tag, sz, szLabel, co, rep))

                # run netperf
                cleanup(); deploy("netperf", serverNode)
                tgt = f"netperf-server.benchmark.svc.cluster.local" if mode=="service" else pod_ip("netperf-server")
                netperf_rows.append(run_netperf(tgt, clientNode, cni, tag, sz, szLabel, co, rep))

                # run fortio
                cleanup(); deploy("fortio", serverNode)
                tgt = f"fortio-server.benchmark.svc.cluster.local" if mode=="service" else pod_ip("fortio-server")
                fortio_rows.append(run_fortio(tgt, clientNode, cni, tag, sz, szLabel, co, rep))

                stop_stats()
    return iperf_rows, netperf_rows, fortio_rows

def write_csv(fname, hdr, rows, append=False):
    fp = os.path.join(DATA_DIR, fname)
    m = 'a' if append else 'w'
    with open(fp, m, newline='') as f:
        w = csv.writer(f)
        if not append:
            w.writerow(hdr)
        w.writerows(rows)
    print(f"  -> {len(rows)} rows -> {fname}")


# ========== main benchamrk functions ==========

def run_baseline(cni):
    """run the full baseline matrix: 3 topologies x 3 sizes x 3 concurrencys x 3 reps"""
    sizes     = [64, 4096, 1048576]
    sizeLabels = ["64B", "4KB", "1MB"]
    concs     = [1, 16, 64]
    reps      = 3

    all_i, all_n, all_f = [],[],[]
    for tag, sn, cn, mode in [("T1",W1,W1,"pod"), ("T2",W1,W2,"pod"), ("T3",W1,W2,"service")]:
        i,n,f = run_scenario(cni, tag, sn, cn, mode, sizes, sizeLabels, concs, reps)
        all_i.extend(i); all_n.extend(n); all_f.extend(f)

    # write out the CSVs
    write_csv(f"1_{cni}_iperf3.csv",
        ["cni","scenario","msg_size","concurrency","rep","protocol","tcp_gbps","udp_gbps","udp_jitter_ms","udp_loss_pct"], all_i)
    write_csv(f"1_{cni}_netperf.csv",
        ["cni","scenario","msg_size","concurrency","rep","mean_lat_us","p50_us","p90_us","p99_us","trans_rate","stream_mbps"], all_n)
    write_csv(f"1_{cni}_fortio.csv",
        ["cni","scenario","msg_size","concurrency","rep","qps","p50_ms","p75_ms","p90_ms","p99_ms","p999_ms"], all_f)

    # also measure pod startup
    su = pod_startup(cni)
    write_csv(f"1_{cni}_pod_startup.csv", ["cni","iter","time_s"], su)
    cleanup()

def run_ext(cni, tag):
    """run extension scenario - smaller matrix (4KB, c=16, 5 reps)"""
    sizes = [4096]; sizeLabels = ["4KB"]; concs = [16]; reps = 5
    i,n,f = run_scenario(cni, tag, W1, W2, "pod", sizes, sizeLabels, concs, reps)
    write_csv(f"1_{cni}_iperf3.csv", None, i, True)
    write_csv(f"1_{cni}_netperf.csv", None, n, True)
    write_csv(f"1_{cni}_fortio.csv", None, f, True)
    cleanup()

if __name__=="__main__":
    cni = sys.argv[1]
    scenario = sys.argv[2]
    print(f"\n{'#'*50}")
    print(f"  {cni} / {scenario} -- {datetime.now()}")
    print(f"  Duration per test: {DUR}s")
    print(f"{'#'*50}\n")

    # dispatch to the right function based on scenario arg
    # FIXME: this dict-dispatch is kinda ugly but it works
    {"baseline": lambda: run_baseline(cni),
     "policy": lambda: run_ext(cni, "E1"),
     "wireguard": lambda: run_ext(cni, "E2"),
     "kpr": lambda: run_ext(cni, "E3"),
    }[scenario]()

    print(f"\n  DONE: {cni}/{scenario} at {datetime.now()}")
    print(f"  Data in: {DATA_DIR}/")

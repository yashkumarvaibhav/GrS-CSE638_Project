#!/usr/bin/env python3
# 1_aggregate_data.py
# loads all the benchmark CSVs, computes means and stdev,
# prints summary tables and exports a json for the plot scripts
#
# usage: python3 scripts/1_aggregate_data.py
# 
# note: run this AFTER all CNI benchmarks are done

import csv, os, sys, json
from collections import defaultdict
import math

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")

def load_csv(path):
    """load a csv file into a list of dicts. returns empty list if file doesnt exist"""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))

def mean(vals):
    # filter out bad values first
    clean = [v for v in vals if v is not None and v!="N/A" and v!="FAIL"]
    if not clean:
        return 0
    return sum(float(v) for v in clean)/len(clean)

def stdev(vals):
    clean = [float(v) for v in vals if v is not None and v!="N/A" and v!="FAIL"]
    if len(clean) < 2:
        return 0
    m = sum(clean)/len(clean)
    return math.sqrt( sum((x-m)**2 for x in clean)/(len(clean)-1) )

def group_by(rows, keys):
    """group rows by a tuple of key fields"""
    groups = defaultdict(list)
    for r in rows:
        k = tuple(r[k] for k in keys)
        groups[k].append(r)
    return groups


def summarize_iperf3():
    print("\n" + "="*80)
    print("  iPERF3 THROUGHPUT SUMMARY")
    print("="*80)
    cnis = ["flannel","calico","cilium"]
    allData = {}
    for cni in cnis:
        rows = load_csv(os.path.join(DATA_DIR, f"1_{cni}_iperf3.csv"))
        if not rows:
            continue
        groups = group_by(rows, ["scenario","msg_size","concurrency"])
        for key, reps in sorted(groups.items()):
            scn,sz,co = key
            tcp_vals = [r.get("tcp_gbps",0) for r in reps]
            tcp_mean = mean(tcp_vals)
            tcp_sd   = stdev(tcp_vals)
            allData[(cni,scn,sz,co)] = {"tcp_mean":tcp_mean, "tcp_sd":tcp_sd}
            print(f"  {cni:8s} {scn} {sz:>5s} c={co:>3s} | TCP: {tcp_mean:8.4f} +/- {tcp_sd:.4f} Gbps")
    return allData

def summarize_netperf():
    print("\n" + "="*80)
    print("  NETPERF SUMMARY")
    print("="*80)
    cnis = ["flannel","calico","cilium"]
    allData = {}
    for cni in cnis:
        rows = load_csv(os.path.join(DATA_DIR, f"1_{cni}_netperf.csv"))
        if not rows: continue
        groups = group_by(rows, ["scenario","msg_size","concurrency"])
        for key,reps in sorted(groups.items()):
            scn,sz,co = key
            trans_vals  = [r.get("trans_rate",0) for r in reps]
            lat_vals    = [r.get("mean_lat_us",0) for r in reps]
            stream_vals = [r.get("stream_mbps",0) for r in reps]
            trans_m  = mean(trans_vals)
            lat_m    = mean(lat_vals)
            stream_m = mean(stream_vals)
            allData[(cni,scn,sz,co)] = {
                "trans_mean":trans_m, "lat_mean":lat_m, "stream_mean":stream_m
            }
            print(f"  {cni:8s} {scn} {sz:>5s} c={co:>3s} | Trans: {trans_m:8.1f}/s  Lat: {lat_m:8.2f}us  Stream: {stream_m:8.2f} Mbps")
    return allData

def summarize_fortio():
    print("\n" + "="*80)
    print("  FORTIO SUMMARY")
    print("="*80)
    cnis = ["flannel","calico","cilium"]
    allData = {}
    for cni in cnis:
        rows = load_csv(os.path.join(DATA_DIR, f"1_{cni}_fortio.csv"))
        if not rows: continue
        groups = group_by(rows, ["scenario","msg_size","concurrency"])
        for key,reps in sorted(groups.items()):
            scn,sz,co = key
            qps_vals = [r.get("qps",0) for r in reps]
            p99_vals = [r.get("p99_ms",0) for r in reps]
            qps_m = mean(qps_vals)
            p99_m = mean(p99_vals)
            allData[(cni,scn,sz,co)] = {"qps_mean":qps_m, "p99_mean":p99_m}
            print(f"  {cni:8s} {scn} {sz:>5s} c={co:>3s} | QPS: {qps_m:10.2f}  p99: {p99_m:.4f}ms")
    return allData

def summarize_startup():
    print("\n" + "="*80)
    print("  POD STARTUP TIME SUMMARY")
    print("="*80)
    cnis = ["flannel","calico","cilium"]
    allData = {}
    for cni in cnis:
        rows = load_csv(os.path.join(DATA_DIR, f"1_{cni}_pod_startup.csv"))
        if not rows: continue
        vals = [float(r["time_s"]) for r in rows]
        m = mean(vals)
        sd = stdev(vals)
        allData[cni] = {"mean": m, "stdev": sd, "values": vals}
        print(f"  {cni:8s} | {m:.3f} +/- {sd:.3f}s  (n={len(vals)})")
    return allData


def export_plot_data(iperf_data, netperf_data, fortio_data, startup_data):
    """dump everything into a json file that the plotting scripts can read"""
    output = {
        "iperf3":  {f"{k[0]}_{k[1]}_{k[2]}_{k[3]}": v for k,v in iperf_data.items()},
        "netperf": {f"{k[0]}_{k[1]}_{k[2]}_{k[3]}": v for k,v in netperf_data.items()},
        "fortio":  {f"{k[0]}_{k[1]}_{k[2]}_{k[3]}": v for k,v in fortio_data.items()},
        "startup": {k: v for k,v in startup_data.items()},
    }
    outpath = os.path.join(DATA_DIR, "1_aggregated_results.json")
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Exported aggregated data to {outpath}")
    return output


if __name__=="__main__":
    iperf_data  = summarize_iperf3()
    netperf_data = summarize_netperf()
    fortio_data = summarize_fortio()
    startup_data = summarize_startup()
    export_plot_data(iperf_data, netperf_data, fortio_data, startup_data)
    print("\n  Done.")

#!/usr/bin/env python3
"""Tiny CPU scheduler simulator for OS Session 3.
usage: python3 sched.py POLICY LENGTHS [QUANTUM]
  POLICY  = FIFO, SJF or RR
  LENGTHS = job run times, comma-separated, all arriving at time 0 (e.g. 100,10,10)
  QUANTUM = time slice for RR (default 1)
"""
import sys

def simulate(policy, lengths, quantum=1):
    jobs = [{"name": chr(65 + i), "left": n, "first": None, "done": None} for i, n in enumerate(lengths)]
    order = sorted(jobs, key=lambda j: j["left"]) if policy == "SJF" else list(jobs)
    t, timeline = 0, []
    if policy in ("FIFO", "SJF"):
        for j in order:
            j["first"] = t
            timeline.append((t, j["name"], j["left"]))
            t += j["left"]; j["left"] = 0; j["done"] = t
    elif policy == "RR":
        queue = list(order)
        while queue:
            j = queue.pop(0)
            if j["first"] is None: j["first"] = t
            run = min(quantum, j["left"])
            timeline.append((t, j["name"], run))
            t += run; j["left"] -= run
            if j["left"] > 0: queue.append(j)
            else: j["done"] = t
    else:
        sys.exit("policy must be FIFO, SJF or RR")
    return jobs, timeline

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    policy = sys.argv[1].upper()
    lengths = [int(x) for x in sys.argv[2].split(",")]
    quantum = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    jobs, timeline = simulate(policy, lengths, quantum)
    print(f"Policy {policy}" + (f", quantum {quantum}" if policy == "RR" else ""))
    shown = timeline if len(timeline) <= 12 else timeline[:9] + [None] + timeline[-2:]
    for step in shown:
        print("   ..." if step is None else f"  t={step[0]:4}: run job {step[1]} for {step[2]}")
    print("\n  Job  Length  Response  Turnaround")
    for j, n in zip(jobs, lengths):
        print(f"  {j['name']:>3}  {n:6}  {j['first']:8}  {j['done']:10}")
    r = sum(j["first"] for j in jobs) / len(jobs)
    ta = sum(j["done"] for j in jobs) / len(jobs)
    print(f"  Average      {r:8.2f}  {ta:10.2f}")

if __name__ == "__main__":
    main()

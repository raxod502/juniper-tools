#!/usr/bin/env python3

import argparse
import json

import pygal

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")

args = parser.parse_args()

results = []
for fname in args.files:
    with open(fname) as throughputDataFile:
        results.extend(json.load(throughputDataFile))

typ_avg_thru = {}
for result in sorted(results, key=lambda r: (r["type"], r["numEntries"])):
    typ = result["type"]
    numEntries = result["numEntries"]
    typ_numEntries = typ + "(" + str(numEntries) + ")"
    throughput = result["throughput"]

    if typ_numEntries not in typ_avg_thru:
        typ_avg_thru[typ_numEntries] = throughput

bar_graph = pygal.HorizontalBar()
bar_graph.title = "Header Type Average Throughput"
for typ, thru in typ_avg_thru.items():
    bar_graph.add(typ, thru)
bar_graph.render_to_file("type_averageThru.svg")

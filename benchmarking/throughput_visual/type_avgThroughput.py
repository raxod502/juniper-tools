#!/usr/bin/env python3

import argparse
import json

import pygal

parser = argparse.ArgumentParser()
parser.add_argument("file")

args = parser.parse_args()

with open(args.file) as throughputDataFile:
    results = json.load(throughputDataFile)

typ_avg_thru = {}
for result in sorted(results, key=lambda r: r["numEntries"]):
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

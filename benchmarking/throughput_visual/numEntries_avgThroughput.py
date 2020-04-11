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

line_chart = pygal.XY()
line_chart.title ="Throughput Relative to Number of Entries"
line_chart.x_title = "Number of Entries"
line_chart.y_title = "Average Throughput"

sortBy = lambda r: (r["type"], r["numEntries"])
sortedEntries = sorted(results, key=sortBy)
type_entries = {}
for entry in sortedEntries:
    if entry["type"] not in type_entries:
        type_entries[entry["type"]] = [(entry["numEntries"], entry["throughput"])]
    else:
        type_entries[entry["type"]] += [(entry["numEntries"], entry["throughput"])]

for typ, data in type_entries.items():
    xyCoords = [(opt[0], opt[1]) for opt in data]
    line_chart.add(typ, xyCoords)

line_chart.render_to_file('numEntries_avgThroughput.svg')

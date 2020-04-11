#!/usr/bin/env python3

import argparse
import json

import pygal
from pygal.style import BlueStyle

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


bar_graph = pygal.StackedBar(x_label_rotation=-45, show_legend=False, style=BlueStyle)
bar_graph.title = "Average Throughput Per Header Type"
bar_graph.x_title = "Header Type"
bar_graph.y_title = "Average Throughput"

xLabels = []
position = 0
num_x_values = len(typ_avg_thru)
for typ, thru in typ_avg_thru.items():
    xValues = [None for x in range(num_x_values)]
    xValues[position] = thru
    bar_graph.add(typ, xValues)
    xLabels += [typ]
    position += 1

bar_graph.x_labels = xLabels

bar_graph.render_to_file("type_averageThru.svg")

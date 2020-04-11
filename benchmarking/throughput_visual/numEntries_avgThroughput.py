#!/usr/bin/env python3

import argparse
import json
import os

import pygal

parser = argparse.ArgumentParser()
parser.add_argument("file")

args = parser.parse_args()

results = []
with open(args.file) as throughputDataFile:
    results = json.load(throughputDataFile)

line_chart = pygal.XY(show_legend=False)
fileName = " (" + os.path.basename(args.file) + ")"
line_chart.title ="Throughput Relative to Number of Entries" + fileName
line_chart.x_title = "Number of Entries"
line_chart.y_title = "Average Throughput"

sortBy = lambda r: r["numEntries"]
sortedList = sorted(results, key=sortBy)
xyCoords = [(opt["numEntries"], opt["throughput"]) for opt in sortedList]
line_chart.add('', xyCoords)
line_chart.render_to_file('numEntries_avgThroughput.svg')

#!/usr/bin/env python3

import argparse
import json
import os

import cairosvg
import pygal

parser = argparse.ArgumentParser()
parser.add_argument("file")
filetypes = ["svg", "png"]
parser.add_argument("filetype", choices=filetypes)

args = parser.parse_args()

results = []
with open(args.file) as throughputDataFile:
    results = json.load(throughputDataFile)

line_chart = pygal.XY(show_legend=False)
fileName = " (" + os.path.basename(args.file) + ")"
line_chart.title ="Packet Throughput" + fileName
line_chart.x_title = "Attempted Throughput (packets)"
line_chart.y_title = "Actual Throughput (packets)"

xyCoords = [(pair[0], pair[1]) for pair in sorted(results, key=lambda r: r[0])]
line_chart.add('', xyCoords)

if args.filetype == "png":
    line_chart.render_to_png("actual_attempted.png")
elif args.filetype == "svg":
    line_chart.render_to_file("actual_attempted.svg")

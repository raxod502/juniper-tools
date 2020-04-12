#!/usr/bin/env python3

import argparse
import json

import cairosvg
import pygal
from pygal.style import Style
from pygal.style import BlueStyle

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
filetypes = ["svg", "png"]
parser.add_argument("filetype", choices=filetypes)

args = parser.parse_args()

results = []
for fname in args.files:
    with open(fname) as throughputDataFile:
        results.extend(json.load(throughputDataFile))

numEntries_typ_thru = {}
xLabels = []
for result in sorted(results, key=lambda r: (r["numEntries"], r["type"])):
    typ = result["type"]
    numEntries = result["numEntries"]
    throughput = result["throughput"]

    if numEntries not in numEntries_typ_thru:
        numEntries_typ_thru[numEntries] = {}

    if typ not in numEntries_typ_thru[numEntries]:
       numEntries_typ_thru[numEntries][typ] = throughput
       if typ not in xLabels:
           xLabels += [typ]
    else:
        typ_num = typ + "(" + numEntries + ")"
        errorMsg = "duplicate data for {}, unsure of which to use."
        raise Exception(erroMsg.format(typ_num))


custom_style = BlueStyle()
labelSize = 17
custom_style.label_font_size = labelSize
custom_style.major_label_font_size = labelSize
custom_style.title_font_size = 23
custom_style.value_label_font_size = 11

bar_graph = pygal.Bar(show_legend=False, width=1750, print_labels=True, style=custom_style)
bar_graph.title = "Average Throughput Per Header Type"
bar_graph.x_title = "Header Type (Number of Entries)"
bar_graph.y_title = "Average Throughput (packets)"
bar_graph.x_labels = xLabels

xAxisLen = len(xLabels)
for numEntries, typList in numEntries_typ_thru.items():
    xValues = [None for x in range(xAxisLen)]
    for typ, throughput in typList.items():
        xValues[xLabels.index(typ)] = {'value': throughput, 'label': str(numEntries)}
    bar_graph.add(str(numEntries), xValues)

if args.filetype == "png":
    bar_graph.render_to_png("type_averageThru.png")
elif args.filetype == "svg":
    bar_graph.render_to_file("type_averageThru.svg")

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

typ_numEntries_thru = {}
typeList = []
xLabels = []
for result in sorted(results, key=lambda r: (r["numEntries"], r["type"])):
    typ = result["type"]
    numEntries = result["numEntries"]
    throughput = result["throughput"]

    if typ not in typ_numEntries_thru:
        typ_numEntries_thru[typ] = {}
        typeList += [typ]

    if numEntries not in typ_numEntries_thru[typ]:
       typ_numEntries_thru[typ][numEntries] = throughput
       if numEntries not in xLabels:
           xLabels += [numEntries]
    else:
        typ_num = typ + "(" + numEntries + ")"
        errorMsg = "duplicate data for {}, unsure of which to use."
        raise Exception(erroMsg.format(typ_num))


# configure bar graph
custom_style = BlueStyle()
# labelSize = 17
# custom_style.label_font_size = labelSize
# custom_style.major_label_font_size = labelSize
# custom_style.title_font_size = 23
# custom_style.value_label_font_size = 11

bar_graph = pygal.Bar(style=custom_style)
# bar_graph.legend_at_bottom = True
# bar_graph.legend_at_bottom_columns = len(typeList)
bar_graph.title = "Average Throughput Per Header Type"
bar_graph.x_title = "Number of Entries (addresses)"
bar_graph.y_title = "Average Throughput (packets)"
bar_graph.x_labels = sorted(xLabels)

# add x values for each header type
xAxisLen = len(xLabels)
for typ, numEntriesList in typ_numEntries_thru.items():
    xValues = [None for x in range(xAxisLen)]
    for numEntries, throughput in numEntriesList.items():
        xValues[numEntries-1] = throughput
    bar_graph.add(typ, xValues)

if args.filetype == "png":
    bar_graph.render_to_png("2type_averageThru.png")
elif args.filetype == "svg":
    bar_graph.render_to_file("2type_averageThru.svg")

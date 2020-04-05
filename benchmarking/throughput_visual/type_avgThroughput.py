import pygal
import json

with open("./test1.json", "r") as throughputDataFile:
    throughputData = throughputDataFile.read()

results = json.loads(throughputData)

typ_avg_thru = {}
for result in results:
    typ = result["type"]
    numEntries = result["numEntries"]
    typ_numEntries = typ + "(" + str(numEntries) + ")"
    throughput = result["throughput"]

    if typ_numEntries not in typ_avg_thru:
        typ_avg_thru[typ_numEntries] = throughput

bar_graph = pygal.HorizontalBar()
bar_graph.title = 'Header Type Average Throughput'
for typ, thru in sorted(typ_avg_thru.items()):
    bar_graph.add(typ, thru)
bar_graph.render_to_file('type_averageThru.svg')

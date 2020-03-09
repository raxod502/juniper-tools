import pygal
import json

with open("./test.json", "r") as throughputDataFile:
    throughputData = throughputDataFile.read()

results = json.loads(throughputData)

types = []
numEntries = []
throughputs = []
for result in results:
    types += [result['type']]
    numEntries += [result['numEntries']]
    throughputs += [result['throughput']]

format_throughputs = []
for index in range(1, 101):
    if index in numEntries:
        format_throughputs += [throughputs[0]]
        throughputs = throughputs[1:]
    else:
        format_throughputs += [None]

line_chart = pygal.Line()
line_chart.x_labels = map(str, range(1, 101))
line_chart.add('line', format_throughputs)
line_chart.render_to_file('throughput.svg')

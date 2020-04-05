import pygal
import json

with open("./rh0_5.json", "r") as throughputDataFile:
    throughputData = throughputDataFile.read()

results = json.loads(throughputData)




line_chart = pygal.Line()
line_chart.title = 'Attempted Throughput vs Actual Throughput'
xyLabels = [(pair[0], pair[1]) for pair in results]
line_chart.add('rh0(5)', x
line_chart.render()

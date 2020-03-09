import pygal                                                       # First import pygal
bar_chart = pygal.HorizontalBar()                                            # Then create a bar graph object
bar_chart.add('Bradley', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])  # Add some values
bar_chart.render_to_file('bar_chart.svg')                          # Save the svg to a file



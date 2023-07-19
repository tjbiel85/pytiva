# Python Tools for Investigating & Visualizing Activity in anesthetic records
A toolkit for extracting, parsing, and processing anesthetic records and making sense of the activity therein, especially intra-operative records.

## Installation
Available via PyPI using your favorite python package manager.
```
$ pip3 install pytiva
```

## What can pytiva do?
* Extract data after export from an electronic health record system
* Define and extract anesthesia activities using intra-operative events or the administration of medications
* Unduplicate these activities by any strata of interest, such as patient or case ID number
* Determine total concurrent activities, including aggregating by day and time
* Visualization of so-called gantt charts and heat maps of activity, as below

### Examples of visualizations
##### Gantt chart of raw activity for one patient
![A gantt chart with labeled activity names on the y-axis and a time duration for each of them illustrated by a horizontal box. This chart in particular seems to show three "groups" of activity, each a mix of NORA, OR, and medication activities, with partial overlap.](devnb/ex-gantt-1.png)

##### Gantt chart of unduplicated activity for one patient
![A gantt chart with four generic activities on the y-axis and a time duration for each drawn as a horizontal box, none of which overlap.](devnb/ex-gantt-2.png)

##### Heatmap of concurrent activity
![A chart with hour of the day on the y-axis, day of the week on the x-axis, and a bar to the right of the chart showing a color gradient corresponding to how much activity is happening. The chart puts a color for each hour of each day of the week to show the average activity in that moment.](devnb/ex-heatmap.png)

## Links and further reading
* Get started with a brief tutorial: https://github.com/tjbiel85/pytiva/blob/main/tutorial.ipynb
* Bugs and issue tracking: https://github.com/tjbiel85/pytiva/issues

## Signal probability along line
This program aims to summarize the probability of finding a signal along a line from multiple samples.

To use it, run __main__.py.

You will need @pandas, @numpy and @PyQt5 to run this program.

In essence, given multiple tables, where column X represents a point within a line and column Y represents the signal intensity measured on each point, this program ouputs a table with the probability of finding signal along bins within this line.

First, the points within the line are binned into a user defined bin size.  Then, a threshold value is defined to filter out undesired signal background and a signal ceiling is defined according to the bitdepth of the measurement and bin size.  For each sample, if at a given bin the measured signal exceeds the threshold, the program scores that point as containing a signal.  Finally, we compute the probability of finding signal within each bin by simply summing up signal-containing-bins number and dividing by the total bin number, for the equivalent bins on each samples.

Find a simple example below:

@parameters
```python
bin_size = 2
threshold = 0.3 #(30% of the bin has to be covered with signal)
ceiling = 510 #(Max signal * bin size)
```

sample1.csv
X | Y
- | -
0 | 255
1 | 234
2 | 0
3 | 0
4 | 0
5 | 255
6 | 233
7 | 233
8 | 255
9 | 255
10 | 255

sample2.csv
X | Y
- | -
0 | 255
1 | 234
2 | 0
3 | 0
4 | 0
5 | 0
6 | 0
7 | 0
8 | 255
9 | 255
10 | 255

summary.csv
X | Score |	sample1.csv | sample2.csv | penetrance
- | ----- | ----------- | ----------- | ----------
(0,2] | 2 | 1 | 1 | 1
(2,4] | 0 | 0 | 0 | 0
(4,6] | 1 | 1 | 0 | 0.5
(6,8] | 2 | 1 | 1 | 1
(8,10] | 2 | 1 | 1 | 1
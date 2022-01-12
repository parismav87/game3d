import csv
import numpy as np

timestamp = 0
previousTimestamp = 0
fpsList = []
with open('real.csv', 'r') as csvFile:
    for k,line in enumerate(csvFile.readlines()):
        if k==1: 
            timestamp = float(line.split(',')[0])
            previousTimestamp = timestamp
        if k>1:
            previousTimestamp = timestamp
            timestamp = float(line.split(',')[0])
            diff = timestamp - previousTimestamp
            fps = 1/diff
            # print(fps)
            fpsList.append(fps)

print(np.mean(fpsList), np.std(fpsList))
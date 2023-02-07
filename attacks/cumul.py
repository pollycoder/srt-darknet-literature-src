import subprocess
import numpy
import math
import time
import sys
from loaders import *

#like svm.py, this file produces the output necessary for svm_predict and svm_train
#therefore similarly it produces no accuracy, and it is a feature extractor
#input is i from 0 to 9, which is the fold-num for 10-fold classification
#cumul-run.py calls this (and svm-predict, svn-train) to produce accuracy

def extract(sinste):
    #sinste: list of packet sizes

    #first 4 features

    insize = 0
    outsize = 0
    inpacket = 0
    outpacket = 0

    for i in range(0, len(sinste)):
        if sinste[i] > 0:
            outsize += sinste[0]
            outpacket += 1
        else:
            insize += abs(sinste[0])
            inpacket += 1
    features = [insize, outsize, inpacket, outpacket]

    #100 interpolants
    
    n = 100 #number of linear interpolants

    x = 0 #sum of packet sizes
    y = 0 #sum of absolute packet sizes
    graph = []
    
    for si in range(0, len(sinste)):
        x += abs(sinste[si])
        y += sinste[si]
        graph.append([x, y])

    #derive interpolants
    max_x = graph[-1][0] 
    gap = float(max_x)/n
    cur_x = 0
    cur_y = 0
    graph_ptr = 0

    for i in range(0, n):
        #take linear line between cur_x and cur_x + gap
        next_x = cur_x + gap
        while (graph[graph_ptr][0] < next_x):
            graph_ptr += 1
            if (graph_ptr >= len(graph) - 1):
                graph_ptr = len(graph) - 1
                #wouldn't be necessary if floats were floats
                break
##        print "graph_ptr=", graph_ptr
        next_pt_y = graph[graph_ptr][1] #not next_y 
        next_pt_x = graph[graph_ptr][0]
        cur_pt_y = graph[graph_ptr-1][1]
        cur_pt_x = graph[graph_ptr-1][0]
##        print "lines are", cur_pt_x, cur_pt_y, next_pt_x, next_pt_y

        slope = (next_pt_y - cur_pt_y)/(next_pt_x - cur_pt_x)
        next_y = slope * (next_x - cur_pt_x) + cur_pt_y

##        print "xy are", cur_x, cur_y, next_x, next_y, max_x
        interpolant = (next_y - cur_y)/(next_x - cur_x)
        features.append(interpolant)
        cur_x = next_x
        cur_y = next_y
        

    return features

def log(msg):
    myname = sys.argv[0].split("/")[-1]
    LOG_FILE = d["OUTPUT_LOC"] + myname + ".log"
    f = open(LOG_FILE, "a+")
    f.write(repr(time.time()) + "\t" + str(msg) + "\n")
    f.close()

def rlog(msg):
    myname = sys.argv[0].split("/")[-1]
    LOG_FILE = d["OUTPUT_LOC"] + myname + ".results"
    f = open(LOG_FILE, "a+")
    f.write(repr(time.time()) + "\t" + str(msg) + "\n")
    f.close()
    


try:
    optfname = sys.argv[1]
    d = load_options(optfname)
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

log(sys.argv[0] + " " + sys.argv[1])
log(repr(d))
rlog(sys.argv[0] + " " + sys.argv[1])
rlog(repr(d))
traindata, trainnames = load_list(d["TRAIN_LIST"])
testdata, testnames = load_list(d["TEST_LIST"])

fnames = ["train", "test"]
datasets = [traindata, testdata]
for type_i in range(0, 2): #train, test
    fname = fnames[type_i]
    fout = open(d["OUTPUT_LOC"] + "cumul." + fname, "w")
    for ci in range(0, len(datasets[type_i])): #class number
        for ti in range(0, len(datasets[type_i][ci])):
            features = extract(datasets[type_i][ci][ti])
            fout.write(str(ci))
            for fi in range(0, len(features)):
                fout.write(" " + str(fi+1) + ":" + str(features[fi]))
            fout.write("\n")
    fout.close()

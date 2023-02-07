import subprocess
import numpy
import scipy
import scipy.stats
import math
import time
import sys
from loaders import *

def class_to_counts(datac):
    #input: all elements of a class in standard format (e.g. data[i])
    #output: dictionary, where item = packetsize, object = list of counts
    #                   for instances in that site
    count_dict = {}
    for trace in datac:
        counts = []
        countsizes = []
        for s in trace:
            size = s[1]
            if size in countsizes:
                counts[countsizes.index(size)][1] += 1
            else:
                counts.append([size, 1])
                countsizes.append(size)
        for count in counts:
            packetsize = count[0]
            packetfreq = count[1]
            if packetsize in count_dict.keys():
                count_dict[packetsize].append(packetfreq)
            else:
                count_dict[packetsize] = [packetfreq]
                
    return count_dict

def class_to_uniqcounts(datac):
    #input: all elements of a class in standard format (e.g. data[i])
    #output: dictionary, where key = packetsize, object = number of sites which had that packetsize
    count_dict = {}
    for trace in datac:
        uniqsizes = []
        for s in trace:
            size = s
            if not(size in uniqsizes):
                uniqsizes.append(size)
        for size in uniqsizes:
            if size in count_dict.keys():
                count_dict[size] += 1
            else:
                count_dict[size] = 1
                
    return count_dict

def sinste_to_uniqsizes(sinste):
    #input: one sinste (e.g. data[i][j])
    #output: list of all packet sizes that occurred in sinste
    uniqsizes = []
    for s in sinste:
        size = s
        if not(size in uniqsizes):
            uniqsizes.append(size)
    return uniqsizes

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
    d = load_options(sys.argv[1])
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

log(sys.argv[0] + " " + sys.argv[1])
log(repr(d))
rlog(sys.argv[0] + " " + sys.argv[1])
rlog(repr(d))
traindata, trainnames = load_list(d["TRAIN_LIST"])
testdata, testnames = load_list(d["TEST_LIST"])

tpc = 0 #true positive counts
tnc = 0 #true negative counts
pc = 0 #positive total
nc = 0 #negative total

#Training:
#Collect the common packetsizes in each site
##    a = time.time()
class_machines = []
#class_machines[i] is a list of packetsizes occurring in that site
for i in range(0, len(traindata)):
    class_machines.append([])
    count_dict = class_to_uniqcounts(traindata[i])
    for k in count_dict.keys():
        if count_dict[k] > len(traindata[i])/2:
            class_machines[-1].append(k)
##    b = time.time()
##    traintime += b - a

#Testing:
for s in range(0, len(testdata)): #cycle over each class
    for i in range(0, len(testdata[s])): #cycle over each instance
        testname = testnames[s][i]

        class_probs = [] #class_probs[i] is the score of class i for this sinste
        for t in range(0, len(traindata)):
            class_probs.append(0)

        uniqsizes = sinste_to_uniqsizes(testdata[s][i]) #find uniqsizes
        for sp in range(0, len(traindata)): #cycle over machines
            intersec = 0 #|uniqsizes intersect class_machines[sp]|
            union = 0 #|uniqsizes union class_machines[sp]|
            for size in uniqsizes:
                if size in class_machines[sp]:
                    intersec += 1
                else:
                    union += 1
            union += len(class_machines[sp])
            class_probs[sp] = intersec/float(union) #jaccard's coefficient

        gs = class_probs.index(max(class_probs)) #guessed site
        if s == gs:
            if s == len(testdata) - 1 and d["OPEN"] > 0: #non-monitored
                tnc += 1
            else:
                tpc += 1
        if s == len(testdata) - 1 and d["OPEN"] > 0:
            nc += 1
        else:
            pc += 1
        rlog(testname + "\t" + str(s) + "\t" + str(gs))

##    c = time.time()
##    testtime += c - b

##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

#Implements VNG++ classifier of Dyer et al.
#Serious details are missing from their write-up.
#1) I assume KDE is used in their Naive Bayes.
#2) I assume there are three KDEs, for time, bandwidth, burst.
#Editing out the first two gives you the base VNG. 
#Dyer et al. claims this is not as good as svm.py.

import subprocess
import numpy
import scipy
import scipy.stats
import math
import time
import sys
import random
from loaders import *

def get_time(sinste):
    return sinste[-1][0] - sinste[0][0]

def get_bw(sinste):
    bw = 0
    for packet in sinste:
        bw += abs(packet[1])
    return bw

def get_bursts(sinste):
    bursts = []
    totalburst = 0
    for s_i in range(0, len(sinste)):
        if s_i >= 1:
            if (sinste[s_i][1] * sinste[s_i-1][1] < 0): #change direction
                bursts.append(totalburst)
                totalburst = 0
        totalburst += abs(sinste[s_i][1])
    return bursts

def learn_kde(trainsinste):
    #INPUT: a list of sinstes from a single class
    #OUTPUT: three kdes, one for total time, one for bw, one for bursts

    times = []
    for sinste in trainsinste:
        times.append(get_time(sinste))
    time_kde = scipy.stats.gaussian_kde(scipy.array(times))

    bws = []
    for sinste in trainsinste:
        bws.append(get_bw(sinste))
    bw_kde = scipy.stats.gaussian_kde(scipy.array(bws))

    bursts = []
    for sinste in trainsinste:
        s_bursts = get_bursts(sinste)
        bursts += s_bursts

    if (len(bursts) > 500):
        bursts = random.sample(bursts, 500)
            
    burst_kde = scipy.stats.gaussian_kde(scipy.array(bursts))

    return [time_kde, bw_kde, burst_kde]

def logprob(size, kde):
    #kde has weird behavior with discrete things?
    #use intervals
##    prob = (kde(size-0.1) + kde(size) + kde(size+0.1)) / 3
##    prob = float(scipy.integrate.quad(kde, size-0.5, size+0.5)[0])
##    prob = max(prob, 0.00001) #don't want one packet to kill everything

    prob = max(kde(size), 0.00001)
    return math.log(prob)

def flog(msg, fname):
    f = open(fname, "a+")
    f.write(repr(time.time()) + "\t" + str(msg) + "\n")
    f.close()    

def log(msg):
    LOG_FILE = d["OUTPUT_LOC"] + sys.argv[0].split("/")[-1] + ".log"
    flog(msg, LOG_FILE)

def rlog(msg):
    LOG_FILE = d["OUTPUT_LOC"] + sys.argv[0].split("/")[-1] + ".results"
    flog(msg, LOG_FILE)

try:
    d = load_options(sys.argv[1])
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

log(sys.argv[0] + " " + sys.argv[1])
log(repr(d))
rlog(sys.argv[0] + " " + sys.argv[1])
rlog(repr(d))
traindata, trainnames = load_list(d["TRAIN_LIST"], time=1)
testdata, testnames = load_list(d["TEST_LIST"], time=1)
#uses 10-fold classification

[tpc, tnc, pc, nc] = [0, 0, 0, 0]

import time
traintime = 0
testtime = 0

#Training:
#Build three KDEs for each class
##atime = time.time()
class_kdes = [] #class_kdes[i] is a list of three KDEs for class i
for i in range(0, len(traindata)): #cycle over each class
    class_kdes.append(learn_kde(traindata[i]))
    
##btime = time.time()
##traintime += btime - atime

#Testing:
for s in range(0, len(testdata)): #cycle over each class
##        print fi, "/ 10", s, "/", len(testdata)
    for i in range(0, len(testdata[s])): #cycle over each instance
##            print fi, s, i
        testname = testnames[s][i]
        test_sinste = testdata[s][i]

        class_probs = [] #class_probs[i] is the score of class i for this sinste
        for t in range(0, len(traindata)):
            class_probs.append(0)

        test_time = get_time(test_sinste)
        test_bw = get_bw(test_sinste)
        test_bursts = get_bursts(test_sinste)

        for sp in range(0, len(traindata)):
            class_probs[sp] += logprob(test_time, class_kdes[sp][0])
            class_probs[sp] += logprob(test_bw, class_kdes[sp][1])
            for b in test_bursts:
                class_probs[sp] += logprob(b, class_kdes[sp][2])
                
        gs = class_probs.index(max(class_probs)) #guessed class
        if s == gs:
            if s == len(testdata) - 1 and d["OPEN"] > 0 : #non-monitored
                tnc += 1
            else:
                tpc += 1
        if s == len(testdata) - 1 and d["OPEN"] > 0:
            nc += 1
        else:
            pc += 1
        rlog(testname + "\t" + str(s) + "\t" + str(gs))

##ctime = time.time()
##testtime += ctime - btime
##
##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

#start with traindata, testdata

#the authors do NOT discuss what to do if several elements
#of the training set exceed the threshold

#we will therefore ignore the threshold scheme and classify to maximum score

import math
import subprocess
import time
import sys
from loaders import *

def sinste_to_timing(sinste):
    #INPUT: sinste, such as data[i][j]
    #OUTPUT: timing data format, t[i] is the number of packets in the ith second

    timing = []
    totalsize = 0
    this_time = sinste[0][0]
    for i in range(0, len(sinste)):
        time = sinste[i][0]
        size = 1 #yarly. not sinste[i][1]
        
        totalsize += size
        while time - this_time > 1:
            this_time += 1
            timing.append(totalsize)
            totalsize = 0

    return timing

def cross_cor(timing1, timing2):
    if len(timing1) == 0 or len(timing2) == 0:
        return 0
    c = 0
    length = min(len(timing1), len(timing2))
    m1 = sum(timing1)/float(length)
    m2 = sum(timing2)/float(length)
    for i in range(0, length): 
        c += (timing1[i] - m1) * (timing2[i] - m2)
    #calculate normalization
    sd1 = 0
    sd2 = 0
    for i in range(0, length):
        sd1 += (timing1[i] - m1) * (timing1[i] - m1)
        sd2 += (timing2[i] - m2) * (timing2[i] - m2)
    sd1 = math.sqrt(sd1)
    sd2 = math.sqrt(sd2)

    sd1 = max(sd1, 0.01 * m1)
    sd2 = max(sd2, 0.01 * m2)

    return c/(sd1*sd2)

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

tpc = 0 #true positive counts
tnc = 0 #true negative counts
pc = 0 #positive total
nc = 0 #negative total

##import time
##traintime = 0
##testtime = 0
    
##    a = time.time()
#Training:
#We learn the timings of each sinste
traintimings = []
for site in traindata:
    traintimings.append([])
    for sinste in site:
        traintimings[-1].append(sinste_to_timing(sinste))
##    b = time.time()
##    traintime += b - a

#Testing:
for s in range(0, len(testdata)): #for each class
    for i in range(0, len(testdata[s])): #and each sinste
        testname = testnames[s][i]
        tsinste = testdata[s][i]
        testtiming = sinste_to_timing(tsinste)
        cross_cor_list = []
        class_list = []
        for trainsite_i in range(0, len(traintimings)):
            for traintiming in traintimings[trainsite_i]:
                #compare timings of test and train
                cross_cor_list.append(cross_cor(testtiming, traintiming))
                class_list.append(trainsite_i)

        #guessed site is max of correlation
        gs = class_list[cross_cor_list.index(max(cross_cor_list))]
        #true site is this
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
##            print "p", tpc, "/", pc,
##            print "n", tnc, "/", nc

##    c = time.time()
##    testtime += c - b

##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

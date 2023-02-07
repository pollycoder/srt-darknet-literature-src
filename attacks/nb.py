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
            size = s
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

def sinste_to_counts(sinste):
    #input: one sinste (e.g. data[i][j])
    #converts standard format to counts
    #each element of counts is [packetsize, count]
    counts = []
    countsizes = []
    for s in sinste:
        size = s
        if size in countsizes:
            counts[countsizes.index(size)][1] += 1
        else:
            counts.append([size, 1])
            countsizes.append(size)
    return counts

def learn_kde(utraincounts):
    #traincounts should come from only one class
    #returns the nb parameters for this site

    #unzip traincount
##    utraincounts = []
##    for c in traincounts:
##        size = c[0]
##        count = c[1]
##        for i in range(0, count):
##            utraincounts.append(size)

    #adding a zero to smooth out the curve
    utraincounts.append(0)

    utraincounts = scipy.array(utraincounts)
    

    #just returns gaussian

    return scipy.stats.gaussian_kde(utraincounts)

##
##    mean = sum(utraincounts)/float(len(utraincounts))
##
##    bstd = numpy.std(utraincounts) #this is biased sample variance
##    bstd = (len(utraincounts) * bstd) /(len(utraincounts)-1)
##    return (mean, std)

def logprob(size, kde):
    #kde has weird behavior with discrete things?
    #use intervals
##    prob = (kde(size-0.1) + kde(size) + kde(size+0.1)) / 3
##    prob = float(scipy.integrate.quad(kde, size-0.5, size+0.5)[0])
##    prob = max(prob, 0.00001) #don't want one packet

    prob = max(kde(size), 0.00001)
    return math.log(prob)

def nb_match(testdata, class_kde):
    testcounts = sinste_to_counts(testdata)

    class_prob = 0
    for k in range(0, len(testcounts)): #cycle over each count
        packetsize = testcounts[k][0]
        packetfreq = testcounts[k][1]
        if packetsize in class_kde.keys():
            class_prob += logprob(packetfreq, class_kde[packetsize])
        else:
            class_prob += math.log(0.00001)
            
    return class_prob

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
nul, trainnames = load_listn(d["TRAIN_LIST"])
nul, testnames = load_listn(d["TEST_LIST"])

[tpc, tnc, pc, nc] = [0, 0, 0, 0]

#Training:
#First, populate count_dict
#Build a KDE for each class and each packet size
##    a = time.time()
class_kdes = []
for site in range(0, len(trainnames)): #cycle over each class
    print "Training site %d of %d" %(site, len(trainnames))
    traindata = []
    for trainname in trainnames[site]:
        traindata.append(load_cell(trainname, time=0))
    count_dict = class_to_counts(traindata)
    kde_dict = {}
    for packetsize in count_dict.keys():
        kde_dict[packetsize] = learn_kde(count_dict[packetsize])
    class_kdes.append(kde_dict)
##    b = time.time()
##    traintime += b - a
    
#Testing:
for site in range(0, len(testnames)): #cycle over each class
    print "Testing site %d of %d" %(site, len(trainnames))
    for inst in range(0, len(testnames[site])): #cycle over each instance
        logmsg = "{}".format(site)
        
        testname = testnames[site][inst]
        testdata = load_cell(testname, time=0)
        
        class_probs = [] #class_probs[i] is the score of class i for this sinste
        for t in range(0, len(class_kdes)):
            class_probs.append(nb_match(testdata, class_kdes[t]))
            logmsg += "\t{}".format(class_probs[t])
        gs = class_probs.index(max(class_probs))

        if site == gs:
            if site == len(testnames) - 1 and d["OPEN"] != 0: #non-monitored
                tnc += 1
            else:
                tpc += 1
        if site == len(testnames) - 1 and d["OPEN"] != 0:
            nc += 1
        else:
            pc += 1
        rlog(logmsg)

##    c = time.time()
##    testtime += c - b


##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

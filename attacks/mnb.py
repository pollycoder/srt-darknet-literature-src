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
    #converts standard format to counts
    #each element of counts is [packetsize, count]
    counts = []
    countsizes = []
    for trace in datac:
        for s in trace:
            size = s
            if size in countsizes:
                counts[countsizes.index(size)][1] += 1
            else:
                counts.append([size, 1])
                countsizes.append(size)
    return counts

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

def learn_kde(traincounts):
    #traincounts should come from only one class
    #returns the nb parameters for this site

    #unzip traincount
    utraincounts = []
    for c in traincounts:
        size = c[0]
        count = c[1]
        for i in range(0, count):
            utraincounts.append(size)

    utraincounts = scipy.array(utraincounts)

    #just returns gaussian

    return scipy.stats.gaussian_kde(utraincounts)

def learn_simpleprob(traincounts):
    #just converts counts to dict
    count_dict = {}
    totalfreq = 0
    for t in traincounts:
        packetsize = t[0]
        packetfreq = t[1]
        count_dict[packetsize] = packetfreq
        totalfreq += packetfreq
    for k in count_dict.keys():
        count_dict[k] /= float(totalfreq)
    return count_dict

def prob(size, machine):
    #kde has weird behavior with discrete things?
    #use intervals
##    prob = (kde(size-0.1) + kde(size) + kde(size+0.1)) / 3
    if size in machine.keys():
        prob = machine[size]
    else:
        prob = 0

    prob = max(prob, 0.00001) #pseudocount
    return prob

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
#data is in this format:
#each data[i] is a class
#each data[i][j] is a standard-format sequence
#standard format is: each element is a pair (time, direction)

#uses 10-fold classification

tpc = 0 #true positive counts
tnc = 0 #true negative counts
pc = 0 #positive total
nc = 0 #negative total

traintime = 0
testtime = 0

a = time.time()
#Training:
#Rather than a KDE, each class is a simple probabilistic count
class_machines = []
#class_machines[i] is the machine for class i, it is a dictionary
#class_machines[i][j] (if exists) is the probability of packet size j
#sum of class_machines[i] should be 1

for i in range(0, len(traindata)): #cycle over each class
    counts = class_to_counts(traindata[i])
    class_machines.append(learn_simpleprob(counts))

#build IDF dictionary
idf_dict = {} #also build IDF dictionary. idf_dict{packetsize} = total freq over all documents
total_sinste = 0
for site in traindata:
    for inst in site:
        uniqpackets = []
        for packet in inst:
            if not(packet in uniqpackets):
                uniqpackets.append(packet)
        for packetsize in uniqpackets:
            if packetsize in idf_dict.keys():
                idf_dict[packetsize] += 1
            else:
                idf_dict[packetsize] = 1

        total_sinste += 1
##b = time.time()
##traintime += b - a

#Testing:
for s in range(0, len(testdata)): #cycle over each class
    for i in range(0, len(testdata[s])): #cycle over each instance
        testname = testnames[s][i]

        class_probs = [] #class_probs[i] is the score of class i for this sinste
        for t in range(0, len(traindata)):
            class_probs.append(0)

        testcounts = sinste_to_counts(testdata[s][i]) #reduce kde calls

        cosine_divider = 0
        for k in range(0, len(testcounts)):
            packetfreq = testcounts[k][1]
            cosine_divider += float(packetfreq * packetfreq)
        cosine_divider = math.sqrt(cosine_divider)

        for k in range(0, len(testcounts)): #cycle over each packet count
            packetsize = testcounts[k][0]
            packetfreq = testcounts[k][1]
            packetfreq = packetfreq/cosine_divider #cosine normalization
            packetfreq = math.log(1+packetfreq) #tf
            for sp in range(0, len(traindata)):
                p = prob(packetsize, class_machines[sp])
                lp = math.log(p)
                lp *= packetfreq

                #in our case idf does nothing
                class_probs[sp] += lp #later use min
                
        gs = class_probs.index(max(class_probs)) #guessed site
        
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
        
##        print "p", tpc, "/", pc,
##        print "n", tnc, "/", nc
        

##c = time.time()
##testtime += c - b
##
##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

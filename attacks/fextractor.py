import sys
import subprocess
import numpy
import os
from loaders import *

def extract(times, sizes, features):

    #Transmission size features
    features.append(len(sizes))

    count = 0
    for x in sizes:
        if x > 0:
            count += 1
    features.append(count)
    features.append(len(times)-count)

    features.append(times[-1] - times[0])

    #Unique packet lengths
##    for i in range(-1500, 1501):
##        if i in sizes:
##            features.append(1)
##        else:
##            features.append(0)

    #Transpositions (similar to good distance scheme)
    count = 0
    for i in range(0, len(sizes)):
        if sizes[i] > 0:
            count += 1
            features.append(i)
        if count == 500:
            break
    for i in range(count, 500):
        features.append("X")
        
    count = 0
    prevloc = 0
    for i in range(0, len(sizes)):
        if sizes[i] > 0:
            count += 1
            features.append(i - prevloc)
            prevloc = i
        if count == 500:
            break
    for i in range(count, 500):
        features.append("X")


    #Packet distributions (where are the outgoing packets concentrated)
    count = 0
    for i in range(0, min(len(sizes), 3000)):
        if i % 30 != 29:
            if sizes[i] > 0:
                count += 1
        else:
            features.append(count)
            count = 0
    for i in range(len(sizes)/30, 100):
        features.append(0)

    #Bursts
    bursts = []
    curburst = 0
    stopped = 0
    for x in sizes:
        if x < 0:
            curburst -= x
        if x > 0:
            if len(bursts) > 0:
                if bursts[-1] != curburst:
                    bursts.append(curburst)
            else:
                bursts.append(curburst)
    if (len(bursts) > 0):
        features.append(max(bursts))
        features.append(numpy.mean(bursts))
        features.append(len(bursts))
    else:
        features.append("X")
        features.append("X")
        features.append("X")
##    print bursts
    counts = [0, 0, 0, 0, 0, 0]
    for x in bursts:
        if x > 2:
            counts[0] += 1
        if x > 5:
            counts[1] += 1
        if x > 10:
            counts[2] += 1
        if x > 15:
            counts[3] += 1
        if x > 20:
            counts[4] += 1
        if x > 50:
            counts[5] += 1
    features.append(counts[0])
    features.append(counts[1])
    features.append(counts[2])
    features.append(counts[3])
    features.append(counts[4])
    features.append(counts[5])
    for i in range(0, 100):
        try:
            features.append(bursts[i])
        except:
            features.append("X")

    for i in range(0, 10):
        try:
            features.append(sizes[i] + 1500)
        except:
            features.append("X")

    itimes = [0]*(len(sizes)-1)
    for i in range(1, len(sizes)):
        itimes[i-1] = times[i] - times[i-1]
    features.append(numpy.mean(itimes))
    features.append(numpy.std(itimes))

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
    optfname = sys.argv[1]
    d = load_options(optfname)
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

traindata, trainnames = load_listn(d["TRAIN_LIST"])
testdata, testnames = load_listn(d["TEST_LIST"])
weightdata, weightnames = load_listn(d["WEIGHT_LIST"])

flist = []
for s in trainnames:
    for n in s:
        flist.append(n)

for s in testnames:
    for n in s:
        flist.append(n)

for s in weightnames:
    for n in s:
        flist.append(n)

if os.path.isfile(flist[0] + "f"):
    print flist[0] + "f already exists, fextractor.py stopping"
    sys.exit(0)

for fname in flist:
    if "-0.cell" in fname:
        print fname
    try:
        f = open(fname + "f", "r")
        continue
    except:
        pass
    f = open(fname, "r")
##        f = open(fold + fname + ".cell", "r")
    
    #Set up times, sizes
    times = []
    sizes = []
    for x in f:
##        sizes.append(int(x))
        x = x.split("\t")
        times.append(float(x[0]))
        sizes.append(int(x[1]))
    f.close()

    #Extract features. All features are non-negative numbers or X. 
    features = []
        
    try: 
        extract(times, sizes, features)

        fout = open(fname + "f", "w")
        for x in features:
            fout.write(repr(x) + " ")
        fout.close()
    except:
        pass

##    f = open("fdetails", "w")
##    f.write(str(len(features)))
##    print len(features)
##    f.close()

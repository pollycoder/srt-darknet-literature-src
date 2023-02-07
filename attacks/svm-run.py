import subprocess
import math
import sys
import time
from loaders import *

##for c_i in range(0, 10):
##    for g_i in range(0, 10):
##        cpow = (c_i - 5) * 2
##        gpow = (g_i - 5) * 2
##        c = math.pow(10, cpow)
##        g = math.pow(10, gpow)
##        cmd = "./svm-train "
##        cmd += "-c " + str(c) + " "
##        cmd += "-g " + str(g) + " "
##        cmd += "svm.train svm.model"
##        subprocess.call(cmd, shell=True)
##
##        cmd = "./svm-predict svm.test svm.model svm.results >> temp-acc"
##        subprocess.call(cmd, shell=True)
##
##        cmd = "grep Accuracy temp-acc"
##        s = subprocess.check_output(cmd, shell=True)
##        print c_i, g_i, c, g, s
##
##        cmd = "rm svm.results"
##        cmd = "rm temp-acc"
##        subprocess.call(cmd, shell=True)

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

log(sys.argv[0] + " " + sys.argv[1])
log(repr(d))
rlog(sys.argv[0] + " " + sys.argv[1])
rlog(repr(d))

of = d["OUTPUT_LOC"] #alias
f = open("svm-conf.results", "w") #clear the file
f.close()
[tpc, tnc, nc, pc] = [0, 0, 0, 0]
##traintime = 0
##testtime = 0
traindata, trainnames = load_listn(d["TRAIN_LIST"])
testdata, testnames = load_listn(d["TEST_LLIST"])

##for i in range(0, 10):
##    print i
c = math.pow(10, 2)
g = math.pow(10, -8)
a = time.time()
cmd = "python svm.py " + optfname
subprocess.call(cmd, shell=True)
print "Start training..."
cmd = "./svm-train -q -c " + str(c) + " -g " + str(g)
cmd += " " + of + "svm.train" +\
       " " + of + "svm.model"
subprocess.call(cmd, shell=True)
##b = time.time()
##traintime += b - a

f = open("svm-conf.results", "w") #clear the file
f.close()

print "Start testing..."
cmd = "./svm-predict " + of + "svm.test" +\
      " " + of + "svm.model" +\
      " " + of + "svm.results"
subprocess.call(cmd, shell=True)

##c = time.time()
##testtime += c - b

f = open("svm-conf.results", "r")
lines = f.readlines()
f.close()
site = 0
inst = 0
for line in lines:
    testname = testnames[site][inst]
    logmsg = "{}".format(site)
    inst += 1
    if inst >= len(testnames[site]):
        site += 1
        inst = 0
    li = line.split(" ")[:-1]
    
    class_probs = [] #class_probs[i] is the score of class i for this sinste
    for t in range(0, len(li)):
        class_probs.append(float(li[t]))
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

##log("Training time" + "\t" + str(traintime))
##log("Testing time" + "\t" + str(testtime))
log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))
    

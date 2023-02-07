import subprocess, sys, time, os
from loaders import *

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

##cmd = "rm WaOSAD-small-0.lev"
##subprocess.call(cmd, shell=True)

##cmd = "./clLev 2 0 " + str(optfname) + " WaOSAD-small-0.lev 0 1"
##subprocess.call(cmd, shell=True)bd

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
traindata, trainnames = load_listn(d["TRAIN_LIST"])
testdata, testnames = load_listn(d["TEST_LIST"])

#Some sanity checks, because Ca-OSAD is heavy

fname = d["LEV_LOC"] + d["LEV_METHOD"]

check_fail = 0

print "Checking lev distance files, generated with clLev..." + fname + "-0.lev", 
if (os.path.isfile(fname + "-0.lev")):
    print " YES"
else:
    print " NO"
    check_fail = 1
    
print "Checking matrix files, generated with clgen_stratify..." + fname + "-0.matrix", 
if (os.path.isfile(fname + "-0.matrix")):
    print " YES"
else:
    print " NO"
    check_fail = 1
    
print "Checking training file, generated with gen-lev-list.py..." + fname + ".train", 
if (os.path.isfile(fname + "-0.train")):
    print " YES"
else:
    print " NO"
    check_fail = 1

if (check_fail == 1):
    print "Some checks failed, aborting"
    sys.exit(0)

cmd = "rm " + fname + ".results " + fname + ".model"
subprocess.call(cmd, shell=True)
    
tpc = 0
tnc = 0
nc = 0
pc = 0

f = open("svm-conf.results", "w") #clear the file
f.close()
cmd = "./svm-train -q -t 4 -c 1024 " + \
      fname + ".train " + fname + ".model"
subprocess.call(cmd, shell=True)
cmd = "./svm-predict " + fname + ".test " + \
      fname + ".model " + fname + ".results"
subprocess.call(cmd, shell=True)

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

log("TPR:" + str(tpc) + "/" + str(pc))
log("TNR:" + str(tnc) + "/" + str(nc))

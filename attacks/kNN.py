import subprocess
import sys
import time
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
##a = time.time()
print "Extracting..."
cmd = "python fextractor.py " + optfname
subprocess.call(cmd, shell=True)
cmd = "rm flearner.log flearner.results"
subprocess.call(cmd, shell=True)
##b = time.time()
##extracttime = b - a
print "flearner..."
cmd = "./flearner " + optfname
subprocess.call(cmd, shell=True)

##f = open("flearner.log", "r")
##lines = f.readlines()
##f.close()
##for line in lines:
##    log(line[:-1])

f = open("flearner.results", "r")
lines = f.readlines()
f.close()
for line in lines:
    rlog(line)

##for i in range(0, len(lines)):
##    line = lines[i]
##    if "Training time" in line:
##        time = float(line.split("\t")[1])
##        lines[i] = "Training time\t" + str(time + extracttime) + "\n"
##    if "Testing time" in line:
##        time = float(line.split("\t")[1])
##        lines[i] = "Testing time\t" + str(time + extracttime) + "\n"

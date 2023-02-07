#for lev, we don't generate trainlist and testlist
#instead, we just combine pre-generated matrices (clgen_stratify)
import subprocess, sys
from loaders import *

try:
    d = load_options(sys.argv[1])
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

attacks = ["lev-files/WaOSAD-heavy", "lev-files/CaOSAD-heavy"]
for attack in attacks:
    if (d["FOLD_MODE"] == 3):
        cmdtest = "cat "
        cmdtrain = "cat "
        for i in range(0, 10):
            if i == d["FOLD_NUM"]:
                cmdtest += attack + "-" + str(i) + ".matrix "
            else:
                cmdtrain += attack + "-" + str(i) + ".matrix "
        cmdtest += "> " + attack + ".test"
        cmdtrain += "> " + attack + ".train"
        subprocess.call(cmdtest, shell=True)
        subprocess.call(cmdtrain, shell=True)

#this should just be a duplicate of Ca-OSAD.py

import subprocess, sys
cmd = "python Ca-OSAD.py {}".format(sys.argv[1])
subprocess.call(cmd, shell=True)

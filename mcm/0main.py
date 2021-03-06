import os
import argparse
import pandas
import sys
import shutil
import time
import numpy as np
from subprocess import Popen

import func as mcfn

# Preliminaries
pyenv, bashenv, mercuryOG_path, rslts_path = mcfn.read_envfile("envfile.txt", "all")
if rslts_path.endswith("/"):
    rslts_path = rslts_path[:-1]
if mercuryOG_path.endswith("/"):
    mercuryOG_path = mercuryOG_path[:-1]

parser = argparse.ArgumentParser()
parser.add_argument('--no_runs', '-no',
                    dest='N_runs',
                    action='store')
parser.add_argument('--process_no', '-pno',
                    dest='process_no',
                    action='store')
args = parser.parse_args()

N_runs = int(args.N_runs)
pno = str(args.process_no)

# Test for nominal resonance directory
mcfn.make_rsltpath(rslts_path)

# Count the number of files which exist already
n_completed = mcfn.count_completed(rslts_path)

# Create instance of mercury
m_inst = mcfn.MercuryInstance(pno, mercuryOG_path)
m_inst.create()

# Main loop
k = 0
while k < N_runs:
    time.sleep(np.random.uniform(0, 5))

    # Count completed
    n_completed = mcfn.count_completed(rslts_path)
    print(" n_completed = {}\n".format(n_completed))

    # Generate small.in
    p_randomize = Popen([pyenv, "randomize.py", "-pno", pno, "-k", str(n_completed), "-btype", "small"])
    p_randomize.wait()

    # Generate big.in
    p_randomize = Popen([pyenv, "randomize.py", "-pno", pno, "-k", str(n_completed), "-btype", "big"])
    p_randomize.wait()

    # Clean up old files from mercury dir
    p_cleanup = Popen([bashenv, "cleanup.sh", pno])
    p_cleanup.wait()

    # Execute Mercury
    p_launch_mercury = Popen([bashenv, "launch_mercury.sh", pno])
    p_launch_mercury.wait()

    # Copy files
    shutil.copyfile("mercury_{}/xv.out".format(pno), "{}/outputs/{}-xv.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/ce.out".format(pno), "{}/outputs/{}-ce.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/info.out".format(pno), "{}/outputs/{}-info.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/big.in".format(pno), "{}/inputs/{}-big.in".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/small.in".format(pno), "{}/inputs/{}-small.in".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/param.in".format(pno), "{}/inputs/{}-param.in".format(rslts_path, n_completed))

    k +=1

    # Get status
    if os.path.exists("status.txt"):
        f = open("status.txt", 'r')
        curr_n = int(f.read())
        f.close()
        new_n = curr_n + 1
        try:
            os.remove("status.txt")
        except:
            pass
    else:
        new_n = 1
    f = open("status.txt", 'w')
    f.write(str(new_n))
    f.close()
    time.sleep(np.random.uniform(0, 5))

# Destroy mercury instance
m_inst.destroy()

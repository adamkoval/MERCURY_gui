import os
import argparse
import pandas
import sys
import shutil
from subprocess import Popen

import func as mcfn

pyenv, bashenv, mercuryOG_path, rslts_path = mcfn.read_envfile("envfile.txt")
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
m_inst = mcfn.mercury_instance(pno, mercuryOG_path)
m_inst.create()

# Main loop
k = 0
while k < N_runs:
    #print(" ~~~~~~~~~~~~~~~~~~~~~~~~\n",
    #      "0main.py:\n",
    #      "Run = {}\n".format(k))

    ## Randomizing input
    #p_randomize = Popen([pyenv, "randomize.py", "-res", res_str, "-pno", pno])
    #p_randomize.wait()

    # Cleaning up old files from mercury dir
    p_cleanup = Popen([bashenv, "cleanup.sh", pno])
    p_cleanup.wait()

    # Execute Mercury
    p_launch_mercury = Popen([bashenv, "launch_mercury.sh", pno])
    p_launch_mercury.wait()

    n_completed = mcfn.count_completed(rslts_path)
    print(" n_completed = {}\n".format(n_completed))
    #print(" Mercury completed, copying files\n",
    #      "~~~~~~~~~~~~~~~~~~~~~~~~\n")

    shutil.copyfile("mercury_{}/xv.out".format(pno), "{}/outputs/{}-xv.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/ce.out".format(pno), "{}/outputs/{}-ce.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/info.out".format(pno), "{}/outputs/{}-info.out".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/big.in".format(pno), "{}/inputs/{}-big.in".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/small.in".format(pno), "{}/inputs/{}-small.in".format(rslts_path, n_completed))
    shutil.copyfile("mercury_{}/param.in".format(pno), "{}/inputs/{}-param.in".format(rslts_path, n_completed))

    k +=1

# Destroy mercury instance
m_inst.destroy()

#!/usr/bin/env python
# Usage: ./genjobs_ga_vs_gurobi.py

import os
import bs_helpers.instancefiltering

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-SOLVER-j30
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=0:35:00
#PBS -l mem=32gb
#PBS -q all
#PBS -W x=PARTITION:tane

module load GCC/7.3.0-2.30
module load Gurobi/7.5.2

cd $PBS_O_WORKDIR
./CPP-RCPSP-OC/CPP-RCPSP-OC SOLVER 1800 -1 INSTANCE timeforbks
"""


def write_script(fn, solvername):
    with open("solvescript_" + fn.replace('.sm', '') + "_" + solvername + "_generated.sh", "w") as fp:
        scr_str = contents.replace("INSTANCE", 'j30/' + fn).replace('SOLVER', solvername)
        fp.write(scr_str)


if __name__ == '__main__':
    for fn in [f for f in os.listdir('j30') if f.endswith('.sm')]:
        if bs_helpers.instancefiltering.is_entry_relevant("j30", fn, False):
            for solvername in ['GA0', 'GA3']:
                write_script(fn, solvername)

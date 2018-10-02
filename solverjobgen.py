#!/usr/bin/env python
# Usage: ./solverjobgen.py

import sys
import os

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-SOLVER-j30
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=200:00:00
#PBS -l mem=64gb
#PBS -q all

module load GAMS/24.7.4
module load Gurobi/7.5.2

cd $PBS_O_WORKDIR
gams modelcli.gms --instname=INSTANCE --iterlim=2e9 --timelimit=719940 --solver=SOLVER --trace=0 --nthreads=1 --outpath=tempoutpath
"""

def write_script(fn, solvername):
    with open("solvescript_" + fn.replace('.sm', '') + "_" + solvername + "_generated.sh", "w") as fp:
        fp.write(contents.replace("INSTANCE", 'j30gdx/'+fn).replace('SOLVER', solvername))

if __name__ == '__main__':
    for fn in [ f.replace('.gdx', '') for f in os.listdir('j30gdx') if f.endswith('.gdx') ]:
        for solvername in ['GUROBI', 'CPLEX', 'SCIP']:
            write_script(fn, solvername)

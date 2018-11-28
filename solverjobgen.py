#!/usr/bin/env python
# Usage: python solverjobgen.py set_name solver1 solver2 ...

import sys
import os

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-SOLVER_NAMES-SET_NAME
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=200:00:00
#PBS -l mem=32gb
#PBS -q all
#PBS -W x=PARTITION:tane

module load GAMS/24.7.4
module load Gurobi/7.5.2

cd $PBS_O_WORKDIR

"""

def write_script(fn, solver_names, set_name):
    instance_name = fn.replace('.sm.gdx', '')
    snames_str = '_'.join(solver_names)
    with open(f'solvescript_{instance_name}_'+snames_str+'_generated.sh', 'w') as fp:
        solver_calls = [ f'gams modelcli.gms --instname=INSTANCE --iterlim=2e9 --timelimit=230000 --solver={solver_name} --trace=0 --nthreads=1 --outpath=tempoutpath' for solver_name in solver_names ]
        fp.write((contents+'\n'.join(solver_calls)).replace("INSTANCE", set_name+'gdx/'+fn.replace('.gdx', '')).replace('SOLVER_NAMES', snames_str).replace('SET_NAME', set_name))

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('Usage: python solverjobgen.py set_name solver1 solver2 ...')
        print('Example: python solverjobgen.py j30 GUROBI CPLEX SCIP')
        exit(0)
    set_name = sys.argv[1]
    solver_selection = sys.argv[2:]
    for fn in [ f for f in os.listdir(set_name+'gdx') if f.endswith('.gdx') ]:
        write_script(fn, solver_selection, set_name)

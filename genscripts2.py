#!/usr/bin/env python
# Usage: ./genscripts2.py

import sys
import os

contents = """
#!/bin/bash -login
#PBS -N GA0_j120_INDEX
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=06:00:00
#PBS -l mem=16gb
#PBS -W x=PARTITION:lena
#PBS -q all

module load gcc/6.2.0
cd $PBS_O_WORKDIR
python cluster_batchsolve.py batch j120_INDEX 1800 -1
"""

def gen_script(index):
	script_contents = contents.replace('INDEX', str(index))
	with open("solvescript"+str(index)+"_generated.sh", "w") as fp:
		fp.write(script_contents)
        
for i in range(60): gen_script(i+1)

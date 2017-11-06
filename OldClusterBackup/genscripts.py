#!/usr/bin/env python
# Usage: ./genscripts.py modelFilename jobsize

import sys

contents = """
#!/bin/bash -login
#PBS -N RCPSPOC-j30-MODEL_FILENAME-START_IX-END_IX
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m ae
#PBS -j oe
#PBS -l nodes=1:ppn=8
#PBS -l walltime=130:00:00
#PBS -l mem=16gb

# show which computer the job ran on
echo "Job ran on:" $(hostname)
# load the relevant modules
module load gams
# change to work dir
cd $PBS_O_WORKDIR
 # correctly specify the number of cores in cplex.opt!!
 # the program to run
python batchsolve.py MODEL_FILENAME j30gdx START_IX END_IX
"""

def gen_script(modelFilename, six, eix):
	script_contents = contents.replace("START_IX", str(six)).replace("END_IX", str(eix)).replace("MODEL_FILENAME", modelFilename)
	with open("solvescript"+str(six)+"-"+str(eix)+"_generated.sh", "w") as fp:
		fp.write(script_contents)

modelFilename = sys.argv[1]
jobsize = int(sys.argv[2])
NUM_PROJS = 480
six = 0
while six < NUM_PROJS:
	eix = six + jobsize - 1
	if eix >= NUM_PROJS:
		eix = NUM_PROJS - 1
	gen_script(modelFilename, six, eix)		
	six = eix + 1

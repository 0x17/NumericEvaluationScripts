#!/usr/bin/env python
# Usage: ./genscripts_srcfile.py modelFilename srcFile

import sys

contents = """#!/bin/bash -login
#PBS -N RCPSPOC-j30-MODEL_FILENAME-INST_NAME
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m ae
#PBS -j oe
#PBS -l nodes=1:ppn=8
#PBS -l walltime=200:00:00
#PBS -l mem=16gb

# show which computer the job ran on
echo "Job ran on:" $(hostname)
# load the relevant modules
module load gams
# change to work dir
cd $PBS_O_WORKDIR
 # correctly specify the number of cores in cplex.opt!!
 # the program to run
gams MODEL_FILENAME lo=2 --instname=INST_NAME
"""

def gen_script(modelFilename, instName):
	script_contents = contents.replace("INST_NAME", instName).replace("MODEL_FILENAME", modelFilename)
	with open("solvescript_"+instName.replace("j30gdx/", "")+"_generated.sh", "w") as fp:
		fp.write(script_contents)

modelFilename = sys.argv[1]
srcFile = sys.argv[2]

with open(srcFile, "r") as fp:
	for line in fp:
		gen_script(modelFilename, "j30gdx/"+line.replace(".gdx", "").replace("\n", ""))

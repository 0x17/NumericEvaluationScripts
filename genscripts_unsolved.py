#!/usr/bin/env python
# Usage: ./genscripts_unsolved.py modelFilename

import sys
import os

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-MODEL_FILENAME-j30
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=96:00:00
#PBS -l mem=62gb
#PBS -q all

echo "Job ran on:" $(hostname)

module load gams

cd $PBS_O_WORKDIR

gams MODEL_FILENAME lo=2 --nthreads=1 --trace=0 --timelimit=337000 --solver=CPLEX --instname=INSTANCE
"""

EXT = ".gdx"

def gdx_files(path):
	return map(lambda f: path + "/" + f, filter(lambda f: f.endswith(EXT), os.listdir(path)))

def rem_ext(fn):
	return fn.replace(EXT, "")

def gen_script(modelFilename, instance):
	script_contents = contents.replace("INSTANCE", instance).replace("MODEL_FILENAME", modelFilename)
	instance_core = instance.replace('j30gdx/', '').replace('.sm', '')
	with open("solvescript_"+instance_core+"_generated.sh", "w") as fp:
		fp.write(script_contents)
		
RESULT_FILE = 'GMS_CPLEX_Results.txt'
		
def not_already_solved(fn):
	with open(RESULT_FILE, 'r') as fp:
		lines = fp.readlines()
		for line in lines:
			if line.startswith(fn):
				return False
	return True			

modelFilename = sys.argv[1]
all_files = list(map(rem_ext, gdx_files('j30gdx')))
unsolved_files = list(filter(not_already_solved, all_files))
for f in unsolved_files:
	gen_script(modelFilename, rem_ext(f))

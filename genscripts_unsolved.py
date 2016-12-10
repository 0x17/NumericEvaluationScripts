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
#PBS -l nodes=1:ppn=8
#PBS -l walltime=1:30:00
#PBS -l mem=62gb
#PBS -W x=PARTITION:lena
#PBS -q all

module load gams
cd $PBS_O_WORKDIR
gams MODEL_FILENAME lo=4 --nthreads=0 --trace=0 --timelimit=3600 --iterlim=2000000000 --solver=CPLEX --instname=INSTANCE --outpath=j30res
"""

EXT = ".gdx"


def gdx_files(path):
    return map(lambda f: path + "/" + f, filter(lambda f: f.endswith(EXT), os.listdir(path)))


def remove_extension(fn):
    return fn.replace(EXT, "")


def core_instance_name(fn):
    return fn.replace('j30gdx/', '').replace('.sm', '')


def insert_placeholders(modelFilename, instance):
    return contents.replace("INSTANCE", instance).replace("MODEL_FILENAME", modelFilename)


def gen_script(modelFilename, instance):
    with open("solvescript_" + core_instance_name(instance) + "_generated.sh", "w") as fp:
        fp.write(insert_placeholders(modelFilename, instance))


def not_already_solved(fn):
    instName = core_instance_name(fn)
    RESULT_FILE = 'GurobiOptimals.txt'
    with open(RESULT_FILE, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if line.startswith(instName):
                return False
    return True


modelFilename = sys.argv[1] if len(sys.argv) >= 2 else "modelcli.gms"
all_files = list(map(remove_extension, gdx_files('j30gdx')))
#unsolved_files = list(filter(not_already_solved, all_files))
unsolved_files = all_files
for f in unsolved_files:
    gen_script(modelFilename, remove_extension(f))

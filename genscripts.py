#!/usr/bin/env python
# Usage: ./genscripts.py modelFilename jobsize

import sys

contents = """
#!/bin/bash -login
#PBS -N j30-MODEL_FILENAME-START_IX-END_IX
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m abe
#PBS -j oe
#PBS -l nodes=1:ppn=4
#PBS -l walltime=128:00:00
#PBS -l mem=32gb
#PBS -q all

echo "Job ran on:" $(hostname)

module load gams

cd $PBS_O_WORKDIR

python batchGAMSrng.py MODEL_FILENAME j30gdx START_IX END_IX
"""


def gen_script(modelFilename, six, eix):
    script_contents = contents.replace("START_IX", str(six)).replace("END_IX", str(eix)).replace("MODEL_FILENAME",
                                                                                                 modelFilename)
    with open("solvescript" + str(six) + "-" + str(eix) + "_generated.sh", "w") as fp:
        fp.write(script_contents)


modelFilename = sys.argv[1]
jobsize = int(sys.argv[2])
NUM_PROJS = 329
six = 0
while six < NUM_PROJS:
    eix = six + jobsize - 1
    if eix >= NUM_PROJS: eix = NUM_PROJS - 1
    gen_script(modelFilename, six, eix)
    six = eix + 1

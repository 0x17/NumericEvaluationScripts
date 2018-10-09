#!/usr/bin/env python
# Usage: ./genjobs_ga_vs_gurobi.py

import os
import bs_helpers.instancefiltering

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-SOLVER-SET_NAME
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


def build_res_cache(method_selection):
    def instances(mn):
        fn = mn + '_results.txt'
        if os.path.isfile(fn):
            with open(fn, 'r') as fp:
                return [line.split(';')[0] for line in fp.readlines()]
        else:
            return []

    return {mn: instances(mn) for mn in method_selection}


def instance_already_solved_with_method(instance_fn, method_name, result_cache):
    return instance_fn in result_cache[method_name]


def write_script(set_name, fn, solvername):
    with open("solvescript_" + fn.replace('.sm', '') + "_" + solvername + "_generated.sh", "w") as fp:
        scr_str = contents.replace("INSTANCE", set_name + '/' + fn).replace('SOLVER', solvername).replace('SET_NAME', set_name)
        fp.write(scr_str)


if __name__ == '__main__':
    method_selection = ['GA0', 'GA3', 'GA4', 'Gurobi']
    res_cache = build_res_cache(method_selection)
    set_name = 'j120'
    for fn in [f for f in os.listdir(set_name) if f.endswith('.sm')]:
        if bs_helpers.instancefiltering.is_entry_relevant(set_name, fn, False):
            for solvername in method_selection:
                if not instance_already_solved_with_method(fn, solvername, res_cache):
                    write_script(set_name, fn, solvername)

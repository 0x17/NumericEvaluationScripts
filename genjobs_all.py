#!/usr/bin/env python
# Usage: ./genjobs_all.py

import os
import sys
import bs_helpers.instancefiltering

contents = """
#!/bin/bash -login
#PBS -N INSTANCE-SOLVER-SET_NAME
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=3:00:00
#PBS -l mem=32gb
#PBS -q all
#PBS -W x=PARTITION:tane

module load GCC/7.3.0-2.30
module load Gurobi/7.5.2

cd $PBS_O_WORKDIR

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


def write_script(set_name, fn, solvernames):
    with open("solvescript_" + fn.replace('.sm', '') + "_" + '_'.join(solvernames) + "_generated.sh", "w") as fp:
        scr_str = contents.replace("INSTANCE", set_name + '/' + fn).replace('SET_NAME', set_name).replace('SOLVER', '_'.join(solvernames))
        for sn in solvernames:
            scr_str += './CPP-RCPSP-OC/CPP-RCPSP-OC SOLVER 1800 -1 INSTANCE timeforbks\n'.replace('SOLVER', sn).replace('INSTANCE', set_name + '/' + fn)
        fp.write(scr_str)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: python genjobs_all.py Method1 Method2 ...')
        exit(0)
    one_method_per_job = False
    method_selection = sys.argv[1:]
    res_cache = build_res_cache(method_selection)
    set_name = 'k120'
    for fn in [f for f in os.listdir(set_name) if f.endswith('.sm')]:
        if bs_helpers.instancefiltering.is_entry_relevant(set_name, fn, False):
            methods_to_do = [ solvername for solvername in method_selection if not instance_already_solved_with_method(fn, solvername, res_cache) ]
            if one_method_per_job:
                for mn in methods_to_do:
                    write_script(set_name, fn, [mn])
            else:
                write_script(set_name, fn, methods_to_do)

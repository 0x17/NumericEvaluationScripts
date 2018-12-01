#!/usr/bin/env python

import os

contents = """
#!/bin/bash -login
#PBS -N JOBNAME
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=24:00:00
#PBS -l mem=48gb
#PBS -W x=PARTITION:tane
#PBS -q all

echo "Job ran on:" $(hostname)

module load GAMS/24.5.4

cd $PBS_O_WORKDIR
gams MODEL_FILENAME lo=4 --nthreads=1 --timelimit=716400 --iterlim=2000000000 --solver=GUROBI --instname=INSTANCE
"""


def instance_filenames(path):
    return [path + '/' + f for f in os.listdir(path) if f.endswith('.gdx')]


def gen_script(name, mapping):
    script_contents = contents
    for k, v in mapping.items():
        script_contents = script_contents.replace(k, v)
    with open("solvescript_" + name + "_generated.sh", "w") as fp:
        fp.write(script_contents)


def str_batch_rem(s, substrs):
    os = s
    for substr in substrs:
        os = os.replace(substr, '')
    return os


def already_solved_genfunc():
    def res_for(model_name_infix):
        with open('GMS_GUROBI_' + model_name_infix + '_Results.txt', 'r') as fp:
            return [line.split()[0] for line in fp.readlines() if len(line.strip())>0 ]

    cache = {'pritsker': res_for('Pritsker'), 'ctab': res_for('CTAB')}
    return lambda model_name, instance_fn: instance_fn.replace('.gdx', '') in cache[model_name]


def main():
    already_solved = already_solved_genfunc()
    instances_path = 'j30gdx_new'
    for model_name in ['pritsker', 'ctab']:
        for instance_fn in instance_filenames(instances_path):
            instance_name_core = str_batch_rem(instance_fn, [instances_path + '/', '.sm', '.gdx'])
            if already_solved(model_name, instance_fn): continue
            gen_script(model_name + '_' + instance_name_core,
                       {'MODEL_FILENAME': 'modelcli_rcpsp_' + model_name + '.gms',
                        'INSTANCE': instance_fn.replace('.gdx', ''),
                        'JOBNAME': instance_name_core + '_' + model_name})


if __name__ == '__main__':
    main()

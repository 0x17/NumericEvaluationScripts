#!/usr/bin/env python

import os
import solverjobgen

solver_names = ['GUROBI', 'CPLEX', 'SCIP']


def parse_results():
    def res_dict(parts):
        return {'obj': parts[0], 'solvetime': parts[1]}

    results = {}
    for solver_name in solver_names:
        with open('GMS_' + solver_name + '_ExtendedResults.txt', 'r') as fp:
            results[solver_name] = {line.split()[0]: res_dict(line.split()[1:]) for line in fp.readlines()}
    return results


def list_unsolved_instance_solver_pairs():
    results = parse_results()
    instance_names = ['j30gdx/' + f.replace('.gdx', '') for f in os.listdir('j30gdx') if f.endswith('.gdx')]
    unsolved = []

    for instance_name in instance_names:
        for solver_name in solver_names:
            if instance_name not in results[solver_name]:
                unsolved.append((instance_name, solver_name))

    return unsolved


def generate_job_scripts(unsolved_pairs):
    for instance_name, solver_name in unsolved_pairs:
        solverjobgen.write_script(instance_name.replace('j30gdx/', ''), solver_name)


def write_unsolved_to_file(unsolved):
    with open('unsolved_pairs.txt', 'w') as fp:
        fp.write('\n'.join([instance_name + ' ' + solver_name for instance_name, solver_name in unsolved]))


if __name__ == '__main__':
    unsolved = list_unsolved_instance_solver_pairs()
    # write_unsolved_to_file(unsolved)
    generate_job_scripts(unsolved)

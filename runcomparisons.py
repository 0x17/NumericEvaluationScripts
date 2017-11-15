#!/bin/env python

import os
import shutil
import json


def maybe_read_json(fn):
    if os.path.exists(fn):
        with open(fn) as fp:
            return json.load(fp)
    else:
        return {}


def opt_or_default(opts, key, default):
    return opts[key] if key in opts else default


opts = maybe_read_json('options.json')
combos = opt_or_default(opts, 'combos', [('TPC', 'best'), ('OPC', 'duel')])
slimits = opt_or_default(opts, 'slimits', [1000, 5000, 50000])


def my_system(s):
    print(s)
    os.system(s)


def my_move(src, dest):
    print('src=%s, dest=%s' % (src, dest))
    shutil.move(src, dest)


def rename_for_reference(nschedules, crossover_scheme, selection_scheme):
    out_path = 'j30_' + str(nschedules) + 'schedules'
    if os.path.exists(out_path):
        my_move(out_path, out_path + '_' + crossover_scheme + '_' + selection_scheme)


def my_write(fp, s):
    print(s)
    fp.write(s)


# OPC best sind standard ergebnisse j30 slimit
for crossover_scheme, selection_scheme in combos:
    for nschedules in slimits:
        with open('GAParameters.json', 'w') as fp:
            obj = {'selectionMethod': selection_scheme, 'crossoverMethod': crossover_scheme}
            my_write(fp, json.dumps(obj, indent=4, sort_keys=True))
        my_system('python batchsolve.py batch j30 -1 ' + str(nschedules))
        os.remove('GAParameters.json')
        rename_for_reference(nschedules, crossover_scheme, selection_scheme)

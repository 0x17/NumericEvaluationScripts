#!/bin/env python

import os
import shutil

for crossover_scheme in ['OPC', 'TPC']:
    for nschedules in [1000, 5000, 50000]:
        with open('GAParameters.json', 'w') as fp:
            fp.write('{ "selectionMethod": "best",\n"crossoverMethod":"' + crossover_scheme + '" }\n')
        os.system('python batchsolve.py batch j30 -1 ' + str(nschedules))
		os.remove('GAParameters.json')
        out_path = 'j30_' + str(nschedules) + 'schedules'
        if os.path.exists(out_path):
            shutil.move(out_path, out_path + crossover_scheme)
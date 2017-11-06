#!/bin/env python

import os
import shutil

for selection_scheme in ['duel']:
    for nschedules in [1000, 5000, 50000]:
        with open('GAParameters.json', 'w') as fp:
            fp.write('{"selectionMethod": "' + selection_scheme + '",\n"crossoverMethod": "TPC" }\n')
        os.system('python batchsolve.py batch j30 -1 ' + str(nschedules))
		os.remove('GAParameters.json')
        out_path = 'j30_' + str(nschedules) + 'schedules'
        if os.path.exists(out_path):
            shutil.move(out_path, out_path + 'TPC' + selection_scheme)

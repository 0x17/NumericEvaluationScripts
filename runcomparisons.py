#!/bin/env python

import os
import shutil
import json

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

for crossover_scheme in ['OPC', 'TPC']:
	for selection_scheme in ['best', 'duel']:
		for nschedules in [1000, 5000, 50000]:
			with open('GAParameters.json', 'w') as fp:
				obj = { 'selectionMethod': selection_scheme, 'crossoverMethod': crossover_scheme }
				fp.write(json.dumps(obj, indent=4, sort_keys=True))				
			my_system('python batchsolve.py batch j30 -1 ' + str(nschedules))
			os.remove('GAParameters.json')
			rename_for_reference(nschedules, crossover_scheme, selection_scheme)
			

#!/bin/env python

import os
import shutil

SCHEDULE_LIMITS = [1000, 5000, 50000]
COMMON_PREFIX = 'j30_'
COMMON_INFIX = 'schedules_'

tuples = []
for crossover_method, selection_method in [('OPC', 'duel'), ('TPC', 'best')]:
    for lim in SCHEDULE_LIMITS:
        tuples.append((crossover_method, selection_method, lim, COMMON_PREFIX + str(lim) + COMMON_INFIX + crossover_method + '_' + selection_method))

DEST_DIR = 'j30_vsmerged'
RESULT_FN = 'GA4Results.txt'

if not os.path.exists(DEST_DIR):
    os.mkdir(DEST_DIR)

for tuple in tuples:
    src_dir = tuple[3] + '/' + RESULT_FN
    dest_dir = DEST_DIR + '/GA4Results_' + tuple[0] + '_' + tuple[1] + '_' + str(tuple[2]) + '.txt'
    shutil.copy(src_dir, dest_dir)

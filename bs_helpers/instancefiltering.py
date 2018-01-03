import os
from bs_helpers import utils, globals


def opt_exists(fn, resultsfile):
    with open(resultsfile, 'r') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            if parts[0] + '.sm' == fn:
                return True
    return False


def min_max_makespan_not_equal(fn):
    utils.syscall('java -jar MinMaxMakespan.jar ' + globals.outPath + ' ' + fn)

    if os.path.isfile(globals.skipfilePath):
        print('Equal min/max-makespan for ' + fn)
        os.remove(globals.skipfilePath)
        return False

    return True


def is_entry_relevant(directory_name, fn, only_optimally_solved):
    return fn.endswith('.sm') and min_max_makespan_not_equal(directory_name + '/' + fn) and (
            not only_optimally_solved or opt_exists(fn, 'GMS_CPLEX_Results.txt'))

import os
import sys


def arg_passed(arg):
    return not [carg for carg in sys.argv if carg == arg]


versus_comparison = arg_passed('vs')
big_instances = arg_passed('j120')

RESULT_SUFFIX = 'Results.txt'
additionalResultFile = ['../GA4Results_Ref1800secs.txt'] if big_instances else ['../GMS_CPLEX_Results.txt']
# additionalResultFile = []
REFERENCE_INSTANCE = 'GA4Results_OPC_duel_1000.txt' if versus_comparison else 'GA0Results.txt'


def compose_result_files():
    result_files = []  # ['Gurobi']
    for ga_index in [0, 3, 4]:
        result_files.append('GA' + str(ga_index))
    for ls_index in [0, 3, 4]:
        result_files.append('LocalSolverNative' + str(ls_index))
    return list(map(lambda rf: rf + RESULT_SUFFIX, result_files)) + additionalResultFile


def compose_result_files_for_vs_comparison():
    result_files = []

    # combos = [('OPC', 'duel'), ('TPC', 'best')]
    combos = [(crossover_method, selection_method) for crossover_method in ['OPC', 'TPC'] for selection_method in
              ['best', 'duel']]
    slimits = [1000, 5000, 50000, 100000]

    for lim in slimits:
        for crossover_method, selection_method in combos:
            fname = 'GA4Results_' + crossover_method + '_' + selection_method + '_' + str(lim) + '.txt'
            if os.path.exists(fname):
                result_files.append(fname)

    return result_files + ['../GMS_CPLEX_Results.txt']


def parse_column(fn, ix):
    col = []
    with open(fn) as f:
        for line in f.readlines():
            parts = line.split(';')
            col.append(parts[ix].strip())
    return col


def parse_instances(fn): return parse_column(fn, 0)


def parse_results(fn):
    if fn == '../GMS_CPLEX_Results.txt':
        instances = parse_instances(REFERENCE_INSTANCE)
        results = []
        with open('../GMS_CPLEX_Results.txt', 'r') as fp:
            lines = fp.readlines()
            for instance in instances:
                for line in lines:
                    if line.split(';')[0] == instance:
                        results.append(line.split(';')[1].replace('\n', ''))
                        break
        return results

    return parse_column(fn, 1)


rfiles = compose_result_files_for_vs_comparison() if versus_comparison else compose_result_files()
resultlines = list(map(parse_results, rfiles))
instances = parse_instances(rfiles[0])

assert (all(len(instances) == len(col) for col in resultlines))


def correct_separator(ix, coll):
    if ix < len(coll) - 1:
        return ';'
    else:
        return '\n'


with open('merged.txt', 'w') as f:
    f.write('instance;')
    for i in range(len(rfiles)):
        f.write(rfiles[i].replace(RESULT_SUFFIX, '') + correct_separator(i, rfiles))

    for i in range(len(instances)):
        resStr = resultlines[0][i]
        f.write(instances[i] + ';')
        for m in range(len(resultlines)):
            f.write(resultlines[m][i].replace('.', ',') + correct_separator(m, resultlines))

# j120
#additionalResultFile = ['../GA4Results_Ref1800secs.txt']
# j30
additionalResultFile = ['../GMS_CPLEX_Results.txt']
# additionalResultFile = []

RESULT_SUFFIX = 'Results.txt'
#REFERENCE_INSTANCE = 'GA0Results.txt'
REFERENCE_INSTANCE = 'GA4Results_OPC_duel_1000.txt'
# REFERENCE_INSTANCE = 'GA4Results_best_1000.txt'


def compose_result_files():
    result_files = []  # ['Gurobi']
    for ga_index in [0, 3, 4]:
        result_files.append('GA' + str(ga_index))
    for ls_index in [0, 3, 4]:
        result_files.append('LocalSolverNative' + str(ls_index))
    return list(map(lambda rf: rf + RESULT_SUFFIX, result_files)) + additionalResultFile


def compose_result_files_for_vs_comparison():
    result_files = []
    for lim in [1000, 5000, 50000]:
        for crossover_method, selection_method in [('OPC', 'duel'), ('TPC', 'best')]:
            result_files.append('GA4Results_' + crossover_method + '_' + selection_method + '_' + str(lim) + '.txt')
    result_files.append('../GMS_CPLEX_Results.txt')
    return result_files


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


#rfiles = compose_result_files()
rfiles = compose_result_files_for_vs_comparison()
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

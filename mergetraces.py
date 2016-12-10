import os
import numpy

NUM_SECONDS = 30
SET_NAME = 'j30'
RESULTS_DIR = './'+SET_NAME+'_'+str(NUM_SECONDS)+'secs/'
OPTS_EXIST = True

###############################################################
# GLOBALS
###############################################################

optimalObjectives = {}

#REF_RESULTSFILE = RESULTS_DIR + 'REF_GMS_CPLEX_Results.txt'
#REF_RESULTSFILE = 'GA4Results_Ref1800secs.txt'
REF_RESULTSFILE = 'GMS_CPLEX_Results.txt'

if OPTS_EXIST:
    with open(REF_RESULTSFILE, 'r') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            optimalObjectives[parts[0]] = float(parts[1])

trace_suffix = 'Trace_'
methodPrefixes = list(map(lambda mpf: mpf + trace_suffix, ['Gurobi', 'GATimeWindowBordersGA', 'GAFixedCapacityGA', 'GATimeVaryingCapacityGA', 'GAGoldenCutSearchGA', 'LocalSolverNative0', 'LocalSolverNative3', 'LocalSolverNative4', 'LocalSolverNative6']))

###############################################################
# METHODS
###############################################################
lines_cache = {}

results_files = list(map(lambda fn: RESULTS_DIR + fn,
                         list(filter(lambda fn: fn.endswith('Results.txt'), list(os.listdir(RESULTS_DIR))))))


def extract_profit_for_instance(instance_name, lines):
    for line in lines:
        parts = line.split(';')
        if parts[0] == instance_name:
            return float(parts[1])
    return 0.0


def best_known_solution_for_instance(instance_name):
    best_obj = 0.0
    for rfn in results_files:
        with open(rfn, 'r') as rfp:
            obj = extract_profit_for_instance(instance_name, rfp.readlines())
            if obj >= best_obj:
                best_obj = obj
    return best_obj


if not (OPTS_EXIST):
    with open(RESULTS_DIR + 'GA0Results.txt') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            optimalObjectives[parts[0].replace(SET_NAME+'/', '')] = best_known_solution_for_instance(parts[0])


def readlines_cached(filename):
    global lines_cache
    if not ('filename' in lines_cache):
        with open(RESULTS_DIR + filename, 'r') as fp:
            lines_cache[filename] = fp.readlines()

    return lines_cache[filename]


def trace_filename_to_instance_name(method_prefix, filename):
    return filename.replace(method_prefix, '').replace('.txt', '').replace(SET_NAME + '/', '')


def gap_in_cplex_trace_file_in_second(filename, sec):
    instance_name = trace_filename_to_instance_name('CPLEXTrace_', filename)
    optimal_profit = round(optimalObjectives[instance_name], 3)
    last_profit = 0.0
    lines = readlines_cached(filename)
    for line in lines[1:]:
        if line.startswith('*'): continue
        parts = line.split(',')
        colsec = float(parts[3])
        if colsec > sec:
            return (optimal_profit - last_profit) / optimal_profit
        best_entry = parts[4] if parts[4].strip() != 'na' else '0.0'
        last_profit = round(float(best_entry), 3)
    return (optimal_profit - last_profit) / optimal_profit


def gap_in_trace_file_in_second(methodPrefix, filename, sec):
    if methodPrefix == 'CPLEXTrace_':
        return gap_in_cplex_trace_file_in_second(filename, sec)

    instance_name = trace_filename_to_instance_name(methodPrefix, filename)

    optimal_profit = round(optimalObjectives[instance_name], 3)
    last_profit = 0.0
    lines = readlines_cached(filename)
    for line in lines[1:]:
        parts = line.split(',')
        colsec = float(parts[0])
        if colsec > sec:
            return (optimal_profit - last_profit) / optimal_profit
        last_profit = round(float(parts[1]), 3)
    return (optimal_profit - last_profit) / optimal_profit


def average_gap_of_method_in_second(method_prefix, sec):
    all_rfiles = list(os.listdir(RESULTS_DIR))
    trace_files = list(filter(lambda fn: fn.startswith(method_prefix) and fn.endswith('.txt'), all_rfiles))
    trace_files_opt_exists = trace_files if not OPTS_EXIST else list(filter(lambda fn: trace_filename_to_instance_name(method_prefix, fn) in optimalObjectives, trace_files))
    gaps = list(map(lambda tfile: gap_in_trace_file_in_second(method_prefix, tfile, sec), trace_files_opt_exists))
    average_gap = sum(gaps) / len(gaps)
    return average_gap


def average_gap_dict_for_method(methodPrefix, xs):
    print('Generating average gap list for method ' + methodPrefix)
    return dict(map(lambda sec: (sec, average_gap_of_method_in_second(methodPrefix, sec)), xs))


def generate_lists(time_limit=NUM_SECONDS):
    stepwidth_small = 0.01
    stepwidth_big = 1.0
    xs = list(numpy.arange(0, 1.0, stepwidth_small))
    if time_limit > 1.0:
        xs += list(numpy.arange(1.0, time_limit + stepwidth_big, stepwidth_big))
    ys = list(map(lambda mpfix: average_gap_dict_for_method(mpfix, xs), methodPrefixes))
    return xs, ys


def serialize_list_to_csv():
    header_line = 'time;'
    for pf in methodPrefixes: header_line += pf + ';'
    header_line = header_line[:-1]

    xs, ys = generate_lists()
    out_str = ''
    for x in xs:
        out_str += str(x) + ';'
        for i in range(len(methodPrefixes)):
            out_str += str(ys[i][x])
            if i < len(methodPrefixes) - 1: out_str += ';'
        out_str += '\n'
    with open('mergedtraces.csv', 'w') as fp:
        fp.write(header_line + '\n')
        fp.write(out_str.replace('.', ','))


serialize_list_to_csv()

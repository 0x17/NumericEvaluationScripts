import os

tracepf_to_resultpf = {
    'GATimeWindowBordersGA': 'GA0',
    'GAFixedCapacityGA': 'GA3',
    'GATimeVaryingCapacityGA': 'GA4',
    'GAGoldenSectionSearchGA': 'GA6',
    'Gurobi': 'Gurobi',
    'LocalSolverNative0': 'LocalSolverNative0',
    'LocalSolverNative3': 'LocalSolverNative3',
    'LocalSolverNative4': 'LocalSolverNative4',
    'LocalSolverNative6': 'LocalSolverNative6',
}


def rounding_method(x):
    return int(x*100)/100
    #return x


def instance_name_from_trace_filename(trace_filename):
    return trace_filename.split('Trace_')[1].replace('.txt', '')


def method_name_from_trace_filename(trace_filename):
    return trace_filename.split('Trace_')[0]


def check_validity_of_trace_file(path_prefix, trace_filename):
    instance_name = instance_name_from_trace_filename(trace_filename)
    method_name = method_name_from_trace_filename(trace_filename)
    result_profit = None
    with open(path_prefix + tracepf_to_resultpf[method_name] + 'Results.txt') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            if parts[0] == instance_name:
                result_profit = rounding_method(float(parts[1]))
        if result_profit is None:
            raise Exception('Cannot find profit for ' + instance_name)
    last_profit = None
    with open(path_prefix + trace_filename) as fp:
        for line in fp.readlines()[1:]:
            if ',' in line:
                last_profit = rounding_method(float(line.split(',')[1]))
    if last_profit != result_profit:
        print('Mismatch for instance: ' + instance_name + " in trace file: " + trace_filename)
        print('Last profit in trace file = ' + str(last_profit))
        print('Profit in results file = ' + str(result_profit))


def list_trace_files_in_path(path):
    trace_files = []
    for entry in os.listdir(path):
        if 'Trace' in entry:
            trace_files.append(entry)
    return trace_files


for tfn in list_trace_files_in_path('j120_60secs'):
    check_validity_of_trace_file('j120_60secs/', tfn)

import os
import collections

slimits = [1000, 5000, 50000]


def extract_column_from_csv_file(fn, col_ix, row_offset, sep=','):
    col = []
    with open(fn, 'r') as fp:
        lines = fp.readlines()
        for line in lines[row_offset:]:
            col.append(line.split(sep)[col_ix])
    return col


def is_tracefile(fn): return fn.endswith('.txt') and 'Trace' in fn


def iterate_matching_files(callback, pred, path='.'):
    for fn in os.listdir(path):
        if pred(fn):
            callback(fn)


def iterate_over_tracefiles(callback):
    iterate_matching_files(callback, is_tracefile)


def enforce_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def method_and_inst_name_from_fn(fn, tracefile_infix='Trace_'):
    parts = fn.split(tracefile_infix)
    method_name = parts[0]
    inst_name = parts[1].replace('.txt', '')
    return method_name, inst_name


def sort_by_instance_name(content):
    lines = list(filter(lambda line: len(line.rstrip()) > 0, content.split('\n')))
    return '\n'.join(sorted(lines, key=lambda line: line.split(',')[0]))


def build_opt_lookup(fn):
    lut = {}
    with open(fn) as fp:
        lines = fp.readlines()
        for line in lines:
            parts = line.split(';')
            lut[parts[0]] = str(round(float(parts[1].rstrip()), 3))
    return lut


def write_obj_values_for_limits(method_name):
    opath = 'ObjectiveValuesForScheduleLimits/'
    enforce_dir(opath)
    write_obj_values_for_limits.ostr = ''

    opt_lookup = build_opt_lookup('../GMS_CPLEX_Results.txt')

    def process_file(fn):
        actual_method_name, inst_name = method_and_inst_name_from_fn(fn)
        if actual_method_name == method_name:
            col = extract_column_from_csv_file(fn, 1, 2)
            entries = [inst_name] + col
            write_obj_values_for_limits.ostr += ';'.join(entries) + ';' + opt_lookup[inst_name] + '\n'

    iterate_over_tracefiles(process_file)

    header_line = 'instance;' + ';'.join(list(map(lambda i: str(i), slimits))) + ';CPLEX\n'

    with open(opath + method_name + '_slimits.txt', 'w') as fp:
        fp.write(header_line + sort_by_instance_name(write_obj_values_for_limits.ostr).replace('.', ','))


def collect_method_names_from_directory(path):
    # could be rewritten using 'reduce' operator
    method_names = []

    def collector(fn):
        method_name, inst_name = method_and_inst_name_from_fn(fn)
        if method_name not in method_names:
            method_names.append(method_name)

    iterate_over_tracefiles(collector)
    return method_names


def batch_write_obj_values_for_limits(path):
    method_names = collect_method_names_from_directory(path)
    for method_name in method_names:
        write_obj_values_for_limits(method_name)


batch_write_obj_values_for_limits('.')


def write_per_instance_times_and_frequencies():
    def extract_req_times_from_file(fn):
        return extract_column_from_csv_file(fn, 0, 2)

    def build_method_name_to_req_times_dict():
        method_name_to_req_times = {}

        def process_file(fn):
            method_name, inst_name = method_and_inst_name_from_fn(fn)
            _req_times = extract_req_times_from_file(fn)
            if method_name not in method_name_to_req_times:
                method_name_to_req_times[method_name] = [[inst_name] + _req_times]
            else:
                method_name_to_req_times[method_name].append([inst_name] + _req_times)

        iterate_over_tracefiles(process_file)
        return method_name_to_req_times

    opath = 'TimeRequiredForScheduleLimit/'
    enforce_dir(opath)

    for mname, req_times_mx in build_method_name_to_req_times_dict().items():
        # for i in range(len(slimits)):
        with open(opath + mname + '.txt', 'w') as fp:
            ostr = ''
            for req_times in req_times_mx:
                ostr += (';'.join(req_times) + '\n').replace('.', ',')
            fp.write(ostr)

        with open(opath + mname + '_frequencies.txt', 'w') as fp2:
            ostr = ''
            freq_dicts = [collections.OrderedDict({}), collections.OrderedDict({}), collections.OrderedDict({})]
            for req_times in req_times_mx:
                actual_times = req_times[1:]
                for i in range(len(actual_times)):
                    if actual_times[i] not in freq_dicts[i]:
                        freq_dicts[i][actual_times[i]] = 1
                    else:
                        freq_dicts[i][actual_times[i]] += 1

            for i in range(len(slimits)):
                ostr += 'slimit=' + str(slimits[i]) + '\n'
                for val, freq in freq_dicts[i].items():
                    ostr += (str(val) + ';' + str(freq) + '\n').replace('.', ',')

            fp2.write(ostr)

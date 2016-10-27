import os
import sys
import mptrace

SET_NAME = 'j30'
OUT_PATH = SET_NAME + '_5secs/'

SCHEDULE_FN = OUT_PATH + 'myschedule.txt'
PROFIT_FN = OUT_PATH + 'myprofit.txt'
SKIPFILE = OUT_PATH + 'plsdoskip'


def syscall(s):
    print('SYSCALL: ' + s)
    os.system(s)


def os_command_str(cmd): return './' + cmd + ' ' if os.name == 'posix' else cmd + '.exe '


def force_delete_file(fn):
    while True:
        try:
            if not (os.path.isfile(fn)): break
            os.remove(fn)
        except OSError:
            print('Deleting ' + fn + ' failed. Retry!')
        else:
            break


def append_to_invalid_lst(fn, method):
    with open('invalids.txt', 'a') as fp:
        fp.write(fn + ';' + method + '\n')


def validate_schedule_and_profit(fn, method):
    if (not os.path.isfile(SCHEDULE_FN)) or (not os.path.isfile(PROFIT_FN)):
        print('Unable to find schedule or profit file for method ' + method + '!')
        force_delete_file(SCHEDULE_FN)
        force_delete_file(PROFIT_FN)
        force_delete_file(SKIPFILE)
    else:
        syscall('java -jar ScheduleValidator.jar ' + OUT_PATH + ' ' + fn)
        if os.path.isfile(SKIPFILE):
            force_delete_file(SKIPFILE)
            force_delete_file(SCHEDULE_FN)
            force_delete_file(PROFIT_FN)
            append_to_invalid_lst(fn, method)
        # raise Exception('Invalid schedule or profit for method ' + method + '!')
        else:
            force_delete_file(SCHEDULE_FN)
            force_delete_file(PROFIT_FN)
            print('Valid solution from ' + method + ' for ' + fn)


def solve_with_method(method, instance_path, trace=False):
    cmd = os_command_str('Solver') + method + ' ' + str(timelimit) + ' ' + str(iterlimit) + ' ' + instance_path
    cmd += ' traceobj' if trace else ''
    print('Running: ' + cmd)
    syscall(cmd)
    validate_schedule_and_profit(instance_path, method)


def convert_sm_to_gdx(fn):
    while not os.path.isfile(fn + '.gdx'):
        syscall(os_command_str('Convert') + fn)
    for f in ['_gams_net_gdb0.gdx', '_gams_net_gjo0.gms', '_gams_net_gjo0.lst']:
        force_delete_file(f)


def core_of_instance_name(instance_name):
    return instance_name.replace(SET_NAME + '/', '').replace('.sm', '')


def already_solved(instance_name, results_filename, checker):
    if os.path.isfile(results_filename):
        with open(results_filename) as f:
            for line in f.readlines():
                if checker(line, instance_name):
                    return True
    return False


def gams_already_solved(instance_name, results_filename):
    return already_solved(instance_name, results_filename,
                          lambda line, iname: line.split(';')[0] == core_of_instance_name(instance_name))


def gurobi_already_solved(instance_name, results_filename):
    return already_solved(instance_name, results_filename,
                          lambda line, iname: line.strip() == core_of_instance_name(instance_name))


def results_filename_for_solver(solver):
    return 'GMS_' + solver + '_Results.txt'


def solve_with_gams(solver, instance_name, trace=False, no_time_limit=False):
    if no_time_limit and gams_already_solved(instance_name, results_filename_for_solver(solver)):
        print('Skipping ' + instance_name)
        return

    trace_str = '1' if trace else '0'
    s_time_limit = '9999999' if no_time_limit else str(timelimit)
    s_iteration_limit = '999999' if iterlimit == -1 else str(iterlimit)
    num_threads = 0 if no_time_limit else 1
    outname = OUT_PATH.replace('/', '')
    gams_prefix = 'gams modelcli.gms --nthreads=' + str(num_threads) \
                  + ' --trace=' + trace_str + ' --timelimit=' + s_time_limit \
                  + ' --iterlim=' + s_iteration_limit + ' --solver=' + solver \
                  + ' --instname=' + instance_name \
                  + ' --outpath=' + outname
    convert_sm_to_gdx(instance_name)
    syscall(gams_prefix)
    force_delete_file(instance_name + '.gdx')

    if not os.path.exists(OUT_PATH): os.mkdir(OUT_PATH)
    if os.path.exists(outname + 'myprofit.txt'):
        os.rename(outname + 'myprofit.txt', OUT_PATH + 'myprofit.txt')
    if os.path.exists(outname + 'myschedule.txt'):
        os.rename(outname + 'myschedule.txt', OUT_PATH + 'myschedule.txt')

    validate_schedule_and_profit(instance_name, 'GMS_' + solver)

    os.rename('CPLEXTrace.txt', OUT_PATH + 'CPLEXTrace_' + core_of_instance_name(instance_name) + '.txt')


def solve_with_selected_ga(pfn, indices, trace=False):
    for i in indices:
        solve_with_method('GA' + str(i), pfn, trace)


def solve_with_selected_native_ls(pfn, indices, trace=False):
    for i in indices:
        solve_with_method('LocalSolverNative' + str(i), pfn, trace)


def solve_with_all_native_ls(pfn, trace=False):
    solve_with_selected_native_ls(pfn, range(6), trace)


def solve_with_gurobi(pfn, trace=False):
    if not (gurobi_already_solved(pfn, 'GurobiOptimals.txt')):
        solve_with_method('Gurobi', pfn, trace)


def show_progress(fn, ctr, num_entries):
    percent_done = float(ctr) / float(num_entries) * 100.0
    print('File: ' + fn + ' ;;; (' + str(ctr) + '/' + str(num_entries) + ') ' + str(percent_done) + '%')


def min_max_makespan_not_equal(fn):
    syscall('java -jar MinMaxMakespan.jar ' + OUT_PATH + ' ' + fn)

    if os.path.isfile(SKIPFILE):
        print('Equal min/max-makespan for ' + fn)
        os.remove(SKIPFILE)
        return False

    return True


def heuristics(pfn, fn, ctr, num_entries):
    solve_with_gurobi(pfn, True)
    show_progress(fn, ctr, num_entries)


def exacts(pfn, fn, ctr, num_entries):
    solve_with_gams('CPLEX', pfn, False, True)


def converter(fn, pfn, ctr, num_entries):
    convert_sm_to_gdx(pfn)


def print_estimated_time(num_instances):
    num_methods = 1.0
    secs = float(timelimit) * float(num_instances) * num_methods
    hours = secs / 3600.0
    print('Estimated time for results\nIn seconds: ' + str(secs) + '\nIn hours: ' + str(hours))


def is_entry_relevant(directory_name, fn, only_optimally_solved):
    return fn.endswith('.sm') and min_max_makespan_not_equal(directory_name + '/' + fn)


def batch_solve(directory_name, callback, only_optimally_solved=False):
    ctr = 1
    entries = os.listdir(directory_name)
    actual_entries = list(filter(lambda fn: is_entry_relevant(directory_name, fn, only_optimally_solved), entries))
    print_estimated_time(len(actual_entries))
    num_entries = len(actual_entries)
    for fn in actual_entries:
        callback(directory_name + '/' + fn, fn, ctr, num_entries)
        ctr += 1


def show_usage():
    print('Usage for batching: python batchsolve.py batch dirname timelimit iterlimit')
    print('Usage for batch gdx: python batchsolve.py convert dirname')


def parse_args(args):
    global timelimit, iterlimit

    if len(args) == 1:
        show_usage()
    else:
        defpairs = {'batch': ('j120', 10), 'trace': ('QBWLBeispiel.sm', 10), 'convert': 'j30'}
        argtuple = (args[2], float(args[3]), int(args[4])) if len(args) >= 5 else defpairs[args[1]]
        if args[1] == 'batch':
            dirname, timelimit, iterlimit = argtuple
            batch_solve(dirname, exacts if timelimit == -1 and iterlimit == -1 else heuristics, True)
        elif args[1] == 'convert':
            dirname = args[2]
            batch_solve(dirname, converter)


def main():
    parse_args(sys.argv)


if __name__ == '__main__': main()

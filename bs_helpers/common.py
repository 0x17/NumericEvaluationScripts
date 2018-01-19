import os, sys
from bs_helpers import utils, validation, instancefiltering, globals, common


def core_of_instance_name(instance_name):
    global setName
    return instance_name.replace(setName + '/', '').replace('.sm', '')


def results_filename_for_solver(solver):
    return 'GMS_' + solver + '_Results.txt'


def show_progress(fn, ctr, num_entries):
    percent_done = float(ctr) / float(num_entries) * 100.0
    print('File: ' + fn + ' ;;; (' + str(ctr) + '/' + str(num_entries) + ') ' + str(percent_done) + '%')


def print_estimated_time(num_instances):
    num_methods = 1.0
    secs = float(globals.timelimit) * float(num_instances) * num_methods
    hours = secs / 3600.0
    print('Estimated time for results\nIn seconds: ' + str(secs) + '\nIn hours: ' + str(hours))


def batch_solve(directory_name, callback, only_optimally_solved=False):
    filter_before = False

    ctr = 1
    entries = os.listdir(directory_name)

    if filter_before:
        actual_entries = list(filter(lambda fn: instancefiltering.is_entry_relevant(directory_name, fn, only_optimally_solved), entries))
        if sys.argv[1] == 'batch': common.print_estimated_time(len(actual_entries))
    else:
        actual_entries = entries

    num_entries = len(actual_entries)

    for fn in actual_entries:
        if filter_before or instancefiltering.is_entry_relevant(directory_name, fn, only_optimally_solved):
            callback(directory_name + '/' + fn, fn, ctr, num_entries)
            ctr += 1


def solve_with_method(method, instance_path, trace=False):
    cmd = utils.os_command_str('Solver') + method + ' ' + str(globals.timelimit) + ' ' + str(globals.iterlimit) + ' ' + instance_path
    cmd += ' traceobj' if trace else ''
    print('Running: ' + cmd)
    utils.syscall(cmd)
    validation.validate_schedule_and_profit(instance_path, method)

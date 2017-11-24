def already_solved(instance_name, results_filename, checker):
    if os.path.isfile(results_filename):
        with open(results_filename) as f:
            for line in f.readlines():
                if checker(line, instance_name):
                    return True
    return False

def gams_already_solved(instance_name, results_filename):
    def line_contains_instance_name(line): return line.split(';')[0] == common.core_of_instance_name(instance_name)

    return already_solved(instance_name, results_filename, line_contains_instance_name)

def gurobi_already_solved(instance_name, results_filename):
    def line_contains_instance_name(line): return line.strip() == common.core_of_instance_name(instance_name)

    return already_solved(instance_name, results_filename, line_contains_instance_name)

def convert_sm_to_gdx(fn):
    while not os.path.isfile(fn + '.gdx'):
        utils.syscall(utils.os_command_str('Convert') + fn)
    utils.batch_del(['_gams_net_gdb0.gdx', '_gams_net_gjo0.gms', '_gams_net_gjo0.lst'])

def solve_with_gams(solver, instance_name, trace=False, no_time_limit=False):
    if no_time_limit and gams_already_solved(instance_name,
                                                          common.results_filename_for_solver(solver)):
        print('Skipping ' + instance_name)
        return

    trace_str = '1' if trace else '0'
    s_time_limit = '9999999' if no_time_limit else str(timelimit)
    s_iteration_limit = '999999' if iterlimit == -1 else str(iterlimit)
    num_threads = 0 if no_time_limit else 1
    outname = outPath.replace('/', '')
    gams_prefix = 'gams modelcli.gms --nthreads=' + str(num_threads) \
                  + ' --trace=' + trace_str + ' --timelimit=' + s_time_limit \
                  + ' --iterlim=' + s_iteration_limit + ' --solver=' + solver \
                  + ' --instname=' + instance_name \
                  + ' --outpath=' + outname
    convert_sm_to_gdx(instance_name)
    utils.syscall(gams_prefix)
    utils.force_delete_file(instance_name + '.gdx')

    if not os.path.exists(outPath): os.mkdir(outPath)
    if os.path.exists(outname + 'myprofit.txt'):
        os.rename(outname + 'myprofit.txt', outPath + 'myprofit.txt')
    if os.path.exists(outname + 'myschedule.txt'):
        os.rename(outname + 'myschedule.txt', outPath + 'myschedule.txt')

    validation.validate_schedule_and_profit(instance_name, 'GMS_' + solver)

    os.rename('CPLEXTrace.txt', outPath + 'CPLEXTrace_' + common.core_of_instance_name(instance_name) + '.txt')

def solve_with_gurobi(pfn, trace=False):
    # if not (gurobi_already_solved(pfn, 'GurobiOptimals.txt')):
    common.solve_with_method('Gurobi', pfn, trace)

def exacts(pfn, fn, ctr, num_entries):
    # solve_with_gams('CPLEX', pfn, False, True)
    solve_with_gurobi(pfn)

def converter(fn, pfn, ctr, num_entries):
    convert_sm_to_gdx(fn)

def filter(fn, pfn, ctr, num_entries):
    with open('relevant_files.txt', 'a') as f:
        f.write(fn + '\n')
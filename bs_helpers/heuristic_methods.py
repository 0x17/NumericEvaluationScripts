def solve_with_selected_ga(pfn, indices, trace=False):
    for i in indices:
        common.solve_with_method('GA' + str(i), pfn, trace)

def solve_with_selected_native_ls(pfn, indices, trace=False):
    for i in indices:
        common.solve_with_method('LocalSolverNative' + str(i), pfn, trace)

def solve_with_all_native_ls(pfn, trace=False):
    solve_with_selected_native_ls(pfn, range(6), trace)

def heuristics(pfn, fn, ctr, num_entries):
    do_trace = (iterlimit == -1 and timelimit != -1)

    if do_trace:
        exact_methods.solve_with_gurobi(pfn, do_trace)
        common.show_progress(fn, ctr, num_entries)

    solve_with_selected_ga(pfn, [0, 3, 4], do_trace)
    common.show_progress(fn, ctr, num_entries)

    solve_with_selected_native_ls(pfn, [0, 3, 4], do_trace)
    common.show_progress(fn, ctr, num_entries)
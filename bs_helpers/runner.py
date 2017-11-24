import sys

def show_usage():
    print('Usage for batching: python batchsolve.py batch dirname timelimit iterlimit')
    print('Usage for batch gdx: python batchsolve.py convert dirname')
    print('Usage for filtering relevants: python batchsolve.py filter dirname')

def set_global_identifiers(dirname):
    global setName, outPath, scheduleFilename, profitFilename, skipfilePath
    setName = dirname
    outPath = setName + '_' + (
    str(int(timelimit)) + 'secs/' if timelimit != -1 else str(int(iterlimit)) + 'schedules/')
    scheduleFilename = outPath + 'myschedule.txt'
    profitFilename = outPath + 'myprofit.txt'
    skipfilePath = outPath + 'plsdoskip'

def parse_args(args):
    global timelimit, iterlimit

    print('Num args = ' + str(len(args)))

    def choose_method_type_fn():
        if timelimit == -1 and iterlimit == -1:
            return exact_methods.exacts
        else:
            return heuristic_methods.heuristics

    if len(args) == 3:
        if args[1] == 'convert':
            dirname = args[2]
            common.batch_solve(dirname, exact_methods.converter)
        elif args[1] == 'filter':
            dirname = args[2]
            global outPath, skipfilePath
            outPath = dirname
            skipfilePath = outPath + 'plsdoskip'
            common.batch_solve(dirname, exact_methods.filter)
    elif len(args) == 5:
        argtuple = (args[2], float(args[3]), int(args[4]))
        if args[1] == 'batch':
            dirname, timelimit, iterlimit = argtuple
            set_global_identifiers(dirname)
            common.batch_solve(dirname, choose_method_type_fn(), dirname == 'j30')
    else:
        show_usage()

def main():
    parse_args(sys.argv)

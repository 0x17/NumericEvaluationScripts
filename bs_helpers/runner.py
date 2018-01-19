import sys
from bs_helpers import common, exact_methods, heuristic_methods, globals


def show_usage():
    print('Usage for batching: python batchsolve.py batch dirname timelimit iterlimit')
    print('Usage for batch gdx conversion: python batchsolve.py convert dirname')
    print('Usage for batch json conversion: python batchsolve.py convertjson dirname')
    print('Usage for filtering relevants: python batchsolve.py filter dirname')


def set_global_identifiers(dirname, timelimit, iterlimit):
    globals.setName = dirname
    globals.outPath = globals.setName + '_' + (str(int(timelimit)) + 'secs/' if timelimit != -1 else str(int(iterlimit)) + 'schedules/')
    globals.scheduleFilename = globals.outPath + 'myschedule.txt'
    globals.profitFilename = globals.outPath + 'myprofit.txt'
    globals.skipfilePath = globals.outPath + 'plsdoskip'


def parse_args(args):
    print('Num args = ' + str(len(args)))

    def choose_method_type_fn():
        if globals.timelimit == -1 and globals.iterlimit == -1:
            return exact_methods.exacts
        else:
            return heuristic_methods.heuristics

    if len(args) == 3:
        if args[1] == 'convert':
            globals.dirname = args[2]
            common.batch_solve(globals.dirname, exact_methods.converter)
        elif args[1] == 'convertjson':
            globals.dirname = args[2]
            common.batch_solve(globals.dirname, exact_methods.json_converter)
        elif args[1] == 'filter':
            globals.dirname = args[2]
            common.batch_solve(globals.dirname, exact_methods.filter)
    elif len(args) == 5:
        argtuple = (args[2], float(args[3]), int(args[4]))
        if args[1] == 'batch':
            dirname, timelimit, iterlimit = argtuple
            set_global_identifiers(dirname, timelimit, iterlimit)
            common.batch_solve(dirname, choose_method_type_fn(), dirname == 'j30')
    else:
        show_usage()


def main():
    parse_args(sys.argv)

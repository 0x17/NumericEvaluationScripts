import sys
import ast
import os
import json


def my_system(cmd):
    print(cmd)
    # os.system(cmd)


def my_system_in_path(cmd, workdir):
    print(cmd + ' in: ' + workdir)
    pwd = os.getcwd()
    # os.chdir(workdir)
    # os.system(cmd)
    # os.chdir(pwd)


def cleanup_options(ofn='options.json'):
    if os.path.exists(ofn):
        os.remove(ofn)


def write_options(options, ofn='options.json'):
    cleanup_options(ofn)
    with open(ofn, 'w') as fp:
        ostr = json.dumps(options, indent=4, sort_keys=True)
        print(ostr)
        # fp.write(ostr)


def run_with_disk_options(cmd, args):
    write_options(args)
    my_system(cmd)
    cleanup_options()


def args_to_obj(args):
    def is_list_or_str(v):
        return v.startswith('[') or v.startswith('"')

    obj = {}
    for arg in args:
        if '=' in arg:
            parts = arg.split('=')
            k, v = parts
            obj[k] = ast.literal_eval(v) if is_list_or_str(v) else v
    return obj


def run_batchsolve_for_options(opts):
    def compose_call(dirname, timelimit, iterlimit):
        return 'python batchsolve.py batch ' + dirname + ' ' + str(timelimit) + ' ' + str(iterlimit)

    def val_or_minus_one(dict, key):
        return int(dict[key]) if key in dict else -1

    if 'slimits' in opts:
        for slimit in opts['slimits']:
            my_system(compose_call(opts['set'], -1, slimit))
            my_system_in_path('python mergeresults.py' + opts['set'], opts['set'] + '_' + slimit + 'schedules')
    else:
        my_system(compose_call(opts['set'], val_or_minus_one(opts, 'timelimit'), val_or_minus_one(opts, 'iterlimit')))
        if 'timelimit' in opts and 'iterlimit' not in opts:
            my_system('python mergetraces.py ' + opts['set'])
            my_system_in_path('python mergeresults.py ' + opts['set'], opts['set'])


def run_comparisons(argobj):
    run_with_disk_options('python runcomparisons.py', argobj)
    run_with_disk_options('python mergeVsComparisonDirectories.py', argobj)
    my_system_in_path('python mergeresults.py j30', 'j30_vsmerged')


task_mapping = {
    'run_comparisons': {'fn': run_comparisons,
                        'shorthand': 'rc',
                        'args': 'combos=[(\'OPC,best\'),(\'TPC,duel\'),...] slimits=[1000,...]',
                        'description': 'Compare crossover and selection methods'},
    'schedule_limit_table': {'fn': run_batchsolve_for_options,
                             'shorthand': 'sl',
                             'args': 'set=j30 slimits=[1000,...]',
                             'description': 'Compute results for table with results for schedule limits'},
    'time_limit_table': {'fn': run_batchsolve_for_options,
                         'shorthand': 'tl',
                         'args': 'set=j30 timelimit=30',
                         'description': 'Compute results for table with results for time limits'}
}


def build_alias_mapping(task_mapping):
    m = {}
    for k, v in task_mapping.items():
        if 'shorthand' in v:
            m[v['shorthand']] = k
    return m


def show_tasks():
    print('Known tasks:\n')
    for task, rec in task_mapping.items():
        argstr = '' if 'args' not in rec else ' ' + rec['args']
        descstr = '' if 'description' not in rec else rec['description']
        print('Task name: ' + task + ' - ' + descstr)
        print('Example usage: python quicktask.py task=' + task + argstr + '\n')


def main(args):
    alias_mapping = build_alias_mapping(task_mapping)

    aobj = args_to_obj(args)
    if 'task' in aobj:
        taskname = aobj['task']
        if taskname in task_mapping:
            task_mapping[taskname]['fn'](aobj)
        elif taskname in alias_mapping.keys():
            task_mapping[alias_mapping[taskname]]['fn'](aobj)
    else:
        show_tasks()


if __name__ == '__main__':
    main(sys.argv[1:])

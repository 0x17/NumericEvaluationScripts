import os


def syscall(s):
    print('SYSCALL: ' + s)
    os.system(s)


def os_command_str(cmd):
    return './' + cmd + ' ' if os.name == 'posix' else cmd + '.exe '


def force_delete_file(fn):
    while True:
        try:
            if not (os.path.isfile(fn)): break
            os.remove(fn)
        except OSError:
            print('Deleting ' + fn + ' failed. Retry!')
        else:
            break


def batch_del(lst):
    for fn in lst:
        force_delete_file(fn)

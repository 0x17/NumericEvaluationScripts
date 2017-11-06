import os
import unittest
import shutil

RDIR = 'j30_30secs'
RDIR_CLEANED = 'j30_30secs_cleaned'
RESULTS_FILE = 'GMS_CPLEX_Results.txt'


def opt_exists(instname, resultsfile):
    with open(resultsfile, 'r') as fp:
        for line in fp.readlines():
            parts = line.split(';')
            if parts[0] == instname:
                return True
    return False


def extract_instance_name(trace_fn):
    return trace_fn[trace_fn.index('Trace') + 6:-4]


class TestFuncs(unittest.TestCase):
    def test_extract_instance_name(self):
        self.assertEqual('j301_1', extract_instance_name('GAFixedCapacityGATrace_j301_1.txt'))
        self.assertEqual('j1201_39', extract_instance_name('SomeMethodNameTrace_j1201_39.txt'))


def mymain():
    os.mkdir(RDIR_CLEANED)
    for entry_fn in os.listdir(RDIR):
        if entry_fn[:-4].endswith('Results'):
            out_lines = []
            with open(RDIR + '/' + entry_fn, 'r') as fp:
                lines = fp.readlines()
                for line in lines:
                    if ';' in line and opt_exists(line.split(';')[0], RESULTS_FILE):
                        out_lines.append(line)
            with open(RDIR_CLEANED + '/' + entry_fn, 'w') as fp:
                fp.writelines(out_lines)
        elif 'Trace' in entry_fn:
            if opt_exists(extract_instance_name(entry_fn), RESULTS_FILE):
                shutil.copyfile(RDIR + '/' + entry_fn, RDIR_CLEANED + '/' + entry_fn)
            # os.remove(RDIR + '/' + entry_fn)


if __name__ == '__main__':
    # unittest.main()
    mymain()

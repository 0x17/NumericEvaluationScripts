titleMapping = {
    'CPLEXTrace.txt': 'GMS/CPLEX',
    'GUROBITrace.txt': 'GMS/GUROBI',
    'GMSLS_Trace.txt': 'GMS/LocalSolver',
    'LocalSolverTrace.txt': 'LSP/LocalSolver',
    'BranchAndBoundTrace.txt': 'B\\&B',
    'GATimeWindowBordersGATrace.txt': 'GA $(\\lambda | \\beta)$',
    'GATimeWindowArbitraryGATrace.txt': 'GA $(\\lambda | \\tau)$',
    'GAFixedCapacityGATrace.txt': 'GA $(\\lambda | z_r)$',
    'GATimeVaryingCapacityGATrace.txt': 'GA $(\\lambda | z_{rt})$',
    'GACompareAlternativesGATrace.txt': 'GA $(\\lambda)$',
    'LocalSolverNative0Trace.txt': 'LS $(\\lambda | \\beta)$',
    'LocalSolverNative1Trace.txt': 'LS $(\\lambda | \\tau)$',
    'LocalSolverNative2Trace.txt': 'LS $(\\lambda | \\tilde{\\tau})$',
    'LocalSolverNative3Trace.txt': 'LS $(\\lambda)$',
    'LocalSolverNative4Trace.txt': 'LS $(\\lambda | z_r)$',
    'LocalSolverNative5Trace.txt': 'LS $(\\lambda | z_{rt})$'
}


def readCommon(fn, readAction):
    with open(fn, 'r') as fp:
        return readAction(fp)


def readLines(fn):
    return readCommon(fn, lambda fp: fp.readlines())


def readPointsFromFile(fn):
    lines = readLines(fn)
    xs = []
    ys = []
    for line in lines[1:]:
        parts = line.split(',')
        xs.append(float(parts[0]))
        ys.append(float(parts[1]))
    return (xs, ys)


def niceLbl(s): return r'{}'.format(s)


def plot(instname):
    pass


# fig, axis = plt.subplots()
# tracefiles = titleMapping.keys()
# for tracefile in tracefiles:
#	if os.path.exists(tracefile):
#		xs, ys = readPointsFromFile(tracefile)
#		axis.plot(xs, ys, label=niceLbl(titleMapping[tracefile]))
# axis.legend(loc='upper right', handlelength=0, numpoints=1, frameon=True)
# plt.savefig('test.pdf')

plot('bla')

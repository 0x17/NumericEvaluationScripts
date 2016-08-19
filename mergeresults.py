RESULT_SUFFIX = 'Results.txt'

def composeResultFiles():
    rfiles = ['GMS_CPLEX_', 'BranchAndBound']
    for i in range(6): rfiles.append('GA' + str(i))
    for i in range(6): rfiles.append('LocalSolverNative' + str(i))
    return list(map(lambda rf: rf + RESULT_SUFFIX, rfiles))


def parseColumn(fn, ix):
    col = []
    with open(fn) as f:
        for line in f.readlines():
            parts = line.split(';')
            col.append(parts[ix].strip())
    return col


def parseInstances(fn): return parseColumn(fn, 0)


def parseResults(fn): return parseColumn(fn, 1)


rfiles = composeResultFiles()
resultlines = list(map(parseResults, rfiles))
instances = parseInstances(rfiles[0])

assert (all(len(instances) == len(col) for col in resultlines))


def correctSep(ix, coll):
    if ix < len(coll) - 1: return ';'
    else: return '\n'


with open('merged.txt', 'w') as f:
    f.write('instance;')
    for i in range(len(rfiles)):
        f.write(rfiles[i].replace(RESULT_SUFFIX, '') + correctSep(i, rfiles))

    for i in range(len(instances)):
        resStr = resultlines[0][i]
        f.write(instances[i] + ';')
        for m in range(len(resultlines)):
            f.write(resultlines[m][i].replace('.', ',') + correctSep(m, resultlines))

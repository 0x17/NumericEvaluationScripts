RESULT_SUFFIX = 'Results.txt'

additionalResultFile = ['../GA4Results_Ref1800secs.txt']
#additionalResultFile = ['../GMS_CPLEX_Results.txt']

def composeResultFiles():
    rfiles = ['Gurobi']
    for i in [0, 3, 4, 6]: rfiles.append('GA' + str(i))
    for i in [0, 3, 4, 6]: rfiles.append('LocalSolverNative' + str(i))
    return list(map(lambda rf: rf + RESULT_SUFFIX, rfiles)) + additionalResultFile


def parseColumn(fn, ix):
    col = []
    with open(fn) as f:
        for line in f.readlines():
            parts = line.split(';')
            col.append(parts[ix].strip())
    return col


def parseInstances(fn): return parseColumn(fn, 0)


def parseResults(fn):
    if fn == '../GMS_CPLEX_Results.txt':
        instances = parseInstances('GA0Results.txt')
        results = []
        with open('../GMS_CPLEX_Results.txt', 'r') as fp:
            lines = fp.readlines()
            for instance in instances:
                for line in lines:
                    if line.split(';')[0] == instance:
                        results.append(line.split(';')[1].replace('\n', ''))
                        break
        return results

    return parseColumn(fn, 1)


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

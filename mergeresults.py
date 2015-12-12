
def composeResultFiles():
	rfiles = ['GMS_Gurobi_Results.txt', 'GMS_LocalSolver_Results.txt', 'BranchAndBoundResults.txt', 'LocalSolverResults.txt']
	for i in range(5): rfiles.append('GA'+str(i)+'Results.txt')
	return rfiles
	
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
resultlines = map(parseResults, rfiles)
instances = parseInstances(rfiles[0])

def correctSep(ix, coll):
	if ix < len(coll)-1: return ';'
	else: return '\n'

with open('merged.txt', 'w') as f:
	f.write('instance;')
	for i in range(len(rfiles)):
		f.write(rfiles[i].replace('Results.txt', '') + correctSep(i, rfiles))

	for i in range(len(instances)):
		resStr = resultlines[0][i]
		if resStr != 'infes' and float(resultlines[0][i].replace(',','.')) > 0.0:
			f.write(instances[i] + ';')
			for m in range(len(resultlines)):
				f.write(resultlines[m][i].replace('.', ',') + correctSep(m, resultlines))

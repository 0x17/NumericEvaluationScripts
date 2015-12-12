import os
import sys
import glob

def osCommandStr(cmd):
	return "./" + cmd + " " if os.name == 'posix' else cmd + ".exe "

def solveWithMethod(method, instancePath, trace = False):
	cmd = osCommandStr("Solver") + method + " " + str(timelimit) + " " + instancePath
	cmd += " traceobj" if trace else ""
	os.system(cmd)

def forceDeleteFile(fn):
	while True:
		try:
			if not(os.path.isfile(fn)): break
			os.remove(fn)
		except OSError:
			print "Deleting " + fn + " failed. Retry!"
		else:
			break

def convertSmToGdx(fn):
	os.system(osCommandStr("Convert") + fn)
	for f in ["_gams_net_gdb0.gdx", "_gams_net_gjo0.gms","_gams_net_gjo0.lst"]:
		forceDeleteFile(f)

def solveWithGams(solver, instname, trace = False):
	traceStr = "1" if trace else "0"
	gams_prefix = "gams modelcli.gms --trace="+traceStr+" --timelimit="+str(timelimit)+" --solver="+solver+" --instname=" + instname
	convertSmToGdx(instname)
	os.system(gams_prefix)
	forceDeleteFile(instname + ".gdx")

def solveWithEachGA(pfn, trace = False):
	for i in range(5):
		solveWithMethod("GA" + str(i), pfn, trace)

def batchSolve(dirname):
	for fn in os.listdir(dirname):
		pfn = dirname + "/" + fn

		if os.name != 'posix':
			solveWithGams("Gurobi", pfn)
			solveWithGams("LocalSolver", pfn)
			solveWithMethod("LocalSolver", pfn)

		solveWithMethod("BranchAndBound", pfn)
		solveWithEachGA(pfn)

def generateGPlotCode():
	plines = '\n'

	GMS_PREFIXES = ['GMSLS', 'GUROBI', 'CPLEX']
	MIP_PREFIXES = ['GUROBI', 'CPLEX']

	def inPrefixList(str, prefixes):
		return any(map(lambda pf: str.startswith(pf), prefixes))
	def isGamsTrace(fn): return inPrefixList(fn, GMS_PREFIXES)
	def mipMethod(fn): return inPrefixList(fn, MIP_PREFIXES)

	ctr = 1
	fsctr = 0

	fsentries = glob.glob('*.*')

	for fsentry in fsentries:
		fsctr += 1
		if fsentry.endswith('Trace.txt'):
			fn = os.path.basename(fsentry)

			if isGamsTrace(fn): colX, colY = (4, 5)
			else: colX, colY = (1, 2)

			if 'GA' in fn: color = '#FF0000'
			elif mipMethod(fn): color = '#00FF00'
			else: color = '#0000FF'

			title = fn

			plines += '\t\'' + fn + '\' using ' + str(colX) + ':' + str(colY) + ' lt rgb \'' + color + '\' dashtype 4 notitle smooth unique, \\ \n'
			plines += '\t\'' + fn + '\' using ' + str(colX) + ':' + str(colY) + ' title \'' + title + '\' with points pointtype ' + str(ctr) + ' lt rgb \'' + color + '\' ps 0.9'
			if fsctr < len(fsentries):
				plines += ', \\\n'

			ctr += 1

	codeTemplate = """
set terminal terminalChoice
set output outputFile
set title instTitle

set key outside top right

set key font 'cmr12,10'
set xtics font 'cmr12,10'
set ytics font 'cmr12,10'
set xlabel font 'cmr12,10'
set ylabel font 'cmr12,10'
set title font 'cmr12,10'

set xlabel 'time [secs]'
set ylabel 'profit'

set datafile separator ','

set xrange [0:*timelimit*]

plot\\\n*plotlines*""".replace('*timelimit*', str(timelimit)).replace('*plotlines*', plines)
	return codeTemplate

def plotCurves(instname, termChoice, ext):
	gpCode = generateGPlotCode()
	with open('plotSolverGenerated.gp', 'w') as f: f.write(gpCode)
	os.system("gnuplot -e \"instTitle='"+instname.replace("_", "\_")+"'; outputFile='"+instname+"_"+termChoice+"_Trace."+ext+"'; terminalChoice='"+termChoice+"'\" plotSolverGenerated.gp")

def traceSolve(instname):
	'''if os.name != 'posix':
		solveWithGams("CPLEX", instname, True)
		solveWithGams("Gurobi", instname, True)
		solveWithGams("LocalSolver", instname, True)
		solveWithMethod("LocalSolver", instname, True)

	solveWithMethod("BranchAndBound", instname, True)
	solveWithEachGA(instname, True)'''

	terms = [("pdfcairo", "pdf"), ("png", "png"), ("pstricks", "tex"), ("latex", "tex"), ("tikz", "tex")]
	for pair in terms:
		plotCurves(instname, pair[0], pair[1])

def showUsage():
	print "Usage for batching: python batchsolve.py batch dirname timelimit"
	print "Usage for tracing: python batchsolve.py trace instname timelimit"

def parseArgs(args):
	global timelimit

	if len(args) == 1: showUsage()
	else:
		defpairs = { "batch" : ("j30", 10), "trace" : ("QBWLBeispiel.sm", 10) }
		argpair = (args[2], float(args[3])) if len(args) >= 4 else defpairs[args[1]]
		if args[1] == "batch":
			dirname, timelimit = argpair
			batchSolve(dirname)
		elif args[1] == "trace":
			instname, timelimit = argpair
			traceSolve(instname)

def main(): parseArgs(sys.argv)
if __name__ == "__main__": main()

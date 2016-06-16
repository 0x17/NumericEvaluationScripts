import os
import sys
import glob
import codecs

titleMapping = {
	'CPLEXTrace.txt': 'GMS/CPLEX',
	'GUROBITrace.txt': 'GMS/GUROBI',
#	'GMSLS_Trace.txt': 'GMS/LocalSolver',
#	'LocalSolverTrace.txt': 'LSP/LocalSolver',
	'BranchAndBoundTrace.txt': 'B\\&B',
#	'GATimeWindowBordersGATrace.txt': 'GA ({/Symbol l}/{/Symbol b})',
#	'GATimeWindowArbitraryGATrace.txt': 'GA ({/Symbol l}/{/Symbol t})',
#	'GAFixedCapacityGATrace.txt': 'GA ({/Symbol l}/zr)',
	'GATimeVaryingCapacityGATrace.txt': 'GA ({/Symbol l}/zrt)',
#	'GACompareAlternativesGATrace.txt': 'GA ({/Symbol l})',
	'LocalSolverNative0Trace.txt': 'LS ({/Symbol l}/{/Symbol b})',
#	'LocalSolverNative1Trace.txt': 'LS ({/Symbol l}/{/Symbol t})',
#	'LocalSolverNative2Trace.txt': 'LS ({/Symbol l}/discr{/Symbol t})',
#	'LocalSolverNative3Trace.txt': 'LS ({/Symbol l})',
#	'LocalSolverNative4Trace.txt': 'LS ({/Symbol l}/zr)',
#	'LocalSolverNative5Trace.txt': 'LS ({/Symbol l}/zrt)'
}
		
def generateGPlotCode():
	plines = ''

	GMS_PREFIXES = ['GMSLS', 'GUROBI', 'CPLEX']
	MIP_PREFIXES = ['GUROBI', 'CPLEX']

	def inPrefixList(str, prefixes):
		return any(map(lambda pf: str.startswith(pf), prefixes))
	def isGamsTrace(fn): return inPrefixList(fn, GMS_PREFIXES)
	def mipMethod(fn): return inPrefixList(fn, MIP_PREFIXES)

	ctr = 1
	fsctr = 0

	#fsentries = glob.glob('*.*')
	
	#entrycount = len(fsentries)
	entrycount = len(titleMapping)

	#for fsentry in fsentries:
	fsentries = titleMapping.keys()
	fsentries.sort()
	for fsentry in fsentries:
		fsctr += 1
		if fsentry.endswith('Trace.txt'):
			fn = os.path.basename(fsentry)

			if isGamsTrace(fn): colX, colY = (4, 5)
			else: colX, colY = (1, 2)

			if 'GA' in fn: color = '#cc0000'
			elif 'Native' in fn: color = '#eb8c00'
			elif mipMethod(fn): color = '#00cc00'
			elif 'LocalSolver' in fn: color = '#cc00cc'
			else: color = '#0000cc'

			title = titleMapping[fn]

			plines += '\t\'' + fn + '\' using ' + str(colX) + ':' + str(colY) + ' lt rgb \'' + color + '\' dashtype 4 notitle smooth unique, \\\n'
			plines += '\t\'' + fn + '\' using ' + str(colX) + ':' + str(colY) + ' title \'' + title + '\' with points pointtype ' + str(ctr) + ' lt rgb \'' + color + '\' ps 0.6'
			if fsctr < entrycount:
				plines += ', \\\n'

			ctr += 1

	codeTemplate = """
set terminal terminalChoice
set output outputFile
set title instTitle

set key outside top right

set key font 'cmr12,10'
set key spacing 2.5
set xtics font 'cmr12,10'
set ytics font 'cmr12,10'
set xlabel font 'cmr12,10'
set ylabel font 'cmr12,10'
set title font 'cmr12,10'

set xlabel 'time [secs]'
set ylabel 'profit'

set datafile separator ','

set xrange [0:*timelimit*]

plot *plotlines*""".replace('*timelimit*', str(timelimit)).replace('*plotlines*', plines)
	return codeTemplate
	
def plotCurves(instname, termChoice, ext):
	gpCode = generateGPlotCode()
	with codecs.open('plotSolverGenerated.gp', 'w', 'utf-8') as f: f.write(gpCode)
	os.system("gnuplot -e \"instTitle='"+instname.replace("_", " ")+"'; outputFile='"+instname+"_"+termChoice+"_Trace."+ext+"'; terminalChoice='"+termChoice+"'\" plotSolverGenerated.gp")
	
def plot(instname):
	'''("png", "png"),'''
	'''("pstricks", "tex"), ("latex", "tex"), ("tikz", "tex")'''
	terms = [('pdfcairo', 'pdf')]
	for pair in terms:
		plotCurves(instname, pair[0], pair[1])

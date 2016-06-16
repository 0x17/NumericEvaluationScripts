import os
import sys
import glob
import codecs
import gplot
import mptrace

SCHEDULE_FN = 'myschedule.txt'
PROFIT_FN = 'myprofit.txt'
SKIPFILE = 'plsdoskip'

def osCommandStr(cmd): return './' + cmd + ' ' if os.name == 'posix' else cmd + '.exe '

def forceDeleteFile(fn):
	while True:
		try:
			if not(os.path.isfile(fn)): break
			os.remove(fn)
		except OSError:
			print('Deleting ' + fn + ' failed. Retry!')
		else:
			break

def appendToInvalidLst(fn, method):
	with open('invalids.txt', 'a') as fp:
		fp.write(fn+';'+method+'\n')

def validateScheduleAndProfit(fn, method):
	if ((not os.path.isfile(SCHEDULE_FN)) or (not os.path.isfile(PROFIT_FN))):
		raise Exception('Unable to find schedule or profit file for method ' + method + '!')
	else:
		os.system('java -jar ScheduleValidator.jar ' + fn)
		if os.path.isfile(SKIPFILE):
			forceDeleteFile(SKIPFILE)
			forceDeleteFile(SCHEDULE_FN)
			forceDeleteFile(PROFIT_FN)
			appendToInvalidLst(fn, method)
			#raise Exception('Invalid schedule or profit for method ' + method + '!')
		else:
			forceDeleteFile(SCHEDULE_FN)
			forceDeleteFile(PROFIT_FN)
			print('Valid solution from ' + method + ' for ' + fn)

def solveWithMethod(method, instancePath, trace = False):
	cmd = osCommandStr('Solver') + method + ' ' + str(timelimit) + ' ' + instancePath
	cmd += ' traceobj' if trace else ''
	os.system(cmd)
	validateScheduleAndProfit(instancePath, method)

def convertSmToGdx(fn):
	while not os.path.isfile(fn+'.gdx'):
		os.system(osCommandStr('Convert') + fn)
	for f in ['_gams_net_gdb0.gdx', '_gams_net_gjo0.gms','_gams_net_gjo0.lst']:
		forceDeleteFile(f)

def gamsAlreadySolved(instname, resultsFilename):
	if os.path.isfile(resultsFilename):
		with open(resultsFilename) as f:
			if any(line.startswith(instname) for line in f.readlines()):
				return True
	return False

def resultsFilenameForSolver(solver):
	return 'GMS_' + solver + '_Results.txt'
	
def solveWithGams(solver, instname, trace = False, noreslim = False):
	if noreslim and gamsAlreadySolved(instname, resultsFilenameForSolver(solver)):
		print('Skipping ' + instname)
		return
	traceStr = '1' if trace else '0'
	sreslim = '9999999' if noreslim else str(timelimit)
	nthreads = 0 if noreslim else 1
	gams_prefix = 'gams modelcli.gms --nthreads='+str(nthreads)+' --trace='+traceStr+' --timelimit='+sreslim+' --solver='+solver+' --instname=' + instname
	convertSmToGdx(instname)
	os.system(gams_prefix)
	forceDeleteFile(instname + '.gdx')
	validateScheduleAndProfit(instname, 'GMS_' + solver) 

def solveWithEachGA(pfn, trace = False):
	for i in range(6):
		solveWithMethod('GA' + str(i), pfn, trace)

def solveWithEachNativeLS(pfn, trace = False):
	for i in range(7):
		solveWithMethod('LocalSolverNative' + str(i), pfn, trace)

def showProgress(fn, ctr, numEntries):
	percDone = float(ctr) / float(numEntries) * 100.0
	print('File: ' + fn + ' ;;; (' + str(ctr) + '/' + str(numEntries) + ') ' + str(percDone) + '%')

def minMaxMsNotEqual(fn):
	os.system('java -jar MinMaxMakespan.jar ' + fn)

	if os.path.isfile(SKIPFILE):
		os.remove(SKIPFILE)
		return False

	return True

def heuristics(fn, pfn, ctr, numEntries):
	solveWithGams('Gurobi', pfn)
	showProgress(fn, ctr, numEntries)
	
	#solveWithGams('LocalSolver', pfn)
	#showProgress(fn, ctr, numEntries)
	
	solveWithMethod('LocalSolver', pfn)
	showProgress(fn, ctr, numEntries)
	solveWithEachNativeLS(pfn)
	showProgress(fn, ctr, numEntries)
	solveWithMethod('BranchAndBound', pfn)
	showProgress(fn, ctr, numEntries)
	solveWithEachGA(pfn)
	showProgress(fn, ctr, numEntries)

def exacts(fn, pfn, ctr, numEntries): solveWithGams('CPLEX', pfn, False, True)

def converter(fn, pfn, ctr, numEntries): convertSmToGdx(pfn)

def batchSolve(dirname, callback):
	ctr = 1
	numEntries = len(os.listdir(dirname))
	entries = os.listdir(dirname)

	for fn in entries:
		if not fn.endswith('.sm'): continue
		pfn = dirname + '/' + fn

		if minMaxMsNotEqual(pfn):
			callback(fn, pfn, ctr, numEntries)

		ctr += 1

def traceSolve(instname):
	solveWithGams('CPLEX', instname, True)
	solveWithGams('Gurobi', instname, True)
	#solveWithGams('LocalSolver', instname, True)
	solveWithMethod('LocalSolver', instname, True)
	solveWithMethod('BranchAndBound', instname, True)
	solveWithEachGA(instname, True)
	solveWithEachNativeLS(instname, True)
	#gplot.plot(instname)
	mptrace.plot(instname)

def showUsage():
	print('Usage for batching: python batchsolve.py batch dirname timelimit')
	print('Usage for tracing: python batchsolve.py trace instname timelimit')
	print('Usage for batch gdx: python batchsolve.py convert dirname')

def parseArgs(args):
	global timelimit

	if len(args) == 1: showUsage()
	else:
		defpairs = { 'batch' : ('j30', 10), 'trace' : ('QBWLBeispiel.sm', 10), 'convert' : 'j30' }
		argpair = (args[2], float(args[3])) if len(args) >= 4 else defpairs[args[1]]
		if args[1] == 'batch':
			dirname, timelimit = argpair
			batchSolve(dirname, exacts if timelimit == -1 else heuristics)
		elif args[1] == 'trace':
			instname, timelimit = argpair
			traceSolve(instname)
		elif args[1] == 'convert':
			dirname = args[2]
			batchSolve(dirname, converter)

def main(): parseArgs(sys.argv)
if __name__ == '__main__': main()

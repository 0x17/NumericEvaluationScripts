import os
import sys


class Utils:
	@staticmethod
	def syscall(s):
		print('SYSCALL: ' + s)
		os.system(s)

	@staticmethod
	def os_command_str(cmd):
		return './' + cmd + ' ' if os.name == 'posix' else cmd + '.exe '

	@staticmethod
	def force_delete_file(fn):
		while True:
			try:
				if not (os.path.isfile(fn)): break
				os.remove(fn)
			except OSError:
				print('Deleting ' + fn + ' failed. Retry!')
			else:
				break

	@staticmethod
	def batch_del(lst):
		for fn in lst:
			Utils.force_delete_file(fn)


class Validation:
	@staticmethod
	def validate_schedule_and_profit(fn, method):
		result_filenames = [scheduleFilename, profitFilename]
		all_filenames = result_filenames + [skipfilePath]

		def append_to_invalid_lst():
			with open('invalids.txt', 'a') as fp:
				fp.write(fn + ';' + method + '\n')

		if (not os.path.isfile(scheduleFilename)) or (not os.path.isfile(profitFilename)):
			print('Unable to find schedule or profit file for method ' + method + '!')
			Utils.batch_del(all_filenames)
		else:
			Utils.syscall('java -jar ScheduleValidator.jar ' + outPath + ' ' + fn)
			if os.path.isfile(skipfilePath):
				Utils.batch_del(all_filenames)
				append_to_invalid_lst()
			# raise Exception('Invalid schedule or profit for method ' + method + '!')
			else:
				Utils.batch_del(result_filenames)
				print('Valid solution from ' + method + ' for ' + fn)


class AbstractSolver:
	@staticmethod
	def solve_with_method(method, instance_path, trace=False):
		cmd = Utils.os_command_str('Solver') + method + ' ' + str(timelimit) + ' ' + str(
			iterlimit) + ' ' + instance_path
		cmd += ' traceobj' if trace else ''
		print('Running: ' + cmd)
		Utils.syscall(cmd)
		Validation.validate_schedule_and_profit(instance_path, method)


class ExactMethods:
	@staticmethod
	def already_solved(instance_name, results_filename, checker):
		if os.path.isfile(results_filename):
			with open(results_filename) as f:
				for line in f.readlines():
					if checker(line, instance_name):
						return True
		return False

	@staticmethod
	def gams_already_solved(instance_name, results_filename):
		def line_contains_instance_name(line): return line.split(';')[0] == Common.core_of_instance_name(instance_name)

		return ExactMethods.already_solved(instance_name, results_filename, line_contains_instance_name)

	@staticmethod
	def gurobi_already_solved(instance_name, results_filename):
		def line_contains_instance_name(line): line.strip() == Common.core_of_instance_name(instance_name)

		return ExactMethods.already_solved(instance_name, results_filename, line_contains_instance_name)

	@staticmethod
	def convert_sm_to_gdx(fn):
		while not os.path.isfile(fn + '.gdx'):
			Utils.syscall(Utils.os_command_str('Convert') + fn)
		Utils.batch_del(['_gams_net_gdb0.gdx', '_gams_net_gjo0.gms', '_gams_net_gjo0.lst'])

	@staticmethod
	def solve_with_gams(solver, instance_name, trace=False, no_time_limit=False):
		if no_time_limit and ExactMethods.gams_already_solved(instance_name,
															  Common.results_filename_for_solver(solver)):
			print('Skipping ' + instance_name)
			return

		trace_str = '1' if trace else '0'
		s_time_limit = '9999999' if no_time_limit else str(timelimit)
		s_iteration_limit = '999999' if iterlimit == -1 else str(iterlimit)
		num_threads = 0 if no_time_limit else 1
		outname = outPath.replace('/', '')
		gams_prefix = 'gams modelcli.gms --nthreads=' + str(num_threads) \
					  + ' --trace=' + trace_str + ' --timelimit=' + s_time_limit \
					  + ' --iterlim=' + s_iteration_limit + ' --solver=' + solver \
					  + ' --instname=' + instance_name \
					  + ' --outpath=' + outname
		ExactMethods.convert_sm_to_gdx(instance_name)
		Utils.syscall(gams_prefix)
		Utils.force_delete_file(instance_name + '.gdx')

		if not os.path.exists(outPath): os.mkdir(outPath)
		if os.path.exists(outname + 'myprofit.txt'):
			os.rename(outname + 'myprofit.txt', outPath + 'myprofit.txt')
		if os.path.exists(outname + 'myschedule.txt'):
			os.rename(outname + 'myschedule.txt', outPath + 'myschedule.txt')

		Validation.validate_schedule_and_profit(instance_name, 'GMS_' + solver)

		os.rename('CPLEXTrace.txt', outPath + 'CPLEXTrace_' + Common.core_of_instance_name(instance_name) + '.txt')

	@staticmethod
	def solve_with_gurobi(pfn, trace=False):
		# if not (gurobi_already_solved(pfn, 'GurobiOptimals.txt')):
		AbstractSolver.solve_with_method('Gurobi', pfn, trace)

	@staticmethod
	def exacts(pfn, fn, ctr, num_entries):
		# solve_with_gams('CPLEX', pfn, False, True)
		ExactMethods.solve_with_gurobi(pfn)

	@staticmethod
	def converter(fn, pfn, ctr, num_entries):
		ExactMethods.convert_sm_to_gdx(fn)

	@staticmethod
	def filter(fn, pfn, ctr, num_entries):
		with open('relevant_files.txt', 'a') as f:
			f.write(fn + '\n')


class HeuristicMethods:
	@staticmethod
	def solve_with_selected_ga(pfn, indices, trace=False):
		for i in indices:
			AbstractSolver.solve_with_method('GA' + str(i), pfn, trace)

	@staticmethod
	def solve_with_selected_native_ls(pfn, indices, trace=False):
		for i in indices:
			AbstractSolver.solve_with_method('LocalSolverNative' + str(i), pfn, trace)

	@staticmethod
	def solve_with_all_native_ls(pfn, trace=False):
		HeuristicMethods.solve_with_selected_native_ls(pfn, range(6), trace)

	@staticmethod
	def heuristics(pfn, fn, ctr, num_entries):
		# ExactMethods.solve_with_gurobi(pfn, True)
		# Common.show_progress(fn, ctr, num_entries)
		# HeuristicMethods.solve_with_selected_ga(pfn, [0, 3, 4, 6], True)
		# Common.show_progress(fn, ctr, num_entries)
		HeuristicMethods.solve_with_selected_native_ls(pfn, [0, 3, 4], True)
		Common.show_progress(fn, ctr, num_entries)


class InstanceFiltering:
	@staticmethod
	def opt_exists(fn, resultsfile):
		with open(resultsfile, 'r') as fp:
			for line in fp.readlines():
				parts = line.split(';')
				if parts[0] + '.sm' == fn:
					return True
		return False

	@staticmethod
	def min_max_makespan_not_equal(fn):
		Utils.syscall('java -jar MinMaxMakespan.jar ' + outPath + ' ' + fn)

		if os.path.isfile(skipfilePath):
			print('Equal min/max-makespan for ' + fn)
			os.remove(skipfilePath)
			return False

		return True

	@staticmethod
	def is_entry_relevant(directory_name, fn, only_optimally_solved):
		return fn.endswith('.sm') and InstanceFiltering.min_max_makespan_not_equal(directory_name + '/' + fn) and (not only_optimally_solved or InstanceFiltering.opt_exists(fn, 'GMS_CPLEX_Results.txt'))


class Common:
	@staticmethod
	def core_of_instance_name(instance_name):
		return instance_name.replace(setName + '/', '').replace('.sm', '')

	@staticmethod
	def results_filename_for_solver(solver):
		return 'GMS_' + solver + '_Results.txt'

	@staticmethod
	def show_progress(fn, ctr, num_entries):
		percent_done = float(ctr) / float(num_entries) * 100.0
		print('File: ' + fn + ' ;;; (' + str(ctr) + '/' + str(num_entries) + ') ' + str(percent_done) + '%')

	@staticmethod
	def print_estimated_time(num_instances):
		num_methods = 1.0
		secs = float(timelimit) * float(num_instances) * num_methods
		hours = secs / 3600.0
		print('Estimated time for results\nIn seconds: ' + str(secs) + '\nIn hours: ' + str(hours))

	@staticmethod
	def batch_solve(directory_name, callback, only_optimally_solved=False):
		ctr = 1
		entries = os.listdir(directory_name)
		actual_entries = list(
			filter(lambda fn: InstanceFiltering.is_entry_relevant(directory_name, fn, only_optimally_solved), entries))
		if sys.argv[1] == 'batch':
			Common.print_estimated_time(len(actual_entries))
		num_entries = len(actual_entries)
		for fn in actual_entries:
			callback(directory_name + '/' + fn, fn, ctr, num_entries)
			ctr += 1


class Runner:
	@staticmethod
	def show_usage():
		print('Usage for batching: python batchsolve.py batch dirname timelimit iterlimit')
		print('Usage for batch gdx: python batchsolve.py convert dirname')
		print('Usage for filtering relevants: python batchsolve.py filter dirname')

	@staticmethod
	def set_global_identifiers(dirname, timelimit):
		global setName, outPath, scheduleFilename, profitFilename, skipfilePath
		setName = dirname
		outPath = setName + '_' + str(int(timelimit)) + 'secs/'
		scheduleFilename = outPath + 'myschedule.txt'
		profitFilename = outPath + 'myprofit.txt'
		skipfilePath = outPath + 'plsdoskip'

	@staticmethod
	def parse_args(args):
		global timelimit, iterlimit

		def choose_method_type_fn():
			if timelimit == -1 and iterlimit == -1:
				return ExactMethods.exacts
			else:
				return HeuristicMethods.heuristics

		if len(args) == 3:
			if args[1] == 'convert':
				dirname = args[2]
				Common.batch_solve(dirname, ExactMethods.converter)
			elif args[1] == 'filter':
				dirname = args[2]
				global outPath, skipfilePath
				outPath = dirname
				skipfilePath = outPath + 'plsdoskip'
				Common.batch_solve(dirname, ExactMethods.filter)
		elif len(args) == 5:
			argtuple = (args[2], float(args[3]), int(args[4]))
			if args[1] == 'batch':
				dirname, timelimit, iterlimit = argtuple
				Runner.set_global_identifiers(dirname, timelimit)
				Common.batch_solve(dirname, choose_method_type_fn(), True)
		else:
			Runner.show_usage()

	@staticmethod
	def main():
		Runner.parse_args(sys.argv)


if __name__ == '__main__': Runner.main()

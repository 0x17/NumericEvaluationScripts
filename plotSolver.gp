outputFile = 'manualtrace.pdf'
instTitle = 'instance.sm, timelimit=30s'
set terminal pdfcairo

#set terminal terminalChoice
set output outputFile
set title instTitle

set key outside top right

set key font "cmr12,10"
set xtics font "cmr12,10"
set ytics font "cmr12,10"
set xlabel font "cmr12,10"
set ylabel font "cmr12,10"
set title font "cmr12,10"

set xlabel 'time [secs]'
set ylabel 'profit'

set datafile separator ","

set xrange [0:30.5]

plot \
   'CompareAlternativesGATrace.txt' using 1:2 lt rgb "#FF0000" dashtype 4 notitle smooth unique, \
   'CompareAlternativesGATrace.txt' using 1:2 title 'GA ({/Symbol l})' with points pointtype 1 lt rgb "#FF0000" ps 0.9, \
   'TimeVaryingCapacityGATrace.txt' using 1:2 lt rgb "#880000" dashtype 4 notitle smooth unique, \
	 'TimeVaryingCapacityGATrace.txt' using 1:2 title 'GA ({/Symbol l};z_r_t)' with points pointtype 2 lt rgb "#880000" ps 0.9, \
   'FixedCapacityGATrace.txt' using 1:2 lt rgb "#FF4444" dashtype 4 notitle smooth unique, \
	 'FixedCapacityGATrace.txt' using 1:2 title 'GA ({/Symbol l};z_r)' with points pointtype 3 lt rgb "#FF4444" ps 0.9, \
   'TimeWindowArbitraryGATrace.txt' using 1:2 lt rgb "#FF0000" dashtype 4 notitle smooth unique, \
	 'TimeWindowArbitraryGATrace.txt' using 1:2 title 'GA ({/Symbol l};{/Symbol t})' with points pointtype 4 lt rgb "#FF0000" ps 0.9, \
   'TimeWindowBordersGATrace.txt' using 1:2 lt rgb "#FF0000" dashtype 4 notitle smooth unique, \
	 'TimeWindowBordersGATrace.txt' using 1:2 title 'GA ({/Symbol l};{/Symbol b})' with points pointtype 5 lt rgb "#FF0000" ps 0.9, \
   'LocalSolverTrace.txt' using 1:2 lt rgb "#0000FF" dashtype 4 notitle smooth unique, \
	 'LocalSolverTrace.txt' using 1:2 title 'LocalSolver' with points pointtype 6 lt rgb "#0000FF" ps 0.9, \
   'GMSLS_Trace.txt' using 4:5 lt rgb "#000055" dashtype 4 notitle smooth unique, \
	 'GMSLS_Trace.txt' using 4:5 title 'GAMS/LocalSolver' with points pointtype 8 lt rgb "#000055" ps 0.9, \
   'BranchAndBoundTrace.txt' using 1:2 lt rgb "#77FF77" dashtype 4 notitle smooth unique, \
	 'BranchAndBoundTrace.txt' using 1:2 title 'Branch And Bound' with points pointtype 7 lt rgb "#77FF77" ps 0.9, \
   'GUROBITrace.txt' using 4:5 lt rgb "#00AA00" dashtype 4 notitle smooth unique, \
	 'GUROBITrace.txt' using 4:5 title 'GAMS/GUROBI' with points pointtype 9 lt rgb "#00AA00" ps 0.9, \
   'CPLEXTrace.txt' using 4:5 lt rgb "#005500" dashtype 4 notitle smooth unique, \
	 'CPLEXTrace.txt' using 4:5 title 'GAMS/CPLEX'  with points pointtype 10 lt rgb "#005500" ps 0.9

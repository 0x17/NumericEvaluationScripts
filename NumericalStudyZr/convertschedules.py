with open('results.txt') as fp:
	lines = fp.readlines()
	for line in lines:
		parts = line.split()
		outsuffix = 'oc' if parts[0] == '-1.00' else str(int(float(parts[0])))
		with open('result_sts_'+outsuffix+'.txt', 'w') as fpw:
			ostr = ''
			for i in range(len(parts)-1):
				ostr += str(i+1) + '->' + str(int(float(parts[1+i]))) + '\n'
			fpw.write(ostr)

			
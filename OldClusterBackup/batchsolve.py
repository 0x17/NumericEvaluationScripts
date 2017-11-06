#!/usr/bin/env python
# Usage: ./batchsolve.py gamsModel path startIndex stopIndex
# e.g. ./batchsolve.py model.gms Projekte/j30gdx 0 9

import os, sys, subprocess

EXT = ".gdx"

def gdx_files(path):
	return map(lambda f: path + "/" + f, filter(lambda f: f.endswith(EXT), os.listdir(path)))

def rem_ext(fn):
	return fn.replace(EXT, "")

def run_and_wait(cmd):
	process = subprocess.Popen(cmd, shell=True)
	process.wait()

def parse_args():
	global path, startIndex, stopIndex, modelFilename
	modelFilename = sys.argv[1]
	path = sys.argv[2]
	startIndex = int(sys.argv[3])
	stopIndex = int(sys.argv[4])

def main():
	parse_args()
	files = gdx_files(path)
	for i in range(startIndex, stopIndex+1):
		instName = rem_ext(files[i])
		run_and_wait("gams "+modelFilename+" lo=2 --instname="+instName)

main()

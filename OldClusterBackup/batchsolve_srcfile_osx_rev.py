#!/usr/bin/env python

import sys, os, subprocess

modelFilename = sys.argv[1]
srcFile = sys.argv[2]

def run_and_wait(cmd):
	process = subprocess.Popen(cmd, shell=True)
	process.wait()

with open(srcFile, "r") as fp:
	lines = fp.readlines()
	lines.reverse()
	for line in lines:
		fn = "ClusterResults2/"+line.replace(".gdx", "").replace("\n", "")
		scmd = "gams " + modelFilename + " --instname=" + fn
		run_and_wait(scmd)

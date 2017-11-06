#!/usr/bin/env python

import sys, os, subprocess

modelFilename = sys.argv[1]
srcFile = sys.argv[2]

def run_and_wait(cmd):
	process = subprocess.Popen(cmd, shell=True)
	process.wait()

with open(srcFile, "r") as fp:
	for line in fp:
		fn = "ClusterResults/"+line.replace(".gdx", "").replace("\n", "")
		scmd = "gams " + modelFilename + " --instname=" + fn + " license=C:\GAMS\lizenzen\gamslice.txt"
		run_and_wait(scmd)

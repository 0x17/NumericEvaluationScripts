#!/usr/bin/env python

import os, sys, subprocess

def run_and_wait(cmd):
	process = subprocess.Popen(cmd, shell=True)
	process.wait()

def gen_script_files(path):
	return filter(lambda f: f.endswith("_generated.sh"), os.listdir(path))
	
for sf in gen_script_files("."):
	run_and_wait("qsub " + sf)
	
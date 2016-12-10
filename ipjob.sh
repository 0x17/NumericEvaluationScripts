#!/bin/bash -login
#PBS -N getipaddr-job
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=0:02:00
#PBS -l mem=1gb
#PBS -q all

cd $PBS_O_WORKDIR
ifconfig > ipaddr.txt
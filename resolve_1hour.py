import os

with open('GMS_CPLEX_Results_RefCluster1hour.txt') as fp:
    lines = fp.readlines()
    for line in lines:
        instname = line.split(';')[0]
        os.system(
            'gams modelcli.gms --instname=j30gdx/' + instname + '.sm --iterlim=99999 --timelimit=99999 --solver=CPLEX --trace=0 --nthreads=0')

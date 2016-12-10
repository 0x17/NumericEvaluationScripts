import os
cmdStr = 'cat '
for i in range(60):
    cmdStr += ' j120_'+str(i+1)+'_1800secs/GA4Results.txt'
cmdStr += ' > GA4ResultsMerged.txt'
print(cmdStr)
os.system(cmdStr)
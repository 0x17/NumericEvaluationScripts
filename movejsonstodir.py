import os
import shutil

def my_move(src, dest):
    shutil.move(src, dest)
    print('Moving {0} to {1}'.format(src, dest))
    
if not os.path.exists('j30_json'):
    os.mkdir('j30_json')

for fn in os.listdir():
    if fn.startswith('j30') and fn.endswith('.json'):
        my_move(fn, 'j30_json/' + fn)

import os
import shutil


def mycopy(src, dest):
    print(f'Copy from {src} -> {dest}')
    shutil.copy(src, dest)


if __name__ == '__main__':
    set_directories = [f for f in os.listdir('.') if 'Set ' in f]
    for set_dir in set_directories:
        setnum = int(set_dir.split()[1])
        for inst_fn in [f for f in os.listdir(set_dir) if f.endswith('.rcp')]:
            patnum = int(inst_fn.replace('Pat', '').replace('.rcp', ''))
            mycopy(f'{set_dir}/{inst_fn}', f'merged/RG30_Set{setnum}_Pat{patnum}.rcp')

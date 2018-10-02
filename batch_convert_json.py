import os

dirname = 'l'


def stem(path):
    return os.path.basename(os.path.splitext(path)[0])


for entry in os.listdir(dirname):
    if entry.endswith('.sm'):
        instanceName = stem(entry)
        cmd = f'./Converter {dirname}/{instanceName}.sm {dirname}_json/{instanceName}.json'
        os.system(cmd)
        print(cmd)

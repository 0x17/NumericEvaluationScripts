import csv

result_directory_prefix = 'j120_'
result_directory_suffices = ['1000schedules', '5000schedules', '50000schedules']
result_file_suffix = '/merged.txt'
result_filenames = [ result_directory_prefix + suffix + result_file_suffix for suffix in result_directory_suffices ]

def parse_result_matrix(fn):
    mx = []
    with open(fn, newline='') as fp:
        reader = csv.reader(fp, delimiter=';')
        for row in reader:
            mx.append(row[1:])
    return mx[1:]


def gap_for_method_in_row(mx, method_index, row):
    result = round(float(mx[row][method_index].replace(',','.')), 4)
    ref_result = round(float(mx[row][-1].replace(',','.')), 4)
    return (ref_result - result) / ref_result


def average_gap_for_method(mx, method_index):
    acc = 0
    for i in range(len(mx)):
        acc += gap_for_method_in_row(mx, method_index, i)
    return acc / len(mx)


def methods_in_file(fn):
    with open(fn, newline='') as fp:
        line = fp.readline()
        return line.rstrip('\n').rstrip('\r').split(';')[1:]


method_names = methods_in_file(result_filenames[0])

ostr = 'result;' + (';'.join(method_names)).replace('../', '').replace('_', '') + '\n'
for result_filename in result_filenames:
    mx = parse_result_matrix(result_filename)
    ostr += result_filename.replace('/merged.txt', '')
    for method_ix in range(len(method_names)):
        agap = average_gap_for_method(mx, method_ix)
        ostr += ';' + str(agap).replace('.', ',')
    ostr += '\n'

with open('aggregated.txt', 'w') as fp:
    fp.write(ostr)
import sys
import numpy as np

def first_line_with_prefix(lines, prefix):
    return next(ix for ix, line in enumerate(lines) if line.startswith(prefix))

def tex_table_to_matrix(lines):
    table_lines = lines[first_line_with_prefix(lines, '\\begin{tabular}'):first_line_with_prefix(lines, '\\end{tabular}') + 1]
    return np.matrix([list(map(lambda x: x.replace('\t', '').rstrip().lstrip(), filter(lambda x: '\\' not in x, line.split('&')))) for line in table_lines if '\hline' not in line and '&' in line])


def matrix_to_tex_table(mx):
    pass


def transpose_tex_table(lines):
    ostr = matrix_to_tex_table(tex_table_to_matrix(lines).transpose())
    print(ostr)

def main(args):
    if len(args) <= 1:
        print('Usage: python tex_table_transpose.py some_file.tex')
        return

    with open(args[1], 'r') as fp:
        transpose_tex_table(fp.readlines())


if __name__ == '__main__':
    main(sys.argv)

from gams import *
import sys
import ast


def ix_from_sym(symbol_name):
    return int(symbol_name[1:]) - 1


def main(args):
    if len(args) < 5 or not args[1].endswith('.gdx'):
        print('Usage: modify_gdx.py input.gdx output.gdx param new_value')

    input_filename = args[1]
    output_filename = args[2]
    param_name = args[3]
    new_values = ast.literal_eval(args[4])

    dim = 2 if type(new_values) == list and type(new_values[0]) == list else (1 if type(new_values) == list else 0)

    ws = GamsWorkspace(working_directory='.')
    db = ws.add_database_from_gdx(input_filename)

    assert (dim == db[param_name].dimension)

    if dim == 0:
        db[param_name].first_record().value = new_values
    elif dim == 1:
        for ix, rec in enumerate(db[param_name]):
            rec.value = new_values[ix]
    elif dim == 2:
        for rec in db[param_name]:
            rec.value = new_values[ix_from_sym(rec.keys[0])][ix_from_sym(rec.keys[1])]

    db.export(output_filename)


if __name__ == '__main__':
    main(sys.argv)

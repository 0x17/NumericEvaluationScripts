from gams import *
import sys
import json


def extract_scalars(db, scalars):
    return {scalar: db[scalar].first_record().value for scalar in scalars}


def extract_finishing_times(db):
    d = {int(j[1:]) - 1: int(t[1:]) for j, t in {tuple(rec.keys): rec.level for rec in db['x'] if rec.level == 1.0}}
    return [d[i] for i in range(len(d))]


def main(args):
    if len(args) < 2 or not args[1].endswith('.gdx'):
        print('Usage: python gdx_results_to_json.py results.gdx')

    input_filename = args[1]
    ws = GamsWorkspace(working_directory='.')
    db = ws.add_database_from_gdx(input_filename)

    results = {
        'fts': extract_finishing_times(db),
        'profit': db['profit'].first_record().level
    }
    obj = {**results, **extract_scalars(db, ['solvetime', 'slvstat', 'modelstat'])}

    with open(input_filename.replace('.gdx', '.json'), 'w') as fp:
        json.dump(obj, fp, sort_keys=True, indent=4)


if __name__ == '__main__':
    main(sys.argv)

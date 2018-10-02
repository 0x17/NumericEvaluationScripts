from list_unsolved_solver_comparison import parse_results, solver_names
import pandas as pd


def merge_extended_results(res):
    def collect_values(instance):
        return [instance.replace('j30gdx/', '').replace('.sm', '')] + [float(v) for solver_name in solver_names for v in res[solver_name][instance].values()]

    header_line = ['instance'] + [solver_name + '_' + attr for solver_name in solver_names for attr in ['obj', 'solvetime']]
    return [header_line] + [collect_values(instance) for instance, vals in res['GUROBI'].items() if all(instance in res[solver_name] for solver_name in solver_names)]


def merge_extended_results_df(res):
    eres = merge_extended_results(res)
    return pd.DataFrame([row[1:] for row in eres[1:]], columns=eres[0][1:], index=[row[0] for row in eres[1:]])


def serialize_merged_extended_results():
    df = merge_extended_results_df(parse_results())
    df.to_csv('merged_extended_results.csv')


def parse_characteristics(fn='flattened_j30.csv'):
    df = pd.read_csv(fn, sep=';', header=0, index_col=0)
    return df


def compose_train_data():
    char_df = parse_characteristics()
    res_df = merge_extended_results_df(parse_results())
    common_ix = char_df.index.intersection(res_df.index)
    xs = char_df.filter(common_ix, axis=0)
    ys = res_df.filter(common_ix, axis=0)
    return pd.concat([xs, ys], axis=1)

def serialize_train_data():
    td = compose_train_data()
    td.to_csv('train_solvetimes.csv')

if __name__ == '__main__':
    # serialize_merged_extended_results()
    serialize_train_data()

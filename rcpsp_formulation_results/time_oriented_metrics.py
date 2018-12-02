import os
import pandas as pd


def competitiveness_time(dfs, name_a, name_b):
    n_a = n_b = n = 0
    for ix, (index, row) in enumerate(dfs[name_a].iterrows()):
        feas_a, solvetime_a, gap_a = row.values
        other_df = dfs[name_b]
        feas_b, solvetime_b, gap_b = other_df.values[ix]
        optimal_a = feas_a and gap_a == 0
        optimal_b = feas_b and gap_b == 0
        if optimal_a and optimal_b:
            n += 1
            if solvetime_a < solvetime_b:
                n_a += 1
            elif solvetime_a > solvetime_b:
                n_b += 1
    return 2 * min(n_a / n, n_b / n)


def competitiveness(dfs, name_a, name_b):
    n_a = n_b = n = 0
    sub_dfs = {model_name: dfs[model_name] for model_name in [name_a, name_b]}
    instances = list(sub_dfs[name_a].index.values)
    for instance in instances:
        res = best_model_for_instance(instance, sub_dfs)
        if res is not None:
            model_name, solvetime, gap = res
            n_a += 1 if model_name == name_a else 0
            n_b += 1 if model_name == name_b else 0
            n += 1
    return 2 * min(n_a / n, n_b / n)


def impact(dfs, name_a, name_b):
    st_a = st_b = st_oracle = 0
    for ix, (index, row) in enumerate(dfs[name_a].iterrows()):
        feas_a, solvetime_a, gap_a = row.values
        other_df = dfs[name_b]
        feas_b, solvetime_b, gap_b = other_df.values[ix]
        optimal_a = feas_a and gap_a == 0
        optimal_b = feas_b and gap_b == 0
        if optimal_a and optimal_b:
            st_a += solvetime_a
            st_b += solvetime_b
            st_oracle += min(solvetime_a, solvetime_b)
    return {'only_a_total_solvetime': st_a,
            'only_b_total_solvetime': st_b,
            'oracle_total_solvetime': st_oracle,
            'best_improvement': max(st_a - st_oracle, st_b - st_oracle)}


def read_dataframes(path, model_file_filter_predicate=None):
    model_filenames = [f for f in os.listdir(path) if f.endswith('.csv') and ('-CT' in f or '-DT' in f) and (model_file_filter_predicate(f) if model_file_filter_predicate is not None else True)]
    return {model_fn.replace('.csv', ''): pd.read_csv(model_fn, index_col=0, header=0) for model_fn in model_filenames}


def collect_results_from_disk(path):
    dfs = read_dataframes(path)
    model_names = [ mn for mn in list(dfs.keys()) if 'Kone' not in mn ]
    results = {}
    for ix_a, name_a in enumerate(model_names):
        for ix_b, name_b in enumerate(model_names):
            if ix_a < ix_b:
                print(f'Computing results for {name_a} and {name_b}')
                results[(name_a, name_b)] = {
                    'competitiveness': competitiveness(dfs, name_a, name_b),
                    'impact': impact(dfs, name_a, name_b)
                }
    return results


def best_model_for_instance(instance, dfs):
    best_model = None
    for model_name, df in dfs.items():
        feas, solvetime, gap = df.loc[instance].values
        this = (model_name, solvetime, gap)
        if feas:
            if best_model is None or solvetime <= best_model[1] and gap <= best_model[2]:
                best_model = this
    return best_model


def best_model_for_instances(path):
    dfs = read_dataframes(path)
    model_names = list(dfs.keys())
    instances = next(iter(dfs.values())).index.values
    data, new_index = [], []
    for instance in instances:
        bm = best_model_for_instance(instance, dfs)
        if bm is not None:
            data.append(bm[0] if model_names is None else model_names.index(bm[0]))
            new_index.append(instance)
    bmdf = pd.DataFrame(index=new_index, data=data, columns=['best_model_name'])
    bmdf.index.name = 'instance'
    return bmdf


def characteristics():
    # TODO: Characteristics for all instances from j30 and j90 without OC data
    model_portfolio = ['Pri-DT.csv', 'Kop-CT1.csv']
    dfs = read_dataframes('.', model_file_filter_predicate=lambda fn: fn in model_portfolio)
    model_names = list(dfs.keys())
    cdf = pd.read_csv('characteristics_kopset_j90.csv', index_col=0, header=0, sep=';')
    data, nindex = [], []
    icount = len(cdf.index)
    for ctr, instance in enumerate(cdf.index):
        print(f'\rDetermining best model for instance {instance}, progress {ctr / icount * 100.0}%', end='', flush=True)
        ext = '.rcp' if 'RG30' in instance else '.sm'
        bm = best_model_for_instance(instance + ext, dfs)
        if bm is not None:
            data.append(list(cdf.loc[instance].values) + [model_names.index(bm[0])])
            nindex.append(instance)
    odf = pd.DataFrame(index=nindex, data=data, columns=list(cdf.columns) + ['best_model'])
    odf.index.name = 'instance'
    return odf


def print_stats():
    def to_csv_line(k, v):
        return ','.join(list(map(lambda x: str(x), [','.join(k), v['competitiveness'], v['impact']['best_improvement']])))

    print('model1,model2,competitiveness,impact_oracle_improvement')
    best_competitiveness = (('', ''), 0)
    glob_best_improvement = (('', ''), 0)
    for k, v in collect_results_from_disk('.').items():
        if v['competitiveness'] > best_competitiveness[1]:
            best_competitiveness = (k, v['competitiveness'])
        if v['impact']['best_improvement'] > glob_best_improvement[1]:
            glob_best_improvement = (k, v['impact']['best_improvement'])
        # print(f'{k}=>{v}\n')
        print(to_csv_line(k, v))
    print(f'Best competitiveness: {best_competitiveness}')
    print(f'Best improvement: {glob_best_improvement}')


if __name__ == '__main__':
    # df = best_model_for_instances('.')
    # df.to_csv('best_model.csv')
    # cf = characteristics()
    # cf.to_csv('char_best_model.csv')
    print_stats()

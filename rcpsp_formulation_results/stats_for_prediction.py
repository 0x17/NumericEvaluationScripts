import pandas as pd
import rcpsp_formulation_results.metrics as tom
import json
import os


def gen_update_dict(feas, solvetime, gap, tlim):
    return {'nfeas': 1 if feas else 0,
            'nopt': 1 if gap == 0 and feas and solvetime < tlim else 0,
            'ngood': 1 if gap < 0.03 and feas else 0,
            'totalsolvetime': solvetime,
            'avggap': gap if feas else 1.0}


def apply_update_dict(d, updater):
    for k, v in updater.items():
        d[k] += v


def stats_for_prediction(pred_fn):
    def correct_avg_gaps(stats, num_instances):
        for method in stats.keys():
            stats[method]['avggap'] /= num_instances

    def is_psplib(inst):
        return any(substr in inst for substr in ['j30', 'j60', 'j90'])

    model_portfolio = ['Kop-DT2.csv', 'Kop-CT1.csv']
    dfs = tom.read_dataframes('.', model_file_filter_predicate=lambda fn: fn in model_portfolio)
    model_names = list(dfs.keys())
    stats = {method: dict(nfeas=0, nopt=0, ngood=0, totalsolvetime=0, avggap=0) for method in model_names + ['as', 'oracle']}
    pdf = pd.read_csv(pred_fn, sep=';', index_col=0, header=None)
    val_instances = list(pdf.index.values)
    nbest_a = nbest_b = npredcorr = 0
    for vinst in val_instances:
        tlim = 1200 if 'j90' in vinst else 600
        vinst_ext = vinst + '.sm' if is_psplib(vinst) else vinst + '.rcp'
        predicted_as_model_index = int(pdf.loc[vinst].values[0])
        oracle_model_index = int(pdf.loc[vinst].values[1])
        feas_a, solvetime_a, gap_a = dfs[model_names[0]].loc[vinst_ext].values
        feas_b, solvetime_b, gap_b = dfs[model_names[1]].loc[vinst_ext].values
        updates_a = gen_update_dict(feas_a, solvetime_a, gap_a, tlim)
        updates_b = gen_update_dict(feas_b, solvetime_b, gap_b, tlim)
        apply_update_dict(stats[model_names[0]], updates_a)
        apply_update_dict(stats[model_names[1]], updates_b)
        apply_update_dict(stats['as'], updates_a if predicted_as_model_index == 0 else updates_b)
        apply_update_dict(stats['oracle'], updates_a if oracle_model_index == 0 else updates_b)
        nbest_a += 1 if oracle_model_index == 0 else 0
        nbest_b += 1 if oracle_model_index == 1 else 0
        npredcorr += 1 if predicted_as_model_index == oracle_model_index else 0

    correct_avg_gaps(stats, len(val_instances))
    stats[model_names[0]]['accuracy'] = nbest_a / len(val_instances)
    stats[model_names[1]]['accuracy'] = nbest_b / len(val_instances)
    stats['as']['accuracy'] = npredcorr / len(val_instances)
    stats['oracle']['accuracy'] = 1

    return stats


def generate_tex_table_code(ofn, data_dict, num_samples):
    column_order = ['Kop-CT1', 'Kop-DT2', 'as', 'oracle']
    row_order = ['accuracy', 'nfeas', 'ngood', 'nopt']
    rmapping = {'accuracy': 'Accuracy',
                'nfeas': 'Feasible',
                'ngood': 'Good',
                'nopt': 'Optimal'}
    ostr = ''

    for row_name in row_order:
        row_values = [rmapping[row_name]]
        for column_name in column_order:
            value = data_dict[column_name][row_name]
            if row_order.index(row_name) > 0:
                value /= num_samples
            value = round(value * 100.0, 2)
            row_values += ["{:.2f}".format(value) + '\\%']

        ostr += ' & '.join(row_values) + '\\\\\n'

    with open(ofn, 'w') as fp:
        fp.write(ostr)


def instances_from_prediction_csv(fn):
    pdf = pd.read_csv(fn, sep=';', index_col=0, header=None)
    return list(pdf.index.values)


def all_model_stats_on_instances(instances):
    def is_res_fn(fn):
        return fn.endswith('.csv') and ('DT' in fn or 'CT' in fn)

    model_portfolio = [fn for fn in os.listdir('.') if is_res_fn(fn)]
    dfs = tom.read_dataframes('.', model_file_filter_predicate=lambda fn: fn in model_portfolio)
    model_names = list(dfs.keys())
    stats = {method: dict(nfeas=0, nopt=0, ngood=0, totalsolvetime=0, avggap=0) for method in model_names}

    def correct_avg_gaps(stats, num_instances):
        for method in stats.keys():
            stats[method]['avggap'] /= num_instances

    def is_psplib(inst):
        return any(substr in inst for substr in ['j30', 'j60', 'j90'])

    for vinst in instances:
        tlim = 1200 if 'j90' in vinst else 600
        vinst_ext = vinst + '.sm' if is_psplib(vinst) else vinst + '.rcp'
        for model_name in model_names:
            if 'Kone' in model_name and 'j90' in vinst: continue
            feas, solvetime, gap = dfs[model_name].loc[vinst_ext].values
            updates = gen_update_dict(feas, solvetime, gap, tlim)
            apply_update_dict(stats[model_name], updates)

    correct_avg_gaps(stats, len(instances))

    return stats


def print_stats(for_dnn=False):
    infix = 'dnn' if for_dnn else 'models'
    print('Stats only on validation data')
    only_val_stats = stats_for_prediction(f'predictions_{infix}_onlyvalidation.csv')
    print(json.dumps(only_val_stats, indent=4))
    print('Stats on all data (train and validation)')
    all_data_stats = stats_for_prediction(f'predictions_{infix}_with_train.csv')
    print(json.dumps(all_data_stats, indent=4))
    generate_tex_table_code(f'only_validation_table_{infix}.tex', only_val_stats, 295)
    generate_tex_table_code(f'train_and_validation_table_{infix}.tex', all_data_stats, 3240)


def generate_all_models_tex_table_code(ofn, data_dict, num_samples):
    column_order = ['ngood', 'nopt', 'nfeas']
    sort_by_desc = 'ngood'
    ostr = 'Ranking & Model & Good (\\%) & Optimal (\\%) & Feasible (\\%) \\\\\n'

    sorted_model_names = sorted(data_dict.keys(), key=lambda model_name: data_dict[model_name][sort_by_desc], reverse=True)
    for ix, row_name in enumerate(sorted_model_names):
        row_values = [str(ix+2), row_name] + ["{:.2f}".format(round(data_dict[row_name][column_name] / num_samples * 100.0, 2)) + '\\%' for column_name in column_order]
        ostr += ' & '.join(row_values) + '\\\\\n'

    with open(ofn, 'w') as fp:
        fp.write(ostr)


if __name__ == '__main__':
    # print_stats(for_dnn=False)
    instances = instances_from_prediction_csv('predictions_models_onlyvalidation.csv')
    stats = all_model_stats_on_instances(instances)
    print(json.dumps(stats, indent=4))
    generate_all_models_tex_table_code(f'all_models_validation_table.tex', stats, 295)

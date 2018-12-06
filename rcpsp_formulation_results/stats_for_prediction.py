import pandas as pd
import rcpsp_formulation_results.metrics as tom
import json


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

    def is_psplib(inst): return any(substr in inst for substr in ['j30', 'j60', 'j90'])

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


if __name__ == '__main__':
    print('Stats only on validation data')
    print(json.dumps(stats_for_prediction('predictions_models_onlyvalidation.csv'), indent=4))
    print('Stats on all data (train and validation)')
    print(json.dumps(stats_for_prediction('predictions_models_with_train.csv'), indent=4))

import pandas as pd
import rcpsp_formulation_results.time_oriented_metrics as tom
import json

def gen_update_dict(feas, solvetime, gap):
    return {'nfeas': 1 if feas else 0,
            'nopt': 1 if gap <= 0.0001 and feas else 0,
            'totalsolvetime': solvetime,
            'avggap': gap if feas else 1.0}


def apply_update_dict(d, updater):
    for k, v in updater.items():
        d[k] += v


def stats_for_prediction(pred_fn):
    def correct_avg_gaps(stats, num_instances):
        for method in stats.keys():
            stats[method]['avggap'] /= num_instances

    model_portfolio = ['Pri-DT.csv', 'Kop-CT1.csv']
    dfs = tom.read_dataframes('.', model_file_filter_predicate=lambda fn: fn in model_portfolio)
    model_names = list(dfs.keys())
    stats = {method: dict(nfeas=0, nopt=0, totalsolvetime=0, avggap=0) for method in model_names + ['as', 'oracle']}
    pdf = pd.read_csv(pred_fn, sep=';', index_col=0, header=None)
    val_instances = list(pdf.index.values)
    for vinst in val_instances:
        vinst_ext = vinst + '.sm' if 'j30' in vinst or 'j60' in vinst else vinst + '.rcp'
        predicted_as_model_index = int(pdf.loc[vinst].values[0])
        oracle_model_index = int(pdf.loc[vinst].values[1])
        feas_a, solvetime_a, gap_a = dfs[model_names[0]].loc[vinst_ext].values
        feas_b, solvetime_b, gap_b = dfs[model_names[1]].loc[vinst_ext].values
        updates_a = gen_update_dict(feas_a, solvetime_a, gap_a)
        updates_b = gen_update_dict(feas_b, solvetime_b, gap_b)
        apply_update_dict(stats[model_names[0]], updates_a)
        apply_update_dict(stats[model_names[1]], updates_b)
        apply_update_dict(stats['as'], updates_a if predicted_as_model_index == 0 else updates_b)
        apply_update_dict(stats['oracle'], updates_a if oracle_model_index == 0 else updates_b)

    correct_avg_gaps(stats, len(val_instances))

    return stats


if __name__ == '__main__':
    print(json.dumps(stats_for_prediction('predictions_models.csv'), indent=4))

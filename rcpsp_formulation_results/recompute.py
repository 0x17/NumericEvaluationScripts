import rcpsp_formulation_results.metrics as metrics
import rcpsp_formulation_results.excel_to_dataframes as excl2df
import rcpsp_formulation_results.stats_for_prediction as stats
import rcpsp_formulation_results.dnn as dnn
import os

if __name__ == '__main__':
    with_excel_conversion = False
    with_dnn = True
    with_weka = False

    os.system('sh collectchars.sh')

    if with_excel_conversion:
        excl2df.merge_results_for_all_models()

    if with_weka:
        cf = metrics.characteristics(one_hot=False)
        cf.to_csv('char_best_model.csv')
        os.system('java -jar WhoIsBetterClassification.jar convert')
        os.system('java -jar WhoIsBetterClassification.jar predict')
        stats.print_stats(for_dnn=False)

    if with_dnn:
        cf = metrics.characteristics(one_hot=True)
        cf.to_csv('char_best_model_dnn.csv')
        dnn.train_dnn_model(True)
        stats.print_stats(for_dnn=True)


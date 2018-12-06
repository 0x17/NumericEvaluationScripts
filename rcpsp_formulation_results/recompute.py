import rcpsp_formulation_results.metrics as metrics
import rcpsp_formulation_results.excel_to_dataframes as excl2df
import rcpsp_formulation_results.stats_for_prediction as stats
import os

if __name__ == '__main__':
    excl2df.merge_results_for_all_models()
    cf = metrics.characteristics(one_hot=False)
    cf.to_csv('char_best_model.csv')
    os.system('java -jar WhoIsBetterClassification.jar convert')
    os.system('java -jar WhoIsBetterClassification.jar predict')
    stats.print_stats()

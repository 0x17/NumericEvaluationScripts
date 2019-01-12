import warnings
import autosklearn.classification
import pandas as pd
import sklearn.metrics
from sklearn.model_selection import train_test_split
from joblib import dump, load
from autosklearn.pipeline.classification import SimpleClassificationPipeline


def load_data():
    data = pd.read_csv('char_best_model.csv', index_col=0, header=0)
    X = data.drop(['revSlope', 'best_model'], axis=1).values
    y = data['best_model'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.9, test_size=0.1, random_state=23)
    return X, y, X_train, y_train, X_test, y_test


def construct_ensemble(do_save=False):
    X, y, X_train, y_train, X_test, y_test = load_data()
    print('Training on ' + str(len(X_train)) + ' samples. Validating on ' + str(len(X_test)) + ' samples.')

    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=RuntimeWarning)

    n_hours = 1
    cls = autosklearn.classification.AutoSklearnClassifier(time_left_for_this_task=60 * 60 * n_hours,
                                                           per_run_time_limit=360,
                                                           ensemble_size=1,
                                                           resampling_strategy='cv',
                                                           resampling_strategy_arguments={'folds': 5})
    cls.fit(X.copy(), y.copy())
    cls.refit(X_train.copy(), y_train.copy())
    if do_save:
        dump(cls, 'final_ensemble.joblib')

    print(cls.show_models())
    print(cls.sprint_statistics())
    predictions = cls.predict(X_test)
    print(f'Accuracy score: {sklearn.metrics.accuracy_score(y_test, predictions)}')

    return cls, X_test, y_test


def load_ensemble():
    cls = load('final_ensemble.joblib')
    return cls


def score_clf(cls, X_test, y_test):
    print(cls.show_models())
    print(cls.sprint_statistics())
    predictions = cls.predict(X_test)
    print(f'Accuracy score: {sklearn.metrics.accuracy_score(y_test, predictions)}')
    # weighted_models = cls.get_models_with_weights()


def train_pipeline(X_train, y_train):
    pipeline = SimpleClassificationPipeline(
        {'balancing:strategy': 'weighting', 'categorical_encoding:__choice__': 'no_encoding', 'classifier:__choice__': 'extra_trees', 'imputation:strategy': 'mean', 'preprocessor:__choice__': 'polynomial', 'rescaling:__choice__': 'standardize', 'classifier:extra_trees:bootstrap': 'True', 'classifier:extra_trees:criterion': 'entropy', 'classifier:extra_trees:max_depth': 'None',
         'classifier:extra_trees:max_features': 0.31690578243532874, 'classifier:extra_trees:max_leaf_nodes': 'None', 'classifier:extra_trees:min_impurity_decrease': 0.0, 'classifier:extra_trees:min_samples_leaf': 2, 'classifier:extra_trees:min_samples_split': 3, 'classifier:extra_trees:min_weight_fraction_leaf': 0.0, 'classifier:extra_trees:n_estimators': 100, 'preprocessor:polynomial:degree': 2,
         'preprocessor:polynomial:include_bias': 'True', 'preprocessor:polynomial:interaction_only': 'True'},
        dataset_properties={
            'task': 1,
            'sparse': False,
            'multilabel': False,
            'multiclass': False,
            'target_type': 'classification',
            'signed': False})

    pipeline.fit(X_train, y_train)
    return pipeline


if __name__ == '__main__':
    #construct_ensemble(False)
    # cls, X_test, y_test = construct_ensemble()
    # score_clf(cls, X_test, y_test)
    # load_ensemble()

    X, y, X_train, y_train, X_test, y_test = load_data()
    cls = train_pipeline(X_train, y_train)
    predictions = cls.predict(X_test)
    print(f'Accuracy score: {sklearn.metrics.accuracy_score(y_test, predictions)}')

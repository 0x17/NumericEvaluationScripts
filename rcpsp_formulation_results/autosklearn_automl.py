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


def construct_ensemble():
    X, y, X_train, y_train, X_test, y_test = load_data()
    print('Training on ' + str(len(X_train)) + ' samples. Validating on ' + str(len(X_test)) + ' samples.')

    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=RuntimeWarning)

    cls = autosklearn.classification.AutoSklearnClassifier(time_left_for_this_task=120,
                                                           per_run_time_limit=30,
                                                           ensemble_size=1,
                                                           resampling_strategy='cv',
                                                           resampling_strategy_arguments={'folds': 5})
    cls.fit(X.copy(), y.copy())
    cls.refit(X_train.copy(), y_train.copy())
    dump(cls, 'final_ensemble.joblib')
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
    pipeline = SimpleClassificationPipeline({'balancing:strategy': 'none', 'categorical_encoding:__choice__': 'one_hot_encoding', 'classifier:__choice__': 'random_forest', 'imputation:strategy': 'mean', 'preprocessor:__choice__': 'no_preprocessing', 'rescaling:__choice__': 'standardize', 'categorical_encoding:one_hot_encoding:use_minimum_fraction': 'True', 'classifier:random_forest:bootstrap': 'True',
                                  'classifier:random_forest:criterion': 'gini', 'classifier:random_forest:max_depth': 'None', 'classifier:random_forest:max_features': 0.5, 'classifier:random_forest:max_leaf_nodes': 'None', 'classifier:random_forest:min_impurity_decrease': 0.0, 'classifier:random_forest:min_samples_leaf': 1, 'classifier:random_forest:min_samples_split': 2,
                                  'classifier:random_forest:min_weight_fraction_leaf': 0.0, 'classifier:random_forest:n_estimators': 100, 'categorical_encoding:one_hot_encoding:minimum_fraction': 0.01},
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
    #cls, X_test, y_test = construct_ensemble()
    #score_clf(cls, X_test, y_test)
    # load_ensemble()
    X, y, X_train, y_train, X_test, y_test = load_data()
    cls = train_pipeline(X_train, y_train)
    predictions = cls.predict(X_test)
    print(f'Accuracy score: {sklearn.metrics.accuracy_score(y_test, predictions)}')


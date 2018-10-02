from subprocess import call
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.tree import export_graphviz

import pandas as pd
import numpy as np
import sklearn.metrics
import sklearn.ensemble
import random


def is_min_in_row(row):
    mval = min(row)
    index_of_min = next(ix for ix, val in enumerate(row) if val == mval)
    return [1 if ix == index_of_min else 0 for ix,val in enumerate(row)]


def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true))


def count_times_gurobi_dominated(ys):
    gurobi_loose_count = sum(1 if min(triple) != triple[0] else 0 for triple in ys.values)
    print('Percentage gurobi got dominated = ' + str(gurobi_loose_count / len(ys.values)))


def load_train_data():
    random.seed(42)
    df = pd.read_csv('train_solvetimes.csv', index_col=0, header=0)
    feature_names = df.columns[1:-6]
    xs_all = df[feature_names]
    ys_all_solvetimes = df[df.columns[-6:]].filter(like='solvetime', axis=1)
    ys_all = pd.DataFrame(index=df.index, columns=ys_all_solvetimes.columns, data=ys_all_solvetimes.apply(is_min_in_row, axis=1).values)
    xs, xs_test, ys, ys_test = train_test_split(xs_all, ys_all, train_size=0.5, random_state=42)

    # count_times_gurobi_dominated(ys_all)

    return xs, xs_test, ys, ys_test, feature_names


def print_tree_infos(cls):
    total_node_count = 0
    for ix, estimator in enumerate(cls.estimators_):
        t = estimator.tree_
        print('Tree ' + str(ix) + ': nodecount=' + str(t.node_count) + ', max_depth=' + str(t.max_depth))
        total_node_count += t.node_count
    print('Total node count: ' + str(total_node_count))


def train_my_forest():
    xs, xs_test, ys, ys_test, feature_names = load_train_data()

    print('Training random forest on ' + str(len(xs)) + ' samples. Validating on ' + str(len(xs_test)) + ' samples.')

    config = dict(n_estimators=100,
                  #criterion='mse',
                  max_features=1.0,
                  n_jobs=4,
                  verbose=2)

    #cls = sklearn.ensemble.RandomForestRegressor(**config)
    cls = sklearn.ensemble.RandomForestClassifier(**config)
    cls.fit(xs, ys)

    print_tree_infos(cls)

    joblib.dump(cls, 'my_trained_forest.pkl')

int_conv = np.vectorize(lambda v: int(v))

def predict_with_my_forest():
    xs, xs_test, ys, ys_test, feature_names = load_train_data()
    cls = joblib.load('my_trained_forest.pkl')
    print('score='+str(cls.score(xs_test, ys_test)))
    ys_test_pred = pd.DataFrame(int_conv(cls.predict(xs_test)), index=ys_test.index, columns=ys_test.columns)
    # print(' MAPE: ' + str(mean_absolute_percentage_error(ys_test.values, ys_test_pred.values) * 100.0) + '%')
    return cls, feature_names


def plot_trees(cls, feature_names):
    for ix, tree in enumerate(cls.estimators_):
        export_graphviz(tree, out_file='tree' + str(ix) + '.dot', feature_names=feature_names, proportion=False, filled=True)
        call(('dot -Tpdf tree' + str(ix) + '.dot -o tree' + str(ix) + '.pdf').split())


if __name__ == '__main__':
    train_my_forest()
    cls, feature_names = predict_with_my_forest()

from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

data = pd.read_csv('char_best_model.csv', index_col=0, header=0)

X = data.drop(['revSlope', 'best_model'], axis=1).values
y = data['best_model'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.75, test_size=0.25, random_state=1)

tpot = TPOTClassifier(generations=5, population_size=50, verbosity=4)
tpot.fit(X_train, y_train)
print(tpot.score(X_test, y_test))
tpot.export('tpot_clf_pipeline.py')
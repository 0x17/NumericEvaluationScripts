from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

data = pd.read_csv('char_best_model.csv', index_col=0, header=0)

X = data.drop(['revSlope', 'best_model'], axis=1).values
y = data['best_model'].values

tpot = TPOTClassifier(generations=10, population_size=50, verbosity=3, n_jobs=-1)
tpot.fit(X, y)
#X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.9, test_size=0.1, random_state=23)
#print(tpot.score(X_test, y_test))
tpot.export('tpot_clf_pipeline.py')
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint

from keras.layers import Dense
from keras.models import Sequential, load_model

import pandas as pd

import os

import matplotlib.pyplot as plt


def plot_model_history(model_history, ofn='multipage.pdf'):
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(ofn) as pp:
        fig, axs = plt.subplots(1, 2, figsize=(15, 5))
        axs[0].plot(range(1, len(model_history.history['acc']) + 1), model_history.history['acc'])
        axs[0].plot(range(1, len(model_history.history['val_acc']) + 1), model_history.history['val_acc'])
        axs[0].set_title('Model Accuracy')
        axs[0].set_ylabel('Accuracy')
        axs[0].set_xlabel('Epoch')
        axs[0].set_xticks(np.arange(1, len(model_history.history['acc']) + 1), len(model_history.history['acc']) / 10)
        axs[0].legend(['train', 'val'], loc='best')
        axs[1].plot(range(1, len(model_history.history['loss']) + 1), model_history.history['loss'])
        axs[1].plot(range(1, len(model_history.history['val_loss']) + 1), model_history.history['val_loss'])
        axs[1].set_title('Model Loss')
        axs[1].set_ylabel('Loss')
        axs[1].set_xlabel('Epoch')
        axs[1].set_xticks(np.arange(1, len(model_history.history['loss']) + 1), len(model_history.history['loss']) / 10)
        axs[1].legend(['train', 'val'], loc='best')
        pp.savefig()


def build_network(ninputs, noutputs, sizes, act='relu', init='uniform', bias=True, output_activation='softmax', regression=False):
    if regression: output_activation = 'relu'
    input_layer = [Dense(sizes[0], input_dim=ninputs, activation=act, kernel_initializer=init, use_bias=bias)]
    output_layer = [Dense(noutputs, activation=output_activation, kernel_initializer=init, use_bias=bias)]
    hidden_layers = [Dense(size, activation=act, kernel_initializer=init, use_bias=bias) for size in sizes[1:]]
    dnn = Sequential(input_layer + hidden_layers + output_layer)
    dnn.compile(loss=('mse' if not regression else 'mape'), optimizer='adam', metrics=(['acc'] if not regression else []))
    dnn.summary()
    return dnn


def load_train_data(fn, num_ys=4):
    data = pd.read_csv(fn, sep=',', header=0, index_col=0)
    ncols = len(data.columns)
    return data.iloc[:, :ncols - num_ys], data.iloc[:, ncols - num_ys:]


def extract_split_from_prediction_data(pred_fn, data_fn, xs, ys):
    def extract_instances(fn, skip_first, sep=';'):
        with open(fn, 'r') as fp:
            return [line.split(sep)[0] for line in fp.readlines()[1 if skip_first else 0:] if sep in line]

    validation_instances = extract_instances(pred_fn, skip_first=False, sep=';')
    ordered_instances = extract_instances(data_fn, skip_first=True, sep=',')
    training_instances = [instance for instance in ordered_instances if instance not in validation_instances]

    def only_training(src_set, inverse):
        return src_set.drop(validation_instances if not inverse else training_instances)

    train_xs = only_training(xs, inverse=False)
    train_ys = only_training(ys, inverse=False)
    val_xs = only_training(xs, inverse=True)
    val_ys = only_training(ys, inverse=True)

    return (train_xs, train_ys), (val_xs, val_ys)


def make_and_save_predictions(dnn, ofn, xs, ys):
    res = dnn.predict(xs)
    best_actual = np.argmax(ys.values, axis=1)
    best_pred = np.argmax(res, axis=1)
    diff = np.subtract(best_actual, best_pred)

    best_pred_and_actual = [[best_pred[ix], b_actual] for ix, b_actual in enumerate(best_actual)]

    print(best_pred)
    print(best_actual)
    print(diff)
    print(f'accuracy: {1 - np.sum(np.abs(diff)) / len(diff)}')

    odf = pd.DataFrame(best_pred_and_actual, index=xs.index, columns=['class_as', 'class_oracle'])
    odf.to_csv(ofn, sep=';', header=None)


def train_dnn_model(skip_model_load=False):
    num_classes = 2
    np.random.seed(23)
    xs, ys = load_train_data('char_best_model_dnn.csv', num_classes)

    train, validation = extract_split_from_prediction_data('predictions_models_onlyvalidation.csv', 'char_best_model_dnn.csv', xs, ys)
    train_xs, train_ys = train
    val_xs, val_ys = validation

    model_fn = 'trained_model.h5'
    checkpoint_fn = 'weights.best.hdf5'

    early_stop = EarlyStopping(monitor='val_acc', min_delta=0.000001, patience=10, verbose=1, mode='auto')
    checkpoint = ModelCheckpoint('weights.best.hdf5', monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks = [checkpoint]

    if os.path.isfile(model_fn) and not skip_model_load:
        dnn = load_model(model_fn)
    else:
        dnn = build_network(ninputs=len(xs.columns), noutputs=len(ys.columns), sizes=[512, 256, 190, 64, 32, 16], regression=False)
        info = dnn.fit(train_xs, train_ys, validation_data=(val_xs, val_ys), batch_size=10, epochs=1000, verbose=2, shuffle=True, callbacks=callbacks)
        dnn.save(model_fn)
        plot_model_history(info)

    dnn = load_model(checkpoint_fn)
    make_and_save_predictions(dnn, 'predictions_dnn_onlyvalidation.csv', val_xs, val_ys)
    make_and_save_predictions(dnn, 'predictions_dnn_with_train.csv', xs, ys)


if __name__ == '__main__':
    train_dnn_model(True)

"""Deep learning models: LSTM, Bi-LSTM, GRU."""

from __future__ import annotations

import numpy as np


def build_lstm(input_shape: tuple, units: int = 64):
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout

    model = Sequential([
        LSTM(units, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(units // 2),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def build_bilstm(input_shape: tuple, units: int = 64):
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import Bidirectional, LSTM, Dense, Dropout

    model = Sequential([
        Bidirectional(LSTM(units, return_sequences=True), input_shape=input_shape),
        Dropout(0.2),
        Bidirectional(LSTM(units // 2)),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def build_gru(input_shape: tuple, units: int = 64):
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout

    model = Sequential([
        GRU(units, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        GRU(units // 2),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def reshape_sequences(X: np.ndarray, seq_len: int = 6) -> np.ndarray:
    n, f = X.shape
    pad = (seq_len - f % seq_len) % seq_len
    if pad:
        X = np.pad(X, ((0, 0), (0, pad)))
    return X.reshape(n, -1, seq_len)

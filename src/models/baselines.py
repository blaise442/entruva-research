"""The three preregistered baselines telemetry must beat."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def class_prior_baseline(train_groups, y_train, test_groups) -> np.ndarray:
    rates = pd.Series(np.asarray(y_train)).groupby(np.asarray(train_groups)).mean()
    fallback = float(np.asarray(y_train).mean())
    return np.array([float(rates.get(g, fallback)) for g in np.asarray(test_groups)])

def _logistic(X_train: np.ndarray, y_train, X_test: np.ndarray) -> np.ndarray:
    scaler = StandardScaler().fit(X_train)
    model = LogisticRegression(max_iter=1000).fit(scaler.transform(X_train), np.asarray(y_train))
    return model.predict_proba(scaler.transform(X_test))[:, 1]

def task_count_baseline(train_counts, y_train, test_counts) -> np.ndarray:
    return _logistic(
        np.asarray(train_counts, dtype=float).reshape(-1, 1),
        y_train,
        np.asarray(test_counts, dtype=float).reshape(-1, 1),
    )

def combined_baseline(train_groups, train_counts, y_train, test_groups, test_counts) -> np.ndarray:
    prior_train = class_prior_baseline(train_groups, y_train, train_groups)
    prior_test = class_prior_baseline(train_groups, y_train, test_groups)
    X_train = np.column_stack([prior_train, np.asarray(train_counts, dtype=float)])
    X_test = np.column_stack([prior_test, np.asarray(test_counts, dtype=float)])
    return _logistic(X_train, y_train, X_test)

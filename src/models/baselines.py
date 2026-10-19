"""The preregistered naive baseline, exactly as published: a model that sees only
agent model identity, task type, and task length. Its keys are shared across
agents by construction, so grouped CV by agent identity cannot collapse it to a
global constant (review findings C1, C2)."""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def naive_baseline(train_model, train_task_type, train_length, y_train,
                   test_model, test_task_type, test_length) -> np.ndarray:
    def stack(model, task, length):
        return np.column_stack([np.asarray(model), np.asarray(task), np.asarray(length, dtype=object)])
    pre = ColumnTransformer([
        ("cats", OneHotEncoder(handle_unknown="ignore"), [0, 1]),
        ("len", StandardScaler(), [2]),
    ])
    pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
    pipe.fit(stack(train_model, train_task_type, train_length), np.asarray(y_train))
    # classes_ is sorted, so for 0/1 labels column 1 is the failure class
    return pipe.predict_proba(stack(test_model, test_task_type, test_length))[:, 1]

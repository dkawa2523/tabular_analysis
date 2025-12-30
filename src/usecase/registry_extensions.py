"""Usecase registry extensions for models/metrics/preprocessors."""

from __future__ import annotations

from ml_platform.registry import register_metric, register_model, register_preprocessor

_REGISTERED = False


class IdentityPreprocessor:
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

    def fit_transform(self, X, y=None):
        self.fit(X, y=y)
        return self.transform(X)


def make_identity_preprocessor():
    return IdentityPreprocessor()


class ConstantModel:
    def __init__(self, value: float = 0.0):
        self.value = float(value)

    def fit(self, X, y=None):
        if y is None:
            return self
        total = 0.0
        count = 0
        for value in y:
            total += float(value)
            count += 1
        if count:
            self.value = total / count
        return self

    def predict(self, X):
        try:
            count = len(X)
        except Exception:
            count = 1
        return [self.value] * count


def make_constant_model(**kwargs):
    return ConstantModel(**kwargs)


def mean_absolute_error(y_true, y_pred):
    total = 0.0
    count = 0
    for actual, pred in zip(y_true, y_pred):
        total += abs(float(actual) - float(pred))
        count += 1
    return total / count if count else 0.0


def register_usecase_extensions() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    # Use usecase-prefixed names to avoid collisions with platform defaults.
    register_preprocessor("usecase.identity", make_identity_preprocessor)
    register_model("usecase.constant", make_constant_model)
    register_metric("usecase.mae", mean_absolute_error)
    _REGISTERED = True

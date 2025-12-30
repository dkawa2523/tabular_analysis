from __future__ import annotations
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt

def plot_pred_vs_true(y_true, y_pred, title: str):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(y_true, y_pred, s=8)
    ax.set_title(title)
    ax.set_xlabel("y_true")
    ax.set_ylabel("y_pred")
    return fig

def plot_residuals(y_true, y_pred, title: str):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    resid = y_true - y_pred
    ax.scatter(y_pred, resid, s=8)
    ax.axhline(0.0, linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("y_pred")
    ax.set_ylabel("residual")
    return fig


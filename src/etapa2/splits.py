"""Particiones train/dev/test estratificadas y reproducibles (70/15/15)."""
import pandas as pd
from sklearn.model_selection import train_test_split

from src.etapa2.config import DEV_SIZE, RANDOM_STATE, TEST_SIZE


def assign_splits(df: pd.DataFrame, label_col: str = "label") -> pd.Series:
    """Devuelve una serie con 'train', 'dev' o 'test' alineada con df.index.

    Dos cortes estratificados: 70 / 30 y luego el 30 en 15 / 15.
    """
    holdout_size = TEST_SIZE + DEV_SIZE
    train_idx, holdout_idx = train_test_split(
        df.index, test_size=holdout_size, shuffle=True,
        random_state=RANDOM_STATE, stratify=df[label_col],
    )
    holdout = df.loc[holdout_idx]
    dev_idx, test_idx = train_test_split(
        holdout.index, test_size=TEST_SIZE / holdout_size, shuffle=True,
        random_state=RANDOM_STATE, stratify=holdout[label_col],
    )
    split = pd.Series("train", index=df.index, name="split")
    split.loc[dev_idx] = "dev"
    split.loc[test_idx] = "test"
    return split


def check_splits(df: pd.DataFrame, label_col: str = "label") -> pd.DataFrame:
    """Tabla clase x split. Falla si alguna clase no aparece en alguna partición."""
    table = pd.crosstab(df[label_col], df["split"])[["train", "dev", "test"]]
    if (table == 0).any().any():
        raise ValueError(f"Hay clases ausentes en alguna partición:\n{table}")
    return table

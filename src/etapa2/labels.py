"""Etiqueta primaria y generación de labeled_documents.tsv.

Política: la etiqueta es `primary_category` de arXiv. Las categorías secundarias
(cross-listing) se guardan en `categories` como metadato y no se usan como etiqueta.

Uso: python -m src.etapa2.labels
"""
import matplotlib.pyplot as plt
import pandas as pd

from src.etapa2.config import (
    CLASSES, DATA_DIR, FIGURES_DIR, LABELED_PATH, RAW_CORPUS_PATH,
)
from src.etapa2.splits import assign_splits, check_splits


def load_raw() -> pd.DataFrame:
    # dtype=str: si no, arxiv_id se lee como float y pierde ceros (2610.00840 -> 2610.0084)
    return pd.read_csv(RAW_CORPUS_PATH, sep="\t", dtype=str, keep_default_na=False)


def check_labels(raw: pd.DataFrame) -> None:
    """Verifica la política de etiqueta; lanza ValueError si algo no cuadra."""
    if (raw["primary_category"] == "").any():
        raise ValueError("Hay documentos sin primary_category")
    unknown = set(raw["primary_category"]) - set(CLASSES)
    if unknown:
        raise ValueError(f"Etiquetas fuera de las clases esperadas: {unknown}")
    first = raw["categories"].str.split().str[0]
    mismatch = raw[raw["primary_category"] != first]
    if len(mismatch):
        raise ValueError(f"{len(mismatch)} documentos con primary_category != categories[0]")
    if not raw["arxiv_id"].is_unique:
        raise ValueError("arxiv_id duplicados")


def build_labeled(raw: pd.DataFrame) -> pd.DataFrame:
    def clean(s: pd.Series) -> pd.Series:
        return s.str.split().str.join(" ")  # colapsa espacios y saltos de línea

    df = pd.DataFrame({
        "document_id": raw["arxiv_id"],
        "text": clean(raw["title"]) + ". " + clean(raw["abstract"]),
        "label": raw["primary_category"],
        "categories": raw["categories"],
    })
    df["split"] = assign_splits(df)
    return df


def load_labeled() -> pd.DataFrame:
    return pd.read_csv(LABELED_PATH, sep="\t", dtype=str, keep_default_na=False)


def cross_listing_rate(df: pd.DataFrame) -> pd.Series:
    """Porcentaje de documentos de cada clase con al menos una categoría secundaria."""
    secondary = df["categories"].str.split().str.len() > 1
    return (secondary.groupby(df["label"]).mean() * 100).round(1)


def plot_distribution(df: pd.DataFrame, path) -> None:
    table = pd.crosstab(df["label"], df["split"])[["train", "dev", "test"]]
    ax = table.plot(kind="bar", stacked=True, figsize=(6, 4), rot=0)
    ax.set_xlabel("Clase (primary_category)")
    ax.set_ylabel("Documentos")
    ax.set_title("Distribución de clases por partición")
    for container in ax.containers:
        ax.bar_label(container, label_type="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main() -> None:
    raw = load_raw()
    check_labels(raw)
    df = build_labeled(raw)
    print(check_splits(df))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(LABELED_PATH, sep="\t", index=False)
    plot_distribution(df, FIGURES_DIR / "class_distribution.png")
    print(f"Guardado {LABELED_PATH} ({len(df)} documentos)")


if __name__ == "__main__":
    main()

"""Tres configuraciones de normalización y su caché.

N0: solo tokenización con spaCy (conserva mayúsculas y puntuación).
N1: tokenización + minúsculas, sin puntuación ni stopwords (token.is_stop).
N2: normalización de la Etapa I (src/normalize.py): minúsculas, lemas y
    eliminación por POS (DET, ADP, CCONJ, SCONJ, PRON, AUX).

La normalización es documento a documento y no aprende de los datos, así que
se calcula una sola vez para los 500 textos. Dentro de los Pipeline se usa
NormalizedText, que recibe document_id y devuelve el texto ya normalizado.

Uso: python -m src.etapa2.normalization
"""
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from src.etapa2.config import NORMALIZATIONS, NORMALIZED_PATH
from src.etapa2.labels import load_labeled
from src.normalize import get_nlp, normalize_doc


def normalize_n0(doc) -> str:
    return " ".join(t.text for t in doc if not t.is_space)


def normalize_n1(doc) -> str:
    return " ".join(
        t.lower_ for t in doc
        if not (t.is_punct or t.is_space or t.is_stop)
    )


NORMALIZERS = {"N0": normalize_n0, "N1": normalize_n1, "N2": normalize_doc}


def build_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Procesa cada texto una vez con nlp.pipe y aplica las tres configuraciones."""
    rows = {name: [] for name in NORMALIZATIONS}
    for doc in get_nlp().pipe(df["text"], batch_size=64):
        for name in NORMALIZATIONS:
            rows[name].append(NORMALIZERS[name](doc))
    out = pd.DataFrame({"document_id": df["document_id"].values})
    for name in NORMALIZATIONS:
        out[f"text_{name.lower()}"] = rows[name]
    return out


def load_variants() -> pd.DataFrame:
    return pd.read_csv(NORMALIZED_PATH, sep="\t", dtype=str, keep_default_na=False)


class NormalizedText(BaseEstimator, TransformerMixin):
    """Primer paso de un Pipeline: document_id -> texto normalizado (N0, N1 o N2).

    No aprende nada en fit; solo busca en la caché. Así train, dev y test pasan
    por el mismo camino y la normalización es un hiperparámetro más.
    """

    def __init__(self, variant: str = "N2"):
        self.variant = variant

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        lookup = _lookup(self.variant)
        return [lookup[doc_id] for doc_id in X]


_CACHE: dict[str, dict[str, str]] = {}


def _lookup(variant: str) -> dict[str, str]:
    if variant not in _CACHE:
        variants = load_variants()
        _CACHE[variant] = dict(zip(variants["document_id"], variants[f"text_{variant.lower()}"]))
    return _CACHE[variant]


def main() -> None:
    df = load_labeled()
    variants = build_variants(df)
    variants.to_csv(NORMALIZED_PATH, sep="\t", index=False)
    for name in NORMALIZATIONS:
        col = variants[f"text_{name.lower()}"].str.split()
        vocab = len(set(t for toks in col for t in toks))
        print(f"{name}: {col.str.len().mean():.1f} tokens/doc, vocabulario {vocab}")
    print(f"Guardado {NORMALIZED_PATH}")


if __name__ == "__main__":
    main()

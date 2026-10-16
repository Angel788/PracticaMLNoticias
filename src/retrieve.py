"""Fase 4 · Recuperación: consulta en texto libre -> top-k documentos por similitud coseno.

Uso (cualquiera de las formas, siempre con la consulta entre comillas):
    python -m src.retrieve "misinformation detection using transformers"   # desde la raíz
    python src/retrieve.py "misinformation detection using transformers"   # desde la raíz
    python retrieve.py "misinformation detection using transformers"       # desde src/
    python -m src.retrieve "image segmentation" --field title --ngram bigram --repr binary -k 5
"""
import argparse
import pickle
import sys
import textwrap
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import normalize as l2_normalize

ROOT = Path(__file__).resolve().parent.parent

# Si se ejecuta como archivo (python src/retrieve.py) y no como módulo
# (python -m src.retrieve), la raíz del repositorio no está en sys.path
if not __package__:
    sys.path.insert(0, str(ROOT))

from src.normalize import normalize  # noqa: E402
MODELS_DIR = ROOT / "models"
RAW_PATH = ROOT / "data" / "scientific_raw_corpus.tsv"

# Metadatos de fuente que acompañan a cada resultado
SOURCE_COLS = ["authors", "primary_category", "categories", "date", "url", "pdf_url", "doi", "source"]

FIELDS = ("title", "abstract")
NGRAMS = ("unigram", "bigram")
REPRS = ("frequency", "binary", "tfidf")


class EmptyQueryError(ValueError):
    """La consulta no tiene términos utilizables tras normalizar."""


#Funcion para carcar los modelos generados frecuncia, binaria, tfidf
@lru_cache(maxsize=None)
def load_model(field: str, ngram: str, repr_: str) -> dict:
    path = MODELS_DIR / f"{field}_{ngram}_{repr_}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"No existe {path.relative_to(ROOT)}; ejecutar los notebooks 03-05")
    with open(path, "rb") as f:
        model = pickle.load(f)
    # Frecuencia y binaria se guardaron sin normalizar; con filas de norma 1
    # el coseno es un producto punto. En TF-IDF no cambia nada.
    model["matrix_l2"] = l2_normalize(model["matrix"])
    return model

#Carga titulo, abstract y metadatos de fuente del corpus crudo con arxiv_id como indice
@lru_cache(maxsize=1)
def load_docs() -> pd.DataFrame:
    corpus = pd.read_csv(RAW_PATH, sep="\t", dtype=str, keep_default_na=False)
    corpus["source"] = "arXiv"
    corpus["pdf_url"] = corpus["url"].str.replace("/abs/", "/pdf/", regex=False)
    return corpus.set_index("arxiv_id")[["title", "abstract", *SOURCE_COLS]]

#Recupera los k documentos mas similares a la consulta
def retrieve(query: str, field: str = "abstract", ngram: str = "unigram",
             repr_: str = "tfidf", k: int = 10) -> pd.DataFrame:
    """Devuelve rank, arxiv_id, score, title, abstract y la fuente (autores, categoría,
    fecha, url, pdf_url, doi) de los k documentos más similares.

    Solo se devuelven documentos con score > 0, así que puede haber menos de k.
    Lanza EmptyQueryError si la consulta queda vacía o fuera del vocabulario.
    """
    if field not in FIELDS or ngram not in NGRAMS or repr_ not in REPRS:
        raise ValueError(f"Configuración inválida: {field}, {ngram}, {repr_}")

    # 1. Misma normalización que el corpus
    query_norm = normalize(query)
    if not query_norm.strip():
        raise EmptyQueryError("La consulta quedó vacía al normalizar (solo tenía stopwords o puntuación)")

    # 2-3. Vectorizar con el vectorizador ya ajustado (transform, nunca fit)
    model = load_model(field, ngram, repr_)
    q = model["vectorizer"].transform([query_norm])
    if q.nnz == 0:
        raise EmptyQueryError(f"Ningún término de la consulta normalizada ('{query_norm}') está en el vocabulario")

    # 4. Similitud coseno contra todos los documentos
    scores = (model["matrix_l2"] @ l2_normalize(q).T).toarray().ravel()

    # 5. Orden descendente, desempate estable por arxiv_id
    ranking = pd.DataFrame({"arxiv_id": model["doc_ids"], "score": scores})
    ranking = ranking[ranking["score"] > 0]
    ranking = ranking.sort_values(["score", "arxiv_id"], ascending=[False, True], kind="stable").head(k)
    ranking.insert(0, "rank", range(1, len(ranking) + 1))
    ranking = ranking.join(load_docs(), on="arxiv_id")
    return ranking.reset_index(drop=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Recupera los artículos más similares a una consulta.")
    parser.add_argument("query", help="consulta en texto libre (entre comillas)")
    parser.add_argument("--field", choices=FIELDS, default="abstract")
    parser.add_argument("--ngram", choices=NGRAMS, default="unigram")
    parser.add_argument("--repr", dest="repr_", choices=REPRS, default="tfidf")
    parser.add_argument("-k", type=int, default=10, help="número de resultados (por defecto 10)")
    parser.add_argument("--chars", type=int, default=300,
                        help="caracteres del abstract a mostrar; 0 = completo (por defecto 300)")
    args = parser.parse_args(argv)

    print(f"Consulta:    {args.query}")
    print(f"Normalizada: {normalize(args.query)}")
    print(f"Config:      {args.field} · {args.ngram} · {args.repr_}\n")
    try:
        ranking = retrieve(args.query, args.field, args.ngram, args.repr_, args.k)
    except EmptyQueryError as e:
        print("Aviso:", e)
        return 1

    if ranking.empty:
        print("Sin resultados")
        return 0
    for r in ranking.itertuples():
        abstract = r.abstract
        if args.chars and len(abstract) > args.chars:
            abstract = abstract[:args.chars].rstrip() + "…"
        print(f"{r.rank:>2}. [{r.score:.4f}] {r.arxiv_id}  {r.title}")
        print(f"    {r.authors}")
        print(f"    {r.source} · {r.primary_category} · {r.date} · {r.url}" + (f" · doi:{r.doi}" if r.doi else ""))
        print(textwrap.fill(abstract, width=100, initial_indent="    ", subsequent_indent="    "))
        print()
    if len(ranking) < args.k:
        print(f"\nSolo {len(ranking)} documentos comparten algún término con la consulta")
    return 0


if __name__ == "__main__":
    sys.exit(main())

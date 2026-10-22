"""Fases 5-6 · Benchmark: valida queries/qrels, ejecuta las consultas y calcula métricas.

Métricas por consulta (k = 10): P@k, R@k, F1@k, RR y nDCG@k.
Los documentos que no aparecen en qrels.tsv cuentan como relevancia 0.

Uso desde la raíz del repositorio:
    python -m src.evaluate --check                       # solo valida queries.tsv y qrels.tsv
    python -m src.evaluate                               # abstract · unigram · tfidf
    python -m src.evaluate --field title --ngram bigram --repr binary
    python -m src.evaluate --all                         # compara las 12 configuraciones

Mientras el benchmark no esté congelado (tag git benchmark-v1) se niega a ejecutar
las consultas, para respetar el protocolo anti-sesgo; --force omite esa comprobación.
"""
import argparse
import math
import subprocess
import sys
from itertools import product
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

if not __package__:
    sys.path.insert(0, str(ROOT))

from src.retrieve import FIELDS, NGRAMS, REPRS, RAW_PATH, EmptyQueryError, retrieve  # noqa: E402

BENCH_DIR = ROOT / "data" / "benchmark"
RESULTS_DIR = ROOT / "results"
QUERIES_PATH = BENCH_DIR / "queries.tsv"
QRELS_PATH = BENCH_DIR / "qrels.tsv"
FREEZE_TAG = "benchmark-v1"

METRICS = ["P@10", "R@10", "F1@10", "RR", "nDCG@10"]
# difficulty_level en queries.tsv sigue el formato del PDF: 1 = fácil, 2 = media, 3 = difícil
LEVELS = ("1", "2", "3")
LEVEL_NAMES = {"1": "easy", "2": "medium", "3": "hard"}
N_QUERIES = 15
MIN_RELEVANT = 10
MAX_RELEVANT = 15  # el PDF pide entre 10 y 15 documentos relevantes por consulta


def load_queries(path: Path = QUERIES_PATH) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def load_qrels(path: Path = QRELS_PATH) -> dict[str, dict[str, int]]:
    """{query_id: {document_id: relevancia}}"""
    df = pd.read_csv(path, sep="\t", dtype={"query_id": str, "document_id": str, "relevance": int})
    qrels: dict[str, dict[str, int]] = {}
    for r in df.itertuples():
        qrels.setdefault(r.query_id, {})[r.document_id] = r.relevance
    return qrels


# ---------------------------------------------------------------- métricas
# `ranked` es la lista de arxiv_id en orden; `rels` el diccionario de qrels de esa consulta

def precision_at_k(ranked: list[str], rels: dict[str, int], k: int = 10) -> float:
    # El denominador es k aunque el sistema devuelva menos documentos
    return sum(1 for d in ranked[:k] if rels.get(d, 0) > 0) / k


def recall_at_k(ranked: list[str], rels: dict[str, int], k: int = 10) -> float:
    n_rel = sum(1 for v in rels.values() if v > 0)
    if n_rel == 0:
        return 0.0
    return sum(1 for d in ranked[:k] if rels.get(d, 0) > 0) / n_rel


def f1(p: float, r: float) -> float:
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def reciprocal_rank(ranked: list[str], rels: dict[str, int], k: int = 10) -> float:
    # Si no hay ningún relevante en el top-k, RR = 0
    for i, d in enumerate(ranked[:k], start=1):
        if rels.get(d, 0) > 0:
            return 1 / i
    return 0.0


def gain(rel: int) -> int:
    # Ganancia exponencial como en el PDF de la práctica: 2^rel - 1 (rel 0 -> 0, 1 -> 1, 2 -> 3)
    return 2 ** rel - 1


def ndcg_at_k(ranked: list[str], rels: dict[str, int], k: int = 10) -> float:
    # Ganancia 2^rel - 1 y descuento log2(rank + 1); el ideal usa todos los qrels
    dcg = sum(gain(rels.get(d, 0)) / math.log2(i + 1) for i, d in enumerate(ranked[:k], start=1))
    ideal = sorted(rels.values(), reverse=True)[:k]
    idcg = sum(gain(g) / math.log2(i + 1) for i, g in enumerate(ideal, start=1))
    return 0.0 if idcg == 0 else dcg / idcg


def query_metrics(ranked: list[str], rels: dict[str, int], k: int = 10) -> dict[str, float]:
    p, r = precision_at_k(ranked, rels, k), recall_at_k(ranked, rels, k)
    return {"P@10": p, "R@10": r, "F1@10": f1(p, r),
            "RR": reciprocal_rank(ranked, rels, k), "nDCG@10": ndcg_at_k(ranked, rels, k)}


# ---------------------------------------------------------------- validación

def validate_benchmark(queries: pd.DataFrame, qrels: dict[str, dict[str, int]],
                       corpus_ids: set[str]) -> list[str]:
    """Devuelve la lista de problemas encontrados (vacía si el benchmark es válido)."""
    problems = []
    if list(queries.columns) != ["query_id", "difficulty_level", "query"]:
        problems.append(f"queries.tsv: columnas inesperadas {list(queries.columns)}")
        return problems
    if len(queries) != N_QUERIES:
        problems.append(f"queries.tsv: hay {len(queries)} consultas, se esperaban {N_QUERIES}")
    if queries["query_id"].duplicated().any():
        problems.append("queries.tsv: query_id duplicados")
    counts = queries["difficulty_level"].value_counts()
    for level in LEVELS:
        if counts.get(level, 0) != N_QUERIES // len(LEVELS):
            problems.append(f"queries.tsv: {counts.get(level, 0)} consultas de nivel '{level}' "
                            f"({LEVEL_NAMES[level]}), se esperaban {N_QUERIES // len(LEVELS)}")
    extra = set(counts.index) - set(LEVELS)
    if extra:
        problems.append(f"queries.tsv: niveles desconocidos {sorted(extra)} (se esperan 1, 2 o 3)")
    for r in queries.itertuples():
        n_words = len(r.query.split())
        if not 3 <= n_words <= 8:
            problems.append(f"{r.query_id}: la consulta tiene {n_words} palabras (se piden 3-8)")

    qids = set(queries["query_id"])
    for qid in sorted(set(qrels) - qids):
        problems.append(f"qrels.tsv: {qid} no existe en queries.tsv")
    for qid in sorted(qids):
        rels = qrels.get(qid, {})
        if len(rels) < MIN_RELEVANT:
            problems.append(f"{qid}: solo {len(rels)} documentos relevantes (mínimo {MIN_RELEVANT})")
        bad_rel = {d: v for d, v in rels.items() if v not in (1, 2)}
        if bad_rel:
            problems.append(f"{qid}: relevancias fuera de {{1, 2}}: {bad_rel}")
        missing = sorted(set(rels) - corpus_ids)
        if missing:
            problems.append(f"{qid}: documentos que no están en el corpus: {missing}")
    return problems


def too_many_relevant(qrels: dict[str, dict[str, int]]) -> dict[str, int]:
    """Consultas con más de MAX_RELEVANT relevantes (el PDF pide 10-15); {query_id: cantidad}."""
    return {q: len(r) for q, r in sorted(qrels.items()) if len(r) > MAX_RELEVANT}


def is_frozen() -> bool:
    out = subprocess.run(["git", "tag", "-l", FREEZE_TAG], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() == FREEZE_TAG


# ---------------------------------------------------------------- ejecución

def run_benchmark(queries: pd.DataFrame, qrels: dict[str, dict[str, int]], field: str = "abstract",
                  ngram: str = "unigram", repr_: str = "tfidf", k: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (rankings, métricas por consulta) para una configuración."""
    rankings, metrics = [], []
    for q in queries.itertuples():
        try:
            ranking = retrieve(q.query, field, ngram, repr_, k)
        except EmptyQueryError as e:
            # Consulta sin términos en el vocabulario: ranking vacío, todas las métricas a 0
            print(f"Aviso ({q.query_id}, {field}·{ngram}·{repr_}): {e}", file=sys.stderr)
            ranking = pd.DataFrame(columns=["rank", "arxiv_id", "score"])
        for r in ranking.itertuples():
            rankings.append({"query_id": q.query_id, "rank": r.rank, "document_id": r.arxiv_id,
                             "score": round(r.score, 6)})
        m = query_metrics(list(ranking["arxiv_id"]), qrels.get(q.query_id, {}), k)
        metrics.append({"query_id": q.query_id, "difficulty_level": q.difficulty_level,
                        "query": q.query, "n_relevant": len(qrels.get(q.query_id, {})), **m})
    return pd.DataFrame(rankings), pd.DataFrame(metrics)


def summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    """Promedios por nivel de dificultad y global (MRR = media de RR)."""
    by_level = metrics.groupby("difficulty_level")[METRICS].mean().reindex(LEVELS)
    overall = metrics[METRICS].mean().to_frame("all").T
    summary = pd.concat([by_level, overall]).rename(columns={"RR": "MRR"})
    summary.index.name = "difficulty_level"
    return summary.reset_index()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Valida y evalúa el benchmark de recuperación.")
    parser.add_argument("--field", choices=FIELDS, default="abstract")
    parser.add_argument("--ngram", choices=NGRAMS, default="unigram")
    parser.add_argument("--repr", dest="repr_", choices=REPRS, default="tfidf")
    parser.add_argument("--all", action="store_true", help="evaluar las 12 configuraciones")
    parser.add_argument("--check", action="store_true", help="solo validar queries.tsv y qrels.tsv")
    parser.add_argument("--force", action="store_true",
                        help=f"ejecutar aunque no exista el tag {FREEZE_TAG} (rompe el protocolo anti-sesgo)")
    args = parser.parse_args(argv)

    for path in (QUERIES_PATH, QRELS_PATH):
        if not path.exists():
            print(f"Error: no existe {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
    queries, qrels = load_queries(), load_qrels()
    corpus_ids = set(pd.read_csv(RAW_PATH, sep="\t", dtype=str, usecols=["arxiv_id"])["arxiv_id"])

    problems = validate_benchmark(queries, qrels, corpus_ids)
    if problems:
        print("El benchmark tiene problemas:", *problems, sep="\n  - ")
        return 1
    n_rel = pd.Series({q: len(r) for q, r in qrels.items()})
    print(f"Benchmark válido: {len(queries)} consultas, {n_rel.sum()} juicios "
          f"(min {n_rel.min()}, max {n_rel.max()} relevantes por consulta)")
    excess = too_many_relevant(qrels)
    if excess:
        detail = ", ".join(f"{q}: {n}" for q, n in excess.items())
        print(f"Aviso: el PDF pide {MIN_RELEVANT}-{MAX_RELEVANT} relevantes por consulta y estas "
              f"tienen más ({detail}). Recortar antes de congelar.", file=sys.stderr)
    if args.check:
        return 0

    if not is_frozen() and not args.force:
        print(f"\nNo existe el tag git '{FREEZE_TAG}'. Congelar el benchmark antes de ejecutar las consultas:\n"
              f"    git add data/benchmark/queries.tsv data/benchmark/qrels.tsv\n"
              f"    git commit -m \"Benchmark v1: 15 consultas y qrels\"\n"
              f"    git tag {FREEZE_TAG}\n"
              f"(o usar --force para saltarse esta comprobación)", file=sys.stderr)
        return 1

    RESULTS_DIR.mkdir(exist_ok=True)
    if args.all:
        rows = []
        for field, ngram, repr_ in product(FIELDS, NGRAMS, REPRS):
            _, metrics = run_benchmark(queries, qrels, field, ngram, repr_)
            # to_dict y no itertuples: itertuples renombra a _1, _2... las columnas
            # cuyo nombre no es un identificador válido (P@10, R@10, F1@10, nDCG@10)
            for row in summarize(metrics).to_dict("records"):
                rows.append({"field": field, "ngram": ngram, "repr": repr_, **row})
        table = pd.DataFrame(rows)
        out = RESULTS_DIR / "metrics_all_configs.tsv"
        table.to_csv(out, sep="\t", index=False, float_format="%.4f")
        overall = table[table["difficulty_level"] == "all"].drop(columns="difficulty_level")
        print(overall.sort_values("nDCG@10", ascending=False).to_string(index=False, float_format="%.4f"))
        print(f"\nGuardado: {out.relative_to(ROOT)}")
        return 0

    rankings, metrics = run_benchmark(queries, qrels, args.field, args.ngram, args.repr_)
    summary = summarize(metrics)
    rankings.to_csv(BENCH_DIR / "rankings.tsv", sep="\t", index=False)
    metrics.to_csv(RESULTS_DIR / "metrics_per_query.tsv", sep="\t", index=False, float_format="%.4f")
    summary.to_csv(RESULTS_DIR / "metrics_summary.tsv", sep="\t", index=False, float_format="%.4f")

    print(f"\nConfig: {args.field} · {args.ngram} · {args.repr_}\n")
    print(metrics.drop(columns="query").to_string(index=False, float_format="%.3f"))
    print()
    print(summary.to_string(index=False, float_format="%.4f"))
    print("\nGuardado: data/benchmark/rankings.tsv, results/metrics_per_query.tsv, results/metrics_summary.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())

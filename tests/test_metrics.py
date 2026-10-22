"""Pruebas de las métricas y del formato del benchmark.

Ejecutar desde la raíz:  python -m pytest tests/ -v

Ninguna prueba ejecuta las consultas reales del benchmark (protocolo anti-sesgo):
las pruebas de extremo a extremo usan consultas inventadas.
"""
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import evaluate as ev  # noqa: E402


# ---------------------------------------------------------------- métricas con ejemplos calculados a mano

RANKED = ["d1", "d2", "d3", "d4", "d5"]
RELS = {"d1": 2, "d3": 1, "d9": 1}  # d9 es relevante pero no se recuperó


def test_precision_recall_f1():
    p = ev.precision_at_k(RANKED, RELS, k=5)
    r = ev.recall_at_k(RANKED, RELS, k=5)
    assert p == pytest.approx(2 / 5)
    assert r == pytest.approx(2 / 3)
    assert ev.f1(p, r) == pytest.approx(0.5)


def test_precision_uses_k_as_denominator():
    # Con menos de k resultados, P@k sigue dividiendo entre k
    assert ev.precision_at_k(["d1"], RELS, k=10) == pytest.approx(0.1)


def test_reciprocal_rank():
    assert ev.reciprocal_rank(RANKED, RELS) == 1.0
    assert ev.reciprocal_rank(["x", "y", "d3"], RELS) == pytest.approx(1 / 3)
    assert ev.reciprocal_rank(["x", "y"], RELS) == 0.0


def test_ndcg():
    # Ganancia 2^rel - 1 (rel 2 -> 3, rel 1 -> 1):
    # DCG  = 3/log2(2) + 1/log2(4)                = 3.5
    # IDCG = 3/log2(2) + 1/log2(3) + 1/log2(4)    ≈ 4.1309
    expected = 3.5 / (3 + 1 / math.log2(3) + 0.5)
    assert ev.ndcg_at_k(RANKED, RELS, k=5) == pytest.approx(expected)
    assert ev.ndcg_at_k(["d1", "d3", "d9"], RELS) == pytest.approx(1.0)


# ---------------------------------------------------------------- ejemplo Q01 del PDF de la práctica

Q01_RELS = {"N003": 2, "N007": 1, "N012": 2, "N018": 1, "N024": 2, "N031": 1}
Q01_RANKED = ["N003", "N050", "N012", "N018", "N060", "N024", "N070", "N031", "N080", "N090"]


def test_pdf_example_q01():
    m = ev.query_metrics(Q01_RANKED, Q01_RELS)
    assert m["P@10"] == pytest.approx(0.50)
    assert m["R@10"] == pytest.approx(5 / 6)           # 0.833
    assert m["F1@10"] == pytest.approx(0.625)
    assert m["RR"] == pytest.approx(1.0)
    # DCG@10 = 6.314, IDCG@10 = 7.567 (el PDF los redondea) -> nDCG@10 = 0.835
    assert m["nDCG@10"] == pytest.approx(0.835, abs=1e-3)
    dcg = sum(ev.gain(Q01_RELS.get(d, 0)) / math.log2(i + 1) for i, d in enumerate(Q01_RANKED, start=1))
    assert dcg == pytest.approx(6.314, abs=1e-3)


def test_too_many_relevant():
    qrels = {"Q01": {f"d{i}": 1 for i in range(15)}, "Q02": {f"d{i}": 1 for i in range(16)}}
    assert ev.too_many_relevant(qrels) == {"Q02": 16}


def test_no_relevant_retrieved():
    m = ev.query_metrics(["x", "y", "z"], RELS)
    assert all(v == 0.0 for v in m.values())


def test_summary_mrr_is_mean_rr():
    metrics = pd.DataFrame({"difficulty_level": ["1", "1", "3"],
                            **{m: [1.0, 0.0, 0.5] for m in ev.METRICS}})
    s = ev.summarize(metrics).set_index("difficulty_level")
    assert s.loc["1", "MRR"] == pytest.approx(0.5)
    assert s.loc["all", "MRR"] == pytest.approx(0.5)
    assert math.isnan(s.loc["2", "MRR"])


def test_summary_rows_keep_metric_column_names():
    # Regresión: con itertuples, "P@10", "R@10", "F1@10" y "nDCG@10" se renombraban a _1, _2...
    # y --all fallaba con KeyError: 'nDCG@10'. La tabla de --all se arma con to_dict("records").
    metrics = pd.DataFrame({"difficulty_level": ["1", "2", "3"],
                            **{m: [1.0, 0.5, 0.0] for m in ev.METRICS}})
    rows = [{"field": "title", "ngram": "bigram", "repr": "tfidf", **r}
            for r in ev.summarize(metrics).to_dict("records")]
    table = pd.DataFrame(rows)
    overall = table[table["difficulty_level"] == "all"].drop(columns="difficulty_level")
    for col in ("P@10", "R@10", "F1@10", "MRR", "nDCG@10"):
        assert col in overall.columns
    overall.sort_values("nDCG@10", ascending=False)  # no debe lanzar KeyError


# ---------------------------------------------------------------- formato del benchmark real (no ejecuta consultas)

def test_benchmark_files_are_valid():
    queries, qrels = ev.load_queries(), ev.load_qrels()
    corpus_ids = set(pd.read_csv(ev.RAW_PATH, sep="\t", dtype=str, usecols=["arxiv_id"])["arxiv_id"])
    assert ev.validate_benchmark(queries, qrels, corpus_ids) == []


def test_validation_detects_problems():
    queries = pd.DataFrame({"query_id": ["Q01"], "difficulty_level": ["1"], "query": ["too short"]})
    qrels = {"Q01": {"no-existe": 3}, "Q99": {"a": 1}}
    problems = "\n".join(ev.validate_benchmark(queries, qrels, corpus_ids={"a"}))
    for fragment in ("1 consultas, se esperaban 15", "2 palabras", "Q99 no existe",
                     "solo 1 documentos", "fuera de {1, 2}", "no están en el corpus"):
        assert fragment in problems


def test_difficulty_levels_use_pdf_format():
    # El PDF pide difficulty_level numérico (1, 2, 3); "easy"/"medium"/"hard" ya no son válidos
    words = ["alpha beta gamma"] * 15
    ok = pd.DataFrame({"query_id": [f"Q{i:02d}" for i in range(1, 16)],
                       "difficulty_level": ["1"] * 5 + ["2"] * 5 + ["3"] * 5, "query": words})
    qrels = {q: {f"d{i}": 1 for i in range(10)} for q in ok["query_id"]}
    corpus = {f"d{i}" for i in range(10)}
    assert ev.validate_benchmark(ok, qrels, corpus) == []
    old = ok.assign(difficulty_level=["easy"] * 5 + ["medium"] * 5 + ["hard"] * 5)
    problems = "\n".join(ev.validate_benchmark(old, qrels, corpus))
    assert "niveles desconocidos" in problems


# ---------------------------------------------------------------- extremo a extremo con consultas inventadas

def test_run_benchmark_end_to_end():
    queries = pd.DataFrame({"query_id": ["T1", "T2"], "difficulty_level": ["1", "3"],
                            "query": ["image segmentation benchmark", "the of and"]})
    qrels = {"T1": {"2609.39681": 2}, "T2": {"2609.39681": 1}}
    rankings, metrics = ev.run_benchmark(queries, qrels)
    assert set(rankings.columns) == {"query_id", "rank", "document_id", "score"}
    assert (rankings.groupby("query_id").size() <= 10).all()
    # T2 queda vacía al normalizar (solo stopwords): sin ranking y métricas en 0
    assert "T2" not in set(rankings["query_id"])
    assert metrics.set_index("query_id").loc["T2", ev.METRICS].sum() == 0

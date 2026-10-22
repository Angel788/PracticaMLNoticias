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
    # DCG  = 2/log2(2) + 1/log2(4)                = 2.5
    # IDCG = 2/log2(2) + 1/log2(3) + 1/log2(4)    ≈ 3.1309
    expected = 2.5 / (2 + 1 / math.log2(3) + 0.5)
    assert ev.ndcg_at_k(RANKED, RELS, k=5) == pytest.approx(expected)
    assert ev.ndcg_at_k(["d1", "d3", "d9"], RELS) == pytest.approx(1.0)


def test_no_relevant_retrieved():
    m = ev.query_metrics(["x", "y", "z"], RELS)
    assert all(v == 0.0 for v in m.values())


def test_summary_mrr_is_mean_rr():
    metrics = pd.DataFrame({"difficulty_level": ["easy", "easy", "hard"],
                            **{m: [1.0, 0.0, 0.5] for m in ev.METRICS}})
    s = ev.summarize(metrics).set_index("difficulty_level")
    assert s.loc["easy", "MRR"] == pytest.approx(0.5)
    assert s.loc["all", "MRR"] == pytest.approx(0.5)
    assert math.isnan(s.loc["medium", "MRR"])


# ---------------------------------------------------------------- formato del benchmark real (no ejecuta consultas)

def test_benchmark_files_are_valid():
    queries, qrels = ev.load_queries(), ev.load_qrels()
    corpus_ids = set(pd.read_csv(ev.RAW_PATH, sep="\t", dtype=str, usecols=["arxiv_id"])["arxiv_id"])
    assert ev.validate_benchmark(queries, qrels, corpus_ids) == []


def test_validation_detects_problems():
    queries = pd.DataFrame({"query_id": ["Q01"], "difficulty_level": ["easy"], "query": ["too short"]})
    qrels = {"Q01": {"no-existe": 3}, "Q99": {"a": 1}}
    problems = "\n".join(ev.validate_benchmark(queries, qrels, corpus_ids={"a"}))
    for fragment in ("1 consultas, se esperaban 15", "2 palabras", "Q99 no existe",
                     "solo 1 documentos", "fuera de {1, 2}", "no están en el corpus"):
        assert fragment in problems


# ---------------------------------------------------------------- extremo a extremo con consultas inventadas

def test_run_benchmark_end_to_end():
    queries = pd.DataFrame({"query_id": ["T1", "T2"], "difficulty_level": ["easy", "hard"],
                            "query": ["image segmentation benchmark", "the of and"]})
    qrels = {"T1": {"2609.39681": 2}, "T2": {"2609.39681": 1}}
    rankings, metrics = ev.run_benchmark(queries, qrels)
    assert set(rankings.columns) == {"query_id", "rank", "document_id", "score"}
    assert (rankings.groupby("query_id").size() <= 10).all()
    # T2 queda vacía al normalizar (solo stopwords): sin ranking y métricas en 0
    assert "T2" not in set(rankings["query_id"])
    assert metrics.set_index("query_id").loc["T2", ev.METRICS].sum() == 0

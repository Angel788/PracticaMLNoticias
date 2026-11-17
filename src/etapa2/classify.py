"""Experimentos de clasificación supervisada (tarea A).

Cada experimento es un Pipeline completo:
    document_id -> NormalizedText -> vectorizador -> [TruncatedSVD] -> clasificador
Los hiperparámetros se buscan con GridSearchCV solo sobre train; dev solo evalúa.

Uso: python -m src.etapa2.classify C-1
"""
import sys
import time

import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from src.etapa2.config import CLASSES, RANDOM_STATE, RESULTS_DIR
from src.etapa2.labels import load_labeled
from src.etapa2.normalization import NormalizedText
from src.etapa2.tracking import load_experiments, log_experiment

RUNS_DIR = RESULTS_DIR / "runs"

MODELS = {
    "MultinomialNB": lambda: MultinomialNB(),
    "LogisticRegression": lambda: LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
    "SVC": lambda: SVC(kernel="linear", random_state=RANDOM_STATE),
}

MODEL_GRIDS = {
    "MultinomialNB": {"clf__alpha": [0.1, 0.5, 1.0]},
    "LogisticRegression": {"clf__C": [0.1, 1, 10]},
    "SVC": {"clf__C": [0.1, 1, 10]},
}

VECTORIZER_GRID = {"vec__min_df": [1, 2]}


def whitespace_tokenizer(text: str) -> list[str]:
    # El texto ya viene normalizado (N0/N1/N2): el vectorizador no debe volver a tokenizar
    return text.split()


def make_vectorizer(representation: str, ngram_range: tuple[int, int]):
    # lowercase=False y tokenizer propio: si no, el vectorizador pasaría todo a
    # minúsculas y quitaría la puntuación, y N0 quedaría igual que N1.
    common = dict(
        tokenizer=whitespace_tokenizer, token_pattern=None,
        lowercase=False, ngram_range=ngram_range,
    )
    if representation == "binary":
        return CountVectorizer(binary=True, **common)
    if representation == "frequency":
        return CountVectorizer(**common)
    if representation == "tfidf":
        return TfidfVectorizer(**common)
    raise ValueError(f"Representación desconocida: {representation}")


def build_pipeline(model, normalization="N2", representation="tfidf",
                   ngram_range=(1, 1), svd_components=None) -> Pipeline:
    if model == "MultinomialNB" and svd_components:
        raise ValueError("MultinomialNB no se combina con SVD (valores negativos)")
    steps = [
        ("norm", NormalizedText(normalization)),
        ("vec", make_vectorizer(representation, ngram_range)),
    ]
    if svd_components:
        steps.append(("svd", TruncatedSVD(n_components=svd_components, random_state=RANDOM_STATE)))
    steps.append(("clf", MODELS[model]()))
    return Pipeline(steps)


def get_split(df: pd.DataFrame, split: str):
    part = df[df["split"] == split]
    return part["document_id"].tolist(), part["label"].to_numpy()


def evaluate(y_true, y_pred) -> dict:
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": p, "macro_recall": r, "macro_f1": f1,
    }


def per_class_table(y_true, y_pred) -> pd.DataFrame:
    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, zero_division=0)
    return pd.DataFrame({
        "label": CLASSES, "precision": p, "recall": r, "f1": f1, "support": support,
    })


def confusion_table(y_true, y_pred) -> pd.DataFrame:
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    return pd.DataFrame(cm, index=pd.Index(CLASSES, name="gold"),
                        columns=pd.Index(CLASSES, name="predicted"))


def format_params(params: dict) -> str:
    return "; ".join(f"{k.split('__', 1)[1]}={v}" for k, v in sorted(params.items()))


def run_experiment(experiment_id, block, model, normalization="N2", representation="tfidf",
                   ngram_range=(1, 1), svd_components=None, df=None, notes="") -> dict:
    """Busca hiperparámetros en train (CV 5), evalúa el mejor en dev y lo registra."""
    df = load_labeled() if df is None else df
    X_train, y_train = get_split(df, "train")
    X_dev, y_dev = get_split(df, "dev")

    pipe = build_pipeline(model, normalization, representation, ngram_range, svd_components)
    grid = {**VECTORIZER_GRID, **MODEL_GRIDS[model]}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    search = GridSearchCV(pipe, grid, cv=cv, scoring="f1_macro", n_jobs=-1, refit=True)

    start = time.perf_counter()
    search.fit(X_train, y_train)
    seconds = time.perf_counter() - start

    y_pred = search.predict(X_dev)
    metrics = evaluate(y_dev, y_pred)
    cv_std = search.cv_results_["std_test_score"][search.best_index_]
    n_features = len(search.best_estimator_.named_steps["vec"].vocabulary_)

    # Archivos por experimento; la Fase 4 los consolida en los TSV de entrega
    run_dir = RUNS_DIR / experiment_id
    run_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"document_id": X_dev, "gold_label": y_dev, "predicted_label": y_pred,
                  "split": "dev", "model": model, "experiment_id": experiment_id}
                 ).to_csv(run_dir / "dev_predictions.tsv", sep="\t", index=False)
    per_class_table(y_dev, y_pred).to_csv(run_dir / "dev_per_class.tsv", sep="\t", index=False)
    confusion_table(y_dev, y_pred).to_csv(run_dir / "dev_confusion.tsv", sep="\t")

    log_experiment(
        experiment_id=experiment_id, task="classification", block=block,
        normalization=normalization, representation=representation,
        ngram_range=f"({ngram_range[0]},{ngram_range[1]})",
        svd_components=svd_components or "", method=model,
        hyperparameters=format_params(search.best_params_),
        cv_macro_f1=f"{search.best_score_:.4f}",
        dev_metric=f"macro_f1={metrics['macro_f1']:.4f}; accuracy={metrics['accuracy']:.4f}",
        extra=f"cv_std={cv_std:.4f}; n_features={n_features}; fit_seconds={seconds:.1f}",
        notes=notes,
    )
    return {
        "experiment_id": experiment_id, "block": block, "model": model,
        "normalization": normalization, "representation": representation,
        "ngram_range": ngram_range, "svd_components": svd_components,
        "best_params": format_params(search.best_params_),
        "cv_macro_f1": search.best_score_, "cv_std": cv_std,
        **{f"dev_{k}": v for k, v in metrics.items()},
        "n_features": n_features, "fit_seconds": seconds,
        "search": search, "y_dev": y_dev, "y_pred": y_pred,
        "report": classification_report(y_dev, y_pred, labels=CLASSES, digits=3, zero_division=0),
    }


def summary(results: list[dict]) -> pd.DataFrame:
    cols = ["experiment_id", "model", "normalization", "representation", "ngram_range",
            "svd_components", "best_params", "cv_macro_f1", "cv_std", "dev_accuracy",
            "dev_macro_f1", "n_features", "fit_seconds"]
    return pd.DataFrame([{c: r[c] for c in cols} for r in results]).set_index("experiment_id")


def cv_table(result: dict) -> pd.DataFrame:
    """Resultado de cada combinación de hiperparámetros en la CV de train."""
    cv = result["search"].cv_results_
    table = pd.DataFrame(cv["params"]).rename(columns=lambda c: c.split("__", 1)[1])
    table["cv_macro_f1"] = cv["mean_test_score"]
    table["cv_std"] = cv["std_test_score"]
    return table.sort_values("cv_macro_f1", ascending=False).reset_index(drop=True)


def run_block_c1(df=None) -> list[dict]:
    """C-1: los tres clasificadores con N2, TF-IDF y unigramas."""
    df = load_labeled() if df is None else df
    return [
        run_experiment(f"C{i:02d}", "C-1", model, df=df)
        for i, model in enumerate(MODELS, start=1)
    ]


def run_block_c2(df=None) -> list[dict]:
    """C-2: N0 y N1 con los tres clasificadores (TF-IDF, unigramas).

    N2 con TF-IDF (1,1) es exactamente C-1, así que no se duplica: se vuelve a
    correr con sus mismos IDs (C01-C03) para tener los nueve resultados juntos.
    El ajuste es determinista y la fila registrada queda igual.
    """
    df = load_labeled() if df is None else df
    results = []
    next_id = 4
    for normalization in ["N0", "N1"]:
        for model in MODELS:
            results.append(run_experiment(f"C{next_id:02d}", "C-2", model,
                                          normalization=normalization, df=df))
            next_id += 1
    results += run_block_c1(df)
    return results


# C-3 en adelante: la normalización se fija a la mejor de C-2 para cada modelo.
# La celda TF-IDF de C-3 es esa misma referencia, así que se reutiliza en vez de
# volver a entrenarla (y se conservan sus notas en experiments.tsv).
C3_NORMALIZATION = {
    "MultinomialNB": "N1",
    "LogisticRegression": "N2",
    "SVC": "N0",
}
C3_REFERENCE = {
    "MultinomialNB": "C07",
    "LogisticRegression": "C02",
    "SVC": "C06",
}
C3_IDS = [f"C{i:02d}" for i in range(10, 16)]   # C10-C15
C4_IDS = [f"C{i:02d}" for i in range(16, 22)]   # C16-C21
C5_IDS = [f"C{i:02d}" for i in range(22, 26)]   # C22-C25


def load_stored_result(experiment_id: str) -> dict:
    """Reconstruye el resumen de un experimento ya registrado.

    Sirve para reutilizar la celda de referencia de un bloque anterior sin
    reentrenar y sin borrar sus notas de experiments.tsv.
    """
    row = load_experiments().set_index("experiment_id").loc[experiment_id]
    dev = dict(part.split("=", 1) for part in row["dev_metric"].split("; "))
    extra = dict(part.split("=", 1) for part in row["extra"].split("; "))
    return {
        "experiment_id": experiment_id,
        "block": row["block"],
        "model": row["method"],
        "normalization": row["normalization"],
        "representation": row["representation"],
        "ngram_range": tuple(int(x) for x in row["ngram_range"].strip("()").split(",")),
        "svd_components": int(row["svd_components"]) if row["svd_components"] else None,
        "best_params": row["hyperparameters"],
        "cv_macro_f1": float(row["cv_macro_f1"]),
        "cv_std": float(extra["cv_std"]),
        "dev_macro_f1": float(dev["macro_f1"]),
        "dev_accuracy": float(dev["accuracy"]),
        "n_features": int(extra["n_features"]),
        "fit_seconds": float(extra["fit_seconds"]),
    }


def load_results(experiment_ids: list[str]) -> list[dict]:
    return [load_stored_result(i) for i in experiment_ids]


def run_block_c3(df=None) -> list[dict]:
    """C-3: binaria, frecuencia y TF-IDF con la mejor normalización de C-2.

    La celda TF-IDF ya está medida en C-2 (C07, C02, C06), así que solo se
    corren las representaciones nuevas: 6 experimentos (C10-C15).
    """
    df = load_labeled() if df is None else df
    results = []
    next_id = 10
    for model in MODELS:
        normalization = C3_NORMALIZATION[model]
        for representation in ["binary", "frequency"]:
            results.append(run_experiment(
                f"C{next_id:02d}", "C-3", model,
                normalization=normalization,
                representation=representation,
                df=df,
                notes=f"C-3: {representation} con {normalization}; TF-IDF es {C3_REFERENCE[model]}",
            ))
            next_id += 1
    return results


def run_block_c4(df=None, best_c3=None) -> list[dict]:
    """C-4: n-gramas (1,2) y (1,3) sobre la mejor representación de C-3.

    La celda (1,1) ya está en C-3, así que no se repite: 6 experimentos
    nuevos (C16-C21).
    """
    df = load_labeled() if df is None else df
    if best_c3 is None:
        raise ValueError("best_c3 es obligatorio: mejor resultado de C-3 por modelo")
    results = []
    next_id = 16
    for model in MODELS:
        ref = best_c3[model]
        for ngram_range in [(1, 2), (1, 3)]:
            results.append(run_experiment(
                f"C{next_id:02d}", "C-4", model,
                normalization=ref["normalization"],
                representation=ref["representation"],
                ngram_range=ngram_range,
                df=df,
                notes=f"C-4: n-gramas {ngram_range} sobre {ref['representation']} ({ref['experiment_id']})",
            ))
            next_id += 1
    return results


def run_block_c5(df=None, best_c4=None) -> list[dict]:
    """C-5: SVD de 100 y 200 componentes para LR y SVC.

    MultinomialNB no se prueba porque SVD produce valores negativos. Se parte
    de la mejor configuración de C-4: 4 experimentos nuevos (C22-C25).
    """
    df = load_labeled() if df is None else df
    if best_c4 is None:
        raise ValueError("best_c4 es obligatorio: mejor resultado de C-4 por modelo")
    results = []
    next_id = 22
    for model in ["LogisticRegression", "SVC"]:
        ref = best_c4[model]
        for n_components in [100, 200]:
            results.append(run_experiment(
                f"C{next_id:02d}", "C-5", model,
                normalization=ref["normalization"],
                representation=ref["representation"],
                ngram_range=ref["ngram_range"],
                svd_components=n_components,
                df=df,
                notes=f"C-5: SVD {n_components} sobre {ref['experiment_id']}",
            ))
            next_id += 1
    return results


def run_from_registry(block: str) -> list[dict]:
    """Ejecuta C-4 o C-5 leyendo del registro el mejor resultado del bloque anterior."""
    df = load_labeled()
    c3_results = load_results(C3_IDS + [C3_REFERENCE[m] for m in MODELS])
    best_c3 = best_per_model(c3_results)
    if block == "C-4":
        return run_block_c4(df, best_c3)
    if block == "C-5":
        c4_results = load_results(C4_IDS + [best_c3[m]["experiment_id"] for m in MODELS])
        return run_block_c5(df, best_per_model(c4_results))
    raise ValueError(f"Bloque no soportado desde el registro: {block}")


def best_per_model(results: list[dict]) -> dict[str, dict]:
    """Mejor resultado de cada modelo por macro-F1 en dev; empate -> mayor CV."""
    best = {}
    for r in results:
        current = best.get(r["model"])
        key = (r["dev_macro_f1"], r["cv_macro_f1"])
        if current is None or key > (current["dev_macro_f1"], current["cv_macro_f1"]):
            best[r["model"]] = r
    return best


BLOCKS = {"C-1": run_block_c1, "C-2": run_block_c2, "C-3": run_block_c3}


if __name__ == "__main__":
    block = sys.argv[1] if len(sys.argv) > 1 else "C-1"
    results = run_from_registry(block) if block in ("C-4", "C-5") else BLOCKS[block]()
    with pd.option_context("display.width", 200):
        print(summary(results).round(4))

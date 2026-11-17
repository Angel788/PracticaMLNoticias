"""Fase 3 y 4: selección final, evaluación única en test y entregables.

Selección: mejor macro-F1 en dev por clasificador. Si la diferencia con el
siguiente es menor que 1 punto (0.01 en la escala 0-1, menos de un documento:
en dev 1 documento ≈ 1.3 puntos), se considera empate y se desempata por el
macro-F1 de la validación cruzada y por la configuración más simple (sin SVD,
n-gramas más cortos).

Después se reajusta SOLO el ganador global con train+dev y se evalúa una vez en
test. Genera:

    classification_predictions.tsv
    classification_metrics.tsv
    classification_per_class.tsv
    confusion_matrices/*.tsv y *.png
    figures/classification_*.png
    error_analysis.md

Uso: python -m src.etapa2.final
"""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, confusion_matrix, precision_recall_fscore_support,
)

from src.etapa2.classify import build_pipeline, load_stored_result
from src.etapa2.config import CLASSES, FIGURES_DIR, RAW_CORPUS_PATH, RESULTS_DIR
from src.etapa2.labels import load_labeled
from src.etapa2.tracking import load_experiments, mark_selected

RUNS_DIR = RESULTS_DIR / "runs"
CONFUSION_DIR = RESULTS_DIR / "confusion_matrices"
TIE_THRESHOLD = 0.01
MODEL_ORDER = ["MultinomialNB", "LogisticRegression", "SVC"]

PAIR_CAUSE = {
    ("cs.CL", "cs.LG"): "frontera difusa LLM/ML: comparten transformer, training, model, language",
    ("cs.LG", "cs.CL"): "frontera difusa ML/LLM: el abstract usa vocabulario de lenguaje",
    ("cs.CV", "cs.CL"): "visión-lenguaje/multimodal: menciona modelos de lenguaje e imágenes",
    ("cs.CL", "cs.CV"): "el abstract usa vocabulario visual o multimodal",
    ("cs.CL", "cs.IR"): "RAG/recuperación: el artículo de NLP usa documentos y ranking",
    ("cs.IR", "cs.CL"): "el artículo de IR usa un LLM como componente principal",
    ("cs.CV", "cs.LG"): "método de aprendizaje general aplicado a visión",
    ("cs.LG", "cs.CV"): "experimento de ML con datos visuales",
    ("cs.IR", "cs.LG"): "recommendation/ranking con métodos de ML",
    ("cs.LG", "cs.IR"): "ML aplicado a búsqueda o recommendation",
}

# Casos revisados a mano: la explicación automática por par no siempre describe
# el documento. Se prioriza esta lectura sobre la plantilla del par.
MANUAL_CAUSES = {
    "2609.39460": ("error de generalización: el abstract es de lingüística computacional, "
                   "pero acumula vocabulario de evaluación de clasificadores (dataset, "
                   "ROC-AUC, classifiers) y pocos términos de NLP; cs.CV no comparte tema"),
    "2610.02251": ("el artículo es de muestreo especulativo (ML), pero evalúa generación en "
                   "pixel-space, FFHQ, CIFAR-10 y difusión latente: el vocabulario visual pesa"),
    "2609.40222": ("world models de vídeo: mezcla atención, memoria y transformers (LG) con "
                   "escenas, cámara y vídeo (CV)"),
    "2610.02249": ("usa retrieval de vecinos cercanos como método; el vocabulario de búsqueda "
                   "y benchmarking pesa aunque la tarea sea predicción molecular"),
}


def classification_results() -> list[dict]:
    exp = load_experiments()
    rows = exp[exp["task"] == "classification"]
    return [load_stored_result(eid) for eid in rows["experiment_id"]]


def select_best_per_model(results: list[dict]) -> dict[str, dict]:
    by_model: dict[str, list[dict]] = {}
    for result in results:
        by_model.setdefault(result["model"], []).append(result)

    best = {}
    for model, candidates in by_model.items():
        top = max(c["dev_macro_f1"] for c in candidates)
        tied = [c for c in candidates if top - c["dev_macro_f1"] <= TIE_THRESHOLD]
        tied.sort(key=lambda c: (
            -c["cv_macro_f1"],
            c["svd_components"] is not None,
            c["ngram_range"],
            c["experiment_id"],
        ))
        best[model] = tied[0]
    return best


def select_global(best: dict[str, dict]) -> dict:
    return max(best.values(), key=lambda r: (r["dev_macro_f1"], r["cv_macro_f1"]))


def parse_hyperparameters(text: str) -> dict:
    params = {}
    for part in text.split("; "):
        key, value = part.split("=", 1)
        param = {"alpha": "clf__alpha", "C": "clf__C", "min_df": "vec__min_df"}[key]
        params[param] = int(value) if key == "min_df" else float(value)
    return params


def refit_on_train_dev(result: dict, df: pd.DataFrame):
    pipe = build_pipeline(
        result["model"], result["normalization"], result["representation"],
        result["ngram_range"], result["svd_components"],
    )
    pipe.set_params(**parse_hyperparameters(result["best_params"]))
    train_dev = df[df["split"].isin(["train", "dev"])]
    test = df[df["split"] == "test"]
    pipe.fit(train_dev["document_id"], train_dev["label"])
    return pipe, test, pipe.predict(test["document_id"])


def metric_row(experiment_id, model, split, y_true, y_pred) -> dict:
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0)
    return {
        "experiment_id": experiment_id, "model": model, "split": split,
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": p, "macro_recall": r, "macro_f1": f1,
    }


def per_class_rows(experiment_id, model, split, y_true, y_pred) -> list[dict]:
    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, zero_division=0)
    return [{
        "experiment_id": experiment_id, "model": model, "split": split,
        "label": label, "precision": p[i], "recall": r[i], "f1": f1[i],
        "support": int(support[i]),
    } for i, label in enumerate(CLASSES)]


def confusion_df(y_true, y_pred) -> pd.DataFrame:
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    return pd.DataFrame(
        cm, index=pd.Index(CLASSES, name="gold"),
        columns=pd.Index(CLASSES, name="predicted"),
    )


def plot_confusion(cm: pd.DataFrame, title: str, path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    im = ax.imshow(cm.values, cmap="Blues", vmin=0)
    ax.set_xticks(range(len(CLASSES)), CLASSES, rotation=30, ha="right")
    ax.set_yticks(range(len(CLASSES)), CLASSES)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Clase real")
    ax.set_title(title, loc="left", fontsize=10)
    peak = cm.values.max()
    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            value = cm.values[i, j]
            ax.text(j, i, str(value), ha="center", va="center", fontsize=10,
                    color="white" if value > peak / 2 else "#222222")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_best_models(best: dict[str, dict], path) -> None:
    dev = [best[m]["dev_macro_f1"] for m in MODEL_ORDER]
    cv = [best[m]["cv_macro_f1"] for m in MODEL_ORDER]
    labels = [f"{best[m]['experiment_id']}\n{m}" for m in MODEL_ORDER]
    x = np.arange(len(MODEL_ORDER))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.5, 4))
    b1 = ax.bar(x - width / 2, cv, width, label="CV en train", color="#2a78d6")
    b2 = ax.bar(x + width / 2, dev, width, label="dev", color="#eb6834")
    ax.bar_label(b1, fmt="%.3f", padding=2, fontsize=8)
    ax.bar_label(b2, fmt="%.3f", padding=2, fontsize=8)
    ax.set_xticks(x, labels)
    ax.set_ylim(0.65, 0.85)
    ax.set_ylabel("macro-F1")
    ax.set_title("Mejor configuración de cada clasificador (dev)", loc="left", fontsize=11)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e4e0", lw=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_block_progress(results: list[dict], path) -> None:
    df = pd.DataFrame(results)
    blocks = ["C-1", "C-2", "C-3", "C-4", "C-5"]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for model in MODEL_ORDER:
        values = []
        for i, _ in enumerate(blocks):
            sub = df[(df["model"] == model) & (df["block"].isin(blocks[:i + 1]))]
            values.append(sub["dev_macro_f1"].max() if len(sub) else np.nan)
        ax.plot(blocks, values, marker="o", label=model)
        ax.annotate(f"{values[-1]:.3f}", (blocks[-1], values[-1]),
                    textcoords="offset points", xytext=(6, 0), fontsize=8)
    ax.set_ylim(0.68, 0.82)
    ax.set_ylabel("macro-F1 en dev")
    ax.set_title("Mejor macro-F1 en dev acumulado por bloque", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e4e0", lw=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def explain_error(row: pd.Series) -> str:
    if row["document_id"] in MANUAL_CAUSES:
        return MANUAL_CAUSES[row["document_id"]]
    categories = str(row["categories"]).split()
    secondary = categories[1:]
    if row["predicted_label"] in secondary:
        return f"cross-listing: el artículo también está listado en {row['predicted_label']}"
    return PAIR_CAUSE.get(
        (row["gold_label"], row["predicted_label"]),
        "abstract genérico o vocabulario poco frecuente para la clase real",
    )


def pick_diverse(errors: pd.DataFrame, n: int = 10) -> list[pd.Series]:
    groups = [g for _, g in errors.groupby(["gold_label", "predicted_label"], sort=True)]
    picked: list[pd.Series] = []
    i = 0
    while len(picked) < n:
        added = False
        for group in groups:
            if len(group) > i:
                picked.append(group.iloc[i])
                added = True
                if len(picked) == n:
                    break
        if not added:
            break
        i += 1
    return picked


def write_error_analysis(dev_pred: pd.DataFrame, path, experiment_id: str,
                         model: str) -> None:
    raw = pd.read_csv(RAW_CORPUS_PATH, sep="\t", dtype=str, keep_default_na=False)
    errors = dev_pred[dev_pred["gold_label"] != dev_pred["predicted_label"]].copy()
    errors = errors.merge(
        raw[["arxiv_id", "title", "abstract", "categories"]],
        left_on="document_id", right_on="arxiv_id", how="left",
    )
    errors["cause"] = errors.apply(explain_error, axis=1)
    cross = errors.apply(
        lambda r: r["predicted_label"] in str(r["categories"]).split()[1:], axis=1)
    picked = pick_diverse(errors, 10)

    lines = [
        f"# Análisis de errores en dev · {experiment_id} ({model})\n",
        "Predicciones de dev del modelo ajustado **solo con train**, antes del "
        "reajuste en train+dev. El test no participa en este análisis.\n",
        f"- Documentos de dev: **{len(dev_pred)}**",
        f"- Errores: **{len(errors)}** ({len(errors) / len(dev_pred):.1%})",
        f"- Errores cuyo gold/pred aparecen en el cross-listing del artículo: "
        f"**{int(cross.sum())} de {len(errors)}** ({cross.mean():.1%})\n",
        "## Pares de confusión\n",
        "| Gold | Predicho | Documentos |",
        "|---|---|---:|",
    ]
    pairs = errors.groupby(["gold_label", "predicted_label"]).size().sort_values(ascending=False)
    for (gold, pred), count in pairs.items():
        lines.append(f"| {gold} | {pred} | {count} |")

    lines += [
        "\n## Los 10 documentos revisados\n",
        "| # | document_id | Gold | Predicho | Título | Categorías secundarias | Causa probable |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(picked, start=1):
        title = str(row["title"]).replace("|", "/")[:90]
        secondary = " ".join(str(row["categories"]).split()[1:]).replace("|", "/")
        lines.append(
            f"| {i} | {row['document_id']} | {row['gold_label']} | "
            f"{row['predicted_label']} | {title} | {secondary or '—'} | {row['cause']} |"
        )

    lines += ["\n## Detalle por documento\n"]
    for i, row in enumerate(picked, start=1):
        abstract = " ".join(str(row["abstract"]).split())[:420]
        lines += [
            f"### {i}. `{row['document_id']}` · {row['gold_label']} → {row['predicted_label']}\n",
            f"**Título:** {row['title']}\n",
            f"**Categorías:** {row['categories']}\n",
            f"**Abstract (inicio):** {abstract}…\n",
            f"**Causa probable:** {row['cause']}.\n",
        ]

    lines += [
        "\n## Lectura\n",
        "- Solo **3 de 15** errores (20%) tienen la clase predicha dentro del "
        "cross-listing del artículo; la mayor parte se explica por solapamiento "
        "de vocabulario, no por la etiqueta secundaria.",
        "- Los pares más frecuentes son `cs.CL → cs.IR` (3), `cs.CV → cs.CL` (3) "
        "y la frontera `cs.CL ↔ cs.LG` (4 en total).",
        "- Varios documentos están listados en la categoría que el modelo predice; "
        "la etiqueta primaria es una convención de arXiv, no una frontera semántica.",
        "- El modelo se apoya en el vocabulario temático del abstract. Cuando un "
        "artículo de NLP usa recuperación o un artículo de IR usa un LLM, los "
        "términos de ambas áreas aparecen juntos y la decisión es ambigua.",
        "- Estos errores son esperables con un corpus de 500 documentos y 4 clases; "
        "el objetivo es documentarlos, no eliminarlos con test.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = load_labeled()
    results = classification_results()
    best = select_best_per_model(results)
    winner = select_global(best)

    for model in MODEL_ORDER:
        result = best[model]
        mark_selected(
            result["experiment_id"],
            notes=(f"Mejor {model} por macro-F1 en dev "
                   f"({result['dev_macro_f1']:.4f}); se reporta en dev"),
        )
    mark_selected(
        winner["experiment_id"],
        notes=("Ganador global por macro-F1 en dev; se reajusta en train+dev "
               "y se evalúa una vez en test"),
    )

    dev_frames = []
    for model in MODEL_ORDER:
        eid = best[model]["experiment_id"]
        dev_frames.append(pd.read_csv(
            RUNS_DIR / eid / "dev_predictions.tsv", sep="\t", dtype=str,
            keep_default_na=False,
        ))
    dev_pred = pd.concat(dev_frames, ignore_index=True)

    _, test, test_pred = refit_on_train_dev(winner, df)
    test_frame = pd.DataFrame({
        "document_id": test["document_id"].values,
        "gold_label": test["label"].values,
        "predicted_label": test_pred,
        "split": "test",
        "model": winner["model"],
        "experiment_id": "test",
    })
    predictions = pd.concat([dev_pred, test_frame], ignore_index=True)
    predictions.to_csv(RESULTS_DIR / "classification_predictions.tsv",
                       sep="\t", index=False)

    metrics, per_class = [], []
    for model in MODEL_ORDER:
        eid = best[model]["experiment_id"]
        part = dev_pred[dev_pred["experiment_id"] == eid]
        metrics.append(metric_row(eid, model, "dev",
                                  part["gold_label"], part["predicted_label"]))
        per_class += per_class_rows(eid, model, "dev",
                                    part["gold_label"], part["predicted_label"])
    metrics.append(metric_row("test", winner["model"], "test",
                              test["label"], test_pred))
    per_class += per_class_rows("test", winner["model"], "test",
                                test["label"], test_pred)
    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(RESULTS_DIR / "classification_metrics.tsv",
                      sep="\t", index=False)
    pd.DataFrame(per_class).to_csv(RESULTS_DIR / "classification_per_class.tsv",
                                   sep="\t", index=False)

    CONFUSION_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODEL_ORDER:
        eid = best[model]["experiment_id"]
        part = dev_pred[dev_pred["experiment_id"] == eid]
        cm = confusion_df(part["gold_label"], part["predicted_label"])
        cm.to_csv(CONFUSION_DIR / f"{eid}_dev.tsv", sep="\t")
        plot_confusion(cm, f"{eid} · {model} · dev",
                       CONFUSION_DIR / f"{eid}_dev.png")
    cm_test = confusion_df(test["label"], test_pred)
    cm_test.to_csv(CONFUSION_DIR / "test.tsv", sep="\t")
    plot_confusion(cm_test, f"Ganador global · {winner['model']} · test",
                   CONFUSION_DIR / "test.png")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_best_models(best, FIGURES_DIR / "classification_best_dev.png")
    plot_block_progress(results, FIGURES_DIR / "classification_blocks_dev.png")
    write_error_analysis(
        dev_pred[dev_pred["experiment_id"] == winner["experiment_id"]],
        RESULTS_DIR / "error_analysis.md", winner["experiment_id"], winner["model"],
    )

    print("Mejor por modelo (dev):")
    for model in MODEL_ORDER:
        r = best[model]
        print(f"  {model:<20} {r['experiment_id']}  dev={r['dev_macro_f1']:.4f}  "
              f"CV={r['cv_macro_f1']:.4f}  {r['normalization']} · "
              f"{r['representation']} {r['ngram_range']} · SVD={r['svd_components']}")
    print(f"\nGanador global: {winner['experiment_id']} ({winner['model']})")
    print(metrics_df.to_string(index=False))
    print(f"\nEscrito en {RESULTS_DIR}")


if __name__ == "__main__":
    main()

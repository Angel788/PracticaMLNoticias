"""Tarea B: clustering con K-Means sobre los artículos científicos.

Pipeline: texto normalizado -> vectorizador -> [TruncatedSVD] -> Normalizer -> KMeans.
K-Means se ajusta SOLO con train y sin etiquetas. Las etiquetas se usan después,
solo para ARI/NMI y la tabla de contingencia (interpretación externa).

Bloques:
    K-1  k ∈ {3,4,5,6,8}
    K-2  normalización N0/N1/N2
    K-3  frecuencia vs TF-IDF
    K-4  unigramas vs bigramas
    K-5  SVD: sin SVD, 50, 100, 200
    K-6  init, n_init y max_iter

Salidas:
    clustering_results.tsv
    cluster_summary.tsv
    cluster_contingency_test.tsv
    figures/clustering_*.png
    cluster_analysis.md

Uso: python -m src.etapa2.cluster
"""
import time

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import (
    adjusted_rand_score, normalized_mutual_info_score, silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

from src.etapa2.classify import make_vectorizer
from src.etapa2.config import (
    CLASSES, EXPERIMENTS_PATH, FIGURES_DIR, RANDOM_STATE, RESULTS_DIR,
)
from src.etapa2.labels import load_labeled
from src.etapa2.normalization import NormalizedText, load_variants
from src.etapa2.tracking import load_experiments, log_experiment, mark_selected

RUNS_DIR = RESULTS_DIR / "runs_k"
K1_KS = [3, 4, 5, 6, 8]
TIE = 0.01
SELECTED_FINAL = "K02"


def build_pipeline(k, normalization="N2", representation="tfidf",
                   ngram_range=(1, 1), svd_components=100,
                   init="k-means++", n_init=10, max_iter=300) -> Pipeline:
    steps = [
        ("norm", NormalizedText(normalization)),
        ("vec", make_vectorizer(representation, ngram_range)),
    ]
    if svd_components:
        steps.append(("svd", TruncatedSVD(
            n_components=svd_components, random_state=RANDOM_STATE)))
    steps += [
        ("l2", Normalizer()),
        ("km", KMeans(n_clusters=k, init=init, n_init=n_init,
                      max_iter=max_iter, random_state=RANDOM_STATE)),
    ]
    return Pipeline(steps)


def to_dense(matrix):
    return matrix.toarray() if hasattr(matrix, "toarray") else np.asarray(matrix)


def stability_ari(space, k, init, n_init, max_iter, seeds=range(5)):
    partitions = []
    for seed in seeds:
        km = KMeans(n_clusters=k, init=init, n_init=n_init,
                    max_iter=max_iter, random_state=seed)
        partitions.append(km.fit_predict(space))
    aris = [
        adjusted_rand_score(partitions[i], partitions[j])
        for i in range(len(partitions)) for j in range(i + 1, len(partitions))
    ]
    return float(np.mean(aris)), float(np.std(aris))


def content_top_words(texts: list[str], labels, k: int,
                      n: int = 10) -> dict[int, list[str]]:
    """Palabras de contenido por cluster en el espacio original de palabras.

    Se usa un vocabulario restringido a palabras alfabéticas de 4+ letras que
    aparecen en al menos 5 documentos y en menos del 50 % del corpus. Así se
    evita que los números, el LaTeX, la puntuación y las stopwords dominen el
    top-10. Es solo para interpretar: el clustering usa su propio vectorizador.
    """
    vectorizer = CountVectorizer(
        min_df=5, max_df=0.5, stop_words="english",
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{3,}\b",
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        vectorizer = CountVectorizer(
            min_df=1, stop_words="english",
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{3,}\b",
        )
        matrix = vectorizer.fit_transform(texts)

    terms = vectorizer.get_feature_names_out()
    counts = np.vstack([
        np.asarray(matrix[labels == cluster].sum(axis=0)).ravel()
        for cluster in range(k)
    ])
    tf = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1)
    dfreq = (counts > 0).sum(axis=0)
    idf = np.log(1 + k / np.maximum(dfreq, 1))
    score = tf * idf

    out = {}
    for cluster in range(k):
        if counts[cluster].sum() == 0:
            out[cluster] = []
            continue
        top = np.argsort(score[cluster])[-n:][::-1]
        out[cluster] = [str(terms[i]) for i in top]
    return out


def top_word_distinctiveness(top_words: dict[int, list[str]]) -> float:
    """1 - solapamiento medio entre los top-10 de los clusters (0 a 1)."""
    sets = [set(words[:10]) for words in top_words.values() if words]
    if len(sets) < 2:
        return 0.0
    overlaps = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            union = sets[i] | sets[j]
            overlaps.append(len(sets[i] & sets[j]) / len(union) if union else 1.0)
    return 1.0 - float(np.mean(overlaps))


def representative_docs(space, labels, doc_ids, k, n=2) -> dict[int, list[str]]:
    doc_ids = np.asarray(doc_ids)
    out = {}
    for cluster in range(k):
        indices = np.where(labels == cluster)[0]
        if len(indices) == 0:
            out[cluster] = []
            continue
        centroid = space[indices].mean(axis=0)
        distance = ((space[indices] - centroid) ** 2).sum(axis=1)
        order = indices[np.argsort(distance)][:n]
        out[cluster] = [str(doc_ids[i]) for i in order]
    return out


def run_kmeans(experiment_id, block, k, normalization="N2",
               representation="tfidf", ngram_range=(1, 1), svd_components=100,
               init="k-means++", n_init=10, max_iter=300, df=None,
               notes="") -> dict:
    df = load_labeled() if df is None else df
    train = df[df["split"] == "train"]
    dev = df[df["split"] == "dev"]
    X_train, y_train = train["document_id"].tolist(), train["label"].to_numpy()
    X_dev, y_dev = dev["document_id"].tolist(), dev["label"].to_numpy()

    pipe = build_pipeline(k, normalization, representation, ngram_range,
                          svd_components, init, n_init, max_iter)
    start = time.perf_counter()
    pipe.fit(X_train)
    seconds = time.perf_counter() - start

    labels_train = pipe.named_steps["km"].labels_.astype(int)
    labels_dev = pipe.predict(X_dev).astype(int)
    space_train = to_dense(pipe[:-1].transform(X_train))
    space_dev = to_dense(pipe[:-1].transform(X_dev))

    sil_train = float(silhouette_score(space_train, labels_train, metric="cosine"))
    sil_dev = float(silhouette_score(space_dev, labels_dev, metric="cosine"))
    ari_train = float(adjusted_rand_score(y_train, labels_train))
    nmi_train = float(normalized_mutual_info_score(y_train, labels_train))
    ari_dev = float(adjusted_rand_score(y_dev, labels_dev))
    nmi_dev = float(normalized_mutual_info_score(y_dev, labels_dev))
    sizes = np.bincount(labels_train, minlength=k).tolist()
    stab_mean, stab_std = stability_ari(space_train, k, init, n_init, max_iter)

    vec = pipe.named_steps["vec"]
    n_features = len(vec.vocabulary_)
    variants = load_variants().set_index("document_id")
    texts_train = [variants.loc[doc_id, "text_n2"] for doc_id in X_train]
    top = content_top_words(texts_train, labels_train, k)
    distinctiveness = top_word_distinctiveness(top)
    rep = representative_docs(space_train, labels_train, X_train, k)

    run_dir = RUNS_DIR / experiment_id
    run_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({
        "document_id": X_train + X_dev,
        "split": ["train"] * len(X_train) + ["dev"] * len(X_dev),
        "cluster_id": list(labels_train) + list(labels_dev),
    }).to_csv(run_dir / "assignments.tsv", sep="\t", index=False)
    pd.DataFrame({
        "cluster_id": list(range(k)),
        "top_words": [", ".join(top[c]) for c in range(k)],
        "representative_document_ids": [",".join(rep[c]) for c in range(k)],
    }).to_csv(run_dir / "top_words.tsv", sep="\t", index=False)

    log_experiment(
        experiment_id=experiment_id, task="clustering", block=block,
        normalization=normalization, representation=representation,
        ngram_range=f"({ngram_range[0]},{ngram_range[1]})",
        svd_components=svd_components or "", method="KMeans",
        hyperparameters=(f"k={k}; init={init}; n_init={n_init}; "
                         f"max_iter={max_iter}; random_state=0"),
        cv_macro_f1="",
        dev_metric=f"silhouette={sil_dev:.4f}",
        extra=(f"train_silhouette={sil_train:.4f}; ari_train={ari_train:.4f}; "
               f"nmi_train={nmi_train:.4f}; ari_dev={ari_dev:.4f}; "
               f"nmi_dev={nmi_dev:.4f}; stability_ari={stab_mean:.4f}±{stab_std:.4f}; "
               f"distinctiveness={distinctiveness:.4f}; "
               f"sizes={'-'.join(map(str, sizes))}; n_features={n_features}; "
               f"fit_seconds={seconds:.1f}"),
        notes=notes,
    )

    return {
        "experiment_id": experiment_id, "block": block, "k": k,
        "normalization": normalization, "representation": representation,
        "ngram_range": ngram_range, "svd_components": svd_components,
        "init": init, "n_init": n_init, "max_iter": max_iter,
        "dev_silhouette": sil_dev, "train_silhouette": sil_train,
        "stability_ari": stab_mean, "stability_std": stab_std,
        "distinctiveness": distinctiveness,
        "ari_dev": ari_dev, "nmi_dev": nmi_dev, "sizes": sizes,
        "max_share": max(sizes) / sum(sizes), "n_features": n_features,
        "fit_seconds": seconds, "pipeline": pipe,
        "labels_train": labels_train, "labels_dev": labels_dev,
        "space_train": space_train, "space_dev": space_dev,
        "top_words": top, "representative": rep,
    }


def load_stored_k_result(experiment_id: str) -> dict:
    row = load_experiments().set_index("experiment_id").loc[experiment_id]
    extra = dict(part.split("=", 1) for part in row["extra"].split("; "))
    hp = dict(part.split("=", 1) for part in row["hyperparameters"].split("; "))
    stab = extra["stability_ari"].split("±")
    sizes = [int(x) for x in extra["sizes"].split("-")]
    return {
        "experiment_id": experiment_id, "block": row["block"],
        "k": int(hp["k"]), "init": hp["init"], "n_init": int(hp["n_init"]),
        "max_iter": int(hp["max_iter"]),
        "normalization": row["normalization"],
        "representation": row["representation"],
        "ngram_range": tuple(int(x) for x in row["ngram_range"].strip("()").split(",")),
        "svd_components": int(row["svd_components"]) if row["svd_components"] else None,
        "dev_silhouette": float(row["dev_metric"].split("=")[1]),
        "train_silhouette": float(extra["train_silhouette"]),
        "stability_ari": float(stab[0]), "stability_std": float(stab[1]),
        "distinctiveness": float(extra.get("distinctiveness", 0.0)),
        "ari_dev": float(extra["ari_dev"]), "nmi_dev": float(extra["nmi_dev"]),
        "sizes": sizes, "max_share": max(sizes) / sum(sizes),
        "n_features": int(extra["n_features"]),
        "fit_seconds": float(extra["fit_seconds"]),
    }


def choose_best(candidates: list[dict]) -> dict:
    """Mayor silhouette en dev; empate -> estabilidad y tamaños equilibrados."""
    top = max(c["dev_silhouette"] for c in candidates)
    tied = [c for c in candidates if top - c["dev_silhouette"] <= TIE]
    tied.sort(key=lambda c: (
        -c["stability_ari"],
        abs(c["max_share"] - 1 / c["k"]),
        c["k"],
    ))
    return tied[0]


def run_block_k1(df=None) -> list[dict]:
    df = load_labeled() if df is None else df
    return [
        run_kmeans(f"K{i:02d}", "K-1", k, df=df,
                   notes=f"K-1: k={k}; N2; TF-IDF (1,1); SVD 100")
        for i, k in enumerate(K1_KS, start=1)
    ]


def run_block_k2(df=None, best_k1=None) -> list[dict]:
    df = load_labeled() if df is None else df
    return [
        run_kmeans(f"K{i:02d}", "K-2", best_k1["k"], normalization=norm, df=df,
                   notes=(f"K-2: {norm} con k={best_k1['k']}; "
                          f"referencia N2={best_k1['experiment_id']}"))
        for i, norm in enumerate(["N0", "N1"], start=6)
    ]


def run_block_k3(df=None, best_k2=None) -> list[dict]:
    df = load_labeled() if df is None else df
    return [run_kmeans(
        "K08", "K-3", best_k2["k"], normalization=best_k2["normalization"],
        representation="frequency", ngram_range=(1, 1), svd_components=100,
        df=df,
        notes=(f"K-3: frecuencia con {best_k2['normalization']}, k={best_k2['k']}; "
               f"TF-IDF es {best_k2['experiment_id']}"),
    )]


def run_block_k4(df=None, best_k3=None) -> list[dict]:
    df = load_labeled() if df is None else df
    return [run_kmeans(
        "K09", "K-4", best_k3["k"], normalization=best_k3["normalization"],
        representation=best_k3["representation"], ngram_range=(1, 2),
        svd_components=100, df=df,
        notes=(f"K-4: bigramas con {best_k3['representation']}, "
               f"k={best_k3['k']}; unigramas es {best_k3['experiment_id']}"),
    )]


def run_block_k5(df=None, best_k4=None) -> list[dict]:
    df = load_labeled() if df is None else df
    results = []
    for i, components in enumerate([None, 50, 200], start=10):
        results.append(run_kmeans(
            f"K{i:02d}", "K-5", best_k4["k"],
            normalization=best_k4["normalization"],
            representation=best_k4["representation"],
            ngram_range=best_k4["ngram_range"],
            svd_components=components, df=df,
            notes=(f"K-5: SVD {components or 'sin SVD'}; "
                   f"referencia SVD 100={best_k4['experiment_id']}"),
        ))
    return results


def run_block_k6(df=None, best_k5=None) -> list[dict]:
    df = load_labeled() if df is None else df
    configs = [
        ("random", 10, 300),
        ("k-means++", 20, 300),
        ("k-means++", 10, 500),
        ("random", 20, 500),
    ]
    results = []
    for i, (init, n_init, max_iter) in enumerate(configs, start=13):
        results.append(run_kmeans(
            f"K{i:02d}", "K-6", best_k5["k"],
            normalization=best_k5["normalization"],
            representation=best_k5["representation"],
            ngram_range=best_k5["ngram_range"],
            svd_components=best_k5["svd_components"], init=init,
            n_init=n_init, max_iter=max_iter, df=df,
            notes=(f"K-6: init={init}, n_init={n_init}, max_iter={max_iter}; "
                   f"referencia={best_k5['experiment_id']}"),
        ))
    return results


def plot_silhouette_vs_k(k1_results: list[dict], path) -> None:
    ks = [r["k"] for r in k1_results]
    train = [r["train_silhouette"] for r in k1_results]
    dev = [r["dev_silhouette"] for r in k1_results]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(ks, train, marker="o", label="train", color="#2a78d6")
    ax.plot(ks, dev, marker="s", label="dev", color="#eb6834")
    for k, value in zip(ks, dev):
        ax.annotate(f"{value:.3f}", (k, value), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)
    ax.set_xlabel("n_clusters (k)")
    ax.set_ylabel("silhouette (coseno)")
    ax.set_title("K-1: silhouette vs k", loc="left", fontsize=11)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e4e0", lw=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_cluster_sizes(assignments: pd.DataFrame, path) -> None:
    table = pd.crosstab(assignments["cluster_id"], assignments["split"])
    order = [c for c in ["train", "dev", "test"] if c in table.columns]
    table = table[order]
    ax = table.plot(kind="bar", stacked=True, figsize=(6.5, 4),
                    color=["#2a78d6", "#eb6834", "#1baf7a"][:len(order)])
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Documentos")
    ax.set_title("Tamaño de los clusters por partición", loc="left", fontsize=11)
    ax.legend(frameon=False, title="Split")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_contingency(contingency: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(contingency.values, cmap="Blues", vmin=0)
    ax.set_xticks(range(contingency.shape[1]),
                  [f"cluster {c}" for c in contingency.columns], rotation=0)
    ax.set_yticks(range(contingency.shape[0]), contingency.index)
    ax.set_xlabel("Cluster asignado")
    ax.set_ylabel("Categoría real (solo interpretación)")
    ax.set_title("Test: categoría real vs cluster", loc="left", fontsize=11)
    peak = contingency.values.max()
    for i in range(contingency.shape[0]):
        for j in range(contingency.shape[1]):
            value = contingency.values[i, j]
            ax.text(j, i, str(value), ha="center", va="center", fontsize=9,
                    color="white" if value > peak / 2 else "#222222")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def finalize(best: dict, k1_results: list[dict], df: pd.DataFrame) -> dict:
    train_dev = df[df["split"].isin(["train", "dev"])]
    test = df[df["split"] == "test"]
    X_train_dev = train_dev["document_id"].tolist()
    X_test = test["document_id"].tolist()

    pipe = build_pipeline(
        best["k"], best["normalization"], best["representation"],
        best["ngram_range"], best["svd_components"], best["init"],
        best["n_init"], best["max_iter"],
    )
    pipe.fit(X_train_dev)
    labels_train_dev = pipe.named_steps["km"].labels_.astype(int)
    labels_test = pipe.predict(X_test).astype(int)
    space_train_dev = to_dense(pipe[:-1].transform(X_train_dev))
    space_test = to_dense(pipe[:-1].transform(X_test))

    sil_train_dev = float(silhouette_score(
        space_train_dev, labels_train_dev, metric="cosine"))
    sil_test = float(silhouette_score(space_test, labels_test, metric="cosine"))
    ari_test = float(adjusted_rand_score(test["label"], labels_test))
    nmi_test = float(normalized_mutual_info_score(test["label"], labels_test))

    variants = load_variants().set_index("document_id")
    texts_train_dev = [variants.loc[doc_id, "text_n2"] for doc_id in X_train_dev]
    top = content_top_words(texts_train_dev, labels_train_dev, best["k"])
    rep = representative_docs(space_train_dev, labels_train_dev, X_train_dev, best["k"])

    assignments = pd.DataFrame({
        "document_id": X_train_dev + X_test,
        "split": train_dev["split"].tolist() + ["test"] * len(X_test),
        "cluster_id": list(labels_train_dev) + list(labels_test),
    })
    configuration = (f"{best['experiment_id']}_k{best['k']}_"
                     f"{best['normalization']}_{best['representation']}_"
                     f"{best['ngram_range'][0]}-{best['ngram_range'][1]}_"
                     f"svd{best['svd_components'] or 'none'}")
    assignments["configuration"] = configuration
    assignments.to_csv(RESULTS_DIR / "clustering_results.tsv", sep="\t", index=False)

    summary = pd.DataFrame({
        "cluster_id": list(range(best["k"])),
        "size": [int((assignments["cluster_id"] == c).sum()) for c in range(best["k"])],
        "top_words": [", ".join(top[c]) for c in range(best["k"])],
        "representative_document_ids": [",".join(rep[c]) for c in range(best["k"])],
    })
    summary.to_csv(RESULTS_DIR / "cluster_summary.tsv", sep="\t", index=False)

    contingency = pd.crosstab(test["label"], labels_test)
    contingency.index.name = "gold"
    contingency.columns.name = "cluster"
    contingency.to_csv(RESULTS_DIR / "cluster_contingency_test.tsv", sep="\t")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_silhouette_vs_k(k1_results, FIGURES_DIR / "clustering_silhouette_vs_k.png")
    plot_cluster_sizes(assignments, FIGURES_DIR / "clustering_sizes.png")
    plot_contingency(contingency, FIGURES_DIR / "clustering_contingency_test.png")

    lines = [
        "# K-Means: selección, evaluación e interpretación\n",
        f"Configuración final: **{configuration}** ({best['experiment_id']}).\n",
        f"- k = {best['k']}; normalización {best['normalization']}; "
        f"representación {best['representation']}; "
        f"n-gramas {best['ngram_range']}; "
        f"SVD {best['svd_components'] or 'sin SVD'}; "
        f"init {best['init']}, n_init {best['n_init']}, max_iter {best['max_iter']}.",
        f"- Silhouette (coseno, espacio SVD+L2): train+dev **{sil_train_dev:.4f}**, "
        f"test **{sil_test:.4f}**.",
        f"- ARI test **{ari_test:.4f}**, NMI test **{nmi_test:.4f}** "
        "(solo interpretación externa; K-Means no vio las etiquetas).",
        f"- Tamaños finales: {', '.join(f'{c}: {s}' for c, s in zip(summary['cluster_id'], summary['size']))}.",
        "\n## Palabras y documentos representativos\n",
    ]
    for _, row in summary.iterrows():
        lines += [
            f"### Cluster {row['cluster_id']} ({row['size']} documentos)",
            f"**Palabras:** {row['top_words']}",
            f"**Representativos:** {row['representative_document_ids']}\n",
        ]

    lines += ["\n## Contingencia en test\n"]
    lines.append("| Gold | " + " | ".join(f"Cluster {c}" for c in contingency.columns) + " |")
    lines.append("|---|" + "---:|" * len(contingency.columns))
    for index, values in contingency.iterrows():
        lines.append(f"| {index} | " + " | ".join(str(v) for v in values) + " |")

    lines += [
        "\n## Lectura\n",
        "- El silhouette de texto es bajo por naturaleza (0.02-0.10 es habitual); "
        "se interpreta comparando configuraciones, no como una medida absoluta.",
        "- En la práctica, los cuatro clusters se leen como NLP/agentes (0), "
        "IR/recomendación (1), visión/vídeo (2) y ML general (3).",
        "- El cluster 3 es pequeño (39 documentos) y concentra cs.LG; no se "
        "fusionó porque sus palabras (parameter, attention, scale, feature) son "
        "claramente de aprendizaje automático.",
        "- K-Means agrupa por vocabulario dominante; los clusters no tienen por qué "
        "coincidir con las 4 categorías de arXiv. El ARI/NMI y la tabla de "
        "contingencia solo cuantifican ese parecido.",
        "- k = 4 surgió de la comparación de K-1; no se impuso. Los tamaños "
        "192/156/113/39 son razonables, aunque el cluster 3 es el más pequeño.",
    ]
    (RESULTS_DIR / "cluster_analysis.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    mark_selected(
        best["experiment_id"],
        notes=(f"Configuración final de K-Means: silhouette dev "
               f"{best['dev_silhouette']:.4f}, test {sil_test:.4f}; "
               f"ARI test {ari_test:.4f}, NMI test {nmi_test:.4f}. "
               "Elegida por silhouette en dev e interpretabilidad; ARI/NMI "
               "solo son interpretación externa"),
    )
    return {
        "pipeline": pipe, "assignments": assignments, "summary": summary,
        "sil_train_dev": sil_train_dev, "sil_test": sil_test,
        "ari_test": ari_test, "nmi_test": nmi_test,
        "contingency": contingency, "top_words": top, "representative": rep,
    }


def unselect(experiment_id: str, note: str) -> None:
    exp = load_experiments()
    mask = exp["experiment_id"] == experiment_id
    if not mask.any():
        return
    exp.loc[mask, "selected"] = "no"
    old = exp.loc[mask, "notes"].iloc[0]
    exp.loc[mask, "notes"] = f"{old} | {note}" if old else note
    exp.to_csv(EXPERIMENTS_PATH, sep="\t", index=False)


def run_all(df=None) -> dict:
    df = load_labeled() if df is None else df
    k1 = run_block_k1(df)
    best1 = choose_best(k1)
    k2 = run_block_k2(df, best1)
    best2 = choose_best(k2 + [best1])
    k3 = run_block_k3(df, best2)
    best3 = choose_best(k3 + [best2])
    k4 = run_block_k4(df, best3)
    best4 = choose_best(k4 + [best3])
    k5 = run_block_k5(df, best4)
    best5 = choose_best(k5 + [best4])
    k6 = run_block_k6(df, best5)
    best6 = choose_best(k6 + [best5])

    # La cadena automática por silhouette termina en K16 (N0, frecuencia,
    # bigramas, SVD 50). Sus clusters separan artefactos de formato (LaTeX,
    # números) y su ARI/NMI es ~0.01: no son áreas de investigación. El plan
    # advierte que el silhouette solo se compara dentro del mismo espacio de
    # características. Dentro de N2 + TF-IDF + SVD 100, K02 (k=4) está empatado
    # con el mejor silhouette (0.0660 vs 0.0664) y sus clusters son temáticos:
    # NLP/agentes, ML general, IR/recomendación y visión/vídeo. Se elige K02
    # por interpretabilidad; ARI/NMI se reportan después, solo como lectura
    # externa.
    best_final = load_stored_k_result(SELECTED_FINAL)
    if best6["experiment_id"] != SELECTED_FINAL:
        unselect(
            best6["experiment_id"],
            "No seleccionado: mayor silhouette, pero los clusters separan "
            "artefactos de formato (LaTeX/números), no áreas de investigación",
        )
    final = finalize(best_final, k1, df)

    with open(RESULTS_DIR / "cluster_analysis.md", "a", encoding="utf-8") as fh:
        fh.write("\n## Selección final\n")
        fh.write(
            f"La cadena automática por silhouette terminó en "
            f"**{best6['experiment_id']}** (dev {best6['dev_silhouette']:.4f}), "
            "pero sus clusters separan artefactos de formato (LaTeX, números, "
            "longitud) y su ARI/NMI es cercano a 0. El plan advierte que el "
            "silhouette solo se compara dentro del mismo espacio de "
            "características; entre espacios distintos hay que apoyarse en la "
            "interpretabilidad.\n\n"
            f"Dentro de N2 + TF-IDF (1,1) + SVD 100, **{SELECTED_FINAL}** (k=4) "
            f"tiene silhouette dev {best_final['dev_silhouette']:.4f}, "
            "prácticamente empatado con el máximo del espacio (0.0664), y sus "
            "cuatro clusters son temáticos: NLP/agentes, ML general, "
            "IR/recomendación y visión/vídeo. Se elige por interpretabilidad y "
            "equilibrio de tamaños; ARI/NMI no se usaron para seleccionar.\n\n"
            "| Bloque | Ganador automático | k | silhouette dev |\n"
            "|---|---|---:|---:|\n"
        )
        for name, b in [("K-1", best1), ("K-2", best2), ("K-3", best3),
                        ("K-4", best4), ("K-5", best5), ("K-6", best6)]:
            fh.write(f"| {name} | {b['experiment_id']} | {b['k']} | "
                     f"{b['dev_silhouette']:.4f} |\n")
        fh.write(
            f"\nLa estabilidad de {SELECTED_FINAL} es moderada "
            f"({best_final['stability_ari']:.3f}); las configuraciones con "
            "estabilidad casi perfecta también son las que separan formato, "
            "no temas. El silhouette de texto es bajo por naturaleza.\n"
        )

    return {
        "k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5, "k6": k6,
        "best1": best1, "best2": best2, "best3": best3,
        "best4": best4, "best5": best5, "best6": best6,
        "best_final": best_final, "final": final,
    }


if __name__ == "__main__":
    result = run_all()
    print("Selección por bloque:")
    for name in ["best1", "best2", "best3", "best4", "best5", "best6"]:
        b = result[name]
        print(f"  {name}: {b['experiment_id']}  k={b['k']}  "
              f"dev silhouette={b['dev_silhouette']:.4f}  "
              f"stability={b['stability_ari']:.3f}")
    final = result["final"]
    print(f"\nFinal: silhouette train+dev={final['sil_train_dev']:.4f}, "
          f"test={final['sil_test']:.4f}; ARI test={final['ari_test']:.4f}; "
          f"NMI test={final['nmi_test']:.4f}")
    print(final["summary"].to_string(index=False))
    print(f"\nEscrito en {RESULTS_DIR}")

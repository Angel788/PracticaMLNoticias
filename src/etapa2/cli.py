"""Interfaz de consulta de la Etapa II.

Uso:
    python -m src.etapa2.cli metrics                      # métricas dev/test
    python -m src.etapa2.cli metrics --experiment C02     # por clase + confusión
    python -m src.etapa2.cli clusters                     # tamaños y top-10 palabras
    python -m src.etapa2.cli clusters --id 2              # documentos representativos
    python -m src.etapa2.cli experiments --task classification --top 10
"""
import argparse

import pandas as pd
from tabulate import tabulate

from src.etapa2.config import RAW_CORPUS_PATH, RESULTS_DIR

EXPERIMENTS_PATH = RESULTS_DIR / "experiments.tsv"
METRICS_PATH = RESULTS_DIR / "classification_metrics.tsv"
PER_CLASS_PATH = RESULTS_DIR / "classification_per_class.tsv"
CONFUSION_DIR = RESULTS_DIR / "confusion_matrices"
CLUSTER_RESULTS_PATH = RESULTS_DIR / "clustering_results.tsv"
CLUSTER_SUMMARY_PATH = RESULTS_DIR / "cluster_summary.tsv"


def read_tsv(path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"No existe {path}. Ejecuta primero el paso que lo genera.")
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def show(df: pd.DataFrame, floatfmt: str = ".4f") -> None:
    print(tabulate(df, headers="keys", tablefmt="simple",
                   showindex=False, floatfmt=floatfmt))


def cmd_metrics(args: argparse.Namespace) -> None:
    metrics = read_tsv(METRICS_PATH)
    for col in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]:
        metrics[col] = pd.to_numeric(metrics[col])

    if not args.experiment:
        print("Métricas de clasificación (dev y test)\n")
        show(metrics)
        print("\nEl test se evaluó una sola vez con el ganador global "
              "(experiment_id = test).")
        return

    rows = metrics[metrics["experiment_id"] == args.experiment]
    if rows.empty:
        raise SystemExit(f"No hay métricas para el experimento {args.experiment}")
    show(rows)

    per_class = read_tsv(PER_CLASS_PATH)
    per_class = per_class[per_class["experiment_id"] == args.experiment]
    for col in ["precision", "recall", "f1"]:
        per_class[col] = pd.to_numeric(per_class[col])

    for split in per_class["split"].unique():
        print(f"\nPor clase · {split}")
        show(per_class[per_class["split"] == split][
            ["label", "precision", "recall", "f1", "support"]])
        name = f"{args.experiment}_{split}.tsv" if split != "test" else "test.tsv"
        path = CONFUSION_DIR / name
        if path.exists():
            cm = pd.read_csv(path, sep="\t", index_col=0)
            print(f"\nMatriz de confusión · {split}")
            print(cm.to_string())


def cmd_clusters(args: argparse.Namespace) -> None:
    summary = read_tsv(CLUSTER_SUMMARY_PATH)
    summary["size"] = pd.to_numeric(summary["size"])

    if args.id is None:
        view = summary.copy()
        view["top_words"] = view["top_words"].str.slice(0, 70)
        view["representative_document_ids"] = (
            view["representative_document_ids"].str.slice(0, 50))
        print("Clusters: tamaño, palabras principales y documentos representativos\n")
        show(view[["cluster_id", "size", "top_words",
                   "representative_document_ids"]], floatfmt=".0f")
        if CLUSTER_RESULTS_PATH.exists():
            results = read_tsv(CLUSTER_RESULTS_PATH)
            print("\nDocumentos por cluster y partición")
            print(pd.crosstab(results["cluster_id"], results["split"]).to_string())
        return

    row = summary[summary["cluster_id"].astype(str) == str(args.id)]
    if row.empty:
        raise SystemExit(f"No existe el cluster {args.id}")
    row = row.iloc[0]
    print(f"Cluster {row['cluster_id']} · {row['size']} documentos\n")
    print(f"Palabras principales: {row['top_words']}\n")
    ids = [d for d in row["representative_document_ids"].split(",") if d]

    raw = pd.read_csv(RAW_CORPUS_PATH, sep="\t", dtype=str, keep_default_na=False)
    print("Documentos representativos (los más cercanos al centroide):")
    for doc_id in ids:
        match = raw[raw["arxiv_id"] == doc_id]
        if match.empty:
            print(f"- {doc_id}")
            continue
        doc = match.iloc[0]
        print(f"- {doc_id} · {doc['primary_category']} · {doc['title'][:110]}")


def cmd_experiments(args: argparse.Namespace) -> None:
    exp = read_tsv(EXPERIMENTS_PATH)
    if args.task:
        exp = exp[exp["task"] == args.task]
    if exp.empty:
        print("No hay experimentos con ese filtro.")
        return

    scores = exp["dev_metric"].str.extract(r"(?:macro_f1|silhouette)=([0-9.]+)")[0]
    exp = exp.assign(_score=pd.to_numeric(scores, errors="coerce"))
    exp = exp.assign(_selected=(exp["selected"] == "yes").astype(int))
    exp = exp.sort_values(["_selected", "_score"], ascending=[False, False],
                          na_position="last")
    view = exp.head(args.top)

    cols = ["experiment_id", "task", "block", "normalization", "representation",
            "ngram_range", "svd_components", "method", "hyperparameters",
            "cv_macro_f1", "dev_metric", "selected", "notes"]
    print(f"Experimentos ({args.task or 'todas las tareas'}), "
          f"top {min(args.top, len(view))} (los seleccionados van primero)\n")
    show(view[cols])


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m src.etapa2.cli",
        description="Consulta de métricas de clasificación y clusters de la Etapa II.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    metrics = sub.add_parser("metrics", help="métricas de clasificación (dev/test)")
    metrics.add_argument("--experiment", help="ID del experimento, p. ej. C02 o test")
    metrics.set_defaults(func=cmd_metrics)

    clusters = sub.add_parser("clusters", help="tamaños, palabras y documentos por cluster")
    clusters.add_argument("--id", type=int, help="ID del cluster a detallar")
    clusters.set_defaults(func=cmd_clusters)

    experiments = sub.add_parser("experiments", help="registro de experimentos")
    experiments.add_argument("--task", choices=["classification", "clustering"])
    experiments.add_argument("--top", type=int, default=10)
    experiments.set_defaults(func=cmd_experiments)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

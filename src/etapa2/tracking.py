"""Registro de experimentos en results/etapa2/experiments.tsv.

Uso: python -m src.etapa2.tracking   (crea el archivo vacío con encabezados)
"""
import pandas as pd

from src.etapa2.config import EXPERIMENTS_PATH

COLUMNS = [
    "experiment_id",    # C07, U03
    "task",             # classification / clustering
    "block",            # C-2, K-1
    "normalization",    # N0, N1, N2
    "representation",   # binary, frequency, tfidf
    "ngram_range",      # (1,2)
    "svd_components",   # 100 o vacío
    "method",           # LogisticRegression, KMeans
    "hyperparameters",  # C=1.0; min_df=2
    "cv_macro_f1",      # solo clasificación
    "dev_metric",       # macro_f1=0.84 / silhouette=0.07
    "extra",            # ARI/NMI, tamaños de cluster
    "selected",         # yes / no
    "notes",            # motivo de la selección o del descarte
]


# Crea experiments.tsv con encabezados si no existe.
def init_experiments(overwrite: bool = False) -> None:
    if EXPERIMENTS_PATH.exists() and not overwrite:
        return
    EXPERIMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=COLUMNS).to_csv(EXPERIMENTS_PATH, sep="\t", index=False)


# Lee experiments.tsv como texto.
def load_experiments() -> pd.DataFrame:
    init_experiments()
    return pd.read_csv(EXPERIMENTS_PATH, sep="\t", dtype=str, keep_default_na=False)


# Agrega una fila. Si el experiment_id ya existe, lo reemplaza (re-ejecuciones).
def log_experiment(**row) -> None:
    unknown = set(row) - set(COLUMNS)
    if unknown:
        raise ValueError(f"Columnas desconocidas: {unknown}")
    if "experiment_id" not in row:
        raise ValueError("Falta experiment_id")
    row.setdefault("selected", "no")
    df = load_experiments()
    df = df[df["experiment_id"] != row["experiment_id"]]
    new = pd.DataFrame([{c: "" if row.get(c) is None else str(row.get(c, "")) for c in COLUMNS}])
    df = pd.concat([df, new], ignore_index=True) if len(df) else new
    df.sort_values("experiment_id").to_csv(EXPERIMENTS_PATH, sep="\t", index=False)


# Escribe la columna notes de un experimento ya registrado.
def annotate(experiment_id: str, notes: str) -> None:
    df = load_experiments()
    mask = df["experiment_id"] == experiment_id
    if not mask.any():
        raise ValueError(f"No existe el experimento {experiment_id}")
    df.loc[mask, "notes"] = notes
    df.to_csv(EXPERIMENTS_PATH, sep="\t", index=False)


# Marca un experimento como seleccionado y, opcionalmente, anota el motivo.
def mark_selected(experiment_id: str, notes: str | None = None,
                  append: bool = True) -> None:
    df = load_experiments()
    mask = df["experiment_id"] == experiment_id
    if not mask.any():
        raise ValueError(f"No existe el experimento {experiment_id}")
    df.loc[mask, "selected"] = "yes"
    if notes:
        old = df.loc[mask, "notes"].iloc[0]
        df.loc[mask, "notes"] = f"{old} | {notes}" if (append and old) else notes
    df.to_csv(EXPERIMENTS_PATH, sep="\t", index=False)


if __name__ == "__main__":
    init_experiments()
    print(f"Listo {EXPERIMENTS_PATH}")

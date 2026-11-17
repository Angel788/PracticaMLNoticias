"""Constantes compartidas de la Etapa II: semilla, rutas y clases."""
from pathlib import Path

RANDOM_STATE = 0

ROOT = Path(__file__).resolve().parents[2]

# Entrada (Etapa I, no se modifica)
RAW_CORPUS_PATH = ROOT / "data" / "scientific_raw_corpus.tsv"

# Datos de la Etapa II
DATA_DIR = ROOT / "data" / "etapa2"
LABELED_PATH = DATA_DIR / "labeled_documents.tsv"
NORMALIZED_PATH = DATA_DIR / "normalized_variants.tsv"

# Resultados de la Etapa II
RESULTS_DIR = ROOT / "results" / "etapa2"
FIGURES_DIR = RESULTS_DIR / "figures"
EXPERIMENTS_PATH = RESULTS_DIR / "experiments.tsv"

CLASSES = ["cs.CL", "cs.CV", "cs.IR", "cs.LG"]

# Proporciones 70/15/15 -> 350/75/75 con 500 documentos
TEST_SIZE = 0.15
DEV_SIZE = 0.15

NORMALIZATIONS = ["N0", "N1", "N2"]

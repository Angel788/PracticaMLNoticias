# Pasos de ejecución · Etapa II

Guía para reproducir de punta a punta la clasificación supervisada (tarea A) y el
clustering con K-Means (tarea B). **Todos los comandos se ejecutan desde la raíz del
repositorio** (`PracticaMLNoticias/`), no desde `Etapa2/`.

## 0. Requisitos

- Python 3.12 o superior (probado con 3.14.7).
- El corpus de la Etapa I ya presente: `data/scientific_raw_corpus.tsv` (no se modifica).
- Todas las semillas están fijadas en 0 (`src/etapa2/config.py`), así que cada paso es
  determinista.

## 1. Preparar el entorno

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt     # incluye el modelo en_core_web_sm de spaCy
```

## 2. Etiquetas y splits

```bash
python -m src.etapa2.labels
```

- Usa `primary_category` de arXiv como etiqueta y verifica que coincide con la primera de
  `categories`.
- Hace los splits 70/15/15 estratificados (`random_state=0`) **antes de ajustar nada**.
- Salida: `data/etapa2/labeled_documents.tsv` (500 documentos: 350 train, 75 dev, 75 test).

## 3. Normalización

```bash
python -m src.etapa2.normalization
```

- Genera las tres variantes: **N0** (solo tokenización), **N1** (minúsculas, sin
  puntuación ni stopwords) y **N2** (lematización de la Etapa I).
- Salida: `data/etapa2/normalized_variants.tsv` (caché que leen los pipelines).
- Es el paso más lento (spaCy procesa los 500 textos una vez).

## 4. Experimentos de clasificación (tarea A)

Los bloques **deben correrse en orden**: C-2 reutiliza C-1, y C-4/C-5 leen el mejor
resultado del bloque anterior desde `results/etapa2/experiments.tsv`.

```bash
python -m src.etapa2.classify C-1    # C01-C03  clasificadores (NB, LR, SVC) con N2 + TF-IDF
python -m src.etapa2.classify C-2    # C04-C09  normalizaciones N0 / N1
python -m src.etapa2.classify C-3    # C10-C15  representaciones binaria / frecuencia
python -m src.etapa2.classify C-4    # C16-C21  n-gramas (1,2) y (1,3)
python -m src.etapa2.classify C-5    # C22-C29  SVD 50 / 100 / 200 (sin NB)
```

- Hiperparámetros con `GridSearchCV` (`StratifiedKFold(5)`, `f1_macro`) **solo sobre train**;
  dev solo evalúa.
- Cada experimento se registra en `results/etapa2/experiments.tsv` (si se re-ejecuta, la
  fila se reemplaza) y sus predicciones/matrices en `results/etapa2/runs/CXX/`.

## 5. Selección y evaluación final en test

```bash
python -m src.etapa2.final
```

- Elige el mejor experimento de cada clasificador por macro-F1 en dev y el ganador global
  (C02, LogisticRegression).
- Reajusta **solo el ganador** con train+dev y evalúa **una sola vez** en test.
- Salidas en `results/etapa2/`:
  - `classification_predictions.tsv`, `classification_metrics.tsv`,
    `classification_per_class.tsv`
  - `confusion_matrices/` (TSV y PNG) y `figures/classification_*.png`
  - `error_analysis.md` (10 documentos de dev mal clasificados)

## 6. Clustering con K-Means (tarea B)

```bash
python -m src.etapa2.cluster
```

- Corre los bloques K-1 a K-6 (k, normalización, representación, n-gramas, SVD e
  hiperparámetros; K01-K17), mide silhouette en dev y estabilidad con 5 semillas.
- Reajusta la configuración elegida (K02: k=4, N2, TF-IDF, SVD 100) con train+dev, asigna
  test con `predict` y reporta silhouette, ARI y NMI.
- Salidas en `results/etapa2/`: `clustering_results.tsv`, `cluster_summary.tsv`,
  `cluster_contingency_test.tsv`, `cluster_analysis.md`, `runs_k/` y
  `figures/clustering_*.png`.

## 7. Consultar los resultados

### CLI

```bash
python -m src.etapa2.cli metrics                                  # métricas dev y test
python -m src.etapa2.cli metrics --experiment C02                 # un experimento
python -m src.etapa2.cli clusters                                 # resumen de clusters
python -m src.etapa2.cli clusters --id 1                          # detalle de un cluster
python -m src.etapa2.cli experiments --task classification --top 10
```

### Interfaz web

```bash
python -m src.etapa2.api
```

Abrir <http://127.0.0.1:8001>. Al arrancar reajusta los dos modelos finales (unos
segundos). Permite clasificar un título + abstract nuevo, ver probabilidades, palabras con
más peso, el cluster asignado, las métricas y el registro de experimentos.

## 8. Notebook y modelos guardados (opcional)

`notebooks/00_etapa2_completo.ipynb` recorre todos los experimentos leyendo los resultados
congelados (no vuelve a usar test) y, al final, guarda los modelos en `models/etapa2/`
(`classifier_c02.pkl`, `kmeans_k02.pkl`, `metadata.json`). Jupyter no está en
`requirements.txt`:

```bash
pip install jupyter
jupyter notebook notebooks/00_etapa2_completo.ipynb
```

Los pipelines guardados reciben **texto ya normalizado** (N2, `normalize_doc`).

## 9. Compilar el informe (opcional)

```bash
cd Etapa2
pdflatex informe.tex
pdflatex informe.tex   # segunda pasada para el índice
```

## Resumen rápido

```bash
source .venv/bin/activate
python -m src.etapa2.labels
python -m src.etapa2.normalization
for b in C-1 C-2 C-3 C-4 C-5; do python -m src.etapa2.classify $b; done
python -m src.etapa2.final
python -m src.etapa2.cluster
python -m src.etapa2.cli metrics
```

## Resultados esperados

| Tarea | Configuración | Dev | Test |
|---|---|---|---|
| Clasificación | C02 · LogisticRegression, N2, TF-IDF (1,1), `C=1` | macro-F1 0.799 | macro-F1 0.761 |
| Clustering | K02 · K-Means k=4, N2, TF-IDF (1,1), SVD 100 | silhouette 0.066 | silhouette 0.083 · ARI 0.372 · NMI 0.486 |

Si los números coinciden, la reproducción es correcta.

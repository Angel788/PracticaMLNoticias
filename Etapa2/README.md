# Etapa II · Clasificación y clustering de artículos científicos

Esta carpeta reúne el plan, el informe y las instrucciones de la Etapa II. El código, los
datos y los resultados viven en la raíz del repositorio (`src/etapa2/`, `data/etapa2/` y
`results/etapa2/`), porque la Etapa II reutiliza el corpus y la estructura de la Etapa I.

## Contenido de la carpeta

| Archivo | Qué es |
|---|---|
| `informe.pdf` | Informe final de la Etapa II (18 páginas). |
| `informe.tex` | Fuente LaTeX del informe. |
| `plan_de_trabajo.md` | Plan de trabajo completo (5 fases, reparto y checklist). |
| `Plan de trabajo — Proyecto Etapa II (equipo de 2).md` | Versión corta del plan. |
| `Proyecto_02_Artículos_Etapa_II.pdf` | Enunciado del profesor. |
| `Supervised text classificacion scripts/` | Scripts de ejemplo del profesor. |
| `Unsupervised text clustering script/` | Script de ejemplo de K-Means. |
| `Unsupervised topic modeling script/` | Script de ejemplo de LDA (no se usó). |

## Resultados principales

| Tarea | Configuración | Dev | Test |
|---|---|---|---|
| Clasificación | LogisticRegression, N2, TF-IDF (1,1), `C=1`, `min_df=1` | macro-F1 0.799 | macro-F1 **0.761** |
| Clustering | K-Means, k=4, N2, TF-IDF (1,1), SVD 100 | silhouette 0.066 | silhouette **0.083**, ARI **0.372**, NMI **0.486** |

- La clase más difícil es `cs.CL` (F1 0.579 en test); la confusión principal es
  `cs.CL` ↔ `cs.LG`.
- TF-IDF superó a binaria y frecuencia; los bigramas/trigramas y el SVD no mejoraron de
  forma material.
- K-Means encontró cuatro clusters interpretables (NLP/agentes, IR/recomendación,
  visión/vídeo y ML general). Las configuraciones con silhouette más alto separaban
  artefactos de formato (LaTeX, números), no temas; por eso la selección final combinó
  silhouette en dev con interpretabilidad.
- **K-3 binaria (K17):** se añadió para completar las tres representaciones de K-Means;
  silhouette dev 0.0477 y ARI $-0.0038$, no mejora a TF-IDF.
- **C-5 complementario (C26-C29):** SVD 50/100/200 sobre la configuración final C02 no
  mejora LR (0.7706/0.7586/0.7475 frente a 0.7993). En SVC, SVD 50 (C29) sube a 0.7880
  en dev, pero con CV 0.7040 frente a 0.7451 y añadido después de evaluar test; se mantiene
  C06 y C29 queda como línea para un test independiente.

## Notebook único

[`../notebooks/00_etapa2_completo.ipynb`](../notebooks/00_etapa2_completo.ipynb) recorre
la historia completa en un solo archivo: datos, bloques C-1 a C-5, K-Means, test, clusters
y guardado de los modelos finales. Lee los resultados congelados, no vuelve a usar test.

Los notebooks 06--14 anteriores se conservan en la rama `etapa2`; esta rama deja solo el
notebook único para no hacer la entrega tan pesada.

## Reproducir

Requisitos: Python 3.12+ (probado con 3.14.7) y las versiones fijadas en
`../requirements.txt`. Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m src.etapa2.labels          # labeled_documents.tsv + splits
python -m src.etapa2.normalization   # caché N0/N1/N2
python -m src.etapa2.classify C-1    # C01-C03
python -m src.etapa2.classify C-2    # C04-C09 (reutiliza C01-C03)
python -m src.etapa2.classify C-3    # C10-C15
python -m src.etapa2.classify C-4    # C16-C21
python -m src.etapa2.classify C-5    # C22-C29
python -m src.etapa2.final           # selección, test único y TSV de entrega
python -m src.etapa2.cluster         # K-1 a K-6 y clustering_results.tsv
```

Los bloques C-4 y C-5 leen el mejor resultado del bloque anterior desde
`results/etapa2/experiments.tsv`; hay que ejecutarlos en orden. Los comandos son
deterministas: todas las semillas son 0 (`random_state=0` en splits, SVD, modelos y
K-Means; `StratifiedKFold(5, shuffle=True, random_state=0)`).

### Interfaz web

```bash
python -m src.etapa2.api      # desde la raíz; desde Etapa2/: python ../src/etapa2/api.py
```

Clasifica un título + abstract nuevo con el modelo final (C02 reajustado con train+dev),
muestra las probabilidades por categoría, las palabras que más pesaron y el cluster de
K-Means asignado. Debajo están las métricas, las matrices de confusión, los clusters y el
registro de experimentos. El botón «Cargar un artículo de test» permite comparar la
predicción con la categoría real. Al arrancar se reajustan los dos modelos (unos
segundos); sus predicciones coinciden con las de `results/etapa2/`.

### Consultar resultados

```bash
python -m src.etapa2.cli metrics
python -m src.etapa2.cli metrics --experiment C02
python -m src.etapa2.cli clusters
python -m src.etapa2.cli clusters --id 1
python -m src.etapa2.cli experiments --task classification --top 10
```

### Compilar el informe

```bash
cd Etapa2
pdflatex informe.tex
pdflatex informe.tex   # segunda pasada para el índice
```

## Modelos finales

Los dos modelos ya ajustados con train+dev quedan en `../models/etapa2/`:

| Archivo | Contenido |
|---|---|
| `../models/etapa2/classifier_c02.pkl` | Pipeline TF-IDF + LogisticRegression(C=1) |
| `../models/etapa2/kmeans_k02.pkl` | Pipeline TF-IDF + SVD 100 + L2 + KMeans(k=4) |
| `../models/etapa2/metadata.json` | Configuración, métricas y versiones |

Los pipelines guardados reciben **texto ya normalizado**; para texto nuevo, normaliza
primero con `normalize_doc`. El notebook 14 muestra cómo cargarlos con `joblib.load`.

## Archivos de resultados

| Archivo | Contenido |
|---|---|
| `../results/etapa2/experiments.tsv` | 46 experimentos (29 de clasificación, 17 de clustering) |
| `../results/etapa2/classification_predictions.tsv` | Predicciones de dev (mejor por modelo) y test |
| `../results/etapa2/classification_metrics.tsv` | Accuracy, macro P/R/F1 por split |
| `../results/etapa2/classification_per_class.tsv` | Métricas por clase |
| `../results/etapa2/confusion_matrices/` | Matrices de confusión (TSV y PNG) |
| `../results/etapa2/error_analysis.md` | 10 errores de dev explicados |
| `../results/etapa2/clustering_results.tsv` | `document_id`, `split`, `cluster_id`, `configuration` |
| `../results/etapa2/cluster_summary.tsv` | Tamaño, top-10 palabras y representativos |
| `../results/etapa2/cluster_analysis.md` | Selección e interpretación de K-Means |

## Notas metodológicas

- El corpus, los identificadores y el benchmark de la Etapa I no se modificaron.
- Test se usó una sola vez por tarea, después de congelar la configuración en dev.
- K-Means no vio etiquetas durante el ajuste; ARI/NMI y la contingencia son solo
  interpretación externa.
- No se usaron LLM ni modelos generativos.
- El equipo es de dos personas; el reparto está en `plan_de_trabajo.md`.

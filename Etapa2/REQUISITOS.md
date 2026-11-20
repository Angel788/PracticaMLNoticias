# Lo que pidió el profesor (Etapa II) y dónde está

Este archivo **no es un requisito extra**: es el índice de la entrega. Resume lo que pide
el PDF del profesor y apunta al archivo exacto que lo cumple.

## 1. Entregables obligatorios (PDF, §11)

| # | Lo que pidió | Dónde está | Estado |
|---|---|---|---|
| 1 | Código fuente con Pipelines, requirements, semillas e instrucciones reproducibles | `src/etapa2/`, `../requirements.txt`, `README.md` | ✅ |
| 2 | `labeled_documents.tsv`: `document_id, text, label, split` + metadata | `../data/etapa2/labeled_documents.tsv` | ✅ 500 filas |
| 3 | `classification_predictions.tsv`: `document_id, gold_label, predicted_label, split, model, experiment_id` | `../results/etapa2/classification_predictions.tsv` | ✅ 300 filas: 225 dev + 75 test |
| 4 | `classification_metrics.tsv` (solo dev y test): `experiment_id, model, split, accuracy, macro_precision, macro_recall, macro_f1` | `../results/etapa2/classification_metrics.tsv` | ✅ 4 filas |
| 5 | Resultados por clase y matrices de confusión | `../results/etapa2/classification_per_class.tsv` y `../results/etapa2/confusion_matrices/` | ✅ |
| 6 | `clustering_results.tsv`: `document_id, split, cluster_id, method/configuration` | `../results/etapa2/clustering_results.tsv` | ✅ 500 filas |
| 7 | Tamaños, top words y documentos representativos de los clusters | `../results/etapa2/cluster_summary.tsv` | ✅ 4 clusters, 2 representativos por cluster |
| 8 | `experiments.tsv`: bitácora completa de experimentos | `../results/etapa2/experiments.tsv` | ✅ 46 experimentos |
| 9 | Informe PDF con figuras, tablas, análisis de errores, limitaciones y nombres | `informe.pdf` | ✅ 18 páginas |
| 10 | `topic_results.tsv` (solo si se elige LDA) | No aplica | Se eligió **K-Means** |

**Notas de lectura**

- `classification_metrics.tsv` es solo dev/test; las métricas por clase y las matrices
  están en archivos separados, como propone el plan.
- `clustering_results.tsv` tiene la asignación documento → cluster; el resumen de tamaños,
  palabras y representativos está en `cluster_summary.tsv`.
- `topic_results.tsv` no se genera porque la tarea opcional elegida fue K-Means.

## 2. Contenido obligatorio del informe (PDF, §12)

| Lo que pidió | Dónde está en `informe.pdf` |
|---|---|
| Tarea y corpus | §1–2 |
| Splits y control de fuga | §3 |
| Política de etiquetas | §2 |
| Alternativas de normalización | §4 |
| Representaciones vectoriales | §5–6 |
| Comparación de clasificadores | §6 |
| Ajuste de hiperparámetros | §5 y Tabla 18 |
| Selección en dev | §6.3 |
| Evaluación final en test | §6.3 |
| Análisis de errores supervisado | §7 |
| Interpretación de K-Means | §8 |
| Limitaciones y reproducibilidad | §10–11 |
| Tabla resumen de experimentos | Tabla 18 |
| Nombres del equipo | Portada |

## 3. Criterios de finalización (PDF, §13)

| Criterio | Estado |
|---|---|
| Splits train/dev/test reproducibles | ✅ 350/75/75, `random_state=0` |
| Clasificación supervisada + **una** tarea no supervisada | ✅ C02 + K02 |
| Variar normalización, representación e hiperparámetros en ambas tareas | ✅ 29 experimentos de clasificación y 17 de clustering |
| Elegir configuraciones sin usar test | ✅ selección congelada en dev |
| Reportar evidencia final en test y análisis cualitativo | ✅ test 0.761; K-Means 0.083 / ARI 0.372 / NMI 0.486 |

## 4. Lo que **no** es requisito

Para que no se pierda entre los archivos:

- `notebooks/00_etapa2_completo.ipynb` y `notebooks/01–05`: **evidencia**, no entregables.
- `src/etapa2/api.py` + `web/`: interfaz extra, no obligatoria.
- `models/etapa2/*.pkl`: modelos guardados para reutilizar, extra.
- `../data/etapa2/normalized_variants.tsv`: caché de normalización.
- `../Etapa2.zip` y `../Evidencias_Practica2.zip`: material fuente/evidencia, no entregables.

## 5. Verificación rápida

```bash
ls data/etapa2/labeled_documents.tsv
ls results/etapa2/classification_predictions.tsv
ls results/etapa2/classification_metrics.tsv
ls results/etapa2/clustering_results.tsv
ls results/etapa2/cluster_summary.tsv
ls results/etapa2/experiments.tsv
pdfinfo Etapa2/informe.pdf | grep Pages
```

El detalle de cómo reproducir todo está en `README.md`.

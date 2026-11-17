# Plan de trabajo: Proyecto Etapa II, ML tradicional sobre artículos científicos

Equipo de 2 personas (**A** y **B**). El PDF pide 3-4 integrantes, así que hay que confirmar con el profesor que un equipo de 2 es válido (ya se hizo así en la Etapa I). Entrega: **17 de noviembre**. Se trabaja en 5 días: día 1 = 12 de noviembre, día 5 = 16 de noviembre; el 17 queda solo para entregar.

---

## 1. Supuestos iniciales

| Tema | Supuesto de trabajo |
|---|---|
| Corpus | Se reutiliza `data/scientific_raw_corpus.tsv` de la Etapa I **sin ampliarlo**: 500 documentos, 125 por categoría (`cs.CL`, `cs.CV`, `cs.IR`, `cs.LG`) |
| `document_id` | `arxiv_id`, igual que en la Etapa I |
| Entrada `X` | `title + ". " + abstract` |
| Etiqueta `y` | Columna `primary_category` (la categoría primaria que asigna arXiv). Se verifica que coincide con el primer elemento de `categories` |
| Splits | 70/15/15 → 350 train / 75 dev / 75 test, estratificado (~87/19/19 por clase) |
| Semilla | `random_state=0` en splits, SVD, modelos y K-Means |
| Tarea opcional | **K-Means (tarea B)**. Reutiliza TF-IDF y SVD de la tarea A, tiene métrica clara (silhouette) y asigna documentos nuevos con `predict`. LDA (tarea C) queda descartada |
| Librerías | Las de `requirements.txt` (spaCy 3.8, scikit-learn 1.9, pandas, numpy) + `matplotlib` para las figuras |
| Restricciones | Sin LLM ni modelos generativos. El benchmark congelado de la Etapa I (`benchmark-v1`) no se toca |

---

## 2. Reparto de roles

**A** se encarga de la clasificación (tarea A, obligatoria) y **B** de K-Means (tarea B) y de la base común. Las tareas marcadas con ⚖️ se hacen entre los dos.

| Área | A | B |
|---|---|---|
| Elegir la tarea opcional | ⚖️ | ⚖️ |
| Política de etiquetas y `labeled_documents.tsv` | ✅ responsable | revisa |
| Splits reproducibles | revisa | ✅ responsable |
| Módulo de normalización (3 configuraciones) | revisa | ✅ responsable |
| Formato del registro de experimentos | revisa | ✅ responsable |
| Experimentos de clasificación | ✅ responsable | apoyo |
| Experimentos de K-Means | apoyo | ✅ responsable |
| Selección en dev y evaluación única en test | ✅ (clasificación) | ✅ (K-Means) |
| Análisis de errores (10 documentos de dev) | ✅ responsable | revisa |
| Interpretación de clusters | revisa | ✅ responsable |
| Interfaz para consultar métricas y clusters | ✅ responsable | apoyo |
| `experiments.tsv` consolidado y `requirements` | revisa | ✅ responsable |
| Informe PDF | ⚖️ (cada quien su parte) | ⚖️ |

---

## 3. Estructura del repositorio

Se añade a lo que ya existe, sin modificar los archivos de la Etapa I.

```
PracticaMLNoticias-ia/
├── requirements.txt              # + matplotlib, versiones fijadas
├── data/
│   ├── scientific_raw_corpus.tsv            # Etapa I, no se modifica
│   └── etapa2/
│       ├── labeled_documents.tsv            # document_id, text, label, split, categories
│       └── normalized_variants.tsv          # document_id, text_n0, text_n1, text_n2 (caché)
├── src/
│   ├── normalize.py                         # Etapa I, se reutiliza como N2
│   └── etapa2/
│       ├── config.py                        # semilla, rutas, constantes
│       ├── labels.py                        # etiqueta primaria y distribución
│       ├── splits.py                        # train/dev/test
│       ├── normalization.py                 # N0, N1, N2
│       ├── tracking.py                      # escribe filas en experiments.tsv
│       ├── classify.py                      # experimentos de la tarea A
│       ├── cluster.py                       # experimentos de K-Means
│       ├── final.py                         # reajuste en train+dev y evaluación en test
│       └── cli.py                           # interfaz de consulta
├── results/
│   └── etapa2/
│       ├── classification_predictions.tsv
│       ├── classification_metrics.tsv
│       ├── classification_per_class.tsv     # métricas por clase
│       ├── confusion_matrices/              # .tsv y .png
│       ├── clustering_results.tsv
│       ├── cluster_summary.tsv              # tamaño, top-10 palabras, documentos representativos
│       ├── experiments.tsv
│       ├── error_analysis.md
│       └── figures/
└── Etapa2/
    ├── plan_de_trabajo.md
    └── informe.pdf
```

---

## 4. Fases y tareas

### Fase 1: Acuerdos y base común (día 1, 12 nov)

**A: etiquetas**
- [ ] Confirmar que `primary_category` coincide con `categories.split()[0]` en los 500 documentos. Si no coincide en algún caso, documentar la regla (se usa `primary_category`).
- [ ] Documentar la política de etiqueta: categoría primaria de arXiv; las categorías secundarias (cross-listing, entre 43 % y 59 % según la clase) se guardan como metadato y no se usan como etiqueta.
- [ ] Reportar la distribución de clases (125 por clase) y confirmar que no hay etiquetas vacías ni ambiguas.
- [ ] Generar `labeled_documents.tsv` con `document_id, text, label, split, categories`.

**B: base común**
- [ ] `config.py` con `RANDOM_STATE = 0` y rutas. Añadir `matplotlib` a `requirements.txt` con versión fija.
- [ ] Splits **antes de ajustar nada**: `train_test_split(shuffle=True, random_state=0, stratify=y)` dos veces (70 / 30, y el 30 en 15 / 15). Verificar que cada clase aparece en las tres particiones.
- [ ] Módulo de normalización con 3 configuraciones:

| ID | Operaciones |
|---|---|
| N0 | Solo tokenización con spaCy (sin minúsculas, conserva puntuación). Es la línea base mínima que pide el PDF |
| N1 | Tokenización + minúsculas + eliminación de puntuación y stopwords (`token.is_stop`) |
| N2 | Normalización de la Etapa I (`src/normalize.py`): minúsculas, lematización y eliminación por POS (DET, ADP, CCONJ, SCONJ, PRON, AUX) |

- [ ] Procesar los 500 textos una sola vez con `nlp.pipe` y guardarlos en `normalized_variants.tsv`. La normalización no aprende nada de los datos (es documento a documento), así que no produce fuga; aun así se aplica dentro del `Pipeline` mediante un transformador que busca el texto ya normalizado, para que dev y test pasen por el mismo camino.
- [ ] Definir el formato de `experiments.tsv` (sección 6) y la función `log_experiment()`.

**Entregable:** `labeled_documents.tsv`, splits fijados, `normalized_variants.tsv` y `experiments.tsv` vacío con encabezados.
**Criterio de aceptación:** al ejecutar dos veces se obtienen exactamente los mismos splits.

### Fase 2: Experimentos (días 2 y 3, 13-14 nov)

Las dos tareas corren en paralelo. Cada experimento es un `Pipeline` completo (vectorizador → SVD opcional → modelo) y se registra en `experiments.tsv`.

#### A: clasificación supervisada

Diseño en bloques, **un factor a la vez**. Cada bloque parte de la mejor opción del bloque anterior, para los tres clasificadores:

| Bloque | Factor que cambia | Fijo | Experimentos |
|---|---|---|---|
| C-1 | Clasificador: MultinomialNB, LogisticRegression, SVC (kernel lineal) | N2, TF-IDF (1,1) | 3 |
| C-2 | Normalización: N0, N1, N2 | TF-IDF (1,1) | 9 |
| C-3 | Representación: binaria, frecuencia, TF-IDF | mejor normalización | 9 |
| C-4 | n-gramas: (1,1), (1,2), (1,3) | mejor representación | 9 |
| C-5 | SVD: `n_components` ∈ {100, 200} | solo LR y SVC | 4 |

- [ ] Hiperparámetros con `GridSearchCV` pequeño **solo sobre train** (`StratifiedKFold(5, shuffle=True, random_state=0)`, `scoring="f1_macro"`):
  - MultinomialNB: `alpha` ∈ {0.1, 0.5, 1.0}
  - LogisticRegression: `C` ∈ {0.1, 1, 10}, `max_iter=2000`
  - SVC: `C` ∈ {0.1, 1, 10}, `kernel="linear"`
  - Vectorizador: `min_df` ∈ {1, 2}
- [ ] El mejor estimador de cada búsqueda se evalúa en dev: `classification_report`, accuracy, precisión/recall/F1 macro, métricas por clase y matriz de confusión.
- [ ] MultinomialNB **no se combina con SVD** (SVD produce valores negativos).
- [ ] Registrar también el F1 macro medio de la validación cruzada en train; con 75 documentos en dev, un documento equivale a ~1.3 puntos de accuracy, y el valor de CV ayuda a ver si una diferencia es real.

#### B: K-Means

Se ajusta solo con train y **sin etiquetas**. Las etiquetas se usan después, solo para ARI/NMI y la tabla de contingencia.

| Bloque | Factor que cambia | Fijo | Experimentos |
|---|---|---|---|
| K-1 | `n_clusters` ∈ {3, 4, 5, 6, 8} | N2, TF-IDF (1,1), SVD 100 | 5 |
| K-2 | Normalización: N0, N1, N2 | mejor k | 3 |
| K-3 | Representación: frecuencia vs TF-IDF | mejor normalización | 2 |
| K-4 | n-gramas: (1,1) vs (1,2) | mejor representación | 2 |
| K-5 | SVD: sin SVD, 50, 100, 200 | mejor configuración | 4 |
| K-6 | `init` (k-means++ vs random), `n_init` ∈ {10, 20}, `max_iter` ∈ {300, 500} | mejor configuración | 4-6 |

- [ ] Pipeline: `vectorizador → TruncatedSVD → Normalizer → KMeans(random_state=0)`, como en el script de ejemplo de `Etapa2/Unsupervised text clustering script/`.
- [ ] Silhouette con distancia coseno, calculado en train y en dev (dev se asigna con `predict`). Se declara siempre en qué espacio se calcula. El silhouette solo se compara entre configuraciones con el mismo espacio de características; entre espacios distintos se compara con cautela y junto con la interpretabilidad.
- [ ] Estabilidad: para la configuración candidata, repetir con 5 semillas y medir el ARI entre las particiones resultantes.
- [ ] Top-10 palabras por cluster **en el espacio original de palabras**: con SVD, se proyectan los centroides de vuelta con `svd.inverse_transform` (o se promedia el TF-IDF de los documentos de cada cluster).
- [ ] No se fuerza k = 4; el número de categorías es solo una referencia.

**Entregable:** `experiments.tsv` con todos los ensayos de las dos tareas.

### Fase 3: Selección y evaluación final (día 4, 15 nov)

**A: clasificación**
- [ ] Elegir la mejor configuración de cada clasificador por **macro-F1 en dev**, y la ganadora global. Anotar el criterio en `experiments.tsv` (columna `selected`).
- [ ] Revisar **10 documentos de dev mal clasificados** y explicar la causa probable: cross-listing (por ejemplo, un artículo de `cs.CL` también listado en `cs.LG`), vocabulario compartido entre `cs.CL` y `cs.LG`, abstracts genéricos sobre LLM, términos de dominio poco frecuentes.
- [ ] Reajustar **solo el mejor modelo** con train+dev y evaluar **una vez** en test.

**B: K-Means**
- [ ] Elegir la configuración por silhouette en dev, estabilidad e interpretabilidad (en ese orden de desempate, documentado).
- [ ] Reportar el tamaño de cada cluster, las 10 palabras principales y 2 documentos representativos (los más cercanos al centroide).
- [ ] Revisar clusters mixtos, diminutos o enormes.
- [ ] Reajustar con train+dev y asignar test con `predict`. Reportar silhouette en test y, como interpretación externa, ARI/NMI y tabla de contingencia contra las etiquetas.

**Entregable:** configuraciones congeladas y resultados en test.

### Fase 4: Entregables e interfaz (días 4 y 5, 15-16 nov)

**A**
- [ ] `classification_predictions.tsv`: `document_id, gold_label, predicted_label, split, model, experiment_id`. Predicciones de dev solo del mejor experimento de cada modelo; en test, `experiment_id = "test"`.
- [ ] `classification_metrics.tsv`: `experiment_id, model, split, accuracy, macro_precision, macro_recall, macro_f1`, solo dev y test, con métricas por clase y matrices de confusión en archivos aparte.
- [ ] Interfaz (CLI):

```bash
python -m src.etapa2.cli metrics                 # tabla de métricas de clasificación (dev y test)
python -m src.etapa2.cli metrics --experiment C14  # reporte por clase y matriz de confusión
python -m src.etapa2.cli clusters                # tamaños y top-10 palabras por cluster
python -m src.etapa2.cli clusters --id 2         # documentos representativos de un cluster
python -m src.etapa2.cli experiments --task classification --top 10
```

- [ ] Opcional, si queda tiempo: exponer lo mismo en la API de la Etapa I (`src/api.py`) con dos rutas nuevas.

**B**
- [ ] `clustering_results.tsv`: `document_id, split, cluster_id, configuration`.
- [ ] `cluster_summary.tsv`: `cluster_id, size, top_words, representative_document_ids`.
- [ ] `experiments.tsv` consolidado y revisado.
- [ ] `requirements.txt` con versiones fijas, semillas e instrucciones de reproducción (un comando por etapa).

### Fase 5: Informe y revisión (día 5, 16 nov)

El informe se empieza a redactar el día 2, conforme salen resultados.

- [ ] **A redacta:** tarea y corpus, política de etiquetas, splits y control de fuga, normalización, representaciones, comparación de clasificadores, ajuste de hiperparámetros, selección en dev, evaluación en test y análisis de errores.
- [ ] **B redacta:** K-Means (configuraciones, silhouette vs k, tamaños, palabras, documentos representativos, ARI/NMI como interpretación externa), limitaciones y reproducibilidad.
- [ ] Figuras mínimas: distribución de clases, macro-F1 en dev por bloque de experimentos, matriz de confusión en test, silhouette vs k.
- [ ] Tabla resumen con el formato sugerido por el PDF (tarea/método, normalización, representación, hiperparámetros, métrica en dev, notas).
- [ ] Revisión cruzada: cada quien revisa la parte del otro.
- [ ] Prueba final: clonar en limpio, instalar `requirements.txt` y reproducir todo de punta a punta.

---

## 5. Cronograma resumido

| Día | A | B |
|---|---|---|
| 1 (12 nov) | Etiquetas, distribución, `labeled_documents.tsv` | Configuración, splits, normalización N0-N2, formato de experimentos |
| 2 (13 nov) | Bloques C-1 y C-2. Empieza el informe | Bloques K-1 y K-2. Empieza el informe |
| 3 (14 nov) | Bloques C-3, C-4 y C-5 | Bloques K-3 a K-6, estabilidad |
| 4 (15 nov) | Selección, análisis de errores, test, TSV de clasificación | Selección, interpretación de clusters, test, TSV de clustering |
| 5 (16 nov) | Interfaz, cierre del informe | `experiments.tsv`, `requirements`, cierre del informe, prueba en limpio |
| 17 nov | **Entrega** | **Entrega** |

---

## 6. Formato de `experiments.tsv`

| Columna | Ejemplo |
|---|---|
| `experiment_id` | `C07`, `U03` |
| `task` | `classification` / `clustering` |
| `block` | `C-2`, `K-1` |
| `normalization` | `N2` |
| `representation` | `tfidf` |
| `ngram_range` | `(1,2)` |
| `svd_components` | `100` o vacío |
| `method` | `LogisticRegression`, `KMeans` |
| `hyperparameters` | `C=1.0; min_df=2` |
| `cv_macro_f1` | solo clasificación |
| `dev_metric` | `macro_f1=0.84` / `silhouette=0.07` |
| `extra` | ARI/NMI, tamaños de cluster |
| `selected` | `yes` / `no` |
| `notes` | motivo de la selección o del descarte |

---

## 7. Decisiones técnicas a documentar

1. **Etiqueta primaria:** `primary_category` de arXiv; las categorías secundarias se conservan como metadato y sirven para explicar errores.
2. **Normalización fuera del ajuste:** se precalcula porque no aprende de los datos; lo que sí aprende (vocabulario, IDF, SVD, modelo) va siempre dentro del `Pipeline` y se ajusta solo con train.
3. **Ajuste en train, selección en dev:** `GridSearchCV` con validación cruzada dentro de train; dev solo compara pipelines ya ajustados; test se usa una vez.
4. **Tamaño de dev:** 75 documentos; diferencias de 1-2 puntos de macro-F1 no se consideran concluyentes por sí solas.
5. **Top palabras con SVD:** se interpretan en el espacio original, no en las componentes de SVD.
6. **Silhouette:** distancia coseno, espacio declarado y comparación solo entre espacios equivalentes.
7. **Reproducibilidad:** `random_state=0` en todo, versiones fijas y versión del modelo de spaCy registrada.

---

## 8. Puntos de control

Estas reglas del PDF se revisan en cada fase y no se negocian.

- **Test se usa una sola vez**, al final. Nunca se elige nada mirando test.
- **Todo va en `Pipeline`**, para que vectorizador, SVD y modelo se ajusten solo con train.
- **K-Means no ve etiquetas** durante el ajuste.
- **Sin LLM ni modelos generativos** en el sistema.
- **Un factor a la vez** en las comparaciones por bloques.
- **El benchmark congelado de la Etapa I no se modifica**, y tampoco el corpus ni sus IDs.
- **MultinomialNB no se combina con SVD.**

---

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Solo 5 días | Búsquedas pequeñas, bloques fijos y el informe se escribe desde el día 2 |
| Dev pequeño (75 documentos) | Reportar también el F1 macro de CV en train y no sobreinterpretar diferencias pequeñas |
| Confusión entre `cs.CL` y `cs.LG` (temas de LLM) | Es material esperado para el análisis de errores; se apoya en el cross-listing |
| spaCy lento al probar variantes | Normalizar una sola vez con `nlp.pipe` y guardar la caché |
| Silhouette bajo en texto (típico 0.02-0.10) | Interpretarlo en relación con otras configuraciones y apoyarlo con palabras y documentos representativos |
| Clusters diminutos o gigantes | Revisarlos explícitamente y probar más `n_init` o otro k |
| Fuga de información | Splits antes de todo, `Pipeline` y revisión cruzada del código |
| Carga desbalanceada con 2 personas | Revisión al final de cada día y reasignar si una tarea se atrasa |

---

## 10. Preguntas abiertas para el profesor

1. ¿Es válido un equipo de 2 personas?
2. ¿El informe puede ir en español?
3. ¿Basta una CLI como interfaz, o se espera una interfaz web?
4. ¿Se acepta usar `primary_category` de arXiv como etiqueta primaria?
5. ¿El análisis de clusters debe hacerse sobre dev, test o ambos?

---

## 11. Checklist de entrega

**A: clasificación (tarea A)**
- [ ] Política de etiqueta primaria documentada y distribución de clases
- [ ] `labeled_documents.tsv`
- [ ] Experimentos de normalización, representación, n-gramas, SVD y clasificadores registrados
- [ ] Selección por macro-F1 en dev
- [ ] 10 documentos mal clasificados analizados
- [ ] Reajuste en train+dev y evaluación única en test
- [ ] `classification_predictions.tsv` y `classification_metrics.tsv` (con métricas por clase y matrices de confusión)
- [ ] Interfaz para consultar métricas y clusters

**B: K-Means y soporte**
- [ ] Splits reproducibles (70/15/15, `random_state=0`, estratificados)
- [ ] Módulo de normalización con 3 configuraciones
- [ ] Experimentos de K-Means registrados
- [ ] Clusters: tamaños, 10 palabras principales y 2 documentos representativos
- [ ] Silhouette, estabilidad y ARI/NMI como interpretación externa
- [ ] `clustering_results.tsv`
- [ ] `experiments.tsv` consolidado
- [ ] `requirements.txt` con versiones, semillas e instrucciones para reproducir

**Entre los dos**
- [ ] Informe en PDF con figuras, tablas, análisis de errores, limitaciones y nombres del equipo
- [ ] Revisión cruzada del informe y del código
- [ ] Reproducción de punta a punta en un entorno limpio

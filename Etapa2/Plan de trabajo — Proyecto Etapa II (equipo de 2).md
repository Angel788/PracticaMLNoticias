# Plan de trabajo — Proyecto Etapa II (equipo de 2)

Nov 12, 2026 · @Bren

## Antes de empezar

- **Fecha de entrega:** 17 de noviembre
- **Tarea A (clasificación supervisada):** es obligatoria.
- **Tarea opcional:** se elige una sola, K-Means (B) o LDA (C), nunca las dos.

## Decisión clave: K-Means o LDA

Se recomienda **K-Means**;

- Reutiliza TF-IDF y SVD, que ya se trabajan en la tarea A.
- Tiene una métrica clara (silhouette) y permite asignar documentos nuevos con `predict`.
- LDA es viable, pero exige `CountVectorizer`, perplexity y una evaluación más cualitativa.

En ambos casos, el número de grupos o temas no tiene que coincidir con el número de categorías de la clasificación.

## Plan por fases

Son cinco fases en 5 días, contados desde hoy (día 1 = 12 de noviembre, día 5 = 16 de noviembre). La base común va primero, las dos tareas corren en paralelo y el informe se escribe sobre la marcha. Para que quepa: búsqueda de hiperparámetros pequeña, 3 clasificadores, 3 normalizaciones y 3 representaciones, cambiando un factor a la vez.

| Fase | Persona 1 | Persona 2 |
| --- | --- | --- |
| **1. Acuerdos y base común** (día 1) | Elegir la tarea opcional junto con la Persona 2. Definir la etiqueta primaria (`primary_category` o la primera de `categories`), reportar la distribución de clases y tratar clases raras o ambiguas. Generar `labeled_documents.tsv` con `text`, `label` y `split`. | Fijar versiones de librerías, `random_state=0`, estructura del repositorio y formato del registro de experimentos. Armar el módulo de normalización con 3 configuraciones, reutilizando la Etapa I. Cuando haya etiquetas, hacer los splits 70/15/15 (`shuffle=True`, `random_state=0`, estratificado) **antes de ajustar nada**. |
| **2. Experimentos** (días 2 y 3) | **Tarea A:** 3 clasificadores (MultinomialNB, LogisticRegression, SVC), 3 normalizaciones, 3 representaciones, n-gramas y SVD. `GridSearchCV` pequeño, solo sobre train. | **Tarea opcional:** variar normalización, representación, n-gramas, SVD e hiperparámetros del método elegido. |
| **3. Selección y evaluación final** (día 4) | Elegir la mejor configuración por **macro-F1 en dev**. Revisar 10 documentos de dev mal clasificados. Reajustar **solo el mejor modelo** con train+dev y evaluar **una vez** en test. | Elegir la configuración de la tarea opcional. Reportar tamaños de cluster, 10 palabras principales y 2 documentos representativos por cluster. Evaluar en test y revisar clusters mixtos, diminutos o enormes. |
| **4. Entregables** (días 4 y 5) | Generar `classification_predictions.tsv`, `classification_metrics.tsv` y la interfaz para consultar métricas. | Generar `clustering_results.tsv` (o `topic_results.tsv`), consolidar `experiments.tsv` y dejar `requirements` con versiones y semillas. |
| **5. Informe y revisión** (día 5) | Terminar corpus, etiquetas, splits, normalización, clasificación y análisis de errores (se empieza a redactar en el día 2). | Terminar la tarea opcional, limitaciones y reproducibilidad. Cada quien revisa lo del otro y se prueba la reproducción de punta a punta. |

## Puntos de control

Estas reglas del PDF se revisan en cada fase y no se negocian.

- **Test se usa una sola vez**, al final. Nunca se elige nada mirando test.
- **Todo va en `Pipeline`**, para que vectorizador, SVD y modelo se ajusten solo con train.
- **Sin LLM ni modelos generativos** en el sistema.
- **Un factor a la vez** en varias comparaciones, para poder explicar qué mejoró, empeoró o no cambió.
- **El benchmark congelado de la Etapa I no se modifica.**
- **MultinomialNB no admite valores negativos**, así que no se combina con SVD.
- **cs.CL y cs.LG se parecen mucho** y es probable que concentren buena parte de los errores; es material para el análisis.

## Checklist y entregables

Cada persona marca lo suyo; los archivos son los que exige el PDF.

**Persona 1: clasificación (tarea A)**

- [ ] Política de etiqueta primaria documentada y distribución de clases
- [ ] `labeled_documents.tsv`
- [ ] Experimentos de normalización, representación y clasificadores registrados
- [ ] Selección por macro-F1 en dev
- [ ] 10 documentos mal clasificados analizados
- [ ] Reajuste en train+dev y evaluación única en test
- [ ] `classification_predictions.tsv` y `classification_metrics.tsv`
- [ ] Interfaz para consultar métricas

**Persona 2: tarea opcional y soporte**

- [ ] Splits reproducibles (70/15/15, `random_state=0`, estratificados)
- [ ] Módulo de normalización con 3 o más configuraciones
- [ ] Experimentos de la tarea opcional registrados
- [ ] Clusters o temas: tamaños, 10 palabras principales y 2 documentos representativos
- [ ] `clustering_results.tsv` (o `topic_results.tsv`)
- [ ] `experiments.tsv` consolidado
- [ ] `requirements` con versiones, semillas e instrucciones para reproducir

**Entre los dos**

- [ ] Informe en PDF con figuras, tablas, análisis de errores, limitaciones y nombres del equipo
- [ ] Revisión cruzada del informe y del código

# Análisis de errores en dev · C02 (LogisticRegression)

Predicciones de dev del modelo ajustado **solo con train**, antes del reajuste en train+dev. El test no participa en este análisis.

- Documentos de dev: **75**
- Errores: **15** (20.0%)
- Errores cuyo gold/pred aparecen en el cross-listing del artículo: **3 de 15** (20.0%)

## Pares de confusión

| Gold | Predicho | Documentos |
|---|---|---:|
| cs.CL | cs.IR | 3 |
| cs.CV | cs.CL | 3 |
| cs.CL | cs.LG | 2 |
| cs.LG | cs.CL | 2 |
| cs.CL | cs.CV | 1 |
| cs.CV | cs.LG | 1 |
| cs.IR | cs.LG | 1 |
| cs.LG | cs.CV | 1 |
| cs.LG | cs.IR | 1 |

## Los 10 documentos revisados

| # | document_id | Gold | Predicho | Título | Categorías secundarias | Causa probable |
|---|---|---|---|---|---|---|
| 1 | 2609.39460 | cs.CL | cs.CV | Right-Wing Rock or Just Rock? A Computational Linguistic Analysis of Frei.Wild | — | error de generalización: el abstract es de lingüística computacional, pero acumula vocabulario de evaluación de clasificadores (dataset, ROC-AUC, classifiers) y pocos términos de NLP; cs.CV no comparte tema |
| 2 | 2610.06902 | cs.CL | cs.IR | Tree Navigation Without LLM Summaries: A Matched-Cost Study of Hierarchical Retrieval for  | cs.IR | cross-listing: el artículo también está listado en cs.IR |
| 3 | 2609.39982 | cs.CL | cs.LG | Mid-Harness: Scaling Actions Between Model and Harness for Terminal Agents | cs.AI cs.MA | frontera difusa LLM/ML: comparten transformer, training, model, language |
| 4 | 2610.00825 | cs.CV | cs.CL | Align Then Reason: A Multimodal Lip-Sync Judge for Dubbing | — | visión-lenguaje/multimodal: menciona modelos de lenguaje e imágenes |
| 5 | 2609.40222 | cs.CV | cs.LG | LOCI: Spatial Linear Memory for Streaming World Models | — | world models de vídeo: mezcla atención, memoria y transformers (LG) con escenas, cámara y vídeo (CV) |
| 6 | 2609.28383 | cs.IR | cs.LG | Beyond a Scalar: Distributional Serving Interfaces for Watch-Time Prediction | — | recommendation/ranking con métodos de ML |
| 7 | 2610.00767 | cs.LG | cs.CL | Pre-training interventions, ex post facto: Grafting model beliefs across checkpoints | cs.AI cs.CL | cross-listing: el artículo también está listado en cs.CL |
| 8 | 2610.02251 | cs.LG | cs.CV | Rank-Aware Speculative Sampling for Diffusion Draft Trees | stat.CO | el artículo es de muestreo especulativo (ML), pero evalúa generación en pixel-space, FFHQ, CIFAR-10 y difusión latente: el vocabulario visual pesa |
| 9 | 2610.02249 | cs.LG | cs.IR | Nearest-neighbour baselines for fingerprint prediction from MS/MS spectra under different  | cs.CE stat.ML | usa retrieval de vecinos cercanos como método; el vocabulario de búsqueda y benchmarking pesa aunque la tarea sea predicción molecular |
| 10 | 2609.38861 | cs.CL | cs.IR | TRACE: Target-Aware Retrieval, Attributed Evidence, and Contract-Constrained Extraction fo | cs.DL cs.IR | cross-listing: el artículo también está listado en cs.IR |

## Detalle por documento

### 1. `2609.39460` · cs.CL → cs.CV

**Título:** Right-Wing Rock or Just Rock? A Computational Linguistic Analysis of Frei.Wild

**Categorías:** cs.CL

**Abstract (inicio):** Rechtsrock is a subgenre of rock music that spreads right-wing ideology, often instrumentalized to recruit adolescents into the radical scene. Monitoring institutions counteract this by manually examining and, in some cases, banning extremist content; however, there are border cases that evade regulation. We present a study aimed at determining whether such a case, the band Frei$.$Wild, should be classified as politi…

**Causa probable:** error de generalización: el abstract es de lingüística computacional, pero acumula vocabulario de evaluación de clasificadores (dataset, ROC-AUC, classifiers) y pocos términos de NLP; cs.CV no comparte tema.

### 2. `2610.06902` · cs.CL → cs.IR

**Título:** Tree Navigation Without LLM Summaries: A Matched-Cost Study of Hierarchical Retrieval for Long-Document QA

**Categorías:** cs.CL cs.IR

**Abstract (inicio):** Retrieval-augmented generation grounds language models in external context, but for long documents flat top-$k$ retrieval can cluster on a single region and miss complementary evidence. RAPTOR-style summary trees address this by recursively clustering chunks and using a language model to summarize each cluster at indexing time, then ranking summary nodes alongside raw chunks at query time. We show the main benefit of…

**Causa probable:** cross-listing: el artículo también está listado en cs.IR.

### 3. `2609.39982` · cs.CL → cs.LG

**Título:** Mid-Harness: Scaling Actions Between Model and Harness for Terminal Agents

**Categorías:** cs.CL cs.AI cs.MA

**Abstract (inicio):** Terminal agents act through stochastic model generations, yet the ability to generate a useful action does not ensure its reliable execution. A poor command (e.g., wrong package install) can change the environment in ways that hinder subsequent progress, even when the model could generate a better alternative. We investigate whether allocating test-time compute at the model-harness boundary can improve action reliabi…

**Causa probable:** frontera difusa LLM/ML: comparten transformer, training, model, language.

### 4. `2610.00825` · cs.CV → cs.CL

**Título:** Align Then Reason: A Multimodal Lip-Sync Judge for Dubbing

**Categorías:** cs.CV

**Abstract (inicio):** Dubbing quality control requires a reference-free judge that can determine whether a candidate text line matches a speaker's visible articulation in both content and timing, using only silent video and text because dubbed audio may not yet exist. Existing visual speech recognizers and video-language models are poorly suited to this setting: even when fine-tuned to recover spoken content from lip motion, they remain l…

**Causa probable:** visión-lenguaje/multimodal: menciona modelos de lenguaje e imágenes.

### 5. `2609.40222` · cs.CV → cs.LG

**Título:** LOCI: Spatial Linear Memory for Streaming World Models

**Categorías:** cs.CV

**Abstract (inicio):** When a camera revisits a previously observed region, a video world model should reproduce what was there before. This requires both remembering past observations and retrieving the right one for the current viewpoint. Key-value caches preserve visual detail but grow with video length; recurrent memory is compact but compresses history into a fixed-size state, so individual past observations are no longer directly acc…

**Causa probable:** world models de vídeo: mezcla atención, memoria y transformers (LG) con escenas, cámara y vídeo (CV).

### 6. `2609.28383` · cs.IR → cs.LG

**Título:** Beyond a Scalar: Distributional Serving Interfaces for Watch-Time Prediction

**Categorías:** cs.IR

**Abstract (inicio):** Watch time is the primary engagement signal in short video feeds, and its prediction directly affects ranking and exposure. Existing methods improve watch time prediction by correcting duration bias or modeling richer distributions, but most expose only an expected or debiased watch time at serving time. Even when video duration is available to later models, the interface gives only one estimate of watch time and no …

**Causa probable:** recommendation/ranking con métodos de ML.

### 7. `2610.00767` · cs.LG → cs.CL

**Título:** Pre-training interventions, ex post facto: Grafting model beliefs across checkpoints

**Categorías:** cs.LG cs.AI cs.CL

**Abstract (inicio):** Pre-training interventions are critical to alignment research, since beliefs formed during pre-training shape how a model generalizes from later training. One recently popular technique for such interventions is synthetic document fine-tuning (SDF), which aims to alter what the model believes. Ideally, synthetic documents would be mixed into pre- or mid-training, but every change to a pre-training corpus must be foll…

**Causa probable:** cross-listing: el artículo también está listado en cs.CL.

### 8. `2610.02251` · cs.LG → cs.CV

**Título:** Rank-Aware Speculative Sampling for Diffusion Draft Trees

**Categorías:** cs.LG stat.CO

**Abstract (inicio):** Speculative sampling accelerates diffusion generation by verifying inexpensive draft states in parallel while preserving the target law. Recent tree-based methods allocate the parallel compute budget more effectively than single-chain drafts, as demonstrated by Diffusion Greedy Rejection Sampling (D-GRS). D-GRS generates $K$ conditionally independent candidates per node, and sequentially tests them in their generatio…

**Causa probable:** el artículo es de muestreo especulativo (ML), pero evalúa generación en pixel-space, FFHQ, CIFAR-10 y difusión latente: el vocabulario visual pesa.

### 9. `2610.02249` · cs.LG → cs.IR

**Título:** Nearest-neighbour baselines for fingerprint prediction from MS/MS spectra under different assumptions

**Categorías:** cs.LG cs.CE stat.ML

**Abstract (inicio):** It has recently been shown that nearest-neighbour retrieval provides a strong baseline for molecular fingerprint prediction from MS/MS spectra, with several variants matching or outperforming current deep learning models (Khoo and Barzilay, 2026; Liu et al., 2026; Gupta et al., 2026). Importantly, "nearest neighbour" encompasses a family of retrieval methods that differ in the information assumed to be available at i…

**Causa probable:** usa retrieval de vecinos cercanos como método; el vocabulario de búsqueda y benchmarking pesa aunque la tarea sea predicción molecular.

### 10. `2609.38861` · cs.CL → cs.IR

**Título:** TRACE: Target-Aware Retrieval, Attributed Evidence, and Contract-Constrained Extraction for LitTraceQA

**Categorías:** cs.CL cs.DL cs.IR

**Abstract (inicio):** Finding a relevant paper is not the same as producing a verifiable answer from it. LitTraceQA requires canonical paper identifiers, exact evidence at the page or object level, and typed answers that match the evaluator. We call the separation between source access and scorer-visible correctness the grounding contract gap. TRACE - Target-Aware Retrieval, Attributed Evidence, and Contract-Constrained Extraction - addre…

**Causa probable:** cross-listing: el artículo también está listado en cs.IR.


## Lectura

- Solo **3 de 15** errores (20%) tienen la clase predicha dentro del cross-listing del artículo; la mayor parte se explica por solapamiento de vocabulario, no por la etiqueta secundaria.
- Los pares más frecuentes son `cs.CL → cs.IR` (3), `cs.CV → cs.CL` (3) y la frontera `cs.CL ↔ cs.LG` (4 en total).
- Varios documentos están listados en la categoría que el modelo predice; la etiqueta primaria es una convención de arXiv, no una frontera semántica.
- El modelo se apoya en el vocabulario temático del abstract. Cuando un artículo de NLP usa recuperación o un artículo de IR usa un LLM, los términos de ambas áreas aparecen juntos y la decisión es ambigua.
- Estos errores son esperables con un corpus de 500 documentos y 4 clases; el objetivo es documentarlos, no eliminarlos con test.

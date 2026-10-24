# Análisis por consulta (Q01–Q15) en las 12 configuraciones

Índice: [README.md](README.md)

Términos que quedan de la consulta tras normalizar y que existen en el vocabulario de cada modelo
(determinan directamente el resultado):

| Consulta | Normalizada | Términos útiles en `title · bigram` | Términos útiles en `abstract · bigram` |
| :--- | :--- | :--- | :--- |
| Q03 | reranke retrieve document large language model | large language, language model | retrieve document, large language, language model |
| Q09 | large language model judge evaluation | large language, language model | large language, language model |
| Q12 | ai read hospital scan to detect illness | — (vacía) | to detect |
| Q13 | defend ai system malicious manipulation | — (vacía) | ai system |
| Q15 | assistant remember past experience | — (vacía) | remember past, past experience |

### Nivel 1 — Fácil

- **Q01 *sequential recommendation with user behavior sequences*** (máx 0.81, `A-Bi-TfIdf`).
  Funciona en todas las configuraciones (RR = 1 en las 12). Los bigramas del abstract capturan la
  expresión fija *sequential recommendation*; `abstract · unigram · frequency` es la peor (0.39) porque
  *user* y *sequence* son frecuentes en muchos abstracts de otros temas.
- **Q02 *long video understanding with vision-language models*** (máx 0.82, `A-Bi-TfIdf`).
  Muy sensible a la representación: en `abstract · bigram` pasa de 0.23 (binary) a 0.82 (tfidf). El
  bigrama *language model* aparece en casi todo el corpus; sin IDF arrastra al ranking documentos de
  LLM sin vídeo.
- **Q03 *reranking retrieved documents with large language models*** (máx 0.46, `A-Uni-TfIdf`).
  La peor consulta fácil: nDCG = 0 en 10 de las 12 configuraciones. El lematizador convierte
  *reranking* en `reranke`, que solo existe en el vocabulario de `abstract · unigram`; en el resto la
  consulta se reduce a *document / large language model* y recupera artículos genéricos de LLM. Solo
  `abstract · unigram` con `binary` o `tfidf` encuentra relevantes (RR = 1).
- **Q04 *video generation with diffusion models*** (máx 0.73, `T-Bi-Fr/Bin`).
  Estable (0.47–0.73). Mejor en `title`: los artículos de generación de vídeo lo dicen en el título.
- **Q05 *retrieval-augmented generation for multi-hop question answering*** (máx 0.67, `T-Uni-TfIdf`).
  Mejor en `title`. En `abstract · unigram` el MRR cae a 0.25–0.33: *generation*, *question* y
  *answer* son demasiado comunes en los abstracts.

### Nivel 2 — Media

- **Q06 *on-policy self-distillation for reasoning models*** (máx 0.84, `T-Uni-TfIdf`).
  El título es el campo adecuado (0.68–0.84). En `abstract · unigram · frequency` cae a 0.21: *model*
  y *policy* se repiten en muchos abstracts de RL y LLM.
- **Q07 *parameter-efficient fine-tuning with low-rank adapters*** (máx 0.74, `A-Bi-TfIdf`).
  La consulta con mayor diferencia entre campos: `title` ≤ 0.29 y `abstract` 0.50–0.74. Probablemente
  los títulos usan el nombre del método (p. ej. *LoRA*) y el abstract lo explica con las palabras de
  la consulta. `adapter` ni siquiera está en el vocabulario de títulos.
- **Q08 *policy optimization in reinforcement learning*** (máx 0.81, varias `title`).
  La consulta más fácil del benchmark (media 0.73, RR = 1 en las 12 configuraciones). Las expresiones
  *policy optimization* y *reinforcement learning* son exactas y frecuentes en títulos.
- **Q09 *large language models as judges for evaluation*** (máx 0.79, `A-Uni-TfIdf`).
  nDCG = 0 en 9 de 12. Con bigramas, *model judge* y *judge evaluation* no existen en el vocabulario y
  la consulta queda en *large language model*, que coincide con medio corpus. Con `title · unigram`
  tampoco basta. Solo `abstract · unigram · tfidf` funciona bien: el IDF da peso a *judge*, que es el
  término discriminativo; con `frequency`/`binary` ese peso se diluye (0.26–0.34).
- **Q10 *multilingual language models for low-resource languages*** (máx 0.73, `A-Uni-TfIdf`).
  Mejor en `abstract · unigram`. En `title · bigram` (frequency/binary) da 0: los bigramas útiles son
  *language model* y *low resource*, y el primero domina sin IDF.

### Nivel 3 — Difícil

- **Q11 *making neural networks smaller and faster*** (máx 0.25, todas las `title`).
  Curioso: las seis configuraciones de `title` dan exactamente 0.254 (un relevante en la posición 1)
  y las seis de `abstract` dan ≈ 0. El único término común es *neural network*; el abstract no tiene
  el vocabulario técnico (*quantization*, *pruning*, *compression*) que usan los relevantes.
- **Q12 *AI reading hospital scans to detect illness*** (máx 0.08, `T-Uni-TfIdf`).
  La peor consulta: 0 en 11 de 12 configuraciones. En `title · bigram` la consulta queda vacía; en el
  resto solo coinciden términos vacíos de significado (*ai*, *read*, *to*). Nota: `to` sobrevive a la
  normalización y genera el bigrama `to detect`, sin valor temático.
- **Q13 *defending AI systems against malicious manipulation*** (máx 0.32, `T-Uni-Bin`).
  Solo funciona con unigramas; en bigramas se reduce a *ai system* (abstract) o queda vacía (title).
  En `title · unigram` alcanza RR = 1 (términos *malicious*, *manipulation*, *system*).
- **Q14 *peeking inside language models to explain their behavior*** (máx 0.19, `A-Bi-Fr`).
  Siempre por debajo de 0.2. La consulta se reduce a *language model / explain / behavior*; los
  relevantes hablan de *interpretability* y *probing*, que no aparecen en la consulta.
- **Q15 *assistants that remember past experiences*** (máx 0.35, `A-Uni-Bin`).
  El abstract con unigramas es claramente mejor (0.32–0.35, RR = 1): *remember* y *experience*
  aparecen en abstracts sobre memoria de agentes. En títulos solo queda *experience* (unigram) o nada
  (bigram).


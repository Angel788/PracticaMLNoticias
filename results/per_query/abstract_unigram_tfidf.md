# Métricas por consulta · `abstract · unigram · tfidf`

Datos: [`abstract_unigram_tfidf.tsv`](abstract_unigram_tfidf.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.472 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.700 | 0.467 | 0.560 | 1.000 | 0.748 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.300 | 0.200 | 0.240 | 1.000 | 0.463 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.565 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.500 | 0.333 | 0.400 | 0.250 | 0.292 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.400 | 0.308 | 0.348 | 1.000 | 0.335 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.501 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.510 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.700 | 0.467 | 0.560 | 1.000 | 0.790 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.727 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.100 | 0.071 | 0.083 | 0.500 | 0.145 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.322 |
| *Promedio fácil* | | | | 0.500 | 0.333 | 0.400 | 0.850 | 0.508 |
| *Promedio media* | | | | 0.520 | 0.355 | 0.422 | 1.000 | 0.573 |
| *Promedio difícil* | | | | 0.120 | 0.081 | 0.097 | 0.300 | 0.093 |
| **Promedio global** | | | | **0.380** | **0.256** | **0.306** | **0.717** | **0.391** |

Mejor consulta: Q09 (nDCG@10 = 0.790). Consultas con nDCG@10 = 0: Q11, Q12, Q14.

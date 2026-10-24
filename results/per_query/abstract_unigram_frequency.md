# Métricas por consulta · `abstract · unigram · frequency`

Datos: [`abstract_unigram_frequency.tsv`](abstract_unigram_frequency.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.393 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.533 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.671 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.400 | 0.267 | 0.320 | 0.333 | 0.302 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.300 | 0.231 | 0.261 | 0.500 | 0.213 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.549 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.620 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.400 | 0.267 | 0.320 | 0.250 | 0.262 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.620 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.320 |
| *Promedio fácil* | | | | 0.360 | 0.240 | 0.288 | 0.667 | 0.380 |
| *Promedio media* | | | | 0.440 | 0.299 | 0.356 | 0.750 | 0.453 |
| *Promedio difícil* | | | | 0.100 | 0.067 | 0.080 | 0.200 | 0.064 |
| **Promedio global** | | | | **0.300** | **0.202** | **0.241** | **0.539** | **0.299** |

Mejor consulta: Q04 (nDCG@10 = 0.671). Consultas con nDCG@10 = 0: Q03, Q11, Q12, Q13, Q14.

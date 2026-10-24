# Métricas por consulta · `abstract · unigram · binary`

Datos: [`abstract_unigram_binary.tsv`](abstract_unigram_binary.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.800 | 0.533 | 0.640 | 1.000 | 0.673 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.422 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.300 | 0.200 | 0.240 | 1.000 | 0.345 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.708 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.700 | 0.467 | 0.560 | 0.333 | 0.481 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.600 | 0.462 | 0.522 | 1.000 | 0.663 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.532 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.700 | 0.467 | 0.560 | 1.000 | 0.707 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.200 | 0.133 | 0.160 | 1.000 | 0.344 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.675 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.100 | 0.067 | 0.080 | 0.125 | 0.080 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.200 | 0.143 | 0.167 | 0.500 | 0.222 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.100 | 0.067 | 0.080 | 0.500 | 0.139 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.353 |
| *Promedio fácil* | | | | 0.600 | 0.400 | 0.480 | 0.867 | 0.526 |
| *Promedio media* | | | | 0.500 | 0.346 | 0.408 | 1.000 | 0.584 |
| *Promedio difícil* | | | | 0.180 | 0.122 | 0.145 | 0.425 | 0.159 |
| **Promedio global** | | | | **0.427** | **0.289** | **0.345** | **0.764** | **0.423** |

Mejor consulta: Q04 (nDCG@10 = 0.708). Consultas con nDCG@10 = 0: Q12.

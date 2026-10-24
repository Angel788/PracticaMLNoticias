# Métricas por consulta · `abstract · bigram · tfidf`

Datos: [`abstract_bigram_tfidf.tsv`](abstract_bigram_tfidf.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.900 | 0.600 | 0.720 | 1.000 | 0.808 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.900 | 0.600 | 0.720 | 1.000 | 0.824 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.481 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.700 | 0.467 | 0.560 | 1.000 | 0.556 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.500 | 0.385 | 0.435 | 1.000 | 0.648 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.739 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.700 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.554 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.100 | 0.067 | 0.080 | 0.250 | 0.032 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.100 | 0.067 | 0.080 | 0.500 | 0.048 |
| *Promedio fácil* | | | | 0.580 | 0.387 | 0.464 | 0.800 | 0.534 |
| *Promedio media* | | | | 0.420 | 0.290 | 0.343 | 0.800 | 0.528 |
| *Promedio difícil* | | | | 0.040 | 0.027 | 0.032 | 0.150 | 0.016 |
| **Promedio global** | | | | **0.347** | **0.235** | **0.280** | **0.583** | **0.359** |

Mejor consulta: Q02 (nDCG@10 = 0.824). Consultas con nDCG@10 = 0: Q03, Q09, Q11, Q12, Q13.

---

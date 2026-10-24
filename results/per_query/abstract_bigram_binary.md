# Métricas por consulta · `abstract · bigram · binary`

Datos: [`abstract_bigram_binary.tsv`](abstract_bigram_binary.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.800 | 0.533 | 0.640 | 1.000 | 0.777 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.100 | 0.067 | 0.080 | 1.000 | 0.230 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.500 | 0.333 | 0.400 | 1.000 | 0.518 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.700 | 0.467 | 0.560 | 1.000 | 0.504 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.500 | 0.385 | 0.435 | 1.000 | 0.645 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.675 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.716 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.200 | 0.133 | 0.160 | 1.000 | 0.330 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.100 | 0.067 | 0.080 | 0.333 | 0.037 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.100 | 0.067 | 0.080 | 0.500 | 0.048 |
| *Promedio fácil* | | | | 0.420 | 0.280 | 0.336 | 0.800 | 0.406 |
| *Promedio media* | | | | 0.380 | 0.264 | 0.311 | 0.800 | 0.473 |
| *Promedio difícil* | | | | 0.040 | 0.027 | 0.032 | 0.167 | 0.017 |
| **Promedio global** | | | | **0.280** | **0.190** | **0.226** | **0.589** | **0.299** |

Mejor consulta: Q01 (nDCG@10 = 0.777). Consultas con nDCG@10 = 0: Q03, Q09, Q11, Q12, Q13.

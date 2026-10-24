# Métricas por consulta · `title · unigram · tfidf`

Datos: [`title_unigram_tfidf.tsv`](title_unigram_tfidf.tsv) · Índice: [README.md](README.md) · Análisis: [analisis_por_consulta.md](analisis_por_consulta.md)

k = 10. En las filas de promedio, la columna RR es el MRR. "Rel." es el número de documentos relevantes en qrels.

| Consulta | Nivel | Texto | Rel. | P@10 | R@10 | F1@10 | RR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | Fácil | sequential recommendation with user behavior sequences | 15 | 0.800 | 0.533 | 0.640 | 1.000 | 0.755 |
| Q02 | Fácil | long video understanding with vision-language models | 15 | 0.400 | 0.267 | 0.320 | 1.000 | 0.503 |
| Q03 | Fácil | reranking retrieved documents with large language models | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q04 | Fácil | video generation with diffusion models | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.672 |
| Q05 | Fácil | retrieval-augmented generation for multi-hop question answering | 15 | 0.600 | 0.400 | 0.480 | 1.000 | 0.667 |
| Q06 | Media | on-policy self-distillation for reasoning models | 13 | 0.900 | 0.692 | 0.783 | 1.000 | 0.843 |
| Q07 | Media | parameter-efficient fine-tuning with low-rank adapters | 15 | 0.100 | 0.067 | 0.080 | 0.250 | 0.124 |
| Q08 | Media | policy optimization in reinforcement learning | 15 | 0.800 | 0.533 | 0.640 | 1.000 | 0.804 |
| Q09 | Media | large language models as judges for evaluation | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q10 | Media | multilingual language models for low-resource languages | 15 | 0.300 | 0.200 | 0.240 | 1.000 | 0.469 |
| Q11 | Difícil | making neural networks smaller and faster | 15 | 0.100 | 0.067 | 0.080 | 1.000 | 0.254 |
| Q12 | Difícil | AI reading hospital scans to detect illness | 11 | 0.100 | 0.091 | 0.095 | 0.111 | 0.081 |
| Q13 | Difícil | defending AI systems against malicious manipulation | 14 | 0.200 | 0.143 | 0.167 | 1.000 | 0.296 |
| Q14 | Difícil | peeking inside language models to explain their behavior | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q15 | Difícil | assistants that remember past experiences | 15 | 0.200 | 0.133 | 0.160 | 0.500 | 0.183 |
| *Promedio fácil* | | | | 0.480 | 0.320 | 0.384 | 0.800 | 0.519 |
| *Promedio media* | | | | 0.420 | 0.298 | 0.349 | 0.650 | 0.448 |
| *Promedio difícil* | | | | 0.120 | 0.087 | 0.100 | 0.522 | 0.163 |
| **Promedio global** | | | | **0.340** | **0.235** | **0.278** | **0.657** | **0.377** |

Mejor consulta: Q06 (nDCG@10 = 0.843). Consultas con nDCG@10 = 0: Q03, Q09, Q14.

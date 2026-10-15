# Representación de frecuencia

- Generado: 2026-10-15 23:05 UTC
- scikit-learn 1.9.1, `CountVectorizer`
- Parámetros: `lowercase=False`, `token_pattern=r"\S+"`, `binary=False`, sin `min_df`/`max_df`
- Matriz guardada sin normalizar (conteos crudos); la similitud coseno normaliza filas en la Fase 4
- Entrada: `data/scientific_normalized_corpus.tsv` (500 documentos)
- Modelos: `models/{campo}_{ngrama}_frequency.pkl`

## Vocabulario y dispersión
| config                     |   documentos |   vocabulario |   no_ceros |   densidad_% |   dispersion_% |   terminos_por_doc |   tokens_por_doc |   conteo_max |   celdas_>1_% |   docs_sin_terminos |
|:---------------------------|-------------:|--------------:|-----------:|-------------:|---------------:|-------------------:|-----------------:|-------------:|--------------:|--------------------:|
| title_unigram_frequency    |          500 |          1863 |       4262 |        0.458 |         99.542 |                8.5 |              8.7 |            3 |          1.64 |                   0 |
| title_bigram_frequency     |          500 |          3545 |       3830 |        0.216 |         99.784 |                7.7 |              7.7 |            2 |          0.16 |                   0 |
| abstract_unigram_frequency |          500 |          7958 |      52894 |        1.329 |         98.671 |              105.8 |            147.1 |           28 |         21.99 |                   0 |
| abstract_bigram_frequency  |          500 |         60073 |      69949 |        0.233 |         99.767 |              139.9 |            146.1 |           12 |          3.48 |                   0 |

- `tokens_por_doc`: n-gramas por documento (suma de la fila).
- `celdas_>1_%`: celdas no nulas con conteo > 1, donde la frecuencia difiere de la binaria.

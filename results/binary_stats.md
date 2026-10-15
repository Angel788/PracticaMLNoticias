# Representación binaria

- Generado: 2026-10-15 23:00 UTC
- scikit-learn 1.9.1, `CountVectorizer(binary=True)`
- Parámetros: `lowercase=False`, `token_pattern=r"\S+"`, `binary=True`, sin `min_df`/`max_df`
- Matriz guardada sin normalizar (valores 0/1); la similitud coseno normaliza filas en la Fase 4
- Entrada: `data/scientific_normalized_corpus.tsv` (500 documentos)
- Modelos: `models/{campo}_{ngrama}_binary.pkl`

## Vocabulario y dispersión
| config                  |   documentos |   vocabulario |   no_ceros |   densidad_% |   dispersion_% |   terminos_por_doc |   docs_sin_terminos |
|:------------------------|-------------:|--------------:|-----------:|-------------:|---------------:|-------------------:|--------------------:|
| title_unigram_binary    |          500 |          1863 |       4262 |        0.458 |         99.542 |                8.5 |                   0 |
| title_bigram_binary     |          500 |          3545 |       3830 |        0.216 |         99.784 |                7.7 |                   0 |
| abstract_unigram_binary |          500 |          7958 |      52894 |        1.329 |         98.671 |              105.8 |                   0 |
| abstract_bigram_binary  |          500 |         60073 |      69949 |        0.233 |         99.767 |              139.9 |                   0 |

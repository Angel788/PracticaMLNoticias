# Representación TF-IDF

- Generado: 2026-10-14 02:43 UTC
- scikit-learn 1.9.1, `TfidfVectorizer`
- Parámetros: `lowercase=False`, `token_pattern=r"\S+"`, `norm="l2"`, `smooth_idf=True`, `sublinear_tf=False`, sin `min_df`/`max_df`
- Entrada: `data/scientific_normalized_corpus.tsv` (500 documentos)
- Modelos: `models/{campo}_{ngrama}_tfidf.pkl`

## Vocabulario y dispersión
| config                 |   documentos |   vocabulario |   no_ceros |   densidad_% |   dispersion_% |   terminos_por_doc |   docs_sin_terminos |
|:-----------------------|-------------:|--------------:|-----------:|-------------:|---------------:|-------------------:|--------------------:|
| title_unigram_tfidf    |          500 |          1863 |       4262 |        0.458 |         99.542 |                8.5 |                   0 |
| title_bigram_tfidf     |          500 |          3545 |       3830 |        0.216 |         99.784 |                7.7 |                   0 |
| abstract_unigram_tfidf |          500 |          7958 |      52894 |        1.329 |         98.671 |              105.8 |                   0 |
| abstract_bigram_tfidf  |          500 |         60073 |      69949 |        0.233 |         99.767 |              139.9 |                   0 |

# Normalización del corpus

- Generado: 2026-10-11 22:56 UTC
- spaCy 3.8.16, modelo `core_web_sm` 3.8.0
- POS eliminadas: ADP, CCONJ, DET, PRON, SCONJ; también puntuación y espacios
- Lematización + minúsculas
- Documentos: 500

## Reducción de tokens
|          |   tokens_antes |   tokens_despues |   reduccion_% |
|:---------|---------------:|-----------------:|--------------:|
| title    |           5417 |             4377 |          19.2 |
| abstract |         103630 |            75535 |          27.1 |

## Reducción en abstracts por categoría
| primary_category   |   tokens_abstract_antes |   tokens_abstract_despues |   reduccion_% |
|:-------------------|------------------------:|--------------------------:|--------------:|
| cs.CL              |                   25303 |                     18361 |          27.4 |
| cs.CV              |                   26274 |                     19337 |          26.4 |
| cs.IR              |                   26624 |                     19494 |          26.8 |
| cs.LG              |                   25429 |                     18343 |          27.9 |

## Tamaño de vocabulario
|               |   vocabulario |
|:--------------|--------------:|
| title_norm    |          1868 |
| abstract_norm |          7974 |

## Palabras eliminadas más frecuentes
| lema   |   veces |
|:-------|--------:|
| the    |    3638 |
| and    |    3427 |
| a      |    2563 |
| of     |    1636 |
| we     |    1142 |
| on     |    1141 |
| in     |    1127 |
| for    |    1111 |
| that   |    1081 |
| with   |     967 |
| to     |     858 |
| from   |     645 |
| this   |     574 |
| by     |     572 |
| an     |     481 |
| as     |     465 |
| across |     448 |
| at     |     395 |
| while  |     390 |
| it     |     321 |

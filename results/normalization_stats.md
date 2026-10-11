# Normalización del corpus

- Generado: 2026-10-11 23:10 UTC
- spaCy 3.8.16, modelo `core_web_sm` 3.8.0
- POS eliminadas: ADP, AUX, CCONJ, DET, PRON, SCONJ; también puntuación y espacios
- Lematización + minúsculas
- Documentos: 500

## Reducción de tokens
|          |   tokens_antes |   tokens_despues |   reduccion_% |
|:---------|---------------:|-----------------:|--------------:|
| title    |           5417 |             4336 |            20 |
| abstract |         103630 |            73532 |            29 |

## Reducción en abstracts por categoría
| primary_category   |   tokens_abstract_antes |   tokens_abstract_despues |   reduccion_% |
|:-------------------|------------------------:|--------------------------:|--------------:|
| cs.CL              |                   25303 |                     17833 |          29.5 |
| cs.CV              |                   26274 |                     18895 |          28.1 |
| cs.IR              |                   26624 |                     19001 |          28.6 |
| cs.LG              |                   25429 |                     17803 |          30   |

## Tamaño de vocabulario
|               |   vocabulario |
|:--------------|--------------:|
| title_norm    |          1863 |
| abstract_norm |          7958 |

## Palabras eliminadas más frecuentes
| lema   |   veces |
|:-------|--------:|
| the    |    3638 |
| and    |    3427 |
| a      |    2563 |
| of     |    1636 |
| be     |    1219 |
| we     |    1142 |
| on     |    1141 |
| in     |    1127 |
| for    |    1111 |
| that   |    1081 |
| with   |     967 |
| to     |     866 |
| from   |     645 |
| this   |     574 |
| by     |     572 |
| an     |     481 |
| as     |     465 |
| across |     448 |
| at     |     395 |
| while  |     390 |

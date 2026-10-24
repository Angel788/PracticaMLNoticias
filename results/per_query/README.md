# Evaluación por consulta de las 12 configuraciones del VSM

**Benchmark:** 15 consultas (5 fáciles, 5 medias, 5 difíciles), 218 juicios de relevancia (`data/benchmark/qrels.tsv`)
**Profundidad:** k = 10 · **Métricas:** P@10, R@10, F1@10, RR (MRR en los promedios), nDCG@10 (ganancia 2^rel − 1)
**Datos:** un `.tsv` por configuración en esta carpeta (15 filas cada uno), generados por `--all`

Reproducir desde la raíz del repositorio:

```bash
.venv/bin/python -m src.evaluate --all --force
```

> El tag `benchmark-v1` no existe en el repositorio, así que se usó `--force`. Las consultas y qrels
> son los del commit `553e1c1` ("Benchmark v1: 15 consultas y qrels") y no se modificaron. Los
> promedios globales coinciden exactamente con `results/metrics_all_configs.tsv`.

Esta carpeta complementa `results/error_analysis.md`: aquel compara las configuraciones con
promedios; aquí se muestra cómo se comporta **cada consulta** en **cada configuración**.

---

## 1. Diseño experimental

Se evaluaron los 2 × 2 × 3 = 12 combinaciones de:

| Parámetro | Valores |
| :--- | :--- |
| Campo indexado | `title`, `abstract` |
| N-gramas | `unigram` (1,1), `bigram` (2,2) |
| Representación | `frequency` (conteo), `binary` (presencia/ausencia), `tfidf` |

En todas se usa similitud coseno (vectores con norma L2) y la consulta pasa por la misma
normalización que el corpus (spaCy: lematización y eliminación de stopwords). Si ningún término de
la consulta normalizada está en el vocabulario del modelo, el ranking queda vacío y todas las
métricas valen 0.

---

## 2. Vista rápida: nDCG@10 por consulta y configuración

Abreviaturas: **T**/**A** = title/abstract · **Uni**/**Bi** = unigram/bigram ·
**Fr**/**Bin**/**TfIdf** = frequency/binary/tfidf. En negrita, el mejor valor de cada consulta.

| Consulta | T-Uni-Fr | T-Uni-Bin | T-Uni-TfIdf | T-Bi-Fr | T-Bi-Bin | T-Bi-TfIdf | A-Uni-Fr | A-Uni-Bin | A-Uni-TfIdf | A-Bi-Fr | A-Bi-Bin | A-Bi-TfIdf | Máx | Media |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Q01 | 0.71 | 0.71 | 0.75 | 0.61 | 0.61 | 0.52 | 0.39 | 0.67 | 0.47 | 0.79 | 0.78 | **0.81** | 0.81 | 0.65 |
| Q02 | 0.32 | 0.30 | 0.50 | 0.10 | 0.10 | 0.56 | 0.53 | 0.42 | 0.75 | 0.58 | 0.23 | **0.82** | 0.82 | 0.43 |
| Q03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | **0.46** | 0.00 | 0.00 | 0.00 | 0.46 | 0.07 |
| Q04 | 0.70 | 0.71 | 0.67 | **0.73** | **0.73** | 0.58 | 0.67 | 0.71 | 0.56 | 0.47 | 0.52 | 0.48 | 0.73 | 0.63 |
| Q05 | 0.59 | 0.61 | **0.67** | 0.59 | 0.59 | 0.55 | 0.30 | 0.48 | 0.29 | 0.45 | 0.50 | 0.56 | 0.67 | 0.52 |
| Q06 | 0.72 | 0.79 | **0.84** | 0.76 | 0.76 | 0.68 | 0.21 | 0.66 | 0.33 | 0.65 | 0.64 | 0.65 | 0.84 | 0.64 |
| Q07 | 0.14 | 0.18 | 0.12 | 0.29 | 0.29 | 0.29 | 0.55 | 0.53 | 0.50 | 0.72 | 0.68 | **0.74** | 0.74 | 0.42 |
| Q08 | 0.77 | 0.77 | 0.80 | **0.81** | **0.81** | **0.81** | 0.62 | 0.71 | 0.51 | 0.71 | 0.72 | 0.70 | 0.81 | 0.73 |
| Q09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.34 | **0.79** | 0.00 | 0.00 | 0.00 | 0.79 | 0.12 |
| Q10 | 0.22 | 0.31 | 0.47 | 0.00 | 0.00 | 0.36 | 0.62 | 0.68 | **0.73** | 0.36 | 0.33 | 0.55 | 0.73 | 0.38 |
| Q11 | **0.25** | **0.25** | **0.25** | **0.25** | **0.25** | **0.25** | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.13 |
| Q12 | 0.00 | 0.00 | **0.08** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.01 |
| Q13 | 0.31 | **0.32** | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.22 | 0.14 | 0.00 | 0.00 | 0.00 | 0.32 | 0.11 |
| Q14 | 0.07 | 0.10 | 0.00 | 0.10 | 0.10 | 0.12 | 0.00 | 0.14 | 0.00 | **0.19** | 0.04 | 0.03 | 0.19 | 0.07 |
| Q15 | 0.18 | 0.18 | 0.18 | 0.00 | 0.00 | 0.00 | 0.32 | **0.35** | 0.32 | 0.05 | 0.05 | 0.05 | 0.35 | 0.14 |

Ninguna configuración es la mejor en la mayoría de las consultas: contando empates, el máximo se
reparte entre 10 de las 12 (solo `abstract · bigram · binary` y `abstract · unigram · frequency` no
ganan ninguna). `title · unigram · tfidf` es la mejor en 4 consultas (Q05, Q06, Q11, Q12),
`abstract · unigram · tfidf` en 3 (Q03, Q09, Q10) y `abstract · bigram · tfidf` en 3 (Q01, Q02, Q07).
La columna **Máx** es una cota de lo que lograría un sistema que eligiera la configuración ideal para
cada consulta: media de 0.57 frente a 0.42 de la mejor configuración fija.

---

## 3. Archivos por configuración

| # | Campo | N-grama | Representación | Tabla | Datos |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `title` | `unigram` | `frequency` | [title_unigram_frequency.md](title_unigram_frequency.md) | [title_unigram_frequency.tsv](title_unigram_frequency.tsv) |
| 2 | `title` | `unigram` | `binary` | [title_unigram_binary.md](title_unigram_binary.md) | [title_unigram_binary.tsv](title_unigram_binary.tsv) |
| 3 | `title` | `unigram` | `tfidf` | [title_unigram_tfidf.md](title_unigram_tfidf.md) | [title_unigram_tfidf.tsv](title_unigram_tfidf.tsv) |
| 4 | `title` | `bigram` | `frequency` | [title_bigram_frequency.md](title_bigram_frequency.md) | [title_bigram_frequency.tsv](title_bigram_frequency.tsv) |
| 5 | `title` | `bigram` | `binary` | [title_bigram_binary.md](title_bigram_binary.md) | [title_bigram_binary.tsv](title_bigram_binary.tsv) |
| 6 | `title` | `bigram` | `tfidf` | [title_bigram_tfidf.md](title_bigram_tfidf.md) | [title_bigram_tfidf.tsv](title_bigram_tfidf.tsv) |
| 7 | `abstract` | `unigram` | `frequency` | [abstract_unigram_frequency.md](abstract_unigram_frequency.md) | [abstract_unigram_frequency.tsv](abstract_unigram_frequency.tsv) |
| 8 | `abstract` | `unigram` | `binary` | [abstract_unigram_binary.md](abstract_unigram_binary.md) | [abstract_unigram_binary.tsv](abstract_unigram_binary.tsv) |
| 9 | `abstract` | `unigram` | `tfidf` | [abstract_unigram_tfidf.md](abstract_unigram_tfidf.md) | [abstract_unigram_tfidf.tsv](abstract_unigram_tfidf.tsv) |
| 10 | `abstract` | `bigram` | `frequency` | [abstract_bigram_frequency.md](abstract_bigram_frequency.md) | [abstract_bigram_frequency.tsv](abstract_bigram_frequency.tsv) |
| 11 | `abstract` | `bigram` | `binary` | [abstract_bigram_binary.md](abstract_bigram_binary.md) | [abstract_bigram_binary.tsv](abstract_bigram_binary.tsv) |
| 12 | `abstract` | `bigram` | `tfidf` | [abstract_bigram_tfidf.md](abstract_bigram_tfidf.md) | [abstract_bigram_tfidf.tsv](abstract_bigram_tfidf.tsv) |

El análisis consulta por consulta está en [analisis_por_consulta.md](analisis_por_consulta.md).

---

## 4. Efecto de cada parámetro

Promedio de las 15 consultas sobre las configuraciones que comparten el valor del parámetro:

| Parámetro | Valor | P@10 | MRR | nDCG@10 | Consultas en que gana (nDCG@10 medio) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Campo | `abstract` | 0.341 | 0.630 | 0.350 | 6 |
| | `title` | 0.282 | 0.585 | 0.323 | 9 |
| N-grama | `unigram` | 0.341 | 0.659 | 0.362 | 9 |
| | `bigram` | 0.282 | 0.556 | 0.312 | 6 |
| Representación | `tfidf` | 0.335 | 0.635 | 0.361 | 5 |
| | `binary` | 0.315 | 0.624 | 0.339 | 9 |
| | `frequency` | 0.285 | 0.563 | 0.311 | 1 |

Lectura:

- **Campo.** En promedio gana `abstract`, pero `title` gana en más consultas (9 de 15). El abstract
  rescata consultas que el título no puede resolver (Q03, Q09, Q10: nDCG 0 o casi en todas las
  variantes de `title`), mientras que el título es más preciso cuando los términos de la consulta son
  justamente los que un autor pone en el título (Q04, Q05, Q06, Q08, Q11, Q13).
- **N-grama.** Los unigramas ganan en 9 consultas y en las tres métricas. Los bigramas solo ayudan
  cuando la consulta contiene una expresión fija que los artículos repiten literalmente
  (Q01 *sequential recommendation*, Q02 *long video*/*video understanding*, Q07 *low rank*/*fine tune*).
- **Representación.** TF-IDF tiene el mejor promedio, pero `binary` gana en más consultas (9). Su
  ventaja aparece sobre todo en `abstract · unigram`: con `frequency`, los abstracts que repiten
  muchas veces una palabra genérica (*model*, *language*) suben en el ranking; `binary` neutraliza
  esa repetición y TF-IDF la compensa con el IDF. `frequency` es la peor representación en casi
  todas las consultas.
- **`title · bigram · binary` = `title · bigram · frequency`.** Las dos tablas son idénticas: un
  título casi nunca repite un bigrama, así que el conteo y la presencia coinciden.

---

## 5. Conclusiones

1. **La mejor configuración depende de la consulta.** `abstract · unigram · binary` es la mejor en
   promedio (nDCG@10 = 0.423), pero solo es la mejor en una consulta (Q15). Elegir la configuración
   por consulta subiría el promedio a 0.57.
2. **TF-IDF es la representación más robusta.** Es la que más rescata consultas con términos
   genéricos (Q02, Q09, Q10), donde *language model* domina el ranking si no se pondera por IDF.
3. **El título es preciso pero frágil.** Gana cuando la consulta reproduce el título (Q04–Q06, Q08)
   y fracasa cuando el concepto se nombra de otra forma (Q03, Q07, Q09, Q10).
4. **Los bigramas solo sirven para expresiones fijas.** Fuera de ellas (Q03, Q09, Q12, Q13, Q15)
   reducen la consulta a uno o dos bigramas genéricos o la dejan vacía.
5. **Las consultas difíciles siguen sin resolverse con ninguna configuración** (máx ≤ 0.35). El
   problema es de vocabulario (*vocabulary mismatch*), no de parámetros del VSM; ver la sección 4 de
   [`../error_analysis.md`](../error_analysis.md).
6. **Problemas de normalización detectados:** *reranking* → `reranke` y la preposición `to` no se
   elimina como stopword. Ambos afectan a Q03, Q12 y Q14.

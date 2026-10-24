# Práctica II · Recuperación de artículos científicos (VSM)

Buscador de artículos científicos basado en el **Modelo de Espacio Vectorial**: dada una consulta en
texto libre, devuelve los artículos más parecidos de un corpus de **500 artículos de arXiv**
(cs.CL, cs.CV, cs.IR y cs.LG) ordenados por similitud coseno. Incluye un benchmark de 15 consultas
con juicios de relevancia y la evaluación de las 12 configuraciones del modelo.

**Equipo:** Angel Garcia · Bren

**Reporte completo:** [`reporte_practica2.docx`](reporte_practica2.docx)

---

## 1. Instalación

Requisitos: Python 3.12 o superior (probado con 3.14) y conexión a internet para instalar las
dependencias. El corpus, el benchmark y los 12 modelos ya vienen en el repositorio, así que **no hace
falta descargar ni entrenar nada** para usar la aplicación.

```bash
git clone <url-del-repositorio>
cd PracticaML

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # incluye el modelo en_core_web_sm de spaCy
```

Todos los comandos siguientes se ejecutan **desde la raíz del repositorio** con el entorno activado.

---

## 2. Usar el buscador

Hay dos interfaces con los mismos parámetros. La primera búsqueda tarda unos segundos porque carga
spaCy y el modelo; las siguientes son inmediatas.

### 2.1 Interfaz web

```bash
python -m src.api
```

Abrir <http://127.0.0.1:8000> en el navegador, escribir una consulta en inglés, elegir la
configuración y pulsar **Buscar**. Cada resultado muestra título, puntaje, autores, categoría, fecha,
enlaces a arXiv/PDF/DOI y el abstract desplegable. También se muestra la consulta ya normalizada.

Otras rutas:

| Ruta | Para qué sirve |
| :--- | :--- |
| `/search?query=...&field=...&ngram=...&repr=...&k=...` | Resultados en JSON |
| `/docs` | Documentación interactiva de la API (Swagger) |

Ejemplo: <http://127.0.0.1:8000/search?query=video+generation+with+diffusion+models&field=title&k=5>

Para detener el servidor: `Ctrl+C`.

### 2.2 Línea de comandos

```bash
python -m src.cli query "video generation with diffusion models"
python -m src.cli query "policy optimization in reinforcement learning" --field title --ngram bigram --repr binary -k 5
```

| Opción | Valores | Por defecto | Significado |
| :--- | :--- | :--- | :--- |
| `--field` | `title`, `abstract` | `abstract` | Campo del artículo donde se busca |
| `--ngram` | `unigram`, `bigram` | `unigram` | Palabras sueltas o pares de palabras consecutivas |
| `--repr` | `frequency`, `binary`, `tfidf` | `tfidf` | Peso de cada término: conteo, presencia/ausencia o TF-IDF |
| `-k` | entero | `10` | Número de resultados |
| `--chars` | entero | `300` | Caracteres del abstract que se muestran (`0` = completo) |

Si ningún término de la consulta existe en el vocabulario del modelo elegido, el programa lo avisa en
lugar de devolver resultados vacíos (pasa, por ejemplo, con algunas consultas en `title · bigram`).

**Consultas de ejemplo** (las 15 del benchmark están en `data/benchmark/queries.tsv`):

- `sequential recommendation with user behavior sequences`
- `retrieval-augmented generation for multi-hop question answering`
- `large language models as judges for evaluation`
- `assistants that remember past experiences`

---

## 3. Evaluar el benchmark

```bash
python -m src.cli benchmark --check           # valida queries.tsv y qrels.tsv (no ejecuta consultas)
python -m src.cli benchmark --force           # una configuración (por defecto abstract · unigram · tfidf)
python -m src.cli benchmark --field title --ngram bigram --repr binary --force
python -m src.cli benchmark --all --force     # las 12 configuraciones
```

`--force` es necesario porque el script exige el tag git `benchmark-v1` como prueba de que el
benchmark se congeló antes de ejecutar consultas. El benchmark se congeló en el commit `553e1c1`, pero
el tag no se creó.

| Comando | Genera |
| :--- | :--- |
| una configuración | `data/benchmark/rankings.tsv`, `results/metrics_per_query.tsv`, `results/metrics_summary.tsv` |
| `--all` | `results/metrics_all_configs.tsv` y `results/per_query/<campo>_<ngrama>_<repr>.tsv` (una tabla por configuración) |

Métricas (k = 10): P@10, R@10, F1@10, RR/MRR y nDCG@10. Los documentos que no están en
`qrels.tsv` cuentan como no relevantes.

### Pruebas unitarias

```bash
pip install pytest
python -m pytest tests/ -v                    # 13 pruebas de métricas y formato del benchmark
```

---

## 4. Resultados principales

| Configuración | P@10 | MRR | nDCG@10 |
| :--- | :---: | :---: | :---: |
| **abstract · unigram · binary** (mejor) | 0.427 | 0.764 | 0.423 |
| abstract · unigram · tfidf | 0.380 | 0.717 | 0.391 |
| title · unigram · tfidf | 0.340 | 0.657 | 0.377 |
| title · bigram · binary (peor) | 0.240 | 0.494 | 0.283 |

Las consultas difíciles (paráfrasis en lenguaje común) no se resuelven con ninguna configuración
(nDCG@10 ≤ 0.35) porque el VSM solo compara términos exactos. El análisis completo está en el
reporte y en:

- `results/error_analysis.md`: comparación de las 12 configuraciones y análisis de errores.
- `results/per_query/README.md`: matriz consulta × configuración y efecto de cada parámetro.
- `results/per_query/analisis_por_consulta.md`: explicación de cada consulta.

---

## 5. Estructura del repositorio

```
data/
  raw/                              respuestas XML originales de la API de arXiv
  scientific_raw_corpus.tsv         corpus crudo (500 artículos)
  scientific_normalized_corpus.tsv  corpus normalizado (title_norm, abstract_norm)
  benchmark/                        queries.tsv, qrels.tsv, rankings.tsv, notas de anotación
models/                             12 modelos .pkl: {campo}_{ngrama}_{repr}.pkl
notebooks/                          01 recolección · 02 normalización · 03-05 vectorización
src/
  normalize.py                      normalización con spaCy (corpus y consultas)
  retrieve.py                       búsqueda por similitud coseno
  evaluate.py                       validación del benchmark y métricas
  cli.py                            línea de comandos (query, benchmark)
  api.py                            interfaz web (FastAPI)
results/                            estadísticas de cada fase, métricas y análisis
tests/test_metrics.py               pruebas unitarias
logs/acquisition.log                registro de la recolección
reporte_practica2.docx              reporte de la práctica
```

---

## 6. Regenerar el corpus y los modelos (opcional)

No es necesario para usar la aplicación. Los subcomandos `collect` y `build` de `src/cli.py` todavía
**no funcionan**, porque los módulos `src/collect.py` y `src/represent.py` no existen. Para
regenerar todo hay que ejecutar los notebooks en orden (requiere `pip install jupyter`):

1. `notebooks/01_recoleccion_corpus.ipynb`: descarga los artículos de arXiv → `data/scientific_raw_corpus.tsv`
2. `notebooks/02_normalizacion_corpus.ipynb`: normaliza → `data/scientific_normalized_corpus.tsv`
3. `notebooks/03_vectorizacion_tfidf.ipynb`, `04_vectorizacion_binaria.ipynb`, `05_vectorizacion_frecuencia.ipynb` → `models/*.pkl`

Al volver a descargar, arXiv puede devolver otros artículos, y entonces los qrels del benchmark
dejarían de ser válidos. Para reproducir los resultados del reporte hay que usar los archivos incluidos.

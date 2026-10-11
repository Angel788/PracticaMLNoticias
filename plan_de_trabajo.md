# Plan de trabajo: Práctica II, Recuperación de artículos científicos (VSM)

Equipo de 2 personas (**A** y **B**). El PDF pide 3-4 integrantes, así que hay que confirmar con el profesor que un equipo de 2 es válido. Las fechas son relativas porque falta conocer la fecha de entrega.

---

## 1. Supuestos iniciales (a confirmar)

| Tema | Supuesto de trabajo |
|---|---|
| Fuente | arXiv vía API oficial (`export.arxiv.org/api/query`) |
| Categorías | 4 categorías: `cs.CL`, `cs.CV`, `cs.IR`, `cs.LG` (hay solapamiento temático útil para consultas difíciles como la 15) |
| Volumen | ~500 documentos (≈125 por categoría) |
| Idioma | Inglés (corpus y consultas) |
| Stopwords | Solo se eliminan DET, ADP, CCONJ/SCONJ y PRON (etiquetas universales de spaCy) |
| `document_id` | `arxiv_id` en todos los archivos TSV |
| Interfaz | CLI con subcomandos (`argparse` o `typer`) |
| Librerías | spaCy (`en_core_web_sm`), scikit-learn, pandas, numpy |

---

## 2. Reparto de roles

El reparto busca carga equilibrada y dependencias claras. Las tareas marcadas con ⚖️ se hacen **entre los dos** para reducir sesgo.

| Área | A | B |
|---|---|---|
| Recolección del corpus | ✅ responsable | revisa |
| Normalización (spaCy + POS) | ✅ responsable | revisa |
| Vectorización (12 configuraciones) | apoyo | ✅ responsable |
| Recuperación (consulta → top-10) | apoyo | ✅ responsable |
| Diseño de las 15 consultas | ⚖️ | ⚖️ |
| Anotación de relevancia (qrels) | ⚖️ | ⚖️ |
| Métricas y script de benchmark | revisa | ✅ responsable |
| CLI | ✅ responsable | apoyo |
| Análisis de errores | ⚖️ | ⚖️ |
| Reporte PDF y README | ✅ responsable | revisa |

---

## 3. Estructura del repositorio

```
practica2-nlp/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # respuestas XML originales de arXiv
│   ├── scientific_raw_corpus.tsv
│   ├── scientific_normalized_corpus.tsv
│   └── benchmark/
│       ├── queries.tsv
│       ├── qrels.tsv
│       └── rankings.tsv
├── models/                   # .pkl con vectorizadores y matrices
├── results/
│   ├── metrics_per_query.tsv
│   ├── metrics_summary.tsv
│   └── error_analysis.md
├── logs/
│   └── acquisition.log
├── src/
│   ├── collect.py
│   ├── normalize.py
│   ├── represent.py
│   ├── retrieve.py
│   ├── evaluate.py
│   └── cli.py
├── tests/
│   └── test_metrics.py       # valida contra el ejemplo Q01 del PDF
└── report/
    └── reporte.pdf
```

---

## 4. Fases y tareas

### Fase 0: Arranque (días 1-2)
- [ ] Enviar al profesor las preguntas abiertas (sección 8).
- [ ] Crear el repositorio y el entorno virtual.
- [ ] Fijar las convenciones: `document_id = arxiv_id`, esquema de columnas y nombres de archivos.
- [ ] Acordar el esquema de columnas de todos los TSV.

**Entregable:** repositorio con la estructura base y `requirements.txt`.

### Fase 1: Recolección del corpus (semana 1) · A
- [ ] Script `collect.py` con la API de arXiv: paginación, pausa de ≥3 s entre peticiones, `User-Agent` identificable.
- [ ] Guardar la respuesta cruda en `data/raw/` para trazabilidad.
- [ ] Extraer los campos: `arxiv_id, doi, title, authors, abstract, categories, date, url, retrieved_at`.
- [ ] Limpiar tabuladores y saltos de línea dentro de los campos de texto.
- [ ] Registrar los errores en `logs/acquisition.log`.
- [ ] Eliminar duplicados (artículos con varias categorías) por `arxiv_id`.
- [ ] Generar un reporte de distribución por categoría, fecha y fuente.
- [ ] Hacer la recolección **reproducible**: misma consulta, mismos parámetros y fecha de corte fija.

**Entregable:** `scientific_raw_corpus.tsv` (~500 filas) y el reporte de distribución.
**Criterio de aceptación:** sin duplicados ni abstracts vacíos, y el TSV se carga con `pandas` sin errores.

### Fase 2: Normalización (semana 1-2) · A
- [ ] Tokenización con spaCy.
- [ ] POS tagging y eliminación de DET, ADP, CCONJ, SCONJ y PRON.
- [ ] Lematización.
- [ ] Normalización de espacios y caracteres de control.
- [ ] Decisión de diseño: pasar a minúsculas, y qué hacer con números, guiones y términos técnicos (por ejemplo "BERT", "fine-tuning"). Documentarlo.
- [ ] Función única `normalize(text) -> str`, reutilizada **sin cambios** para las consultas.
- [ ] Prueba unitaria que garantice que corpus y consulta usan la misma función.

**Entregable:** `scientific_normalized_corpus.tsv` con `title_norm` y `abstract_norm`.

### Fase 3: Representación VSM (semana 2) · B
- [ ] Generar 12 configuraciones: {título, abstract} × {unigrama, bigrama} × {frecuencia, binario, TF-IDF}.
- [ ] Usar `CountVectorizer` (frecuencia), `CountVectorizer(binary=True)` y `TfidfVectorizer`.
- [ ] Definir `ngram_range=(1,1)` para unigramas y `(2,2)` para bigramas.
- [ ] Guardar cada vectorizador y su matriz en `.pkl`, con una convención como `models/{campo}_{ngrama}_{tipo}.pkl`.
- [ ] Reportar el tamaño del vocabulario y la dispersión de cada matriz.

**Entregable:** 12 pares vectorizador+matriz.
**Nota:** los vectorizadores ya se ajustan sobre texto normalizado, así que se les pasa `analyzer` por defecto y `lowercase=False` si ya se normalizó a minúsculas.

### Fase 4: Recuperación (semana 2-3) · B
- [ ] `retrieve(query, campo, ngrama, tipo, k=10)`:
  1. Normaliza la consulta con `normalize()`.
  2. Transforma con el vectorizador correspondiente.
  3. Calcula similitud coseno contra la matriz.
  4. Ordena de forma descendente y devuelve el top-10 con puntaje.
- [ ] Manejar el caso de consulta vacía o sin términos en el vocabulario (norma cero).
- [ ] Mostrar `rank, arxiv_id, score, título`.

**Entregable:** función de recuperación probada con 3 consultas manuales.

### Fase 5: Benchmark (semana 3) · A + B
- [ ] Redactar 15 consultas: 5 fáciles, 5 medias y 5 difíciles. Distribuirlas por tema para que cada categoría tenga cobertura.
- [ ] Para cada consulta, identificar 10-15 documentos relevantes con relevancia 1 o 2.
- [ ] Guardar `queries.tsv` (`query_id, difficulty_level, query`) y `qrels.tsv` (`query_id, document_id, relevance`).
- [ ] **Congelar** el benchmark (commit/tag `benchmark-v1`) antes de ejecutar cualquier ranking.

**Protocolo anti-sesgo (importante):**
1. Redactar las consultas **antes** de ver los resultados del sistema.
2. Anotar con búsqueda por palabras clave sobre el corpus crudo y lectura manual de abstracts, **no** con el top-10 del propio VSM, para no inflar P@10.
3. Cada persona anota 7-8 consultas y la otra revisa una muestra. Las discrepancias se resuelven en conjunto.
4. Registrar el criterio: 2 = el abstract trata directamente el tema; 1 = lo trata parcialmente o como componente.

**Riesgo:** con ~500 documentos, algunas consultas difíciles pueden no tener 10 relevantes. Se mitiga eligiendo las consultas **después** de explorar el corpus.

### Fase 6: Evaluación (semana 3-4) · B
- [ ] Implementar P@10, R@10, F1@10, MRR y nDCG@10 en `evaluate.py`.
- [ ] Prueba unitaria con el ejemplo Q01 del PDF. Valores esperados: P@10 = 0.50, R@10 = 0.833, F1@10 = 0.625, RR = 1.0, nDCG@10 ≈ 0.835.
- [ ] Documentos no listados en qrels = relevancia 0.
- [ ] Si no hay ningún relevante en el top-10, RR = 0.
- [ ] Generar `rankings.tsv` para la configuración principal.
- [ ] Generar métricas por consulta y promedios, también por nivel de dificultad.
- [ ] Opcional: comparar las 12 configuraciones en una tabla (es el mejor material para el reporte).

**Entregable:** `rankings.tsv`, `metrics_per_query.tsv`, `metrics_summary.tsv`.

### Fase 7: CLI (semana 4) · A
Cuatro comandos separados:

```bash
python -m src.cli collect    --categories cs.CL cs.CV cs.IR cs.LG --max 500
python -m src.cli build      # normaliza y genera las representaciones
python -m src.cli query "misinformation detection using transformers" \
                     --field abstract --ngram unigram --repr tfidf
python -m src.cli benchmark  --field abstract --ngram unigram --repr tfidf
```

- [ ] Validar argumentos (`--field`, `--ngram`, `--repr` con opciones cerradas).
- [ ] Mensajes de error claros si faltan los archivos previos.

### Fase 8: Análisis de errores (semana 4-5) · A + B
- [ ] Elegir **≥5 consultas buenas** y **≥5 malas** según nDCG@10 y P@10.
- [ ] Para cada una, explicar la causa: falta de solapamiento léxico, sinónimos, términos muy frecuentes, ambigüedad, normalización inadecuada, nombres propios o vocabulario de dominio.
- [ ] Incluir ejemplos concretos: qué relevante quedó fuera y qué irrelevante entró.
- [ ] Guardar los casos para la comparación futura con embeddings.

### Fase 9: Reporte y entrega (semana 5) · A (redacta), B (revisa)
- [ ] PDF con: introducción, corpus (distribución), normalización, representaciones, metodología del benchmark, resultados, análisis de errores, conclusiones y nombres del equipo.
- [ ] README con instrucciones de ejecución desde cero.
- [ ] Prueba final: clonar el repositorio en limpio y ejecutar los 4 comandos.

---

## 5. Cronograma resumido

| Semana | A | B |
|---|---|---|
| 1 | Recolección, inicio de normalización | Prototipo de métricas con el ejemplo del PDF |
| 2 | Normalización terminada | Vectorización y recuperación |
| 3 | Diseño de consultas y anotación (mitad) | Diseño de consultas y anotación (mitad) |
| 4 | CLI, análisis de errores | Evaluación completa, análisis de errores |
| 5 | Reporte PDF, README | Revisión, prueba en entorno limpio |

---

## 6. Decisiones técnicas a documentar

1. **Texto de los vectorizadores:** se ajustan sobre el texto ya normalizado.
2. **Bigramas:** se calculan sobre la secuencia **tras** quitar stopwords, de modo que "analysis of text" produzca el bigrama "analysis text". Es una decisión que se debe justificar en el reporte.
3. **Consultas sin vocabulario:** si todos los términos quedan fuera del vocabulario, devolver aviso en lugar de scores en cero.
4. **Desempates:** orden estable por `arxiv_id`.
5. **Reproducibilidad:** fijar versiones en `requirements.txt` y registrar la versión del modelo de spaCy.

---

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Límites de la API de arXiv | Pausas entre peticiones, guardar crudo, reintentos con backoff |
| Pocos relevantes para consultas difíciles | Explorar el corpus antes de fijar las consultas |
| Sesgo en las qrels | Anotación independiente del sistema + revisión cruzada |
| Errores en las métricas | Pruebas unitarias contra el ejemplo Q01 |
| Lematización que rompe términos técnicos | Revisar una muestra del corpus normalizado |
| Carga desbalanceada con 2 personas | Revisar el avance cada semana y reasignar |

---

## 8. Preguntas abiertas para el profesor

1. ¿Es válido un equipo de 2 personas?
2. ¿Las categorías de arXiv requieren aprobación previa?
3. ¿Corpus y consultas deben estar en inglés?
4. ¿Hay que evaluar las 12 configuraciones o solo una? ¿Cuál alimenta `rankings.tsv`?
5. ¿`document_id` es el `arxiv_id` o un índice numérico? (El PDF mezcla `3` y `N003`.)
6. En el ejemplo de `rankings.tsv`, el documento 18 aparece en los rangos 2 y 7. ¿Es un error?
7. ¿Se permite apoyo de un LLM o de embeddings para encontrar candidatos a relevantes, o la anotación debe ser manual?
8. ¿Interfaz CLI o web? ¿Idioma del PDF? ¿Fecha de entrega y rúbrica?

---

## 9. Checklist de entrega

- [ ] Código fuente
- [ ] `scientific_raw_corpus.tsv`
- [ ] `scientific_normalized_corpus.tsv`
- [ ] Vectorizadores y matrices (`.pkl`)
- [ ] `queries.tsv` y `qrels.tsv` (congelados)
- [ ] `rankings.tsv`
- [ ] Métricas por consulta y promedios
- [ ] PDF con resultados, análisis de errores y nombres del equipo
- [ ] README con instrucciones de ejecución

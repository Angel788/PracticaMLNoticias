# Guía para diseñar las consultas del benchmark (Fase 5)

Cómo redactar las 15 consultas, cómo anotar sus documentos relevantes y cómo guardarlas. Seguir el orden de las secciones: **primero consultas y anotación, después ejecutar el sistema**.

---

## 1. Qué hay que entregar

Dos archivos en `data/benchmark/`, separados por tabuladores:

**`queries.tsv`**
```
query_id	difficulty_level	query
Q01	easy	video understanding with multimodal large language models
Q02	medium	...
```

**`qrels.tsv`**
```
query_id	document_id	relevance
Q01	2609.39662	2
Q01	2610.00417	1
```

- `query_id`: `Q01` … `Q15`.
- `difficulty_level`: `easy`, `medium` o `hard`. Van **5 de cada una**.
- `document_id`: el `arxiv_id` del corpus.
- `relevance`: `2` o `1`. Los documentos que no aparecen en `qrels.tsv` cuentan como relevancia 0, así que no se anotan los irrelevantes.

---

## 2. Reglas antes de empezar (protocolo anti-sesgo)

1. **No ejecutar `src/retrieve.py` con las consultas del benchmark** hasta congelarlo (sección 7). Si se eligen consultas o relevantes viendo el top-10 del sistema, las métricas salen infladas y el análisis de errores no vale.
2. Los relevantes se buscan en el **corpus crudo** (`data/scientific_raw_corpus.tsv`) con palabras clave y leyendo abstracts. La sección 5 trae el código.
3. Cada quien redacta y anota 7-8 consultas. Luego cada uno revisa una muestra de las del otro, y las diferencias se resuelven juntos.

---

## 3. Cómo redactar una consulta

**Formato**
- En inglés, como el corpus.
- Una frase corta, de 3 a 8 palabras, escrita como la teclearía alguien en un buscador: `misinformation detection using transformers`.
- Debe describir **un tema**, no un artículo concreto. Si solo un documento la responde, no sirve.

**Requisito de cobertura:** cada consulta debe tener **al menos 10 documentos relevantes** en el corpus (el plan pide entre 10 y 15). Antes de fijarla, comprobarlo con la búsqueda de la sección 5.

> Ejemplo de lo que **no** sirve: `misinformation detection using transformers` solo tiene 1 documento con *misinformation*, *fake news* o *disinformation* en todo el corpus.

**Distribución por categoría:** el corpus tiene 125 documentos de cada categoría (`cs.CL`, `cs.CV`, `cs.IR`, `cs.LG`). Cada categoría debe ser el tema principal de 3 o 4 consultas, y conviene que algunas difíciles mezclen categorías.

**Palabras que conviene evitar:** términos genéricos como `approach`, `method`, `novel`, `paper` o `model` (cuando va solo). Aparecen en casi todos los abstracts y meten ruido, sobre todo en las representaciones binaria y de frecuencia.

---

## 4. Qué hace fácil, media o difícil a una consulta

La dificultad depende de **cuánto se parecen las palabras de la consulta a las de los abstracts relevantes**, porque el modelo vectorial solo compara términos.

| Nivel | Características | Ejemplo de forma |
|---|---|---|
| **easy** | Usa los mismos términos técnicos que los abstracts. El tema es concreto y casi todo cae en una categoría | `sequential recommendation with user behavior` |
| **medium** | Combina 2 conceptos (solo algunos documentos tienen ambos), o usa un término común con varios sentidos | `parameter-efficient fine-tuning of language models` |
| **hard** | Usa sinónimos o paráfrasis en vez del término técnico, o es un tema transversal a varias categorías, o depende de siglas | `making neural networks smaller and faster` (los relevantes dicen *quantization*, *pruning*, *compression*) |

Las consultas difíciles son las que más sirven en la Fase 8, porque muestran las limitaciones del modelo (falta de solapamiento léxico, sinónimos, ambigüedad).

---

## 5. Cómo buscar los documentos relevantes

Desde la raíz del repositorio, con el entorno activado (`source .venv/bin/activate.fish`), en un notebook o en `python`:

```python
import pandas as pd

corpus = pd.read_csv("data/scientific_raw_corpus.tsv", sep="\t", dtype=str, keep_default_na=False)
text = (corpus["title"] + " " + corpus["abstract"]).str.lower()

def candidatos(*patrones):
    """Documentos cuyo título o abstract contiene alguno de los patrones (regex)."""
    mask = pd.Series(False, index=corpus.index)
    for p in patrones:
        mask |= text.str.contains(p, regex=True)
    out = corpus.loc[mask, ["arxiv_id", "primary_category", "title"]]
    print(len(out), "candidatos")
    return out

def leer(arxiv_id):
    doc = corpus.set_index("arxiv_id").loc[arxiv_id]
    print(doc["title"], "\n\n", doc["abstract"])

candidatos(r"quantiz", r"pruning", r"compression")
leer("2609.40127")
```

Pasos para cada consulta:
1. Buscar con **varios** patrones: el término principal, sus sinónimos, siglas y variantes (`fine-tun` encuentra *fine-tuning*, *fine-tuned*, *fine-tune*).
2. Leer el título y el abstract de cada candidato con `leer()`.
3. Anotar los relevantes con su nivel de relevancia (sección 6).
4. Si quedan menos de 10 relevantes, ampliar la consulta o cambiarla.

---

## 6. Criterio de relevancia

| Valor | Significado | Ejemplo con `parameter-efficient fine-tuning of language models` |
|---|---|---|
| **2** | El abstract trata **directamente** el tema de la consulta | Proponen un método nuevo tipo LoRA para LLMs |
| **1** | Lo trata **parcialmente** o como componente | Usan LoRA para adaptar su modelo, pero el artículo trata de otra cosa |
| (no se anota) | No trata el tema, aunque comparta palabras | Mencionan *fine-tuning* de pasada en el trabajo relacionado |

Juzgar por el **tema**, no por las palabras. Un documento puede ser relevante sin contener ningún término de la consulta (pasa en las difíciles), y uno que contiene todos los términos puede no serlo.

---

## 7. Congelar el benchmark

Cuando estén las 15 consultas y sus qrels, revisadas por los dos:

```bash
git add data/benchmark/queries.tsv data/benchmark/qrels.tsv
git commit -m "Benchmark v1: 15 consultas y qrels"
git tag benchmark-v1
```

A partir de aquí no se cambian. Si algo se corrige, se hace en un tag nuevo (`benchmark-v2`) y se explica en el reporte.

---

## 8. Temas con suficientes documentos

Conteo de documentos cuyo título o abstract contiene las palabras clave (búsqueda en el corpus crudo). Son **candidatos, no relevantes confirmados**: un documento que menciona el término no siempre trata el tema, así que hay que leerlos.

| Tema (palabras clave buscadas) | Docs | Categoría principal | Nivel sugerido |
|---|---:|---|---|
| recomendación (`recommend`) | 64 | cs.IR (59) | easy / medium |
| video (`video`) | 57 | cs.CV (45) | easy |
| multimodal / vision-language (`multimodal`, `vision-language`, `vlm`) | 69 | cs.CV (41) | easy / medium |
| agentes (`agent`) | 69 | mezclado | medium |
| razonamiento (`reasoning`) | 88 | cs.CL (37) | medium |
| fine-tuning (`fine-tun`) | 63 | mezclado | medium |
| e-commerce / productos (`e-commerce`, `product`) | 41 | cs.IR (28) | easy / medium |
| fairness / sesgo (`fairness`, `bias`) | 37 | mezclado | medium / hard |
| compresión de modelos (`quantiz`, `pruning`, `compression`) | 33 | mezclado | hard (con paráfrasis) |
| LLM como evaluador (`judge`, `evaluation metric`) | 30 | cs.IR / cs.CL | medium |
| aprendizaje por refuerzo (`reinforcement learning`) | 28 | cs.LG (11) | medium |
| LoRA / parameter-efficient (`lora`, `parameter-efficient`) | 27 | cs.CL / cs.LG | medium |
| 3D / nubes de puntos (`3d`, `point cloud`) | 23 | cs.CV (19) | easy |
| reranking (`rerank`, `re-rank`) | 22 | cs.IR (20) | easy |
| medicina / clínica (`medical`, `clinical`) | 21 | mezclado | medium / hard |
| ataques adversariales (`adversarial`, `attack`) | 18 | mezclado | hard |
| question answering | 17 | mezclado | medium |
| multilingüe / bajos recursos (`multilingual`, `low-resource`) | 16 | cs.CL (10) | medium |
| interpretabilidad (`explainab`, `interpretab`) | 16 | cs.LG (6) | hard |
| RAG (`retrieval-augmented`, `rag`) | 12 | cs.IR (10) | easy |
| difusión / texto a imagen (`diffusion model`, `text-to-image`) | ~15 | cs.CV | easy |
| segmentación (`segmentation`) | 10 | cs.CV (9) | easy (justo en el límite) |

**Temas que no conviene usar** porque tienen muy pocos documentos: desinformación (1), traducción automática (0), análisis de sentimiento (4), reconocimiento de entidades (1), redes neuronales de grafos (5), aprendizaje federado (5), series de tiempo (6), detección de objetos (4).

---

### Comandos para probar la CLI

Prueba la interacción en tu terminal mediante los siguientes comandos:

1. **Búsqueda directa**:

```bash
python -m src.cli query "image segmentation" --field abstract --repr binary -k 5

```

2. **Evaluación del benchmark**:

```bash
python -m src.cli benchmark --all

```

3. **Validación del benchmark**:

```bash
python -m src.cli benchmark --check
```


## 9. Checklist por consulta

- [ ] Está en inglés y tiene de 3 a 8 palabras.
- [ ] Se escribió **sin** ejecutar el sistema de recuperación.
- [ ] Tiene al menos 10 documentos relevantes anotados con 1 o 2.
- [ ] Se buscaron sinónimos y variantes, no solo las palabras de la consulta.
- [ ] El nivel (easy, medium, hard) está justificado según la sección 4.
- [ ] La otra persona revisó una muestra de sus relevantes.

Y para el conjunto: 5 easy, 5 medium y 5 hard, y las 4 categorías cubiertas.

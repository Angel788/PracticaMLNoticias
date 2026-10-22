
# Notas de anotación del benchmark ( sin congelar)

**Estado:** por congelar con el tag `benchmark-v2`.

**Cómo se anotó:** se buscó por palabras clave en `data/scientific_raw_corpus.tsv` (término principal, sinónimos, siglas y variantes) y se leyeron título y abstract de cada candidato. No se ejecutó `src/retrieve.py` ni la API con estas consultas.

**Criterio:** Las 15 consultas salieron del borrador que preparé en la sesión anterior; aquí las explico. Cada una pertenece a un nivel de dificultad según cuánto se parecen sus palabras a las de los abstracts relevantes.

## Cómo se construyó el conjunto
- **5 fáciles:** la consulta usa los mismos términos técnicos que los abstracts.
- **5 medias:** el tema es claro, pero los abstracts lo dicen con variantes (siglas, nombres de métodos, idiomas concretos).
- **5 difíciles:** la consulta es una paráfrasis en lenguaje común, y los abstracts relevantes usan el vocabulario técnico que la consulta evita.
- **Cobertura temática:** cs.IR y cs.CV son el tema principal de 4 consultas cada una, cs.CL y cs.LG de 3, y Q15 mezcla las cuatro categorías.

## Fáciles (fuerte coincidencia de palabras)

| ID | Consulta | Qué busca | Por qué es fácil |
|---|---|---|---|
| Q01 | sequential recommendation with user behavior sequences | Recomendadores que predicen lo siguiente a partir del historial del usuario | Los abstracts repiten *sequential recommendation* y *user behavior* |
| Q02 | long video understanding with vision-language models | Modelos que entienden videos largos con texto e imagen | Vocabulario técnico compartido (*long video*, *video question*) |
| Q03 | reranking retrieved documents with large language models | Reordenar resultados de búsqueda con LLMs | El término *rerank* es muy específico |
| Q04 | video generation with diffusion models | Generar video con modelos de difusión | Tema concreto de visión; el único cuidado es que *diffusion* aparece en otros contextos |
| Q05 | retrieval-augmented generation for multi-hop question answering | RAG para preguntas que requieren combinar varias fuentes | Los abstracts usan los mismos términos y la sigla RAG |

## Medias (variación léxica)

| ID | Consulta | Qué busca | Por qué es media |
|---|---|---|---|
| Q06 | on-policy self-distillation for reasoning models | Destilación de un modelo en sí mismo, entrenada con sus propios datos, para razonar | *Distillation* tiene varios sentidos (compresión, difusión, visión) y solo algunos combinan *on-policy* con razonamiento |
| Q07 | parameter-efficient fine-tuning with low-rank adapters | Ajuste fino eficiente, típicamente LoRA | Los abstracts dicen *LoRA* en vez de *low-rank adapters*, y muchos solo lo usan como herramienta |
| Q08 | policy optimization in reinforcement learning | Optimización de políticas en RL | Tema amplio que cruza RL clásico y RL para LLMs; *policy* tiene otros sentidos |
| Q09 | large language models as judges for evaluation | LLMs usados para evaluar texto o sistemas | Combina dos conceptos, y *evaluation* aparece en casi todos los abstracts |
| Q10 | multilingual language models for low-resource languages | Modelos para idiomas con pocos datos | Muchos relevantes nombran el idioma (árabe, bengalí, rumano) en vez de *low-resource* |

## Difíciles (paráfrasis, poca coincidencia de palabras)

| ID | Consulta | Qué busca | El vocabulario que usan los abstracts |
|---|---|---|---|
| Q11 | making neural networks smaller and faster | Compresión y aceleración de modelos | *quantization*, *pruning*, *compression*, *KV cache* |
| Q12 | AI reading hospital scans to detect illness | IA en imagen médica | *MRI*, *X-ray*, *radiology*, *diagnosis* |
| Q13 | defending AI systems against malicious manipulation | Robustez y seguridad | *adversarial*, *backdoor*, *poisoning*, *jailbreak* |
| Q14 | peeking inside language models to explain their behavior | Interpretabilidad | *interpretability*, *mechanistic*, *probing*, *sparse autoencoder* |
| Q15 | assistants that remember past experiences | Memoria de agentes | *agent memory*, *long-term*, *lifelong*; repartida en las 4 categorías |

## Cosas que conviene saber
- **Q12:** está limitada a imagen médica. Si prefieren «IA en salud» en general, hay que cambiar también el texto de la consulta.
- **Q06 y Q08 son las más discutibles como «medias».** Comparten bastantes términos con sus abstracts y podrían pasar por fáciles. Tenerlo presente al interpretar los resultados por nivel.
- **Revisen el formato de `difficulty_level`.** El PDF muestra los niveles como números (1, 2, 3) en `queries.tsv`, pero `evaluate.py` espera las palabras `easy`, `medium` y `hard` (y por eso tu `--check` pasó). Si el profesor revisa el archivo con el formato del PDF, conviene cambiarlo. Es un ajuste pequeño: lo hago en `evaluate.py` y las pruebas si quieren.

Si me pasan `queries.tsv`, confirmo qué formato tiene y reviso que cada consulta tenga entre 3 y 8 palabras, como exige la validación.


## Cómo probarlo
**Nota:** asegurate de instalar pytest "pip install pytest"

source .venv/bin/activate
python -m pytest tests/ -v          # 9 pruebas (ahora: 9 passed)
python -m src.evaluate --check      # valida los TSV sin ejecutar consultas (ahora: válido)

Las pruebas comprueban las métricas con ejemplos calculados a mano, que el formato de los TSV sea válido y el flujo completo con consultas inventadas. Ninguna usa las consultas reales.

Después de revisar y congelar:

git add data/benchmark/queries.tsv data/benchmark/qrels.tsv
git commit -m "Benchmark v1: 15 consultas y qrels"
git tag benchmark-v2 #Cambiar el tag en evaluate si cambia la versión

python -m src.evaluate
python -m src.evaluate --field title --ngram bigram --repr binary
python -m src.evaluate --all

Con eso se generan data/benchmark/rankings.tsv, results/metrics_per_query.tsv y results/metrics_summary.tsv (con --all, results/metrics_all_configs.tsv).
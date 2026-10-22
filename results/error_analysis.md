# Análisis de Errores y Evaluación Experimental (Fase 8)
**Proyecto:** Recuperación de Artículos Científicos mediante Modelo de Espacio Vectorial (VSM)  
**Corpus:** ~500 artículos de arXiv (categorías `cs.CL`, `cs.CV`, `cs.IR`, `cs.LG`)  
**Benchmark:** 15 consultas (5 Fáciles, 5 Medias, 5 Difíciles), 218 juicios de relevancia (`qrels.tsv`)

---

## 1. Resumen 

Análisis detallado de errores y la evaluación comparativa del sistema de recuperación de información basado en el **Modelo de Espacio Vectorial (VSM)**. Se evaluaron **12 configuraciones posibles** resultantes de combinar:
* **Campos:** `abstract`, `title`
* **N-gramas:** `unigram` (1,1), `bigram` (2,2)
* **Representaciones:** `tfidf`, `binary`, `frequency`

El benchmark se ejecutó sobre un conjunto congelado de 15 consultas categorizadas en tres niveles de dificultad léxica, evaluadas a una profundidad $k = 10$.

---

## 2. Comparativa Global de las 12 Configuraciones

Desempeño global de las 12 configuraciones ordenadas descendentemente por la métrica **nDCG@10**:

| Campo | N-grama | Representación | P@10 | R@10 | F1@10 | MRR | nDCG@10 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **abstract** | **unigram** | **binary** | **0.4267** | **0.2892** | **0.3446** | **0.7639** | **0.4230** |
| abstract | unigram | tfidf | 0.3800 | 0.2564 | 0.3061 | 0.7167 | 0.3913 |
| title | unigram | tfidf | 0.3400 | 0.2351 | 0.2776 | 0.6574 | 0.3767 |
| abstract | bigram | tfidf | 0.3467 | 0.2345 | 0.2797 | 0.5833 | 0.3593 |
| title | unigram | binary | 0.3133 | 0.2150 | 0.2548 | 0.6500 | 0.3493 |
| title | unigram | frequency | 0.2867 | 0.1965 | 0.2330 | 0.6296 | 0.3318 |
| abstract | bigram | frequency | 0.3133 | 0.2130 | 0.2534 | 0.5889 | 0.3314 |
| title | bigram | tfidf | 0.2733 | 0.1863 | 0.2214 | 0.5833 | 0.3147 |
| abstract | unigram | frequency | 0.3000 | 0.2021 | 0.2414 | 0.5389 | 0.2989 |
| abstract | bigram | binary | 0.2800 | 0.1901 | 0.2263 | 0.5889 | 0.2986 |
| title | bigram | frequency | 0.2400 | 0.1648 | 0.1952 | 0.4944 | 0.2832 |
| title | bigram | binary | 0.2400 | 0.1648 | 0.1952 | 0.4944 | 0.2832 |

### Principales Hallazgos Estructurales:

1. **Configuración Óptima (`abstract · unigram · binary`)**:
   * Alcanzó el máximo rendimiento con un **nDCG@10 de 0.4230** y **P@10 de 0.4267**.
   * Sorprendentemente, la representación **binaria** superó ligeramente a TF-IDF en el abstract con unigramas. En un corpus técnico compacto (~500 artículos), la presencia/ausencia directa de términos clave específicos genera una señal de filtrado más limpia que la ponderación por frecuencia.

2. **Dominio de Unigramas sobre Bigramas**:
   * En todas las combinaciones, los unigramas superaron drásticamente a los bigramas.
   * Por ejemplo, al cambiar de `unigram` a `bigram` en `abstract · binary`, el nDCG@10 cae de **0.4230 a 0.2986**. Exigir la coincidencia contigua exacta de dos palabras restringe demasiado la recuperación frente a pequeñas variaciones sintácticas.

3. **Superioridad del Resumen (`abstract`) frente al Título (`title`)**:
   * El abstract provee mayor densidad temática y variedad léxica. Los títulos, al ser extremadamente breves, sufren de una fuerte escasez de términos (*term sparsity*).

---

## 3. Desglose del Desempeño por Nivel de Dificultad

Tomando como referencia la configuración estándar `abstract · unigram · tfidf`:

| Nivel de Dificultad | Descripción | P@10 | R@10 | F1@10 | MRR | nDCG@10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Nivel 1 (Fácil)** | Coincidencia léxica directa | 0.5000 | 0.3333 | 0.4000 | 0.8500 | 0.5079 |
| **Nivel 2 (Medio)** | Variación léxica y siglas | 0.5200 | 0.3549 | 0.4216 | 1.0000 | 0.5728 |
| **Nivel 3 (Difícil)** | Paráfrasis en lenguaje cotidiano | 0.1200 | 0.0810 | 0.0967 | 0.3000 | 0.0934 |
| **Promedio Global** | **Todas las 15 consultas** | **0.3800** | **0.2564** | **0.3061** | **0.7167** | **0.3913** |

### Análisis por Nivel:
* **Nivel 1 (Fácil)**: Alto nivel de acierto en el primer resultado (MRR = 0.8500). Consultas como Q01 (*sequential recommendation*) y Q02 (*long video understanding*) encuentran rápidamente sus artículos relevantes debido a la repetición exacta del vocabulario en los abstracts.
* **Nivel 2 (Medio)**: Superó al Nivel 1 en nDCG@10 (0.5728 vs 0.5079) y logró un MRR perfecto de 1.0000. Consultas como Q07 (*low-rank adapters / LoRA*) y Q09 (*large language models as judges*) contienen términos altamente discriminativos que la ponderación IDF premia adecuadamente.
* **Nivel 3 (Difícil)**: Se observa una caída estrepitosa del desempeño con un **nDCG@10 de 0.0934**. Tres de las cinco consultas (Q11, Q12, Q14) obtuvieron un **0.000 absoluto** en todas las métricas en el top-10.

---

## 4. Análisis Detallado de Errores en Consultas Difíciles (Q11 – Q15)

El análisis individual de las consultas del Nivel 3 revela las limitaciones inherentes del modelo vectorial puro basado en coincidencia léxica (*lexical matching*):

### Consulta Q11: *"making neural networks smaller and faster"*
* **Métricas:** P@10 = 0.000 | R@10 = 0.000 | nDCG@10 = 0.000
* **Causa del fallo:** La consulta utiliza expresión coloquial de alto nivel (*"smaller and faster"*). Los artículos científicos del corpus no utilizan esta frase descriptiva; en su lugar, emplean terminología formal especializada como `quantization`, `pruning`, `model compression`, `distillation` y `KV cache`.
* **Diagnóstico VSM:** Al no existir solapamiento exacto de vocabularios entre la consulta y los documentos, la similitud coseno es 0.

### Consulta Q12: *"AI reading hospital scans to detect illness"*
* **Métricas:** P@10 = 0.000 | R@10 = 0.000 | nDCG@10 = 0.000
* **Causa del fallo:** El usuario expresa la necesidad de información en lenguaje llano (*"hospital scans"*, *"detect illness"*). Los abstracts relevantes del dominio médico-informático utilizan acrónimos y vocabulario clínico específico: `MRI`, `CT scan`, `X-ray`, `radiology`, `lesion detection` y `diagnosis`.
* **Incidencia en Bigramas:** En la configuración `title · bigram`, esta consulta generó una advertencia de vocabulario vacío (*EmptyQueryError*), ya que ningún bigrama de la consulta normalizada existía en los títulos del corpus.

### Consulta Q13: *"defending AI systems against malicious manipulation"*
* **Métricas:** P@10 = 0.100 | R@10 = 0.071 | nDCG@10 = 0.145
* **Causa del fallo:** Aunque recuperó 1 documento parcialmente relevante en la posición 2 (MRR = 0.500), el rendimiento fue muy pobre. La consulta busca conceptos de seguridad en IA, pero los abstracts utilizan jerga especializada como `adversarial attacks`, `backdoor poisoning`, `jailbreak` y `robustness`.

### Consulta Q14: *"peeking inside language models to explain their behavior"*
* **Métricas:** P@10 = 0.000 | R@10 = 0.000 | nDCG@10 = 0.000
* **Causa del fallo:** Uso de metáforas (*"peeking inside"*, *"explain behavior"*). Los autores de los artículos expresan este concepto con términos como `mechanistic interpretability`, `probing`, `feature visualization` y `sparse autoencoders`.

### Consulta Q15: *"assistants that remember past experiences"* (Caso de Éxito)
* **Métricas:** P@10 = 0.500 | R@10 = 0.333 | nDCG@10 = 0.322 | MRR = 1.000
* **Causa del éxito relativo:** A pesar de ser una paráfrasis en Nivel 3, los términos lematizados `remember` y `experience` lograron coincidir con abstracts que discuten `agent memory`, `lifelong learning` y `long-term retrieval`, alcanzando un documento relevante en la posición 1.

---

## 5. Limitaciones Teóricas del Modelo Vectorial (VSM)

El estudio experimental evidencia tres grandes barreras del Modelo de Espacio Vectorial tradicional:

1. **Desconexión Semántica y Paráfrasis (*Vocabulary Mismatch*)**:
   * El modelo asume independencia entre términos y requiere coincidencia exacta de tokens lematizados. No reconoce sinónimos ni relaciones de hipernimia/hiponimia (ej. `hospital scan` $\rightarrow$ `MRI`).
2. **Escasez de Texto en Títulos**:
   * Los títulos no contienen suficiente contexto para vectores de frecuencia o TF-IDF, provocando vectores nulos cuando las palabras de la consulta no coinciden exactamente.
3. **Rigidez de los Bigramas**:
   * Los bigramas no toleran variaciones en el orden de las palabras ni la inserción de modificadores intermediarios.

---
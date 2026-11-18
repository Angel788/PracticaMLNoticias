# K-Means: selección, evaluación e interpretación

Configuración final: **K02_k4_N2_tfidf_1-1_svd100** (K02).

- k = 4; normalización N2; representación tfidf; n-gramas (1, 1); SVD 100; init k-means++, n_init 10, max_iter 300.
- Silhouette (coseno, espacio SVD+L2): train+dev **0.0395**, test **0.0829**.
- ARI test **0.3719**, NMI test **0.4860** (solo interpretación externa; K-Means no vio las etiquetas).
- Tamaños finales: 0: 192, 1: 156, 2: 113, 3: 39.

## Palabras y documentos representativos

### Cluster 0 (192 documentos)
**Palabras:** training, task, language, token, datum, improve, prompt, target, base, reasoning
**Representativos:** 2610.00673,2609.23449

### Cluster 1 (156 documentos)
**Palabras:** retrieval, evidence, item, recommendation, query, user, base, agent, language, search
**Representativos:** 2609.38473,2609.37574

### Cluster 2 (113 documentos)
**Palabras:** video, image, visual, generation, scene, training, physical, benchmark, introduce, representation
**Representativos:** 2609.40347,2610.00812

### Cluster 3 (39 documentos)
**Palabras:** parameter, training, learn, attention, cost, scale, noise, long, introduce, feature
**Representativos:** 2610.00545,2609.39855


## Lectura

- El silhouette de texto es bajo por naturaleza (0.02-0.10 es habitual); se interpreta comparando configuraciones, no como una medida absoluta.
- En la práctica, los cuatro clusters se leen como NLP/agentes (0), IR/recomendación (1), visión/vídeo (2) y ML general (3).
- El cluster 3 es pequeño (39 documentos) y concentra cs.LG; no se fusionó porque sus palabras (parameter, attention, scale, feature) son claramente de aprendizaje automático.
- K-Means agrupa por vocabulario dominante; los clusters no tienen por qué coincidir con las 4 categorías de arXiv. El ARI/NMI y la tabla de contingencia solo cuantifican ese parecido.
- k = 4 surgió de la comparación de K-1; no se impuso. Los tamaños 192/156/113/39 son razonables, aunque el cluster 3 es el más pequeño.

## Tabla de contingencia en test

| Gold | cluster 0 | cluster 1 | cluster 2 | cluster 3 |
|---|---:|---:|---:|---:|
| cs.CL | 13 | 5 | 1 | 0 |
| cs.CV | 4 | 2 | 13 | 0 |
| cs.IR | 1 | 18 | 0 | 0 |
| cs.LG | 12 | 0 | 0 | 6 |

El cluster 1 captura casi todo `cs.IR` (18/19) y el cluster 2 casi todo `cs.CV` (13/19). El cluster 0 mezcla `cs.CL` y `cs.LG`, que es justo la frontera que también confunde al clasificador. El cluster 3 concentra 6 de los 18 `cs.LG` y no recibe documentos de otras clases.

## Selección final
La cadena automática por silhouette terminó en **K16** (dev 0.2085), pero sus clusters separan artefactos de formato (LaTeX, números, longitud) y su ARI/NMI es cercano a 0. El plan advierte que el silhouette solo se compara dentro del mismo espacio de características; entre espacios distintos hay que apoyarse en la interpretabilidad.

Dentro de N2 + TF-IDF (1,1) + SVD 100, **K02** (k=4) tiene silhouette dev 0.0660, prácticamente empatado con el máximo del espacio (0.0664), y sus cuatro clusters son temáticos: NLP/agentes, ML general, IR/recomendación y visión/vídeo. Se elige por interpretabilidad y equilibrio de tamaños; ARI/NMI no se usaron para seleccionar.

| Bloque | Ganador automático | k | silhouette dev |
|---|---|---:|---:|
| K-1 | K01 | 3 | 0.0651 |
| K-2 | K06 | 3 | 0.0986 |
| K-3 | K08 | 3 | 0.1727 |
| K-4 | K09 | 3 | 0.1873 |
| K-5 | K11 | 3 | 0.2085 |
| K-6 | K16 | 3 | 0.2085 |

La estabilidad de K02 es moderada (0.234); las configuraciones con estabilidad casi perfecta también son las que separan formato, no temas. El silhouette de texto es bajo por naturaleza.

## K-3 binaria (K17)
- Se añadió la representación binaria para completar las tres opciones de K-3.
- Silhouette dev 0.0477, ARI dev -0.0038, estabilidad 0.415.
- No mejora a TF-IDF (0.0660/0.3755) ni a frecuencia en silhouette; los clusters no se alinean con las categorías.

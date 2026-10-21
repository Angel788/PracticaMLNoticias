# Notas de anotación del benchmark 

**Cómo se anotó:** se buscó por palabras clave en `data/scientific_raw_corpus.tsv` (término principal, sinónimos, siglas y variantes) y se leyeron título y abstract de cada candidato. No se ejecutó `src/retrieve.py` ni la API con estas consultas.

**Criterio:** 2 = el abstract trata directamente el tema; 1 = lo trata de forma parcial o como componente. Los que solo comparten palabras no se anotan.

| ID | Nivel | Consulta | Rel. 2 / 1 | Categoría principal | Patrones buscados | Por qué ese nivel |
|---|---|---|---:|---|---|---|
| Q01 | easy | sequential recommendation with user behavior sequences | 9 / 9 | cs.IR | `sequential recommend`, `session-based`, `user behavior`, `behavior sequence`, `user history`, `generative recommend`, `semantic id` | Mismos términos que los abstracts, tema concreto de una categoría |
| Q02 | easy | long video understanding with vision-language models | 9 / 6 | cs.CV | `long video`, `temporal grounding`, `video question`, `video understanding`, `video-language`, `egocentric video`, `keyframe` | Vocabulario técnico compartido |
| Q03 | easy | reranking retrieved documents with large language models | 8 / 9 | cs.IR | `rerank`, `re-rank`, `cross-encoder`, `listwise`, `late interaction` | Término muy específico (*rerank*) |
| Q04 | easy | video generation with diffusion models | 10 / 7 | cs.CV | `video generat`, `video diffusion`, `text-to-video`, `image-to-video`, `talking`, `avatar`, `try-on`, `world model` | Tema concreto de cs.CV; *diffusion* aparece también en otros contextos |
| Q05 | easy | retrieval-augmented generation for multi-hop question answering | 9 / 9 | cs.IR | `retrieval-augmented`, `rag`, `graphrag`, `multi-hop`, `question answering` | Mismos términos y siglas que los abstracts |
| Q06 | medium | on-policy self-distillation for reasoning models | 9 / 4 | cs.CL | `distill`, `self-distill`, `on-policy` | *Distillation* tiene varios sentidos (compresión, difusión, visión); solo algunos combinan *on-policy* con razonamiento |
| Q07 | medium | parameter-efficient fine-tuning with low-rank adapters | 5 / 12 | cs.LG | `lora`, `qlora`, `parameter-efficient`, `low-rank adapt`, `adapter`, `peft` | Muchos abstracts usan LoRA solo como herramienta (relevancia 1) y dicen *LoRA* en vez de *low-rank adapters* |
| Q08 | medium | policy optimization in reinforcement learning | 13 / 9 | cs.LG | `reinforcement learning`, `policy optimization`, `grpo`, `policy gradient`, `rl`, `markov decision`, `actor-critic` | Tema amplio que cruza RL clásico y RL para LLMs; *policy* también tiene otros sentidos |
| Q09 | medium | large language models as judges for evaluation | 7 / 12 | cs.IR / cs.CL | `judge`, `llm-as-a`, `evaluator`, `automatic evaluation`, `relevance judgment` | Combina dos conceptos; *evaluation* aparece en casi todos los abstracts |
| Q10 | medium | multilingual language models for low-resource languages | 10 / 9 | cs.CL | `multilingual`, `low-resource`, `cross-lingual`, `languages`, nombres de idiomas (`arabic`, `bengali`, `romanian`, `yorùbá`, …) | Muchos relevantes nombran el idioma concreto en vez de *low-resource* |
| Q11 | hard | making neural networks smaller and faster | 7 / 9 | cs.LG | `quantiz`, `pruning`, `compress`, `slimm`, `kv cache`, `speculative`, `low-precision` | Paráfrasis: los abstracts dicen *quantization*, *pruning*, *compression* |
| Q12 | hard | AI reading hospital scans to detect illness | 6 / 5 | cs.CV | `medical`, `clinical`, `patient`, `diagnos`, `mri`, `x-ray`, `radiology`, `health` | Paráfrasis: los relevantes dicen *MRI*, *X-ray*, *radiology*, *diagnosis* |
| Q13 | hard | defending AI systems against malicious manipulation | 9 / 5 | cs.CV / cs.LG | `adversarial`, `attack`, `backdoor`, `jailbreak`, `poison`, `watermark` | Paráfrasis: *adversarial*, *backdoor* y *poisoning* no aparecen en la consulta; tema transversal |
| Q14 | hard | peeking inside language models to explain their behavior | 11 / 5 | cs.CL | `interpretab`, `mechanistic`, `probing`, `probe`, `logit lens`, `sparse autoencoder`, `steering`, `residual stream` | Paráfrasis de *interpretability* y *mechanistic*; *language models* aparece en cientos de abstracts no relevantes |
| Q15 | hard | assistants that remember past experiences | 9 / 6 | mezclada | `memory`, `experience`, `remember`, `long-term`, `lifelong`, `past interaction` | Paráfrasis de *agent memory*; repartida en las 4 categorías |

**Totales:** 247 juicios. Por consulta hay entre 11 y 22 relevantes y 5 consultas de cada nivel. Por categoría principal: cs.IR 4, cs.CV 4, cs.CL 3, cs.LG 3 y 1 mezclada.

## Casos dudosos para la revisión

- **Q01:** los recomendadores generativos con *semantic IDs* (2609.29973, 2609.29983, 2609.39828) se marcaron como 1 porque predicen el siguiente ítem a partir del historial, pero no hablan de *sequential recommendation*.
- **Q07:** solo 5 documentos tienen relevancia 2, porque la mayoría usa LoRA como herramienta.
- **Q09:** 2610.00825 (juez multimodal de *lip-sync*) y 2610.00369 (sesgo de LLM como seleccionadores) se marcaron como 1.
- **Q11:** la decodificación especulativa y la poda de KV cache (más rápido, pero no más pequeño) se marcaron como 1.
- **Q12:** se limitó a **imagen médica**. Los trabajos clínicos solo de texto (2610.00562, 2609.39049, 2609.38543, …) no se anotaron. Si el equipo prefiere "IA en salud" en general, hay que cambiar el texto de la consulta y no solo los qrels.
- **Q13:** 2610.00680 usa MedMNIST, pero se anotó por el tema de los fallos adversariales y no por el dominio médico.

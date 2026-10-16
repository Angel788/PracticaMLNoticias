"""Normalización de textos (corpus y consultas) con spaCy.

Es la misma función del notebook 02. Corpus y consultas deben pasar por aquí
para que sus términos coincidan con el vocabulario de los vectorizadores.
"""
from functools import lru_cache

import spacy

SPACY_MODEL = "en_core_web_sm"

# Etiquetas POS (universales de spaCy) que se consideran stopwords y se eliminan.
STOP_POS = {
    "DET",    # determinantes: the, a, an, this, each
    "ADP",    # preposiciones: of, in, on, with, from
    "CCONJ",  # conjunciones coordinantes: and, or, but
    "SCONJ",  # conjunciones subordinantes: that, because, if, while
    "PRON",   # pronombres: we, it, they, which
    "AUX",    # verbos auxiliares: be, have, can, will (decisión del equipo, no la pide el enunciado)
}


@lru_cache(maxsize=1)
def get_nlp():
    # ner no cambia lemas ni POS (verificado en el notebook 02) y se desactiva por velocidad
    return spacy.load(SPACY_MODEL, disable=["ner"])


def normalize_doc(doc) -> str:
    return " ".join(
        t.lemma_.lower() for t in doc
        if not (t.is_punct or t.is_space) and t.pos_ not in STOP_POS
    )


def normalize(text: str) -> str:
    """Normaliza un texto suelto (documento o consulta)."""
    return normalize_doc(get_nlp()(text))

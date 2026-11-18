"""Interfaz web de la Etapa II con FastAPI.

Clasifica un título + abstract nuevo con el modelo final (C02: LogisticRegression,
N2, TF-IDF (1,1), C=1, min_df=1, reajustado con train+dev) y lo asigna a un cluster
de K-Means (K02: k=4, N2, TF-IDF (1,1), SVD 100). También muestra los resultados
congelados de results/etapa2/.

Uso (con el entorno .venv activo):
    python -m src.etapa2.api               # desde la raíz del repositorio
    python ../src/etapa2/api.py            # desde Etapa2/, o la ruta que toque
    -> http://127.0.0.1:8001

Rutas:
    GET  /              página
    POST /api/classify  {"text": "..."} -> probabilidades, términos y cluster
    GET  /api/example   un artículo de test al azar
    GET  /api/results   métricas, matrices, clusters y experimentos
    GET  /docs          documentación interactiva (Swagger)
"""
import random
import sys
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

from src.etapa2.classify import make_vectorizer
from src.etapa2.config import CLASSES, RANDOM_STATE, RAW_CORPUS_PATH, RESULTS_DIR
from src.etapa2.labels import load_labeled
from src.etapa2.normalization import load_variants
from src.normalize import get_nlp, normalize_doc

PAGE_PATH = Path(__file__).resolve().parent / "web" / "index.html"
CONFUSION_DIR = RESULTS_DIR / "confusion_matrices"

# Lectura de cluster_analysis.md
CLUSTER_NAMES = {0: "NLP y agentes", 1: "IR y recomendación",
                 2: "Visión y vídeo", 3: "ML general"}


# Lee un TSV de results/etapa2 sin convertir los valores.
def read_tsv(name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / name, sep="\t", dtype=str, keep_default_na=False)


class Models:
    """Modelos finales reajustados con train+dev, igual que en final.py y cluster.py."""

    # Ajusta C02 y K02 con train+dev al iniciar la API.
    def __init__(self) -> None:
        df = load_labeled()
        texts = load_variants().set_index("document_id")["text_n2"]
        train_dev = df[df["split"].isin(["train", "dev"])]
        X = texts.loc[train_dev["document_id"]].tolist()

        self.clf = Pipeline([
            ("vec", make_vectorizer("tfidf", (1, 1))),
            ("clf", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ]).set_params(clf__C=1.0, vec__min_df=1)
        self.clf.fit(X, train_dev["label"])

        self.km = Pipeline([
            ("vec", make_vectorizer("tfidf", (1, 1))),
            ("svd", TruncatedSVD(n_components=100, random_state=RANDOM_STATE)),
            ("l2", Normalizer()),
            ("km", KMeans(n_clusters=4, init="k-means++", n_init=10,
                          max_iter=300, random_state=RANDOM_STATE)),
        ])
        self.km.fit(X)

        raw = pd.read_csv(RAW_CORPUS_PATH, sep="\t", dtype=str, keep_default_na=False)
        self.raw = raw.set_index("arxiv_id")
        self.test_ids = df.loc[df["split"] == "test", "document_id"].tolist()
        self.gold = dict(zip(df["document_id"], df["label"]))

    # Normaliza el texto, predice clase, cluster y términos influyentes.
    def classify(self, text: str) -> dict:
        norm = normalize_doc(get_nlp()(text))
        vec = self.clf.named_steps["vec"]
        lr = self.clf.named_steps["clf"]
        x = vec.transform([norm])
        if x.nnz == 0:
            raise ValueError("Ningún término del texto está en el vocabulario del modelo.")

        proba = lr.predict_proba(x)[0]
        order = list(lr.classes_)
        best = order[int(np.argmax(proba))]

        # Contribución de cada término a la clase ganadora: peso TF-IDF × coeficiente
        coef = lr.coef_[order.index(best)]
        idx = x.indices
        contrib = x.data * coef[idx]
        names = vec.get_feature_names_out()
        top = sorted(zip(idx, contrib), key=lambda t: -t[1])[:8]
        terms = [{"term": names[i], "weight": float(w)} for i, w in top if w > 0]

        # Distancia euclídea a cada centroide en el espacio SVD + L2 (predict elige la menor).
        # Cercanía = 1 − d/2, en [0, 1] porque el vector es unitario y ‖centroide‖ ≤ 1.
        dist = self.km.transform([norm])[0]
        cluster = int(np.argmin(dist))
        closeness = [{"id": i, "name": CLUSTER_NAMES[i], "distance": float(d),
                      "closeness": float(max(0.0, 1 - d / 2))}
                     for i, d in enumerate(dist)]
        return {
            "prediction": best,
            "probabilities": [{"label": c, "p": float(proba[order.index(c)])}
                              for c in CLASSES],
            "terms": terms,
            "cluster": {"id": cluster, "name": CLUSTER_NAMES[cluster], "closeness": closeness},
            "normalized": norm,
            "known_terms": int(x.nnz),
        }


MODELS: Models | None = None


# Carga spaCy y ajusta los modelos finales al arrancar la API.
@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODELS
    get_nlp()
    MODELS = Models()
    yield


app = FastAPI(title="Etapa II · Clasificación y clustering", lifespan=lifespan)


class ClassifyIn(BaseModel):
    text: str = Field(..., min_length=1, description="título y abstract en inglés")


# Endpoint POST /api/classify: clasifica un texto nuevo.
@app.post("/api/classify")
def classify(body: ClassifyIn):
    try:
        return MODELS.classify(body.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# Endpoint GET /api/example: devuelve un artículo de test al azar.
@app.get("/api/example")
def example():
    doc_id = random.choice(MODELS.test_ids)
    row = MODELS.raw.loc[doc_id]
    return {
        "arxiv_id": doc_id,
        "title": " ".join(row["title"].split()),
        "abstract": " ".join(row["abstract"].split()),
        "gold": MODELS.gold[doc_id],
        "url": row["url"],
    }


# Lee una matriz de confusión y la convierte en listas JSON.
def confusion(name: str) -> dict:
    cm = pd.read_csv(CONFUSION_DIR / name, sep="\t", index_col=0)
    return {"labels": list(cm.columns), "rows": cm.values.tolist()}


# Arma el JSON con métricas, clusters, contingencia y experimentos.
@lru_cache
def results_payload() -> dict:
    metrics = read_tsv("classification_metrics.tsv")
    per_class = read_tsv("classification_per_class.tsv")
    summary = read_tsv("cluster_summary.tsv")
    contingency = pd.read_csv(RESULTS_DIR / "cluster_contingency_test.tsv",
                              sep="\t", index_col=0)
    experiments = read_tsv("experiments.tsv")

    clusters = []
    for _, row in summary.iterrows():
        cid = int(row["cluster_id"])
        docs = []
        for doc_id in filter(None, row["representative_document_ids"].split(",")):
            title = MODELS.raw.loc[doc_id, "title"] if doc_id in MODELS.raw.index else ""
            docs.append({"arxiv_id": doc_id, "title": " ".join(title.split()),
                         "label": MODELS.gold.get(doc_id, "")})
        clusters.append({
            "id": cid, "name": CLUSTER_NAMES[cid], "size": int(row["size"]),
            "top_words": row["top_words"].split(", "), "representatives": docs,
        })

    return {
        "metrics": metrics.to_dict(orient="records"),
        "per_class": per_class.to_dict(orient="records"),
        "confusion": {"test": confusion("test.tsv"), "C02_dev": confusion("C02_dev.tsv")},
        "clusters": clusters,
        "contingency": {"labels": list(contingency.index),
                        "clusters": [int(c) for c in contingency.columns],
                        "rows": contingency.values.tolist()},
        "experiments": experiments.to_dict(orient="records"),
    }


# Endpoint GET /api/results: devuelve el payload anterior.
@app.get("/api/results")
def results():
    return results_payload()


# Endpoint GET /: sirve la página web.
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(PAGE_PATH)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)

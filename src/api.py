"""Interfaz web de la recuperación con FastAPI.

Mismos parámetros que src/retrieve.py: query, field, ngram, repr y k.

Uso desde la raíz del repositorio:
    python -m src.api                      # http://127.0.0.1:8000
    uvicorn src.api:app --reload           # alternativa, recarga al editar

Rutas:
    GET /          formulario de búsqueda
    GET /search    resultados en JSON, p. ej. /search?query=video+understanding&field=title&repr=binary
    GET /docs      documentación interactiva (Swagger) generada por FastAPI
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402

from src.normalize import get_nlp, normalize  # noqa: E402
from src.retrieve import EmptyQueryError, load_docs, retrieve  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga spaCy y el corpus al arrancar para que la primera búsqueda no tarde
    get_nlp()
    load_docs()
    yield


app = FastAPI(title="Recuperación de artículos científicos (VSM)", lifespan=lifespan)


@app.get("/search")
def search(
    query: str = Query(..., min_length=1, description="consulta en texto libre"),
    field: Literal["title", "abstract"] = "abstract",
    ngram: Literal["unigram", "bigram"] = "unigram",
    repr: Literal["frequency", "binary", "tfidf"] = "tfidf",
    k: int = Query(10, ge=1, le=100, description="número de resultados"),
):
    query_norm = normalize(query)
    try:
        ranking = retrieve(query, field, ngram, repr, k)
    except EmptyQueryError as e:
        raise HTTPException(status_code=422, detail={"message": str(e), "query_norm": query_norm})
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail={"message": str(e)})

    return {
        "query": query,
        "query_norm": query_norm,
        "config": {"field": field, "ngram": ngram, "repr": repr, "k": k},
        "n_results": len(ranking),
        "results": ranking.to_dict(orient="records"),
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE


PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Búsqueda VSM</title>
<style>
  :root { --bg:#fafafa; --fg:#1d1d1f; --muted:#6b6b70; --line:#e2e2e6; --accent:#2457d6; --card:#fff; --warn:#a15c00; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#141416; --fg:#ececf0; --muted:#9a9aa3; --line:#2c2c31; --accent:#7ea2ff; --card:#1c1c20; --warn:#f0b35a; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; }
  main { max-width:900px; margin:0 auto; padding:24px 16px; }
  h1 { font-size:20px; margin:0 0 16px; }
  form { display:grid; gap:10px; grid-template-columns:1fr; }
  .row { display:flex; flex-wrap:wrap; gap:10px; }
  input, select, button { font:inherit; padding:8px 10px; border:1px solid var(--line); border-radius:6px; background:var(--card); color:var(--fg); }
  input[name=query] { width:100%; }
  input[name=k] { width:80px; }
  button { background:var(--accent); color:#fff; border:none; cursor:pointer; padding:8px 18px; }
  label { display:flex; flex-direction:column; font-size:12px; color:var(--muted); gap:2px; }
  #meta { color:var(--muted); font-size:13px; margin:18px 0 8px; }
  #meta code { color:var(--fg); }
  .warn { color:var(--warn); }
  .res { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 14px; margin-bottom:10px; }
  .res h2 { font-size:15px; margin:0 0 4px; }
  .res .info { font-size:12px; color:var(--muted); margin-bottom:6px; font-variant-numeric:tabular-nums; }
  .res a { color:var(--accent); text-decoration:none; }
  .res p { margin:0; font-size:14px; }
  .res details summary { cursor:pointer; color:var(--accent); font-size:13px; margin-top:4px; }
</style>
</head>
<body>
<main>
  <h1>Recuperación de artículos científicos</h1>
  <form id="f">
    <input name="query" placeholder="p. ej. reranking documents with large language models" required>
    <div class="row">
      <label>Campo<select name="field"><option>abstract</option><option>title</option></select></label>
      <label>N-grama<select name="ngram"><option>unigram</option><option>bigram</option></select></label>
      <label>Representación<select name="repr"><option>tfidf</option><option>frequency</option><option>binary</option></select></label>
      <label>k<input name="k" type="number" value="10" min="1" max="100"></label>
      <label>&nbsp;<button>Buscar</button></label>
    </div>
  </form>
  <div id="meta"></div>
  <div id="out"></div>
</main>
<script>
const f = document.getElementById("f"), meta = document.getElementById("meta"), out = document.getElementById("out");
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
f.addEventListener("submit", async e => {
  e.preventDefault();
  const params = new URLSearchParams(new FormData(f));
  meta.textContent = "Buscando…"; out.innerHTML = "";
  const r = await fetch("/search?" + params);
  const data = await r.json();
  if (!r.ok) {
    const d = data.detail || {};
    meta.innerHTML = (d.query_norm !== undefined ? `Normalizada: <code>${esc(d.query_norm)}</code><br>` : "")
      + `<span class="warn">${esc(d.message || JSON.stringify(d))}</span>`;
    return;
  }
  const c = data.config;
  meta.innerHTML = `Normalizada: <code>${esc(data.query_norm)}</code> · ${c.field} · ${c.ngram} · ${c.repr} · ${data.n_results} resultados`
    + (data.n_results < c.k ? ` <span class="warn">(solo ${data.n_results} comparten algún término)</span>` : "");
  out.innerHTML = data.results.map(d => `
    <div class="res">
      <h2>${d.rank}. ${esc(d.title)}</h2>
      <div class="info">score ${d.score.toFixed(4)} · ${esc(d.source)} · ${esc(d.primary_category)} · ${esc(d.date)}
        · <a href="${esc(d.url)}" target="_blank">${d.arxiv_id}</a> · <a href="${esc(d.pdf_url)}" target="_blank">PDF</a>
        ${d.doi ? `· <a href="https://doi.org/${esc(d.doi)}" target="_blank">DOI</a>` : ""}</div>
      <div class="info">${esc(d.authors)}</div>
      <details><summary>Abstract</summary><p>${esc(d.abstract)}</p></details>
    </div>`).join("");
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api:app", host="127.0.0.1", port=8000)

"""
Fase 7 · CLI Unificada para Recuperación de Artículos Científicos (VSM).

Punto de entrada único que centraliza el flujo del proyecto:
  - collect:   recolección de artículos desde la API de arXiv.
  - build:     normalización del corpus y generación de los 12 modelos .pkl.
  - query:     búsqueda individual sobre el corpus.
  - benchmark: evaluación y cálculo de métricas sobre el benchmark.

Uso desde la raíz del repositorio:
  python -m src.cli collect --categories cs.CL cs.CV cs.IR cs.LG --max 500
  python -m src.cli build
  python -m src.cli query "video understanding with multimodal models" --field abstract --ngram unigram --repr binary -k 5
  python -m src.cli benchmark --all
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not __package__:
    sys.path.insert(0, str(ROOT))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Interfaz de línea de comandos unificada para Recuperación de Artículos Científicos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Subcomando a ejecutar (collect, build, query, benchmark)",
    )

    # ------------------------------------------------------------------ Subcomando: collect
    p_collect = subparsers.add_parser(
        "collect",
        help="Recolecta artículos científicos desde la API de arXiv.",
    )
    p_collect.add_argument(
        "--categories",
        nargs="+",
        default=["cs.CL", "cs.CV", "cs.IR", "cs.LG"],
        help="Categorías de arXiv a recolectar (por defecto: cs.CL cs.CV cs.IR cs.LG)",
    )
    p_collect.add_argument(
        "--max",
        type=int,
        default=500,
        dest="max_docs",
        help="Número máximo de artículos a recolectar (por defecto: 500)",
    )

    # ------------------------------------------------------------------ Subcomando: build
    p_build = subparsers.add_parser(
        "build",
        help="Normaliza el corpus y genera los 12 modelos vectoriales (.pkl).",
    )

    # ------------------------------------------------------------------ Subcomando: query
    p_query = subparsers.add_parser(
        "query",
        help="Ejecuta una búsqueda individual sobre el corpus.",
    )
    p_query.add_argument("query", type=str, help="Texto de la consulta de búsqueda")
    p_query.add_argument(
        "--field",
        choices=["title", "abstract"],
        default="abstract",
        help="Campo del artículo a consultar (por defecto: abstract)",
    )
    p_query.add_argument(
        "--ngram",
        choices=["unigram", "bigram"],
        default="unigram",
        help="Tipo de n-grama (por defecto: unigram)",
    )
    p_query.add_argument(
        "--repr",
        dest="repr_",
        choices=["tfidf", "binary", "frequency"],
        default="tfidf",
        help="Tipo de representación (por defecto: tfidf)",
    )
    p_query.add_argument(
        "-k",
        type=int,
        default=10,
        help="Número de resultados a recuperar (por defecto: 10)",
    )
    p_query.add_argument(
        "--chars",
        type=int,
        default=300,
        help="Caracteres del abstract a mostrar (0 = completo, por defecto: 300)",
    )

    # ------------------------------------------------------------------ Subcomando: benchmark
    p_bench = subparsers.add_parser(
        "benchmark",
        help="Valida y evalúa el benchmark de recuperación (Fases 5-6).",
    )
    p_bench.add_argument(
        "--field",
        choices=["title", "abstract"],
        default="abstract",
        help="Campo del artículo a evaluar (por defecto: abstract)",
    )
    p_bench.add_argument(
        "--ngram",
        choices=["unigram", "bigram"],
        default="unigram",
        help="Tipo de n-grama (por defecto: unigram)",
    )
    p_bench.add_argument(
        "--repr",
        dest="repr_",
        choices=["tfidf", "binary", "frequency"],
        default="tfidf",
        help="Tipo de representación (por defecto: tfidf)",
    )
    p_bench.add_argument(
        "--all",
        action="store_true",
        help="Evaluar las 12 configuraciones posibles",
    )
    p_bench.add_argument(
        "--check",
        action="store_true",
        help="Solo validar queries.tsv y qrels.tsv sin ejecutar consultas",
    )
    p_bench.add_argument(
        "--force",
        action="store_true",
        help="Forzar ejecución sin exigir el tag git de congelamiento",
    )

    args = parser.parse_args(argv)

    # ------------------------------------------------------------------ Ejecución
    if args.subcommand == "collect":
        try:
            from src.collect import main as collect_main
            return collect_main(["--categories"] + args.categories + ["--max", str(args.max_docs)])
        except (ImportError, AttributeError):
            try:
                from src.collect import collect
                collect(categories=args.categories, max_docs=args.max_docs)
                return 0
            except Exception as e:
                print(f"Error al ejecutar collect: {e}", file=sys.stderr)
                return 1

    elif args.subcommand == "build":
        print("=== Paso 1/2: Normalizando el corpus ===")
        try:
            from src.normalize import main as normalize_main
            normalize_main()
        except (ImportError, AttributeError):
            try:
                from src.normalize import normalize_corpus
                normalize_corpus()
            except Exception as e:
                print(f"Aviso en normalización: {e}", file=sys.stderr)

        print("\n=== Paso 2/2: Generando representaciones VSM (12 modelos .pkl) ===")
        try:
            from src.represent import main as represent_main
            return represent_main()
        except (ImportError, AttributeError):
            try:
                from src.represent import build_models
                build_models()
                return 0
            except Exception as e:
                print(f"Error en representación: {e}", file=sys.stderr)
                return 1

    elif args.subcommand == "query":
        try:
            from src.retrieve import main as retrieve_main
            query_argv = [
                args.query,
                "--field", args.field,
                "--ngram", args.ngram,
                "--repr", args.repr_,
                "-k", str(args.k),
                "--chars", str(args.chars),
            ]
            return retrieve_main(query_argv)
        except (ImportError, AttributeError):
            from src.retrieve import retrieve
            df = retrieve(args.query, field=args.field, ngram=args.ngram, repr_=args.repr_, k=args.k)
            print(df.to_string(index=False))
            return 0

    elif args.subcommand == "benchmark":
        try:
            from src.evaluate import main as evaluate_main
            bench_argv = [
                "--field", args.field,
                "--ngram", args.ngram,
                "--repr", args.repr_,
            ]
            if args.all:
                bench_argv.append("--all")
            if args.check:
                bench_argv.append("--check")
            if args.force:
                bench_argv.append("--force")
            return evaluate_main(bench_argv)
        except Exception as e:
            print(f"Error al ejecutar benchmark: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

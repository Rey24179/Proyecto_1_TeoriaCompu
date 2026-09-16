"""Exportación DOT y dibujos SVG/PNG de AFN y AFD mediante Graphviz."""

from pathlib import Path
import shutil
import subprocess

from .modelos import AFD, AFN


def _citar_dot(texto: str) -> str:
    """Protege las comillas, barras y saltos de línea de una etiqueta DOT."""
    texto = texto.replace("\\", "\\\\").replace('"', '\\"')
    texto = texto.replace("\r", "\\r").replace("\n", "\\n")
    return f'"{texto}"'


def _etiqueta_simbolo(simbolo: str) -> str:
    """Hace visibles los espacios y evita confundir una coma con el separador."""
    if simbolo.isspace() or not simbolo.isprintable() or simbolo in ",\"'\\":
        return repr(simbolo)
    return simbolo


def automata_a_dot(automata: AFN | AFD, titulo: str | None = None) -> str:
    """Describe todos los estados y transiciones, sin modificar el autómata.

    El estado inicial recibe una flecha de entrada y los finales doble círculo.
    Las transiciones con los mismos extremos se agrupan en una sola flecha.
    No requiere Graphviz instalado.
    """
    if not isinstance(automata, (AFN, AFD)):
        raise TypeError("Se esperaba un objeto AFN o AFD.")
    automata.validar()
    if titulo is None:
        titulo = "AFN" if isinstance(automata, AFN) else "AFD"
    estados = sorted(automata.estados)
    identificadores = {estado: f"s{indice}" for indice, estado in enumerate(estados)}
    lineas = [
        "digraph Automata {",
        '  graph [rankdir=LR, bgcolor="white", pad=0.3, nodesep=0.45, ranksep=0.65,',
        f'         fontname="Arial", fontsize=18, labelloc=t, label={_citar_dot(titulo)}];',
        '  node [fontname="Arial", fontsize=12, color="#334155", penwidth=1.5,',
        '        style=filled, fillcolor="#eff6ff", margin=0.08];',
        '  edge [fontname="Arial", fontsize=12, color="#475569", arrowsize=0.8];',
        '  __inicio [shape=point, width=0.08, label="", fillcolor="#334155"];',
    ]
    for estado in estados:
        final = estado in automata.estados_aceptacion
        forma = "doublecircle" if final else "circle"
        color = "#dcfce7" if final else "#eff6ff"
        lineas.append(
            f'  {identificadores[estado]} [label={_citar_dot(f"q{estado}")}, '
            f'shape={forma}, fillcolor="{color}"];'
        )
    lineas.append(f"  __inicio -> {identificadores[automata.estado_inicial]};")

    aristas: dict[tuple[int, int], set[str]] = {}
    for (origen, simbolo), destino in automata.transiciones.items():
        destinos = destino if isinstance(automata, AFN) else {destino}
        for estado in destinos:
            aristas.setdefault((origen, estado), set()).add(simbolo)
    for (origen, destino), simbolos in sorted(aristas.items()):
        etiqueta = ", ".join(_etiqueta_simbolo(simbolo) for simbolo in sorted(simbolos))
        lineas.append(
            f"  {identificadores[origen]} -> {identificadores[destino]} "
            f"[label={_citar_dot(etiqueta)}];"
        )
    lineas.append("}")
    return "\n".join(lineas) + "\n"


def _buscar_dot() -> str | None:
    """Busca Graphviz en PATH o en una distribución portátil local de Windows."""
    instalado = shutil.which("dot")
    if instalado:
        return instalado
    portable = Path(__file__).resolve().parents[1] / ".tools" / "graphviz"
    candidatos = [portable / "bin" / "dot.exe", *sorted(portable.glob("*/bin/dot.exe"))]
    return next((str(ruta) for ruta in candidatos if ruta.is_file()), None)


def dibujar_automata(
    automata: AFN | AFD,
    ruta: str | Path,
    titulo: str | None = None,
    *,
    ejecutable_dot: str | Path | None = None,
) -> Path:
    """Guarda DOT, SVG o PNG según la extensión y devuelve la ruta del archivo.

    SVG y PNG requieren el ejecutable dot de Graphviz. Los directorios se crean
    si faltan. Un archivo existente se reemplaza solo tras generar el contenido.
    El renderizado tiene un límite de 30 segundos y no abre ventanas.
    """
    ruta = Path(ruta)
    formato = ruta.suffix.lower().lstrip(".")
    if formato not in {"dot", "svg", "png"}:
        raise ValueError("La ruta debe terminar en .dot, .svg o .png.")
    dot = automata_a_dot(automata, titulo)

    if formato == "dot":
        contenido = dot.encode("utf-8")
    else:
        ejecutable = str(ejecutable_dot) if ejecutable_dot is not None else _buscar_dot()
        if not ejecutable:
            raise FileNotFoundError(
                "No se encontró Graphviz. Instala dot y agrégalo a PATH, coloca "
                "la versión portátil en .tools/graphviz o usa ejecutable_dot. "
                "Puedes exportar .dot sin instalar Graphviz. Consulta docs/visualizacion.md."
            )
        try:
            resultado = subprocess.run(
                [ejecutable, f"-T{formato}"],
                input=dot.encode("utf-8"),
                capture_output=True,
                check=True,
                timeout=30,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except FileNotFoundError as error:
            raise FileNotFoundError(f"No se encontró el ejecutable de Graphviz: {ejecutable}") from error
        except subprocess.CalledProcessError as error:
            detalle = error.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Graphviz no pudo generar el dibujo: {detalle}") from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("Graphviz superó el límite de 30 segundos.") from error
        contenido = resultado.stdout
        if not contenido:
            raise RuntimeError("Graphviz terminó sin producir un dibujo.")

    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
    return ruta

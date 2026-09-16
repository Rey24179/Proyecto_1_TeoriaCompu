"""Ejecutar desde la raíz con: python -m ejemplos.dibujar."""

from pathlib import Path

from automatas import afn_a_afd, dibujar_automata, minimizar_afd, regex_a_afn


def main() -> None:
    afn = regex_a_afn("(a|b)*abb")
    afd = afn_a_afd(afn)
    minimo = minimizar_afd(afd)
    carpeta = Path("salidas") / "ejemplo"
    automatas = (
        ("afn", afn, "AFN - Thompson"),
        ("afd", afd, "AFD - Subconjuntos"),
        ("afd_minimo", minimo, "AFD mínimo - Hopcroft"),
    )

    # Los archivos DOT se generan incluso cuando aún falta instalar Graphviz.
    for nombre, automata, titulo in automatas:
        print(dibujar_automata(automata, carpeta / f"{nombre}.dot", titulo))
    for nombre, automata, titulo in automatas:
        for formato in ("svg", "png"):
            print(dibujar_automata(automata, carpeta / f"{nombre}.{formato}", titulo))


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, RuntimeError) as error:
        raise SystemExit(str(error)) from None

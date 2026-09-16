"""Interfaz de consola. Ejecutar sin argumentos para abrir el menú."""

import argparse
from pathlib import Path
import sys

from automatas.analisis import OPERACIONES, ResultadoAnalisis, analizar_expresion
from automatas.archivos import ResultadoLinea, analizar_archivo
from automatas.modelos import AFN
from automatas.visualizacion import dibujar_automata


NOMBRES = {
    "afn": "AFN (Thompson)",
    "afd": "AFD (Subconjuntos)",
    "afd_minimo": "AFD mínimo (Hopcroft)",
    "afd_directo": "AFD directo (Followpos)",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Expresiones regulares y autómatas finitos. Sin argumentos: menú interactivo."
    )
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--regex", help="Expresión regular infix; usar comillas.")
    entrada.add_argument("--archivo", type=Path, help="Archivo UTF-8 con una expresión por línea.")
    parser.add_argument("--cadena", action="append", help="Cadena a simular. Se puede repetir; por defecto se evalúa la cadena vacía.")
    parser.add_argument("--operacion", choices=OPERACIONES, default="todo", help="Operación que se quiere mostrar (por defecto: todo).")
    parser.add_argument("--directo", action="store_true", help="Agregar el AFD directo a la operación todo.")
    parser.add_argument("--detalles", action="store_true", help="Mostrar los estados y las tablas de transiciones completas.")
    parser.add_argument("--dibujar", action="store_true", help="Guardar dibujos de los autómatas producidos.")
    parser.add_argument("--formato", nargs="+", choices=("svg", "png", "dot"), default=["svg"], help="Formatos de dibujo (por defecto: svg).")
    parser.add_argument("--salida", type=Path, default=Path("salidas"), help="Carpeta de dibujos (por defecto: salidas).")
    parser.add_argument("--dot", type=Path, help="Ruta personalizada al ejecutable dot de Graphviz.")
    return parser


def _mostrar(resultado: ResultadoAnalisis, cadenas: list[str], detalles: bool) -> bool:
    print(f"Expresión: {resultado.expresion}")
    print(f"Postfix: {resultado.postfix}")
    for nombre, automata in resultado.automatas.items():
        finales = ", ".join(f"q{q}" for q in sorted(automata.estados_aceptacion)) or "ninguno"
        print(f"{NOMBRES[nombre]}: {len(automata.estados)} estados; inicial q{automata.estado_inicial}; finales: {finales}")
        if detalles:
            print(f"  Estados: {sorted(automata.estados)}")
            print(f"  Alfabeto: {sorted(automata.alfabeto)!r}")
            print("  Transiciones:")
            if not automata.transiciones:
                print("    (sin transiciones)")
            for (origen, simbolo), destino in sorted(automata.transiciones.items()):
                destinos = sorted(destino) if isinstance(automata, AFN) else [destino]
                etiqueta = ", ".join(f"q{q}" for q in destinos) or "conjunto vacío"
                print(f"    q{origen} --{simbolo!r}--> {etiqueta}")

    consistente = True
    if resultado.automatas:
        for cadena in cadenas:
            print(f"Cadena {cadena!r}:")
            evaluaciones = resultado.simular(cadena)
            for nombre, aceptada in evaluaciones.items():
                print(f"  {NOMBRES[nombre]}: {'ACEPTADA' if aceptada else 'RECHAZADA'}")
            if len(set(evaluaciones.values())) > 1:
                print("ERROR: los autómatas no coinciden.", file=sys.stderr)
                consistente = False
    return consistente


def _menu_interactivo() -> int:
    opciones = {
        "1": "postfix", "2": "afn", "3": "afd", "4": "minimo",
        "5": "todo", "6": "todo", "7": "todo", "8": "directo",
    }
    while True:
        print("\nProyecto 1 - Teoría de la Computación")
        print("1. Infix a postfix\n2. Construir AFN\n3. Construir AFD\n4. Minimizar AFD")
        print("5. Simular en los tres autómatas\n6. Dibujar los tres autómatas")
        print("7. Procesar archivo de expresiones\n8. Construcción directa de AFD\n0. Salir")
        try:
            opcion = input("Opción: ").strip()
            if opcion == "0":
                return 0
            if opcion not in opciones:
                print("Opción inválida.")
                continue
            if opcion == "7":
                argumentos = ["--archivo=" + input("Ruta del archivo UTF-8: ").strip()]
            else:
                argumentos = ["--regex=" + input("Expresión regular (epsilon = ε): ")]
            argumentos.extend(["--operacion", opciones[opcion]])
            if opcion != "1":
                argumentos.append("--cadena=" + input("Cadena (Enter = vacía): "))
            if opcion in {"2", "3", "4", "8"}:
                argumentos.append("--detalles")
            if opcion == "6":
                formato = input("Formato svg, png o dot [svg]: ").strip().lower() or "svg"
                if formato not in {"svg", "png", "dot"}:
                    print("Formato inválido.")
                    continue
                argumentos.extend(["--dibujar", "--formato", formato])
        except EOFError:
            return 0
        main(argumentos)


def main(argv: list[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argv is None else argv)
    if not argumentos:
        return _menu_interactivo()
    parser = _parser()
    args = parser.parse_args(argumentos)
    if args.directo and args.operacion != "todo":
        parser.error("--directo solo puede combinarse con --operacion todo.")
    if args.dibujar and args.operacion == "postfix":
        parser.error("La operación postfix no genera un autómata para dibujar.")
    cadenas = args.cadena if args.cadena is not None else [""]
    try:
        if args.archivo is not None:
            lineas = analizar_archivo(args.archivo, args.operacion, incluir_directo=args.directo)
        else:
            resultado = analizar_expresion(args.regex, args.operacion, incluir_directo=args.directo)
            lineas = [ResultadoLinea(1, args.regex, resultado=resultado)]
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    if not lineas:
        print("El archivo no contiene expresiones regulares.")
        return 0

    hubo_error = False
    for linea in lineas:
        if args.archivo is not None:
            print(f"\nLínea {linea.numero}:")
        if linea.error is not None:
            print(f"Error en línea {linea.numero}: {linea.error}", file=sys.stderr)
            hubo_error = True
            continue
        resultado = linea.resultado
        if not _mostrar(resultado, cadenas, args.detalles):
            hubo_error = True
        if args.dibujar:
            subcarpeta = f"linea_{linea.numero:03d}" if args.archivo is not None else "individual"
            for nombre, automata in resultado.automatas.items():
                for formato in dict.fromkeys(args.formato):
                    ruta = args.salida / subcarpeta / f"{nombre}.{formato}"
                    try:
                        dibujar_automata(automata, ruta, NOMBRES[nombre], ejecutable_dot=args.dot)
                    except (OSError, RuntimeError, ValueError) as error:
                        print(f"Error al dibujar {nombre}: {error}", file=sys.stderr)
                        hubo_error = True
                    else:
                        print(f"Dibujo: {ruta}")
    return 1 if hubo_error else 0


if __name__ == "__main__":
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nEjecución cancelada.", file=sys.stderr)
        raise SystemExit(130)

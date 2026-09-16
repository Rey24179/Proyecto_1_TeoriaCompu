"""Lectura UTF-8 y procesamiento independiente de cada expresión por línea."""

from dataclasses import dataclass
from pathlib import Path

from .analisis import OPERACIONES, ResultadoAnalisis, analizar_expresion


@dataclass
class ResultadoLinea:
    numero: int
    expresion: str
    resultado: ResultadoAnalisis | None = None
    error: str | None = None


def leer_expresiones(ruta: str | Path) -> list[tuple[int, str]]:
    """Lee UTF-8 (con o sin BOM), omite líneas vacías y conserva su numeración."""
    expresiones = []
    with Path(ruta).open(encoding="utf-8-sig") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            expresion = linea.rstrip("\r\n")
            if expresion.strip():
                expresiones.append((numero, expresion))
    return expresiones


def analizar_archivo(
    ruta: str | Path, operacion: str = "todo", *, incluir_directo: bool = False
) -> list[ResultadoLinea]:
    """Continúa con las siguientes líneas si alguna expresión tiene mala sintaxis."""
    if operacion not in OPERACIONES:
        raise ValueError(f"Operación no soportada: {operacion}")
    if incluir_directo and operacion != "todo":
        raise ValueError("incluir_directo solo se combina con la operación 'todo'.")
    resultados = []
    for numero, expresion in leer_expresiones(ruta):
        try:
            resultado = analizar_expresion(expresion, operacion, incluir_directo=incluir_directo)
        except ValueError as error:
            resultados.append(ResultadoLinea(numero, expresion, error=str(error)))
        else:
            resultados.append(ResultadoLinea(numero, expresion, resultado=resultado))
    return resultados

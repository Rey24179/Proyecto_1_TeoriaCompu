"""Coordinación de las conversiones y simulación de sus resultados."""

from dataclasses import dataclass

from .directo import regex_a_afd_directo
from .hopcroft import minimizar_afd
from .modelos import AFD, AFN
from .regex import infix_a_postfix
from .simulacion import simular_afd, simular_afn
from .subconjuntos import afn_a_afd
from .thompson import postfix_a_afn


OPERACIONES = ("todo", "postfix", "afn", "afd", "minimo", "directo")


@dataclass
class ResultadoAnalisis:
    expresion: str
    postfix: str
    automatas: dict[str, AFN | AFD]

    def simular(self, cadena: str) -> dict[str, bool]:
        """Evalúa la misma cadena completa en cada autómata producido."""
        return {
            nombre: simular_afn(automata, cadena) if isinstance(automata, AFN)
            else simular_afd(automata, cadena)
            for nombre, automata in self.automatas.items()
        }


def analizar_expresion(
    expresion: str, operacion: str = "todo", *, incluir_directo: bool = False
) -> ResultadoAnalisis:
    """Realiza las operaciones seleccionadas y conserva los autómatas originales."""
    if operacion not in OPERACIONES:
        raise ValueError(f"Operación no soportada: {operacion}")
    if incluir_directo and operacion != "todo":
        raise ValueError("incluir_directo solo se combina con la operación 'todo'.")
    postfix = infix_a_postfix(expresion)
    automatas: dict[str, AFN | AFD] = {}
    if operacion in {"todo", "afn", "afd", "minimo"}:
        afn = postfix_a_afn(postfix)
        if operacion in {"todo", "afn"}:
            automatas["afn"] = afn
        if operacion in {"todo", "afd", "minimo"}:
            afd = afn_a_afd(afn)
            if operacion in {"todo", "afd"}:
                automatas["afd"] = afd
            if operacion in {"todo", "minimo"}:
                automatas["afd_minimo"] = minimizar_afd(afd)
    if operacion == "directo" or incluir_directo:
        automatas["afd_directo"] = regex_a_afd_directo(expresion)
    return ResultadoAnalisis(expresion, postfix, automatas)

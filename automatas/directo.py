"""Construcción directa de AFD con posiciones, firstpos, lastpos y followpos."""

from collections import deque
from dataclasses import dataclass

from .modelos import AFD, EPSILON
from .regex import infix_a_postfix


@dataclass
class _Nodo:
    anulable: bool
    primeros: set[int]
    ultimos: set[int]


def regex_a_afd_directo(expresion: str) -> AFD:
    """Construye un AFD completo desde infix sin construir un AFN intermedio.

    Cada aparición de un literal tiene su propia posición. El marcador final
    es una posición interna, por lo que no reserva ningún carácter del alfabeto.
    """
    postfix = infix_a_postfix(expresion)
    simbolos: dict[int, str] = {}
    siguientes: dict[int, set[int]] = {}
    pila: list[_Nodo] = []

    for simbolo in postfix:
        if simbolo == EPSILON:
            pila.append(_Nodo(True, set(), set()))
        elif simbolo in ".|":
            derecho, izquierdo = pila.pop(), pila.pop()
            if simbolo == "|":
                pila.append(_Nodo(
                    izquierdo.anulable or derecho.anulable,
                    izquierdo.primeros | derecho.primeros,
                    izquierdo.ultimos | derecho.ultimos,
                ))
            else:
                for posicion in izquierdo.ultimos:
                    siguientes[posicion].update(derecho.primeros)
                pila.append(_Nodo(
                    izquierdo.anulable and derecho.anulable,
                    izquierdo.primeros | (derecho.primeros if izquierdo.anulable else set()),
                    derecho.ultimos | (izquierdo.ultimos if derecho.anulable else set()),
                ))
        elif simbolo in "*+?":
            interior = pila.pop()
            if simbolo in "*+":
                for posicion in interior.ultimos:
                    siguientes[posicion].update(interior.primeros)
            pila.append(_Nodo(
                simbolo in "*?" or interior.anulable,
                interior.primeros,
                interior.ultimos,
            ))
        else:
            posicion = len(simbolos)
            simbolos[posicion] = simbolo
            siguientes[posicion] = set()
            pila.append(_Nodo(False, {posicion}, {posicion}))

    raiz = pila.pop()
    marcador = len(simbolos)
    siguientes[marcador] = set()
    for posicion in raiz.ultimos:
        siguientes[posicion].add(marcador)
    inicial = frozenset(raiz.primeros | ({marcador} if raiz.anulable else set()))

    alfabeto = set(simbolos.values())
    ordenados = sorted(alfabeto)
    identificadores = {inicial: 0}
    pendientes = deque([inicial])
    transiciones: dict[tuple[int, str], int] = {}
    finales: set[int] = set()
    while pendientes:
        posiciones = pendientes.popleft()
        origen = identificadores[posiciones]
        if marcador in posiciones:
            finales.add(origen)
        for simbolo in ordenados:
            destinos: set[int] = set()
            for posicion in posiciones:
                if simbolos.get(posicion) == simbolo:
                    destinos.update(siguientes[posicion])
            destino = frozenset(destinos)
            if destino not in identificadores:
                identificadores[destino] = len(identificadores)
                pendientes.append(destino)
            transiciones[(origen, simbolo)] = identificadores[destino]

    return AFD(set(identificadores.values()), alfabeto, 0, finales, transiciones)

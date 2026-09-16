"""Operaciones sobre conjuntos de estados y simulación de autómatas finitos."""

from .modelos import AFD, AFN, EPSILON


def cierre_epsilon(afn: AFN, estados: set[int] | frozenset[int]) -> set[int]:
    """Obtiene los estados alcanzables con cero o más transiciones epsilon.

    Requiere un AFN válido y estados que le pertenezcan. Devuelve un conjunto
    nuevo; los estados visitados evitan recorridos infinitos ante ciclos.
    """
    if not estados <= afn.estados:
        raise ValueError("El cierre epsilon recibió estados que no pertenecen al AFN.")
    cierre = set(estados)
    pendientes = list(estados)

    while pendientes:
        estado = pendientes.pop()
        for destino in afn.transiciones.get((estado, EPSILON), ()):
            if destino not in cierre:
                cierre.add(destino)
                pendientes.append(destino)

    return cierre


def mover(afn: AFN, estados: set[int] | frozenset[int], simbolo: str) -> set[int]:
    """Obtiene destinos al consumir un símbolo, sin calcular el cierre epsilon.

    Requiere un AFN válido y estados que le pertenezcan. Un símbolo fuera del
    alfabeto (incluido epsilon) produce el conjunto vacío.
    """
    if not estados <= afn.estados:
        raise ValueError("El movimiento recibió estados que no pertenecen al AFN.")
    destinos: set[int] = set()
    if simbolo not in afn.alfabeto:
        return destinos
    for estado in estados:
        destinos.update(afn.transiciones.get((estado, simbolo), ()))
    return destinos


def simular_afn(afn: AFN, cadena: str) -> bool:
    """Indica si el AFN acepta la cadena completa; no modifica el autómata.

    Valida el AFN antes del recorrido y conserva exactamente la cadena recibida.
    La cadena vacía es ""; el carácter epsilon no es un símbolo de entrada.
    """
    afn.validar()
    actuales = cierre_epsilon(afn, {afn.estado_inicial})

    for simbolo in cadena:
        if simbolo not in afn.alfabeto:
            return False
        actuales = cierre_epsilon(afn, mover(afn, actuales, simbolo))
        if not actuales:
            return False

    return bool(actuales & afn.estados_aceptacion)


def simular_afd(afd: AFD, cadena: str) -> bool:
    """Indica si el AFD acepta la cadena completa, sin modificarlo.

    Valida el AFD antes de simular. Un símbolo ajeno al alfabeto o una transición
    ausente produce rechazo; también admite los AFD con tablas parciales.
    """
    afd.validar()
    actual = afd.estado_inicial

    for simbolo in cadena:
        if simbolo not in afd.alfabeto:
            return False
        destino = afd.transiciones.get((actual, simbolo))
        if destino is None:
            return False
        actual = destino

    return actual in afd.estados_aceptacion

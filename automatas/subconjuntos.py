"""Conversión de AFN con epsilon a AFD mediante construcción de subconjuntos."""

from collections import deque

from .modelos import AFD, AFN
from .simulacion import cierre_epsilon, mover


def afn_a_afd(afn: AFN) -> AFD:
    """Construye un AFD completo con los subconjuntos alcanzables del AFN.

    El subconjunto inicial recibe el identificador 0. Los demás se numeran en
    orden de descubrimiento, recorriendo el alfabeto ordenado. El conjunto vacío
    se incluye como sumidero solo si es alcanzable. No modifica el AFN recibido.
    """
    afn.validar()
    inicial = frozenset(cierre_epsilon(afn, {afn.estado_inicial}))
    identificadores: dict[frozenset[int], int] = {inicial: 0}
    pendientes = deque([inicial])
    simbolos = sorted(afn.alfabeto)
    transiciones: dict[tuple[int, str], int] = {}
    estados_aceptacion: set[int] = set()

    while pendientes:
        subconjunto = pendientes.popleft()
        origen = identificadores[subconjunto]

        # Basta con que una de las posibilidades del AFN sea un estado final.
        if subconjunto & afn.estados_aceptacion:
            estados_aceptacion.add(origen)

        for simbolo in simbolos:
            destino = frozenset(cierre_epsilon(afn, mover(afn, subconjunto, simbolo)))
            if destino not in identificadores:
                identificadores[destino] = len(identificadores)
                pendientes.append(destino)
            transiciones[(origen, simbolo)] = identificadores[destino]

    return AFD(
        estados=set(identificadores.values()),
        alfabeto=set(afn.alfabeto),
        estado_inicial=0,
        estados_aceptacion=estados_aceptacion,
        transiciones=transiciones,
    )

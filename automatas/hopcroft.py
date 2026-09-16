"""Minimización de AFD mediante refinamiento de particiones de Hopcroft."""

from collections import deque

from .modelos import AFD


def _preparar_afd(afd: AFD) -> AFD:
    """Copia la parte alcanzable y completa las transiciones que falten."""
    alcanzables = {afd.estado_inicial}
    pendientes = [afd.estado_inicial]
    while pendientes:
        origen = pendientes.pop()
        for simbolo in afd.alfabeto:
            destino = afd.transiciones.get((origen, simbolo))
            if destino is not None and destino not in alcanzables:
                alcanzables.add(destino)
                pendientes.append(destino)

    transiciones = {
        (origen, simbolo): destino
        for (origen, simbolo), destino in afd.transiciones.items()
        if origen in alcanzables
    }
    # Evita reutilizar incluso el identificador de un estado inaccesible.
    sumidero = max(afd.estados) + 1
    necesita_sumidero = False
    for estado in alcanzables:
        for simbolo in afd.alfabeto:
            if (estado, simbolo) not in transiciones:
                transiciones[(estado, simbolo)] = sumidero
                necesita_sumidero = True
    if necesita_sumidero:
        alcanzables.add(sumidero)
        for simbolo in afd.alfabeto:
            transiciones[(sumidero, simbolo)] = sumidero

    return AFD(
        estados=alcanzables,
        alfabeto=set(afd.alfabeto),
        estado_inicial=afd.estado_inicial,
        estados_aceptacion=afd.estados_aceptacion & alcanzables,
        transiciones=transiciones,
    )


def _particiones_hopcroft(afd: AFD) -> tuple[list[set[int]], dict[int, int]]:
    """Separa estados distinguibles de un AFD completo y alcanzable."""
    finales = set(afd.estados_aceptacion)
    no_finales = afd.estados - finales
    bloques = [grupo for grupo in (finales, no_finales) if grupo]
    bloque_de = {
        estado: indice
        for indice, bloque in enumerate(bloques)
        for estado in bloque
    }

    # Los predecesores permiten visitar solo los bloques afectados por un corte.
    predecesores: dict[tuple[str, int], set[int]] = {}
    for (origen, simbolo), destino in afd.transiciones.items():
        predecesores.setdefault((simbolo, destino), set()).add(origen)

    menor = min(range(len(bloques)), key=lambda indice: len(bloques[indice]))
    pendientes = deque([menor])
    en_pendientes = {menor}
    simbolos = sorted(afd.alfabeto)

    while pendientes:
        indice_divisor = pendientes.popleft()
        en_pendientes.remove(indice_divisor)
        # El bloque podría dividirse mientras procesamos sus distintos símbolos.
        divisor = set(bloques[indice_divisor])

        for simbolo in simbolos:
            afectados: dict[int, set[int]] = {}
            for destino in divisor:
                for origen in predecesores.get((simbolo, destino), ()):
                    afectados.setdefault(bloque_de[origen], set()).add(origen)

            for indice, interseccion in afectados.items():
                bloque = bloques[indice]
                if len(interseccion) == len(bloque):
                    continue

                # El bloque original conserva el resto; el nuevo recibe el corte.
                bloque.difference_update(interseccion)
                nuevo = len(bloques)
                bloques.append(interseccion)
                for estado in interseccion:
                    bloque_de[estado] = nuevo

                if indice in en_pendientes:
                    # El resto ya está pendiente: agregar también la otra mitad.
                    siguiente = nuevo
                else:
                    # Regla de Hopcroft: trabajar con la mitad más pequeña.
                    siguiente = nuevo if len(interseccion) <= len(bloque) else indice
                pendientes.append(siguiente)
                en_pendientes.add(siguiente)

    return bloques, bloque_de


def minimizar_afd(afd: AFD) -> AFD:
    """Devuelve un AFD completo mínimo, equivalente e independiente del original.

    Elimina estados inaccesibles y completa tablas parciales antes de aplicar
    Hopcroft. Numera el resultado por recorrido en anchura, desde el estado 0
    y con el alfabeto ordenado. No modifica el AFD recibido.
    """
    afd.validar()
    completo = _preparar_afd(afd)
    bloques, bloque_de = _particiones_hopcroft(completo)

    inicial = bloque_de[completo.estado_inicial]
    identificadores = {inicial: 0}
    pendientes = deque([inicial])
    simbolos = sorted(completo.alfabeto)
    transiciones: dict[tuple[int, str], int] = {}
    finales: set[int] = set()

    while pendientes:
        bloque = pendientes.popleft()
        origen = identificadores[bloque]
        representante = min(bloques[bloque])
        if representante in completo.estados_aceptacion:
            finales.add(origen)

        for simbolo in simbolos:
            destino = bloque_de[completo.transiciones[(representante, simbolo)]]
            if destino not in identificadores:
                identificadores[destino] = len(identificadores)
                pendientes.append(destino)
            transiciones[(origen, simbolo)] = identificadores[destino]

    return AFD(
        estados=set(identificadores.values()),
        alfabeto=set(completo.alfabeto),
        estado_inicial=0,
        estados_aceptacion=finales,
        transiciones=transiciones,
    )

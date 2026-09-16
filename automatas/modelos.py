"""Representación de autómatas mediante conjuntos y tablas de transición."""

from dataclasses import dataclass, field


EPSILON = "ε"


def _validar_componentes(
    estados: set[int],
    alfabeto: set[str],
    estado_inicial: int,
    estados_aceptacion: set[int],
) -> None:
    """Comprueba las condiciones comunes a ambos tipos de autómata."""
    if estado_inicial not in estados:
        raise ValueError("El estado inicial debe pertenecer al conjunto de estados.")
    if not estados_aceptacion <= estados:
        raise ValueError("Los estados de aceptación deben pertenecer al autómata.")
    if EPSILON in alfabeto:
        raise ValueError("Épsilon no debe formar parte del alfabeto de entrada.")
    if any(len(simbolo) != 1 for simbolo in alfabeto):
        raise ValueError("Cada símbolo del alfabeto debe ser un solo carácter.")


@dataclass
class AFN:
    """Autómata no determinista; cada transición tiene un conjunto de destinos.

    Las claves (estado, EPSILON) representan transiciones sin consumir entrada.
    Los datos se validan al construir el objeto o al llamar a validar().
    """

    estados: set[int]
    alfabeto: set[str]
    estado_inicial: int
    estados_aceptacion: set[int]
    transiciones: dict[tuple[int, str], set[int]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        """Lanza ValueError si la definición del autómata es inconsistente."""
        _validar_componentes(
            self.estados, self.alfabeto, self.estado_inicial, self.estados_aceptacion
        )
        for (origen, simbolo), destinos in self.transiciones.items():
            if origen not in self.estados or not destinos <= self.estados:
                raise ValueError("Una transición referencia estados inexistentes.")
            if simbolo != EPSILON and simbolo not in self.alfabeto:
                raise ValueError("La transición usa un símbolo fuera del alfabeto.")


@dataclass
class AFD:
    """Autómata determinista; cada transición registrada tiene un solo destino.

    Se permiten tablas parciales: una transición ausente representará rechazo.
    Los datos se validan al construir el objeto o al llamar a validar().
    """

    estados: set[int]
    alfabeto: set[str]
    estado_inicial: int
    estados_aceptacion: set[int]
    transiciones: dict[tuple[int, str], int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        """Lanza ValueError si la definición del autómata es inconsistente."""
        _validar_componentes(
            self.estados, self.alfabeto, self.estado_inicial, self.estados_aceptacion
        )
        for (origen, simbolo), destino in self.transiciones.items():
            if origen not in self.estados or destino not in self.estados:
                raise ValueError("Una transición referencia estados inexistentes.")
            if simbolo not in self.alfabeto:
                raise ValueError("Un AFD solo permite transiciones con su alfabeto.")

"""Construcción de AFN con el método de Thompson y una pila de fragmentos."""

from dataclasses import dataclass

from .modelos import AFN, EPSILON
from .regex import infix_a_postfix, insertar_concatenacion


@dataclass(frozen=True)
class _Fragmento:
    """Extremos de un fragmento con un único inicio y un único final."""

    inicio: int
    fin: int


def postfix_a_afn(postfix: str) -> AFN:
    """Construye un AFN desde postfix; una entrada inválida produce ValueError.

    Admite literales, epsilon, unión (|), concatenación (.) y unarios (*, +, ?).
    Los espacios se ignoran. Los estados y transiciones son nuevos en cada llamada.
    """
    estados: set[int] = set()
    alfabeto: set[str] = set()
    transiciones: dict[tuple[int, str], set[int]] = {}
    pila: list[_Fragmento] = []

    def nuevo_estado() -> int:
        estado = len(estados)
        estados.add(estado)
        return estado

    def conectar(origen: int, simbolo: str, destino: int) -> None:
        transiciones.setdefault((origen, simbolo), set()).add(destino)

    for posicion, simbolo in enumerate(postfix, start=1):
        if simbolo.isspace():
            continue

        if simbolo in ".|":
            if len(pila) < 2:
                raise ValueError(
                    f"El operador {simbolo!r} en la posición {posicion} "
                    "requiere dos operandos en postfix."
                )
            derecho = pila.pop()
            izquierdo = pila.pop()

            if simbolo == ".":
                conectar(izquierdo.fin, EPSILON, derecho.inicio)
                pila.append(_Fragmento(izquierdo.inicio, derecho.fin))
            else:
                inicio, fin = nuevo_estado(), nuevo_estado()
                conectar(inicio, EPSILON, izquierdo.inicio)
                conectar(inicio, EPSILON, derecho.inicio)
                conectar(izquierdo.fin, EPSILON, fin)
                conectar(derecho.fin, EPSILON, fin)
                pila.append(_Fragmento(inicio, fin))
        elif simbolo in "*+?":
            if not pila:
                raise ValueError(
                    f"El operador {simbolo!r} en la posición {posicion} "
                    "requiere un operando en postfix."
                )
            interior = pila.pop()
            inicio, fin = nuevo_estado(), nuevo_estado()
            conectar(inicio, EPSILON, interior.inicio)
            conectar(interior.fin, EPSILON, fin)

            # * y ? permiten omitir el fragmento; * y + permiten repetirlo.
            if simbolo in "*?":
                conectar(inicio, EPSILON, fin)
            if simbolo in "*+":
                conectar(interior.fin, EPSILON, interior.inicio)
            pila.append(_Fragmento(inicio, fin))
        else:
            # Reutilizamos las reglas léxicas de infix para un solo operando.
            # Esto también rechaza paréntesis, escapes y clases en postfix.
            try:
                insertar_concatenacion(simbolo)
            except ValueError:
                raise ValueError(
                    f"Símbolo postfix no soportado {simbolo!r} "
                    f"en la posición {posicion}."
                ) from None

            inicio, fin = nuevo_estado(), nuevo_estado()
            conectar(inicio, simbolo, fin)
            if simbolo != EPSILON:
                alfabeto.add(simbolo)
            pila.append(_Fragmento(inicio, fin))

    if not pila:
        raise ValueError("La expresión postfix está vacía; usa 'ε' para la cadena vacía.")
    if len(pila) != 1:
        raise ValueError("Postfix inválida: faltan operadores para combinar los operandos.")

    fragmento = pila.pop()
    return AFN(
        estados=estados,
        alfabeto=alfabeto,
        estado_inicial=fragmento.inicio,
        estados_aceptacion={fragmento.fin},
        transiciones=transiciones,
    )


def regex_a_afn(expresion: str) -> AFN:
    """Convierte una expresión infix a AFN usando Shunting Yard y Thompson."""
    return postfix_a_afn(infix_a_postfix(expresion))

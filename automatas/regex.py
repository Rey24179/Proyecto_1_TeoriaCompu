"""Validación de expresiones regulares y conversión mediante Shunting Yard."""


_UNARIOS = frozenset("*+?")
_PRECEDENCIA = {"|": 1, ".": 2}
_NO_SOPORTADOS = frozenset("\\[]{}^$")


def insertar_concatenacion(expresion: str) -> str:
    """Valida una expresión infix e inserta los puntos de concatenación.

    Ignora espacios en blanco y conserva los puntos explícitos. Los errores
    lanzan ValueError con posiciones contadas desde 1 en la expresión original.
    Por ejemplo, '(a|b)*abb' se transforma en '(a|b)*.a.b.b'.
    """
    resultado: list[str] = []
    parentesis: list[int] = []
    espera_operando = True

    for posicion, simbolo in enumerate(expresion, start=1):
        if simbolo.isspace():
            continue
        if simbolo in _NO_SOPORTADOS or not simbolo.isprintable():
            raise ValueError(
                f"Símbolo no soportado {simbolo!r} en la posición {posicion}."
            )

        if simbolo == "(":
            if not espera_operando:
                resultado.append(".")
            parentesis.append(posicion)
            espera_operando = True
        elif simbolo == ")":
            if not parentesis:
                raise ValueError(
                    f"Paréntesis ')' sin apertura en la posición {posicion}."
                )
            if espera_operando:
                raise ValueError(
                    f"Falta un operando antes de ')' en la posición {posicion}."
                )
            parentesis.pop()
            espera_operando = False
        elif simbolo in _UNARIOS:
            if espera_operando:
                raise ValueError(
                    f"El operador {simbolo!r} en la posición {posicion} "
                    "necesita un operando a su izquierda."
                )
        elif simbolo in _PRECEDENCIA:
            if espera_operando:
                raise ValueError(
                    f"El operador {simbolo!r} en la posición {posicion} "
                    "necesita un operando a su izquierda."
                )
            espera_operando = True
        else:
            # Un literal o epsilon inicia un nuevo operando.
            if not espera_operando:
                resultado.append(".")
            espera_operando = False

        resultado.append(simbolo)

    if not resultado:
        raise ValueError("La expresión está vacía; usa 'ε' para la cadena vacía.")
    if parentesis:
        raise ValueError(
            f"Paréntesis '(' sin cierre en la posición {parentesis[-1]}."
        )
    if espera_operando:
        raise ValueError("Falta un operando al final de la expresión.")

    return "".join(resultado)


def infix_a_postfix(expresion: str) -> str:
    """Convierte infix a postfix con Shunting Yard, sin evaluar la expresión.

    La precedencia es: unarios (*, +, ?), concatenación (.) y unión (|).
    Los binarios se asocian por la izquierda; los unarios ya son posfijos.
    Se valida la sintaxis antes de convertir. Ejemplo: 'a|bc' -> 'abc.|'.
    """
    normalizada = insertar_concatenacion(expresion)
    salida: list[str] = []
    operadores: list[str] = []

    for simbolo in normalizada:
        if simbolo == "(":
            operadores.append(simbolo)
        elif simbolo == ")":
            while operadores[-1] != "(":
                salida.append(operadores.pop())
            operadores.pop()
        elif simbolo in _UNARIOS:
            # El operando (literal o grupo completo) ya está en la salida.
            salida.append(simbolo)
        elif simbolo in _PRECEDENCIA:
            while (
                operadores
                and operadores[-1] != "("
                and _PRECEDENCIA[operadores[-1]] >= _PRECEDENCIA[simbolo]
            ):
                salida.append(operadores.pop())
            operadores.append(simbolo)
        else:
            salida.append(simbolo)

    salida.extend(reversed(operadores))
    return "".join(salida)

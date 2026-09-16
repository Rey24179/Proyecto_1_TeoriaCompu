# Construcción directa de AFD: recuperación

`regex_a_afd_directo(expresion)` genera un AFD a partir de posiciones en la
expresión regular, sin construir un AFN. Utiliza el postfix validado de
Shunting Yard y una pila de resúmenes de nodos del árbol sintáctico.

## Posiciones y propiedades

Cada aparición de un literal recibe una posición distinta, aunque el mismo
carácter aparezca varias veces. Epsilon no recibe posición. Cada nodo guarda:

- `anulable`: indica si reconoce la cadena vacía.
- `primeros` (`firstpos`): posiciones que pueden iniciar una palabra del nodo.
- `ultimos` (`lastpos`): posiciones que pueden terminar una palabra del nodo.

Un diccionario `siguientes` (`followpos`) guarda las posiciones que pueden seguir
inmediatamente a cada posición. Las reglas son:

| Operación | Anulable | Primeros y últimos | Cambio en siguientes |
| --- | --- | --- | --- |
| Literal | No | La posición del literal | Ninguno |
| Epsilon | Sí | Conjuntos vacíos | Ninguno |
| Unión | Si alguno de los hijos lo es | Unión de los conjuntos correspondientes | Ninguno |
| Concatenación | Si ambos hijos lo son | Incluir el otro hijo cuando el extremo es anulable | Agregar los primeros del derecho a los siguientes de los últimos del izquierdo |
| `*` | Sí | Los del hijo | Agregar los primeros a los siguientes de los últimos |
| `+` | Igual que el hijo | Los del hijo | Igual que `*` |
| `?` | Sí | Los del hijo | Ninguno |

Al final se agrega una posición de aceptación interna. Se añade a los siguientes
de las últimas posiciones de la expresión y a los primeros si la expresión es
anulable. Este marcador no es un carácter: `#` sigue siendo un literal válido.

## Estados del AFD

El primer conjunto de posiciones es el estado inicial. Desde un conjunto y un
símbolo `a`, se unen los `followpos` de las posiciones cuyo literal es `a`.
Un estado acepta si contiene la posición del marcador final.

Se descubren los conjuntos con una cola y se identifican usando `frozenset`,
igual que en la representación de conjuntos de la construcción por subconjuntos,
pero aquí sus elementos son posiciones de la expresión, no estados de un AFN.
El resultado es completo e incluye el conjunto vacío cuando se alcanza.

```python
from automatas import regex_a_afd_directo, simular_afd

afd = regex_a_afd_directo("(a|b)*abb")
print(len(afd.estados))            # 4
print(simular_afd(afd, "abb"))     # True
print(simular_afd(afd, "aba"))     # False
```

El AFD directo no se considera mínimo en general. Se puede aplicar
`minimizar_afd` al resultado si se necesita minimizarlo.

## Verificación

Las pruebas recorren el producto del AFD directo y del AFD de subconjuntos para
23 expresiones, verificando igualdad del lenguaje para todas las longitudes.
Incluyen operadores unarios encadenados, epsilon, símbolos repetidos, Unicode y
el literal `#`. También se verifica la tabla conocida de `(a|b)*abb`.

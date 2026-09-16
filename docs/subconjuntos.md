# Parte 4: de AFN a AFD mediante subconjuntos

El simulador de AFN mantiene varios estados posibles a la vez. La construcción
de subconjuntos convierte cada conjunto de posibilidades en un único estado de
un AFD, conservando el lenguaje que acepta.

## Uso

```python
from automatas import afn_a_afd, regex_a_afn, simular_afd, simular_afn

afn = regex_a_afn("(a|b)*abb")
afd = afn_a_afd(afn)

for cadena in ("abb", "aabb", "aba", ""):
    print(repr(cadena), simular_afn(afn, cadena), simular_afd(afd, cadena))
```

Las dos columnas de aceptación coinciden: ambas aceptan `abb` y `aabb`, y
rechazan `aba` y la cadena vacía. La conversión devuelve un objeto `AFD` nuevo
y conserva el AFN para poder simularlo y dibujarlo después.

## Construcción

1. Validar el AFN recibido.
2. Calcular el cierre epsilon de su estado inicial. Ese subconjunto se convierte
   en el estado inicial `0` del AFD y se agrega a una cola de pendientes.
3. Extraer un subconjunto `S` de la cola. Marcar su estado como final si `S`
   contiene al menos un estado de aceptación del AFN.
4. Para cada símbolo del alfabeto, calcular el conjunto destino:
   `T = cierre_epsilon(afn, mover(afn, S, simbolo))`.
5. Si `T` es nuevo, asignarle un número y agregarlo a la cola. Registrar la
   transición desde el número de `S` hacia el número de `T` con ese símbolo.
6. Repetir hasta que no queden subconjuntos pendientes.

El diccionario interno usa `frozenset` como clave porque es inmutable y permite
reconocer un mismo conjunto independientemente del orden de sus elementos.
Los estados se numeran en orden de descubrimiento y los símbolos se recorren
ordenados; esto hace reproducible la numeración.

El resultado no tiene transiciones epsilon. Su efecto ya está incorporado en
los subconjuntos mediante los cierres.

## Ejemplo con una tabla completa

Consideremos este AFN, cuyo lenguaje es una o más `a` seguidas de cero o más `b`:

```python
from automatas import AFN, EPSILON, afn_a_afd, simular_afd

afn = AFN(
    estados={0, 1, 2},
    alfabeto={"a", "b"},
    estado_inicial=0,
    estados_aceptacion={2},
    transiciones={
        (0, EPSILON): {1},
        (1, "a"): {1, 2},
        (2, "b"): {2},
    },
)
afd = afn_a_afd(afn)
print(simular_afd(afd, "aab"))  # True
print(simular_afd(afd, "aba"))  # False
```

Su cierre inicial es `{0, 1}`. Recorriendo `a` antes que `b`, se obtienen:

| Estado AFD | Subconjunto del AFN | Con `a` | Con `b` | ¿Final? |
| --- | --- | --- | --- | --- |
| `0` (inicial) | `{0, 1}` | `1` | `2` | No |
| `1` | `{1, 2}` | `1` | `3` | Sí |
| `2` | `∅` | `2` | `2` | No |
| `3` | `{2}` | `2` | `3` | Sí |

Al leer `aab`, el AFD recorre `0 → 1 → 1 → 3`. Como termina en el estado final
`3`, acepta. Para `aba`, recorre `0 → 1 → 3 → 2` y rechaza.

## Estado sumidero y casos especiales

El conjunto vacío representa que el AFN ya no tiene estados posibles. Cualquier
movimiento desde él vuelve a producir el conjunto vacío, por lo que su estado
es un sumidero no final. Solo se agrega cuando algún movimiento lo alcanza.

La conversión genera un AFD completo sobre su alfabeto: cada pareja de estado
y símbolo tiene un destino. No genera subconjuntos inaccesibles ni enumera
de antemano todas las combinaciones posibles de estados.

Si el alfabeto es vacío, el resultado tiene un único estado y ninguna transición.
Ese estado puede ser final o no, según el cierre inicial. Los ciclos epsilon no
producen recorridos infinitos porque el cierre registra los estados visitados.

La construcción no minimiza. Dos subconjuntos diferentes podrían aceptar las
mismas continuaciones; la [parte 5](hopcroft.md) usa Hopcroft para unir estados
equivalentes.

## Simulación del AFD

`simular_afd` valida el AFD y comienza en su estado inicial. Recorre la cadena
carácter por carácter y actualiza el estado con la tabla de transiciones.
Después de consumir toda la entrada, comprueba si el estado es final.

Un símbolo fuera del alfabeto produce `False`. Si se simula un AFD parcial
construido manualmente, una transición ausente también produce `False`.
No se eliminan espacios ni se interpreta el carácter `ε` como cadena vacía;
la cadena vacía se representa con `""`.

Después de validar el autómata, simular una cadena de longitud `n` cuesta
`O(n)` en tiempo y `O(1)` en espacio adicional. La validación inicial recorre
los componentes del AFD, por lo que el costo total de una llamada también
incluye esa comprobación.

## Costo de la conversión y pruebas

Para un AFN con `Q` estados puede haber hasta `2^Q` subconjuntos diferentes.
Si se descubren `K` subconjuntos, hay `A` símbolos en el alfabeto y `E`
transiciones individuales en el AFN, el recorrido tiene una cota de tiempo
`O(K * A * (Q + E) + K * Q)`, además de validar el AFN y ordenar el alfabeto.
El segundo término cubre el recorrido de los subconjuntos y la comprobación de
estados finales, incluso con un alfabeto vacío. El almacenamiento de subconjuntos
y transiciones usa `O(K * Q + K * A)` espacio.

Ejecutar desde la raíz:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas verifican una tabla conocida, estados inaccesibles, ciclos epsilon,
sumideros, alfabetos vacíos, varios finales y que el AFN original se conserve.
También comparan AFN y AFD para 18 expresiones y las 364 cadenas de longitud
cero a cinco sobre `{a, b, c}`: 6,552 comparaciones de aceptación. Una prueba
adicional comprueba directamente que `(a|b)*abb` acepta exactamente las cadenas
binarias que terminan en `abb`, para longitudes de cero a siete.

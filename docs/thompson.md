# Parte 3: construcción de Thompson y simulación de AFN

Esta parte conecta el resultado de Shunting Yard con un autómata capaz de
evaluar cadenas. Se utiliza una pila de fragmentos para construir el AFN y un
conjunto de estados activos para simularlo.

## Funciones disponibles

```python
from automatas import infix_a_postfix, postfix_a_afn, regex_a_afn, simular_afn

postfix = infix_a_postfix("(a|b)*abb")
afn = postfix_a_afn(postfix)

print(simular_afn(afn, "abb"))   # True
print(simular_afn(afn, "aba"))   # False

# Atajo que hace las dos conversiones:
otro_afn = regex_a_afn("a?")
print(simular_afn(otro_afn, ""))  # True
```

`postfix_a_afn` recibe postfix, por ejemplo `ab|`. `regex_a_afn` recibe infix,
por ejemplo `a|b`. Ambas funciones devuelven un objeto `AFN` nuevo.

## Construcción con fragmentos

Cada fragmento tiene un estado inicial y un único estado final. Sus transiciones
se guardan en una tabla compartida únicamente dentro de esa construcción.
Un contador implícito, el tamaño del conjunto de estados, asigna identificadores
consecutivos desde cero. Cada nueva llamada comienza una construcción independiente.

La expresión postfix se recorre de izquierda a derecha:

| Símbolo | Acción |
| --- | --- |
| Literal `a` | Crear dos estados, unirlos con `a` y apilar el fragmento |
| `ε` | Crear dos estados, unirlos con epsilon y apilar el fragmento; no agregar epsilon al alfabeto |
| `.` | Sacar primero el fragmento derecho y después el izquierdo; conectar el final izquierdo al inicio derecho con epsilon |
| `\|` | Sacar dos fragmentos; agregar un nuevo inicio con caminos epsilon hacia ambos y un nuevo final alcanzable desde sus finales |
| `*` | Sacar un fragmento; agregar inicio y final, permitir omitir el fragmento y repetirlo mediante epsilon |
| `+` | Como el cierre de Kleene, pero sin el camino que omite el fragmento |
| `?` | Permitir omitir el fragmento o recorrerlo una vez, sin agregar un ciclo de repetición |

Cada operación apila el fragmento resultante. Al terminar debe quedar
exactamente uno. Un operador sin suficientes fragmentos o varios fragmentos
sobrantes indican una expresión postfix inválida y producen `ValueError`.

En `+` se exige al menos un recorrido del fragmento, pero ese recorrido puede
consumir cero caracteres si el operando acepta epsilon. Por eso `(a?)+` acepta
la cadena vacía.

## Ejemplo de construcción: `(a|b)*`

Su postfix es `ab|*`. La pila se muestra desde la base hacia la cima:

| Símbolo | Fragmentos en la pila | Cambio principal |
| --- | --- | --- |
| `a` | `(0, 1)` | Transición `0 --a--> 1` |
| `b` | `(0, 1)`, `(2, 3)` | Transición `2 --b--> 3` |
| `\|` | `(4, 5)` | Epsilon de `4` a `0` y `2`, y de `1` y `3` a `5` |
| `*` | `(6, 7)` | Epsilon de `6` a `4` y `7`, y de `5` a `4` y `7` |

El AFN resultante comienza en `6`, acepta en `7` y tiene alfabeto `{a, b}`.
Las múltiples transiciones epsilon de un origen se acumulan en un conjunto;
ninguna rama reemplaza a otra.

## Simulación con conjuntos de estados

Un AFN puede estar en varios estados posibles después de leer el mismo prefijo.
El simulador conserva todos esos estados, sin escoger una única rama.

`cierre_epsilon(afn, estados)` incluye los estados dados y todos los alcanzables
mediante epsilon. Mantiene un conjunto de visitados y una pila de pendientes:
cada estado se visita como máximo una vez por cierre, aunque existan ciclos.

`mover(afn, estados, simbolo)` une los destinos de las transiciones etiquetadas
con ese símbolo desde los estados dados. No calcula el cierre automáticamente.

El algoritmo de simulación sigue estos pasos:

1. Validar el AFN.
2. Calcular `actuales = cierre_epsilon(afn, {afn.estado_inicial})`.
3. Por cada carácter de la cadena, comprobar que pertenezca al alfabeto y calcular
   `actuales = cierre_epsilon(afn, mover(afn, actuales, caracter))`.
4. Si no quedan estados posibles, rechazar.
5. Después de consumir toda la cadena, aceptar si algún estado actual es final.

Si la cadena es vacía, se comprueba directamente el cierre del estado inicial.
Los espacios de la cadena se conservan; el simulador no los elimina.

Para el AFN anterior y la cadena `ab`:

| Entrada consumida | Estados activos después del cierre epsilon |
| --- | --- |
| Cadena vacía | `{0, 2, 4, 6, 7}` |
| `a` | `{0, 1, 2, 4, 5, 7}` |
| `ab` | `{0, 2, 3, 4, 5, 7}` |

Se acepta `ab` porque al terminar está activo el estado `7`. El mismo AFN acepta
la cadena vacía porque `7` ya pertenece al cierre inicial.

## Costo y validación

Para una expresión postfix de longitud `m`, Thompson usa tiempo y espacio
`O(m)`: cada operador agrega una cantidad constante de estados y transiciones.
Los fragmentos solo guardan sus extremos, por lo que no se copian subautómatas
completos al combinarlos.

Para un AFN con `Q` estados y `E` transiciones individuales, el cierre epsilon
tiene una cota `O(Q + E)`. Después de validar el autómata, simular una cadena de
longitud `n` tiene una cota `O((n + 1)(Q + E))`, con espacio adicional `O(Q)`.
Los recorridos no usan recursión.

Ejecuta las pruebas desde la raíz:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas comprueban cada operador, errores de postfix, ciclos epsilon,
conjuntos de destinos, ausencia de modificaciones al AFN y consumo de la cadena
completa. También se comparan ocho expresiones con `re.fullmatch` para todas las
121 cadenas de longitud cero a cuatro sobre `{a, b, c}`: 968 comparaciones.
Las expresiones de referencia traducen explícitamente epsilon y concatenación.
El motor `re` se usa únicamente en las pruebas.

La conversión a AFD y su simulación corresponden a la siguiente parte.

# Parte 5: minimización de AFD con Hopcroft

Dos estados son equivalentes si, para cualquier continuación de la entrada,
ambos aceptan o ambos rechazan. Hopcroft agrupa estados equivalentes y produce
un AFD mínimo que reconoce el mismo lenguaje.

## Uso

```python
from automatas import afn_a_afd, minimizar_afd, regex_a_afn, simular_afd

afd = afn_a_afd(regex_a_afn("(a|b)*abb"))
minimo = minimizar_afd(afd)

print(len(afd.estados), len(minimo.estados))  # 5 4
print(simular_afd(minimo, "abb"))            # True
print(simular_afd(minimo, "aba"))            # False
print(minimizar_afd(minimo) == minimo)        # True
```

La función recibe y devuelve objetos `AFD`. El resultado tiene sus propios
conjuntos y diccionario de transiciones: el AFD original permanece disponible.

## Preparación del autómata

Primero se valida el AFD. Luego se recorre desde el estado inicial para conservar
únicamente los estados alcanzables. Los estados inaccesibles no pueden influir
en la aceptación de ninguna cadena y se eliminan.

Si falta una transición, se completa con un estado sumidero no final. El
sumidero tiene transiciones hacia sí mismo para todo el alfabeto. Se le asigna
un identificador que no aparece en el AFD recibido, ni siquiera entre sus estados
inaccesibles. Esta preparación se realiza sobre una copia.

El objetivo es un AFD **mínimo completo**. Una tabla parcial puede usar menos
estados porque representa el rechazo mediante transiciones ausentes. Por
ejemplo, un único estado inicial y final, sin transiciones, acepta solamente
la cadena vacía. Si su alfabeto contiene `a`, su representación completa necesita
dos estados: el inicial final y un sumidero no final. Esto conserva el lenguaje.

## Refinamiento de particiones

Una partición divide todos los estados en bloques disjuntos. Al inicio se crean
el bloque de estados finales y el de no finales, omitiendo los vacíos. Un estado
final y uno no final ya son distinguibles mediante la cadena vacía.

Se mantiene una cola de bloques divisores. Inicialmente contiene el más pequeño
de los bloques existentes. Para cada divisor `A` y símbolo `c`:

1. Encontrar los predecesores `X`: estados cuya transición con `c` entra en `A`.
2. Para cada bloque `Y` afectado, separar `Y ∩ X` de `Y - X` si ambos son no vacíos.
3. Si `Y` estaba pendiente como divisor, reemplazarlo por ambas mitades. En el
   código, el bloque original conserva una mitad y la otra recibe un índice nuevo.
4. Si no estaba pendiente, agregar únicamente la mitad más pequeña a la cola.
5. Repetir hasta vaciar la cola.

El índice de predecesores evita recorrer todas las transiciones en cada paso.
El diccionario `bloque_de` permite agrupar los predecesores por su bloque y
procesar solo los bloques afectados. La regla de la mitad más pequeña es la
característica de Hopcroft que limita el trabajo de los refinamientos.

Se copia el divisor al retirarlo de la cola: si ese bloque se divide durante
el procesamiento de un símbolo, los símbolos restantes deben seguir usando
el mismo divisor de esa iteración.

## Construcción del AFD mínimo

Cuando la partición es estable, cada bloque se convierte en un estado. Todos
los estados de un bloque tienen el mismo comportamiento de aceptación y sus
transiciones con un símbolo llegan al mismo bloque destino. Por eso basta tomar
un representante para construir las transiciones del nuevo estado.

El bloque que contiene el estado inicial recibe el identificador `0`. Se recorre
el autómata por anchura, con los símbolos ordenados, y se asignan los demás
identificadores en orden de descubrimiento. Así, la numeración del resultado no
depende de los nombres de los estados originales. Minimizar nuevamente el
resultado produce el mismo objeto en términos de sus componentes.

## Ejemplo: `(a|b)*abb`

El AFD que genera subconjuntos tiene esta tabla:

| Estado | Con `a` | Con `b` | ¿Final? |
| --- | --- | --- | --- |
| `0` (inicial) | `1` | `2` | No |
| `1` | `1` | `3` | No |
| `2` | `1` | `2` | No |
| `3` | `1` | `4` | No |
| `4` | `1` | `2` | Sí |

La partición inicial es `{4}` y `{0, 1, 2, 3}`. El símbolo `b` hacia el bloque
`{4}` separa el estado `3`, porque es el único que entra directamente a ese final.
Después, `b` hacia `{3}` separa el estado `1`. Los estados `0` y `2` permanecen
juntos: no hay continuación que permita distinguirlos.

La partición final es `{0, 2}`, `{1}`, `{3}`, `{4}`. Tras renumerar:

| Estado mínimo | Estados originales | Con `a` | Con `b` | ¿Final? |
| --- | --- | --- | --- | --- |
| `0` (inicial) | `{0, 2}` | `1` | `0` | No |
| `1` | `{1}` | `1` | `2` | No |
| `2` | `{3}` | `1` | `3` | No |
| `3` | `{4}` | `1` | `0` | Sí |

El número de estados baja de cinco a cuatro. Se sigue aceptando exactamente el
lenguaje de cadenas sobre `{a, b}` que terminan en `abb`.

## Casos especiales y costo

- Si no hay finales alcanzables, el mínimo completo tiene un estado no final.
- Si todos los estados de un AFD completo son finales, el mínimo tiene un estado
  final. En un AFD parcial se debe completar primero: sus transiciones ausentes
  pueden distinguir estados que inicialmente eran todos finales.
- Con alfabeto vacío solo el estado inicial es alcanzable y el mínimo tiene un
  estado, final o no según la aceptación de la cadena vacía.
- Los estados muertos alcanzables pueden fusionarse con el sumidero; no se
  eliminan antes de representar correctamente las transiciones de rechazo.

Para `n` estados del AFD completo preparado y `k` símbolos, el refinamiento de
Hopcroft tiene la cota habitual `O(k * n * log n)` para `n >= 2`, con acceso
promedio constante a diccionarios y conjuntos. Se utilizan predecesores, índices
de bloques y la regla del bloque pequeño. El espacio es `O(n + k * n)`.
La validación, la preparación y la construcción del resultado tienen costos
adicionales lineales en sus tablas y conjuntos, salvo la ordenación del alfabeto.

## Verificación independiente

```powershell
python -m unittest discover -s tests -v
```

Las pruebas comprueban equivalencia y minimalidad sin volver a implementar
Hopcroft:

- Para equivalencia, recorren pares de estados del AFD original y del mínimo.
  Una diferencia de aceptación en un par alcanzable demuestra que los lenguajes
  difieren. Las transiciones ausentes del original se tratan como rechazo
  permanente. Recorrer todo ese producto comprueba todas las longitudes de cadena.
- Para minimalidad, buscan una continuación que distinga cada par de estados
  del resultado. También comprueban que todos sean alcanzables y la tabla sea total.
- Se prueban los 324 AFD parciales de dos estados sobre `{a, b}` con estado
  inicial `0`: hay tres opciones por transición y cuatro conjuntos de finales.
- Se agregan 100 AFD con semilla fija, tablas conocidas, casos límite y
  comprobaciones de que minimizar dos veces da el mismo resultado.
- El flujo de expresiones regulares compara además la aceptación del AFN y del
  AFD mínimo para diez expresiones y 121 cadenas cortas por expresión.

Los dibujos de los tres autómatas corresponden a la siguiente parte.

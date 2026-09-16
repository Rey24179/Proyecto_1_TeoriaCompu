# Parte 2: de infix a postfix con Shunting Yard

En infix, los operadores binarios aparecen entre sus operandos: `a|b`.
En postfix, aparecen después: `ab|`. Esta representación permite que Thompson
construya el autómata usando una pila, sin resolver nuevamente la precedencia.

## Paso 1: validar e insertar concatenación

`insertar_concatenacion` recorre la entrada y mantiene:

- Un indicador de si falta un operando.
- Una pila con las posiciones de los paréntesis abiertos.
- Una lista con los caracteres de la expresión normalizada.

Cuando un operando completo va seguido de otro literal o de `(`, inserta `.`.
Por ejemplo, `a(b|c)*` se transforma en `a.(b|c)*`.

Un operando puede ser un literal, `ε`, un grupo o el resultado de aplicar un
operador unario. Un operador binario necesita operandos a ambos lados y un unario
necesita uno a su izquierda. Los paréntesis deben estar balanceados y no pueden
encerrar una expresión vacía.

Los espacios se ignoran sin perder las posiciones originales para los errores.
Si la validación falla, se lanza `ValueError` y no se devuelve un resultado parcial.

## Paso 2: convertir con una pila de operadores

`infix_a_postfix` recorre la expresión normalizada y mantiene una salida y una
pila de operadores. Aplica estas reglas:

1. Un literal o `ε` pasa directamente a la salida.
2. `(` se apila y delimita un grupo.
3. `)` mueve operadores a la salida hasta encontrar `(` y descarta ese paréntesis.
4. Un unario (`*`, `+`, `?`) pasa directamente a la salida: su operando ya está
   completo y estos operadores tienen la mayor precedencia.
5. Ante un binario, se desapilan primero los binarios de mayor o igual
   precedencia; luego se apila el nuevo operador. `.` tiene mayor precedencia
   que `|`. La comparación con igualdad produce asociación por la izquierda.
6. Al terminar, los operadores restantes pasan a la salida desde la cima.

## Traza de ejemplo

Entrada: `a(b|c)*`. Expresión normalizada: `a.(b|c)*`.
La cima de la pila aparece a la derecha; `—` indica una lista vacía.

| Símbolo leído | Salida | Pila de operadores |
| --- | --- | --- |
| `a` | `a` | — |
| `.` | `a` | `.` |
| `(` | `a` | `. (` |
| `b` | `ab` | `. (` |
| `\|` | `ab` | `. ( \|` |
| `c` | `abc` | `. ( \|` |
| `)` | `abc\|` | `.` |
| `*` | `abc\|*` | `.` |
| Fin | `abc\|*.` | — |

El resultado `abc|*.` significa: unir `b` y `c`, aplicar el cierre de Kleene
al resultado y concatenarlo después de `a`.

Otros ejemplos:

| Infix | Postfix |
| --- | --- |
| `a\|bc` | `abc.\|` |
| `ab\|c` | `ab.c\|` |
| `(a\|b)*abb` | `ab\|*a.b.b.` |
| `(ab)+c?` | `ab.+c?.` |
| `(a\|ε)b*` | `aε\|b*.` |

## Costo y límites

Para una entrada de longitud `n`, ambos recorridos usan tiempo `O(n)` y espacio
`O(n)`: cada símbolo se procesa una vez y cada operador se apila y desapila a lo
sumo una vez. La concatenación implícita agrega como máximo una cantidad lineal
de puntos. No se utiliza recursión, incluso con grupos profundamente anidados.

Las funciones trabajan con la sintaxis del proyecto; no llaman al motor `re`
de Python. Esta parte solo cambia la representación de la expresión: todavía
no construye autómatas ni determina si una cadena pertenece al lenguaje.

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas cubren precedencia, asociación, agrupación, operadores unarios,
concatenación implícita y explícita, epsilon, espacios y entradas inválidas.

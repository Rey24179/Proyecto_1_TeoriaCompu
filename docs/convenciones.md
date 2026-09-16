# Convenciones del proyecto

El enunciado exige elegir explícitamente un símbolo para épsilon. Usaremos `ε`.
Las siguientes decisiones definen la sintaxis que implementaremos a partir de
la parte 2; no son requisitos adicionales del enunciado.

## Expresiones regulares

| Símbolo | Significado | Ejemplo |
| --- | --- | --- |
| `ε` | Cadena vacía | `a\|ε` |
| `\|` | Unión | `a\|b` |
| Concatenación implícita | Un símbolo seguido de otro | `ab` |
| `.` | Concatenación explícita e interna | `a.b` |
| `*` | Cero o más repeticiones | `a*` |
| `+` | Una o más repeticiones | `a+` |
| `?` | Cero o una aparición | `a?` |
| `(` y `)` | Agrupación | `(a\|b)*` |

- Cada literal representa un carácter. Por ejemplo, `abc` son tres literales.
- La precedencia será: operadores unarios (`*`, `+`, `?`), concatenación (`.`)
  y unión (`|`), de mayor a menor. Los paréntesis cambian la agrupación.
- Los operadores binarios se asociarán por la izquierda.
- El conversor insertará `.` donde exista concatenación implícita.
- Se ignorarán los espacios en blanco de las expresiones regulares. En las
  cadenas a simular, los caracteres se conservarán exactamente.
- Para expresar la cadena vacía se escribirá `ε`; una expresión vacía se
  considerará un error. Las líneas vacías de archivos se omitirán.
- La sintaxis inicial no incluirá escapes, clases como `[a-z]`, comodines ni
  repeticiones como `{2,3}`. Esas formas se reportarán como no soportadas.
- Los operadores y `ε` son símbolos reservados y no podrán usarse como literales.

## Autómatas y cadenas

- Los estados se identifican con enteros. No necesitan ser consecutivos.
- El alfabeto contiene caracteres y nunca incluye `ε`.
- La constante `EPSILON` del paquete contiene el carácter `ε`.
- Una transición epsilon cambia de estado sin consumir caracteres.
- Una cadena vacía para simular se representa mediante `""`; no se pasa el
  carácter `ε` como si fuera parte de la cadena de entrada.
- Una transición ausente equivale a no tener un movimiento válido.
- Un AFD podrá almacenarse de forma parcial; antes de aplicar Hopcroft se
  completará, cuando haga falta, con un estado sumidero.
- Los archivos de texto se leerán en UTF-8 para conservar `ε` correctamente.

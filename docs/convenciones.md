# Convenciones del proyecto

El enunciado exige elegir explícitamente un símbolo para épsilon. Usaremos `ε`.
Las siguientes decisiones definen la sintaxis implementada en la parte 2;
no son requisitos adicionales del enunciado.

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
- La precedencia es: operadores unarios (`*`, `+`, `?`), concatenación (`.`)
  y unión (`|`), de mayor a menor. Los paréntesis cambian la agrupación.
- Los operadores binarios se asocian por la izquierda.
- Los unarios son posfijos y pueden encadenarse: `a*?` equivale a `(a*)?`.
  No se interpretan como cuantificadores perezosos de otras bibliotecas de regex.
- El conversor inserta `.` donde existe concatenación implícita.
- Se ignoran los espacios en blanco de las expresiones regulares. En las
  cadenas a simular, los caracteres se conservarán exactamente.
- Para expresar la cadena vacía se escribirá `ε`; una expresión vacía se
  considera un error. Las líneas vacías de archivos se omitirán.
- No se admiten escapes, clases como `[a-z]`, repeticiones como `{2,3}` ni
  anclas `^` o `$`. Los caracteres `\`, `[`, `]`, `{`, `}`, `^` y `$` producen
  un error de símbolo no soportado. Tampoco se admiten caracteres no imprimibles,
  salvo los espacios en blanco que se ignoran.
- No hay comodines: `.` siempre significa concatenación.
- Los demás caracteres imprimibles, incluidos dígitos, `ñ`, `_`, `-` y `,`,
  se consideran literales de un carácter.
- Los operadores y `ε` son símbolos reservados y no pueden usarse como literales.
- Los grupos vacíos `()` son inválidos; se debe escribir `(ε)` si se desea
  agrupar la cadena vacía.
- La entrada postfix de Thompson usa los mismos literales y operadores, pero
  no admite paréntesis y exige todos los puntos de concatenación. Por ejemplo,
  `ab.` es válido y `ab` es inválido porque le falta el operador. Los espacios
  en blanco también se ignoran en la entrada postfix.

## Autómatas y cadenas

- Los estados se identifican con enteros. No necesitan ser consecutivos.
- El alfabeto contiene caracteres y nunca incluye `ε`.
- La constante `EPSILON` del paquete contiene el carácter `ε`.
- Una transición epsilon cambia de estado sin consumir caracteres.
- Una cadena vacía para simular se representa mediante `""`; no se pasa el
  carácter `ε` como si fuera parte de la cadena de entrada.
- Una transición ausente equivale a no tener un movimiento válido.
- La simulación de AFN mantiene un conjunto de estados posibles y aplica cierre
  epsilon al inicio y después de cada símbolo. Solo acepta si, tras consumir
  toda la cadena, ese conjunto contiene algún estado de aceptación.
- Un símbolo de entrada fuera del alfabeto produce rechazo (`False`). Esto
  incluye el carácter `ε`: para simular la cadena vacía se utiliza `""`.
- La simulación de AFD mantiene un único estado actual. Acepta si, después de
  consumir toda la cadena, ese estado es final. La cadena vacía se acepta
  únicamente cuando el estado inicial es final.
- El modelo AFD admite tablas parciales y su simulador rechaza si falta una
  transición. La conversión por subconjuntos genera un AFD completo: crea el
  sumidero que representa el conjunto vacío solo si es alcanzable.
- Antes de aplicar Hopcroft a un AFD parcial se completará su tabla, cuando haga
  falta, con un estado sumidero.
- Los archivos de texto se leerán en UTF-8 para conservar `ε` correctamente.

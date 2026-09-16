# Guía de uso

## Requisitos

Python 3.10 o posterior. El código usa la biblioteca estándar; no requiere
instalar paquetes con `pip`. Graphviz es una dependencia externa únicamente
para dibujos SVG y PNG. Consulta [visualización](visualizacion.md) para instalarlo.

Todos los comandos siguientes se ejecutan desde la raíz del proyecto.

## Menú interactivo

```powershell
python main.py
```

Ofrece postfix, AFN, AFD, minimización, simulación, dibujos, archivos y AFD
directo. La opción `0` termina. Al introducir una cadena, presiona Enter para
probar la cadena vacía; no escribas el carácter `ε` como cadena de entrada.

## Operaciones por argumentos

```powershell
python main.py --help
python main.py --regex 'a(b|c)*' --operacion postfix
python main.py --regex 'a(b|c)*' --operacion afn --cadena abcc --detalles
python main.py --regex '(a|b)*abb' --operacion afd --cadena abb
python main.py --regex '(a|b)*abb' --operacion minimo --cadena aba
python main.py --regex '(a|b)*abb' --operacion directo --cadena abb
```

Sin `--operacion`, se ejecuta `todo`: postfix, Thompson, subconjuntos, Hopcroft
y simulación. `--directo` agrega la construcción directa a ese flujo.

```powershell
python main.py --regex '(a|b)*abb' --cadena abb --cadena aabb --cadena aba --cadena= --directo
```

Las cadenas se conservan exactamente. `--cadena` se puede repetir. Si no se
especifica ninguna, se evalúa la cadena vacía. Para valores que comienzan con
guion usa `=`, por ejemplo `--regex=-a --cadena=-a`. Los argumentos con símbolos
especiales o espacios deben ir entre comillas.

`--detalles` imprime conjuntos de estados, alfabeto y tabla de transiciones.
La opción postfix solo convierte la expresión y no construye autómatas.

## Archivos de expresiones

```powershell
python main.py --archivo ejemplos/expresiones.txt --cadena abb --cadena= --directo
python main.py --archivo ejemplos/expresiones_con_errores.txt --cadena ab
```

Los archivos se leen como UTF-8, con o sin BOM. Se omiten las líneas vacías,
conservando los números originales de línea. Cada expresión se procesa de
forma independiente, y las mismas cadenas se prueban en cada una.

Una expresión inválida se identifica con su número de línea y el programa
continúa con las siguientes. Las líneas no admiten comentarios: `#` es un
literal del lenguaje del proyecto. Una cadena inválida para un autómata se
reporta como `RECHAZADA`; no es un error de ejecución.

## Dibujos

```powershell
python main.py --regex '(a|b)*abb' --cadena abb --directo --dibujar --formato svg png dot
python main.py --archivo ejemplos/expresiones.txt --cadena= --dibujar --formato svg --salida salidas/lote
```

Los formatos disponibles son SVG, PNG y DOT. El formato predeterminado es SVG.
`--dot` permite indicar una ruta personalizada al ejecutable de Graphviz.

Para una expresión individual se escribe en `salidas/individual/`. Para
archivos se crean carpetas como `salidas/linea_001/`, `salidas/linea_002/`, etc.
Los nombres son `afn`, `afd`, `afd_minimo` y, si se solicitó, `afd_directo`.
No se derivan nombres de archivo del texto de la expresión regular.

Los archivos de salida existentes con el mismo nombre se reemplazan. Una línea
inválida no genera dibujos. Si falla un renderizado, se informa el error y se
continúa con los demás resultados. Los errores no borran dibujos de ejecuciones
anteriores; usa una carpeta distinta para conservar o separar ejecuciones.

## Uso desde Python

```python
from automatas import analizar_expresion

resultado = analizar_expresion("(a|b)*abb", incluir_directo=True)
print(resultado.postfix)  # ab|*a.b.b.
print(resultado.simular("abb"))  # Todos los valores son True.
```

`resultado.automatas` contiene los objetos producidos, con las claves `afn`,
`afd`, `afd_minimo` y `afd_directo` cuando corresponda. Cada uno se puede dibujar
con `dibujar_automata`. Para archivos, `analizar_archivo` devuelve objetos
`ResultadoLinea` con el número original, la expresión y el resultado o error.

## Códigos de salida y pruebas

| Código | Significado |
| --- | --- |
| `0` | Ejecución correcta; también cuando una cadena es rechazada |
| `1` | Error de archivo, expresión, renderizado o discrepancia entre autómatas |
| `2` | Argumentos de consola inválidos |
| `130` | Interrupción con Ctrl+C |

En modo archivo, el código final es `1` si hubo alguna línea inválida, aunque
las demás se hayan procesado correctamente. Un archivo vacío se informa y
termina con `0`.

```powershell
python -m unittest discover -s tests -v
```

Las pruebas cubren los algoritmos, equivalencia, minimalidad, renderizado,
archivos, el menú y una ejecución real de `main.py` con caracteres UTF-8.

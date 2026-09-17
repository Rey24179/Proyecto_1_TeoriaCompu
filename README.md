# Proyecto 1 - Teoría de la Computación

Implementación en Python de conversiones entre expresiones regulares y autómatas
finitos, para el curso CC2019 de la Universidad del Valle de Guatemala.

## Estado actual: código completo

El proyecto convierte expresiones regulares de infix a postfix con Shunting Yard,
construye su AFN con Thompson, lo convierte a AFD mediante subconjuntos y minimiza
el AFD con Hopcroft. Es posible simular la misma cadena sobre los tres autómatas.
La minimización conserva el lenguaje, elimina estados inaccesibles y completa
las tablas parciales cuando hace falta. También exporta y dibuja los autómatas
en DOT, SVG y PNG. Incluye menú interactivo, procesamiento de archivos y la
construcción directa de AFD mediante followpos como recuperación.

## Ejecutar el programa

Desde la raíz del repositorio, abre el menú con:

```powershell
python main.py
```

También puedes ejecutar el flujo completo por argumentos:

```powershell
python main.py --regex '(a|b)*abb' --cadena abb --cadena aba --directo --dibujar --formato svg png
```

Procesar un archivo, con una expresión por línea:

```powershell
python main.py --archivo ejemplos/expresiones.txt --cadena abb --cadena= --directo --dibujar
```

`--cadena=` representa explícitamente la cadena vacía y funciona en PowerShell.
Si omites `--cadena`, también se prueba la cadena vacía. Los dibujos se guardan
en `salidas/individual/` o en una subcarpeta por línea del archivo. Puedes elegir
otra carpeta con `--salida`.

Usa `python main.py --help` para consultar las opciones. La [guía de uso](docs/uso.md)
explica las operaciones, los archivos, los errores y los formatos de salida.

## Requisitos

- Python 3.10 o posterior.
- El código Python utiliza únicamente la biblioteca estándar.
- Para generar SVG y PNG se requiere Graphviz. La exportación DOT y los
  algoritmos funcionan sin él. Consulta [instalación y dibujos](docs/visualizacion.md).

Desde la raíz del repositorio, ejecuta las pruebas con:

```powershell
python -m unittest discover -s tests -v
```

## Probar la conversión a postfix

Desde la raíz del repositorio:

```powershell
python -c "from automatas import infix_a_postfix; print(infix_a_postfix('(a|b)*abb'))"
```

Resultado esperado: `ab|*a.b.b.`

También puedes usar las funciones desde Python:

```python
from automatas import infix_a_postfix, insertar_concatenacion

print(insertar_concatenacion("a(b|c)*"))  # a.(b|c)*
print(infix_a_postfix("a(b|c)*"))         # abc|*.
```

Una expresión inválida como `a|` o `(ab` produce `ValueError` con una explicación.
Los operadores disponibles son `|`, `.`, `*`, `+`, `?` y paréntesis; `ε`
representa la cadena vacía. Consulta la [explicación de Shunting Yard](docs/shunting_yard.md).

## Construir y simular un AFN

```python
from automatas import regex_a_afn, simular_afn

afn = regex_a_afn("(a|b)*abb")
print(simular_afn(afn, "abb"))    # True
print(simular_afn(afn, "aabb"))   # True
print(simular_afn(afn, "aba"))    # False
print(simular_afn(afn, ""))       # False

opcional = regex_a_afn("a?")
print(simular_afn(opcional, ""))  # True
```

También puedes probarlo directamente desde PowerShell:

```powershell
python -c "from automatas import regex_a_afn, simular_afn; afn = regex_a_afn('(a|b)*abb'); print('abb:', simular_afn(afn, 'abb')); print('aba:', simular_afn(afn, 'aba'))"
```

La salida esperada es `abb: True` y `aba: False` en líneas separadas.
Si ya tienes postfix, usa `postfix_a_afn("ab|*a.b.b.")`. Consulta la
[explicación de Thompson y la simulación](docs/thompson.md).

## Convertir a AFD y comparar la aceptación

```python
from automatas import afn_a_afd, regex_a_afn, simular_afd, simular_afn

afn = regex_a_afn("(a|b)*abb")
afd = afn_a_afd(afn)

for cadena in ("", "abb", "aabb", "aba"):
    print(repr(cadena), simular_afn(afn, cadena), simular_afd(afd, cadena))
```

Salida esperada:

```text
'' False False
'abb' True True
'aabb' True True
'aba' False False
```

Cada estado del AFD representa un conjunto de estados del AFN. El AFD generado
es completo sobre su alfabeto e incluye un estado sumidero cuando se necesita.
El AFN original se conserva. La minimización se realiza en una llamada separada
a Hopcroft. Consulta la [explicación de subconjuntos](docs/subconjuntos.md).

## Minimizar con Hopcroft

```python
from automatas import afn_a_afd, minimizar_afd, regex_a_afn, simular_afd, simular_afn

afn = regex_a_afn("(a|b)*abb")
afd = afn_a_afd(afn)
minimo = minimizar_afd(afd)

print(len(afd.estados), len(minimo.estados))  # 5 4
for cadena in ("abb", "aba", ""):
    print(
        repr(cadena),
        simular_afn(afn, cadena),
        simular_afd(afd, cadena),
        simular_afd(minimo, cadena),
    )
```

Los tres autómatas aceptan `abb` y rechazan `aba` y la cadena vacía. El AFD
original se conserva. `minimizar_afd` devuelve un AFD mínimo completo sobre el
mismo alfabeto; si recibe una tabla parcial, puede necesitar un estado adicional
para representar el rechazo permanente. Consulta la
[explicación de Hopcroft](docs/hopcroft.md).

## Dibujar los tres autómatas

Desde la raíz del repositorio:

```powershell
python -m ejemplos.dibujar
```

Genera `afn`, `afd` y `afd_minimo` en los formatos DOT, SVG y PNG dentro de
`salidas/ejemplo/`. Abre los SVG en tu navegador o los PNG en un visor de imágenes.

Para dibujar cualquier AFN o AFD creado con los modelos del proyecto:

```python
from automatas import dibujar_automata, regex_a_afn

afn = regex_a_afn("a|ε")
dibujar_automata(afn, "salidas/afn.svg", "AFN para a o epsilon")
dibujar_automata(afn, "salidas/afn.dot")  # No necesita Graphviz.
```

## Estructura actual

```text
automatas/
    __init__.py       # Exportaciones del paquete
    modelos.py        # Representación y validación de AFN y AFD
    regex.py          # Validación, concatenación y Shunting Yard
    thompson.py       # Construcción de AFN desde postfix o infix
    subconjuntos.py   # Conversión de AFN a AFD
    hopcroft.py       # Preparación y minimización del AFD
    simulacion.py     # Cierre epsilon, movimientos y simulación de AFN y AFD
    visualizacion.py  # Exportación DOT y dibujos con Graphviz
    directo.py        # AFD directo mediante posiciones y followpos
    analisis.py       # Coordinación de operaciones y simulación
    archivos.py       # Archivos UTF-8 y errores por línea
ejemplos/
    dibujar.py        # Genera los tres autómatas de ejemplo
    expresiones.txt   # Entrada válida para el procesamiento por archivo
    expresiones_con_errores.txt # Muestra recuperación después de errores
docs/
    arquitectura.md  # Objetos y comunicación entre módulos
    convenciones.md  # Símbolos y sintaxis aceptada
    shunting_yard.md  # Explicación del conversor con ejemplo paso a paso
    thompson.md       # Reglas de construcción y ejemplo de simulación
    subconjuntos.md   # Conversión a AFD con tabla de estados
    hopcroft.md       # Particiones, minimización y verificación
    visualizacion.md # Instalación, formatos y convenciones de dibujo
    directo.md       # Construcción directa con followpos
    uso.md           # Menú y opciones de consola
tests/
    test_modelos.py   # Pruebas de las estructuras de datos
    test_regex.py     # Pruebas de conversión y errores de sintaxis
    test_thompson.py  # Construcción y aceptación de lenguajes
    test_subconjuntos.py # Conversión y equivalencia entre AFN y AFD
    test_hopcroft.py  # Equivalencia y minimalidad del AFD resultante
    test_simulacion.py # Recorridos sobre autómatas definidos a mano
    test_visualizacion.py # Exportación y renderizado real de imágenes
    test_directo.py   # Equivalencia de la construcción directa
    test_integracion.py # Archivos y programa completo
main.py              # Punto de entrada del programa
```

La cadena vacía se representa con `ε` en las expresiones regulares y las
transiciones. Una cadena de entrada vacía se representa con `""` en Python.
El símbolo `ε` no pertenece al alfabeto de entrada ni se consume al simular.

Consulta la [arquitectura](docs/arquitectura.md) y las
[convenciones](docs/convenciones.md).

## Entrega final



**Enlace al video:** (https://youtu.be/zEXoY0udQjY?si=Po6kCHCOfB5XoQ93)

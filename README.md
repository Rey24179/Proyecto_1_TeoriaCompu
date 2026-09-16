# Proyecto 1 - Teoría de la Computación

Implementación en Python de conversiones entre expresiones regulares y autómatas
finitos, para el curso CC2019 de la Universidad del Valle de Guatemala.

## Estado actual: parte 3

El proyecto convierte expresiones regulares de infix a postfix con Shunting Yard,
construye su AFN con Thompson y simula cadenas sobre ese AFN. El conversor valida
la sintaxis y la simulación considera las transiciones epsilon. La conversión
a AFD, su simulación y su minimización se agregarán en las siguientes partes.

## Requisitos

- Python 3.10 o posterior.
- Esta parte utiliza únicamente la biblioteca estándar de Python.

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

## Estructura actual

```text
automatas/
    __init__.py       # Exportaciones del paquete
    modelos.py        # Representación y validación de AFN y AFD
    regex.py          # Validación, concatenación y Shunting Yard
    thompson.py       # Construcción de AFN desde postfix o infix
    simulacion.py     # Cierre epsilon, movimientos y simulación del AFN
docs/
    arquitectura.md  # Objetos y comunicación entre módulos
    convenciones.md  # Símbolos y sintaxis aceptada
    plan.md          # Entregas separadas por commits
    shunting_yard.md  # Explicación del conversor con ejemplo paso a paso
    thompson.md       # Reglas de construcción y ejemplo de simulación
tests/
    test_modelos.py   # Pruebas de las estructuras de datos
    test_regex.py     # Pruebas de conversión y errores de sintaxis
    test_thompson.py  # Construcción y aceptación de lenguajes
    test_simulacion.py # Recorridos sobre autómatas definidos a mano
```

La cadena vacía se representa con `ε` en las expresiones regulares y las
transiciones. Una cadena de entrada vacía se representa con `""` en Python.
El símbolo `ε` no pertenece al alfabeto de entrada ni se consume al simular.

Consulta el [plan de commits](docs/plan.md), la
[arquitectura](docs/arquitectura.md) y las [convenciones](docs/convenciones.md).

## Entrega final

Queda pendiente implementar subconjuntos, simulación de AFD, Hopcroft, los dibujos
y la interfaz con lectura de archivos, además de completar la documentación y
agregar el enlace al video explicativo no listado de YouTube, de un máximo de
10 minutos. El enunciado solicita entregar el proyecto en un repositorio privado
de GitHub o Bitbucket.

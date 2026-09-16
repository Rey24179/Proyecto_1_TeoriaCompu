# Proyecto 1 - Teoría de la Computación

Implementación en Python de conversiones entre expresiones regulares y autómatas
finitos, para el curso CC2019 de la Universidad del Valle de Guatemala.

## Estado actual: parte 2

El proyecto define los objetos `AFN` y `AFD` y convierte expresiones regulares
de infix a postfix con Shunting Yard. El conversor valida la sintaxis, inserta
concatenación explícita y respeta la precedencia de los operadores. La generación
de autómatas y la simulación de cadenas se agregarán en las siguientes partes.

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

## Estructura actual

```text
automatas/
    __init__.py       # Exportaciones del paquete
    modelos.py        # Representación y validación de AFN y AFD
    regex.py          # Validación, concatenación y Shunting Yard
docs/
    arquitectura.md  # Objetos y comunicación entre módulos
    convenciones.md  # Símbolos y sintaxis aceptada
    plan.md          # Entregas separadas por commits
    shunting_yard.md  # Explicación del conversor con ejemplo paso a paso
tests/
    test_modelos.py   # Pruebas de las estructuras de datos
    test_regex.py     # Pruebas de conversión y errores de sintaxis
```

La cadena vacía se representa con `ε` en las expresiones regulares y las
transiciones. Una cadena de entrada vacía se representará con `""` en Python.
El símbolo `ε` no pertenece al alfabeto de entrada ni se consume al simular.

Consulta el [plan de commits](docs/plan.md), la
[arquitectura](docs/arquitectura.md) y las [convenciones](docs/convenciones.md).

## Entrega final

Queda pendiente implementar los algoritmos de autómatas, los dibujos y la lectura de archivos,
además de completar la documentación y agregar el enlace al video explicativo
no listado de YouTube, de un máximo de 10 minutos. El enunciado solicita entregar
el proyecto en un repositorio privado de GitHub o Bitbucket.

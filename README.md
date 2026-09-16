# Proyecto 1 - Teoría de la Computación

Implementación en Python de conversiones entre expresiones regulares y autómatas
finitos, para el curso CC2019 de la Universidad del Valle de Guatemala.

## Estado actual: parte 1

Esta primera entrega define los objetos `AFN` y `AFD`, sus validaciones y las
convenciones del proyecto. Los algoritmos se agregarán en los siguientes commits;
todavía no se procesan expresiones regulares ni se simulan cadenas.

## Requisitos

- Python 3.10 o posterior.
- Esta parte utiliza únicamente la biblioteca estándar de Python.

Desde la raíz del repositorio, ejecuta las pruebas con:

```powershell
python -m unittest discover -s tests -v
```

## Estructura actual

```text
automatas/
    __init__.py       # Exportaciones del paquete
    modelos.py        # Representación y validación de AFN y AFD
docs/
    arquitectura.md  # Objetos y comunicación entre módulos
    convenciones.md  # Símbolos y sintaxis prevista
    plan.md          # Entregas separadas por commits
tests/
    test_modelos.py   # Pruebas de las estructuras de datos
```

La cadena vacía se representa con `ε` en las expresiones regulares y las
transiciones. Una cadena de entrada vacía se representará con `""` en Python.
El símbolo `ε` no pertenece al alfabeto de entrada ni se consume al simular.

Consulta el [plan de commits](docs/plan.md), la
[arquitectura](docs/arquitectura.md) y las [convenciones](docs/convenciones.md).

## Entrega final

Queda pendiente implementar los algoritmos, los dibujos y la lectura de archivos,
además de completar la documentación y agregar el enlace al video explicativo
no listado de YouTube, de un máximo de 10 minutos. El enunciado solicita entregar
el proyecto en un repositorio privado de GitHub o Bitbucket.

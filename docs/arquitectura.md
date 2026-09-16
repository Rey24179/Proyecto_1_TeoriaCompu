# Arquitectura y estructuras de datos

## Implementado en la parte 1

El paquete `automatas` expone `AFN`, `AFD` y `EPSILON`. Los objetos se basan en
la definición formal de un autómata `(Q, Σ, δ, q0, F)`:

| Componente | Atributo | Tipo en Python |
| --- | --- | --- |
| Estados `Q` | `estados` | `set[int]` |
| Alfabeto `Σ` | `alfabeto` | `set[str]` |
| Estado inicial `q0` | `estado_inicial` | `int` |
| Estados de aceptación `F` | `estados_aceptacion` | `set[int]` |
| Transiciones `δ` en un AFN | `transiciones` | `dict[tuple[int, str], set[int]]` |
| Transiciones `δ` en un AFD | `transiciones` | `dict[tuple[int, str], int]` |

En el AFN, una pareja `(estado, símbolo)` puede llevar a varios estados. En el
AFD, esa pareja solo tiene un destino. En ambos casos, una clave ausente
representa una transición no definida. La función de transición de un AFD
parcial se completará para los algoritmos que necesiten un AFD total.

Ejemplo de un AFN con una transición epsilon y dos destinos para `a`:

```python
from automatas import AFN, EPSILON

afn = AFN(
    estados={0, 1, 2},
    alfabeto={"a"},
    estado_inicial=0,
    estados_aceptacion={2},
    transiciones={
        (0, EPSILON): {1},
        (1, "a"): {1, 2},
    },
)
```

Ejemplo de un AFD para la cadena `a`, con tabla parcial:

```python
from automatas import AFD

afd = AFD(
    estados={0, 1},
    alfabeto={"a"},
    estado_inicial=0,
    estados_aceptacion={1},
    transiciones={(0, "a"): 1},
)
```

### Validación

Al construir un objeto se comprueba que el estado inicial, los estados finales
y los extremos de las transiciones existan. Los símbolos del alfabeto deben
tener un carácter y no pueden ser `ε`. Las etiquetas de las transiciones deben
pertenecer al alfabeto, salvo `ε` en un AFN. Una inconsistencia produce `ValueError`.

Los conjuntos y diccionarios son mutables. Si un algoritmo los modifica después
de construir el objeto, debe llamar a `validar()` al terminar. Los algoritmos de
conversión crearán nuevos objetos para conservar los autómatas anteriores.
Los tipos de datos indicados son parte del contrato entre módulos; estas
validaciones comprueban la coherencia del autómata, no sustituyen un verificador
de tipos de Python.

## Conversión de expresiones: parte 2

El módulo `automatas.regex` implementa estas funciones, también exportadas
desde `automatas`:

| Función | Entrada | Salida |
| --- | --- | --- |
| `insertar_concatenacion(expresion: str) -> str` | Expresión infix | Infix validada, sin espacios y con concatenación explícita |
| `infix_a_postfix(expresion: str) -> str` | Expresión infix | Expresión postfix validada |

`infix_a_postfix` llama a `insertar_concatenacion` y después aplica Shunting Yard.
Ambas funciones producen `ValueError` ante una expresión inválida. Las posiciones
indicadas en los errores se cuentan desde 1 sobre la entrada original, incluidos
sus espacios. El error de expresión vacía o de operando faltante al final se
describe sin una posición concreta.

El resultado es una cadena, sin espacios ni paréntesis: cada carácter representa
un literal, `ε` o un operador. Thompson consume esta representación para construir
el AFN. La explicación y una traza están en [Shunting Yard](shunting_yard.md).

## Thompson y simulación de AFN: parte 3

Las siguientes funciones también se exportan desde el paquete `automatas`:

| Función | Entrada | Salida |
| --- | --- | --- |
| `postfix_a_afn(postfix: str) -> AFN` | Expresión postfix | Nuevo AFN con un único estado de aceptación |
| `regex_a_afn(expresion: str) -> AFN` | Expresión infix | Nuevo AFN construido con Shunting Yard y Thompson |
| `cierre_epsilon(afn, estados) -> set[int]` | AFN válido y conjunto de estados | Estados alcanzables usando cero o más transiciones epsilon |
| `mover(afn, estados, simbolo) -> set[int]` | AFN válido, conjunto de estados y símbolo | Destinos al consumir el símbolo, sin cierre epsilon |
| `simular_afn(afn: AFN, cadena: str) -> bool` | AFN y cadena completa | `True` si acepta, `False` si rechaza |

`postfix_a_afn` guarda fragmentos en una pila. Cada `_Fragmento` contiene dos
enteros: `inicio` y `fin`. Los estados, el alfabeto y las transiciones se acumulan
en estructuras locales a la llamada, y el constructor de `AFN` valida el
resultado final. Los errores de postfix producen `ValueError`.

`regex_a_afn` llama a `infix_a_postfix` y entrega su resultado a `postfix_a_afn`.
La llamada no altera otros autómatas ni utiliza contadores globales de estados.

`cierre_epsilon` y `mover` aceptan `set[int]` o `frozenset[int]`, comprueban que
los estados pertenezcan al AFN y devuelven conjuntos nuevos. Requieren un AFN
válido; no repiten la validación completa en cada movimiento. Si se les pasan
estados ajenos al AFN, lanzan `ValueError`. `mover` devuelve el conjunto vacío
para símbolos fuera del alfabeto, incluido `ε`.

`simular_afn` valida primero el AFN y luego combina estas operaciones. No elimina
espacios de la cadena ni acepta solamente un prefijo: debe consumirse toda la
entrada. Un símbolo fuera del alfabeto implica rechazo. La simulación conserva
el autómata para futuras cadenas y conversiones.

Las reglas de construcción y una traza se describen en [Thompson](thompson.md).

## Subconjuntos y simulación de AFD: parte 4

Se agregan dos funciones, también exportadas desde `automatas`:

| Función | Entrada | Salida |
| --- | --- | --- |
| `afn_a_afd(afn: AFN) -> AFD` | AFN válido | Nuevo AFD completo y equivalente |
| `simular_afd(afd: AFD, cadena: str) -> bool` | AFD y cadena completa | `True` si acepta, `False` si rechaza |

`afn_a_afd` valida el AFN y reutiliza `cierre_epsilon` y `mover`. La construcción
mantiene un diccionario local `dict[frozenset[int], int]` que asigna un entero a
cada subconjunto descubierto, y una cola `deque` con los subconjuntos pendientes.
El cierre del estado inicial recibe el número `0`; los demás se numeran por
orden de descubrimiento, recorriendo el alfabeto ordenado para obtener resultados
reproducibles. El diccionario es interno: la función devuelve únicamente el AFD.

Un estado del AFD es final si su subconjunto contiene algún final del AFN. Solo
se generan subconjuntos alcanzables. Si se alcanza el conjunto vacío, se crea
su estado sumidero, con transiciones hacia sí mismo para todo el alfabeto. La
tabla resultante es total, incluso si el AFN tenía transiciones ausentes.
Todos los conjuntos y diccionarios del AFD son independientes del AFN recibido.

`simular_afd` valida el autómata y mantiene un único estado actual. Por cada
carácter sigue la transición correspondiente; un símbolo ajeno al alfabeto o
una transición ausente implica rechazo. También funciona con los AFD parciales
que permite `modelos.py`. Al terminar acepta únicamente si el estado actual es
final. No modifica el AFD ni elimina espacios de la cadena.

Una entrada inconsistente produce `ValueError` al validar; una cadena que no
pertenece al lenguaje devuelve `False`. El ejemplo de la construcción está en
[Subconjuntos](subconjuntos.md).

## Módulos del proyecto y previstos

Actualmente existen `modelos.py`, `regex.py`, `thompson.py`, `subconjuntos.py` y
`simulacion.py` para ambos tipos de autómata. Los demás módulos forman parte del
diseño de las siguientes entregas.

| Módulo | Responsabilidad | Entrada y salida previstas |
| --- | --- | --- |
| `modelos.py` | Definir y validar autómatas | Componentes → `AFN` o `AFD` |
| `regex.py` | Validar sintaxis e implementar Shunting Yard | `str` infix → `str` postfix |
| `thompson.py` | Construir un AFN con fragmentos | `str` postfix o infix → `AFN` |
| `subconjuntos.py` | Aplicar cierre epsilon y conjuntos de estados | `AFN` → `AFD` |
| `hopcroft.py` | Eliminar estados inaccesibles, completar y minimizar | `AFD` → `AFD` |
| `simulacion.py` | Evaluar la pertenencia de una cadena | `AFN` o `AFD`, `str` → `bool` |
| `visualizacion.py` | Dibujar estados y transiciones | `AFN` o `AFD`, ruta → archivo |
| `archivos.py` | Leer expresiones e informar errores por línea | Ruta UTF-8 → expresiones con número de línea |
| `main.py` (en la raíz) | Coordinar las opciones del usuario | Argumentos de consola → resultados |

La construcción directa de AFD se reservará para un módulo adicional si se
realiza la parte de recuperación.

## Flujo previsto

1. La interfaz recibe una expresión regular y una cadena.
2. Shunting Yard valida y transforma la expresión a postfix.
3. Thompson construye el AFN.
4. Subconjuntos transforma ese AFN en un AFD.
5. Hopcroft produce un nuevo AFD mínimo.
6. La simulación evalúa la misma cadena sobre cada autómata producido.
7. La visualización dibuja los autómatas solicitados.

Los módulos se comunicarán mediante llamadas a funciones y los objetos
anteriores, sin variables globales para guardar estados. Los errores de entrada
se comunicarán mediante `ValueError`; la interfaz los presentará al usuario.
Para un archivo, se procesará una expresión por línea y se identificará cada
resultado con su número de línea, continuando después de una expresión inválida.

## Documentación pendiente

La arquitectura se actualizará conforme se implementen las funciones. La entrega
final debe incluir ejemplos completos de uso y el enlace al video no listado de
YouTube, con duración máxima de 10 minutos. El video todavía no se ha creado.

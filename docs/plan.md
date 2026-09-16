# Plan de trabajo por commits

Cada parte debe quedar funcionando y revisada antes de pasar a la siguiente.
Los commits los realiza el estudiante después de probar y comprender la entrega.
La documentación se actualizará junto con el código de cada parte.

| Parte | Entrega | Comprobación antes del commit | Mensaje sugerido |
| --- | --- | --- | --- |
| 1 | Estructura, convenciones y modelos AFN/AFD | Pruebas de objetos válidos e inconsistencias | `feat: agregar estructura inicial y modelos de automatas` |
| 2 | Infix a postfix con Shunting Yard | Precedencia, concatenación, paréntesis y sintaxis inválida | `feat: convertir expresiones infix a postfix` |
| 3 | Thompson y simulación de AFN | Unión, concatenación, cierres y cadena vacía | `feat: construir y simular AFN con Thompson` |
| 4 | Subconjuntos y simulación de AFD | Comparar aceptación entre AFN y AFD | `feat: convertir AFN a AFD mediante subconjuntos` |
| 5 | Minimización con Hopcroft | Conservar el lenguaje y reducir estados en casos conocidos | `feat: minimizar AFD con Hopcroft` |
| 6 | Dibujos de AFN y AFD | Revisar estado inicial, finales, epsilon y etiquetas | `feat: dibujar automatas finitos` |
| 7 | Interfaz de consola y archivos de expresiones | Probar el flujo completo y errores por línea | `feat: integrar consola y procesamiento de archivos` |
| 8 | Documentación final y referencia al video | Revisar requisitos, ejemplos y enlace al video | `docs: completar documentacion y guia de uso` |
| 9 (opcional) | Construcción directa de AFD y su integración | Comparar aceptación con los otros autómatas y dibujar el AFD directo | `feat: agregar construccion directa de AFD` |

## Requisitos del enunciado

- [x] Convertir de infix a postfix usando Shunting Yard.
- [x] Construir un AFN mediante Thompson.
- [x] Construir un AFD mediante subconjuntos.
- [x] Minimizar un AFD con Hopcroft.
- [x] Simular la cadena sobre cada AFN y AFD producido e informar aceptación
  (funciones e interfaz de consola implementadas).
- [x] Dibujar un AFN o AFD dado.
- [x] Procesar un archivo UTF-8 con una expresión regular por línea y producir
  los resultados requeridos para cada expresión.
- [x] Definir explícitamente el símbolo epsilon: `ε`.
- [x] Definir los objetos que representan AFN y AFD.
- [x] Completar la documentación de arquitectura y comunicación entre módulos.
- [ ] Incluir un enlace a un video no listado de YouTube de hasta 10 minutos.
- [ ] Verificar que el repositorio usado para entregar sea privado.
- [x] Opcional: construcción directa de AFD para recuperación.

La rúbrica asigna 15 puntos a los requisitos base y 3 puntos adicionales a la
construcción directa. El dibujo y la lectura de archivos también son requisitos,
aunque no aparezcan como filas separadas en la tabla de ponderaciones.

## Parte 1: cómo revisar y guardar

Ejecutar desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
git diff --stat
git status --short
git add .gitignore README.md automatas docs tests
git diff --cached --stat
git commit -m "feat: agregar estructura inicial y modelos de automatas"
```

Antes de agregar los archivos, `git diff --stat` no muestra los archivos nuevos
sin seguimiento; estos sí aparecen en `git status --short`. Después de
`git add`, `git diff --cached --stat` muestra lo que entrará en el commit.

## Parte 2: cómo revisar y guardar

Incluye el conversor, sus pruebas y la documentación actualizada. Esta entrega
todavía no implementa Thompson ni la interfaz de consola completa.

```powershell
python -m unittest discover -s tests -v
python -c "from automatas import infix_a_postfix; print(infix_a_postfix('(a|b)*abb'))"
git status --short
git add automatas/regex.py automatas/__init__.py tests/test_regex.py README.md docs
git diff --cached --stat
git commit -m "feat: convertir expresiones infix a postfix"
```

La conversión del ejemplo debe imprimir `ab|*a.b.b.`.

## Parte 3: cómo revisar y guardar

Incluye Thompson, cierre epsilon, movimientos y simulación de AFN. La conversión
a AFD y su simulación se reservan para la parte 4.

```powershell
python -m unittest discover -s tests -v
python -c "from automatas import regex_a_afn, simular_afn; afn = regex_a_afn('(a|b)*abb'); print('abb:', simular_afn(afn, 'abb')); print('aba:', simular_afn(afn, 'aba'))"
git status --short
git add automatas/thompson.py automatas/simulacion.py automatas/__init__.py tests/test_thompson.py tests/test_simulacion.py README.md docs
git diff --cached --stat
git commit -m "feat: construir y simular AFN con Thompson"
```

El ejemplo debe imprimir `abb: True` y `aba: False` en líneas separadas.

## Parte 4: cómo revisar y guardar

Incluye construcción de subconjuntos, simulación del AFD y comparaciones de
aceptación con el AFN. Hopcroft se reserva para la parte 5.

```powershell
python -m unittest discover -s tests -v
python -c "from automatas import regex_a_afn, afn_a_afd, simular_afd; afd = afn_a_afd(regex_a_afn('(a|b)*abb')); print('abb:', simular_afd(afd, 'abb')); print('aba:', simular_afd(afd, 'aba'))"
git status --short
git add automatas tests README.md docs
git diff --cached --stat
git commit -m "feat: convertir AFN a AFD mediante subconjuntos"
```

El ejemplo debe imprimir `abb: True` y `aba: False` en líneas separadas.

## Parte 5: cómo revisar y guardar

Incluye eliminación de estados inaccesibles, completado de tablas parciales y
minimización con Hopcroft. El resultado se simula con `simular_afd`.

```powershell
python -m unittest discover -s tests -v
python -c "from automatas import regex_a_afn, afn_a_afd, minimizar_afd; afd = afn_a_afd(regex_a_afn('(a|b)*abb')); minimo = minimizar_afd(afd); print(len(afd.estados), len(minimo.estados))"
git status --short
git add automatas tests README.md docs
git diff --cached --stat
git commit -m "feat: minimizar AFD con Hopcroft"
```

El ejemplo debe imprimir `5 4`: el AFD pasa de cinco estados a cuatro sin cambiar
su lenguaje. La siguiente parte agregará los dibujos de los autómatas.

## Parte 6: cómo revisar y guardar

```powershell
python -m unittest discover -s tests -v
python -m ejemplos.dibujar
git status --short
git add .gitignore automatas tests ejemplos README.md docs
git diff --cached --stat
git commit -m "feat: dibujar automatas finitos"
```

Los dibujos quedan en `salidas/ejemplo/`. Los binarios portátiles de Graphviz
en `.tools/` no se incluyen en el commit.

## Integración final del código

Se implementaron también la consola, la lectura de archivos y la construcción
directa. Para guardar todos los cambios restantes juntos:

```powershell
python -m unittest discover -s tests -v
python main.py --regex '(a|b)*abb' --cadena abb --cadena aba --directo --dibujar
python main.py --archivo ejemplos/expresiones.txt --cadena abb --cadena= --directo
git add .gitignore main.py automatas tests ejemplos README.md docs
git diff --cached --stat
git commit -m "feat: completar visualizacion consola archivos y AFD directo"
```

La grabación del video, su enlace y la privacidad del repositorio son los pasos
de entrega que debe realizar el estudiante.

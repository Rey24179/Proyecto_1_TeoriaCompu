# Parte 6: dibujos de los autómatas

Se dibujan AFN, AFD y AFD mínimo a partir de sus estados y tablas de transiciones.
Graphviz se encarga de distribuir el grafo; los algoritmos de construcción,
simulación y minimización siguen siendo implementaciones propias del proyecto.

## Dependencia de Graphviz

El código Python no necesita paquetes de `pip`. Para SVG y PNG utiliza el
ejecutable `dot` de [Graphviz](https://graphviz.org/download/). Instalar solamente
el paquete Python llamado `graphviz` no proporciona ese ejecutable.

Puedes instalar Graphviz en tu sistema y agregar su carpeta `bin` a `PATH`.
Comprueba la instalación desde una terminal nueva con:

```powershell
dot -V
```

En Windows también puedes descargar el ZIP oficial y extraerlo dentro de
`.tools/graphviz/`, conservando sus bibliotecas. El programa detecta estas formas:

```text
.tools/graphviz/bin/dot.exe
.tools/graphviz/Graphviz-<version>-win64/bin/dot.exe
```

En este equipo se preparó la distribución portátil oficial Graphviz 16.1.0 de
64 bits y se verificó su SHA-256 contra la suma publicada. La carpeta `.tools/`
está excluida de Git: al clonar el repositorio en otro equipo debes configurar
Graphviz nuevamente. No se modificó el `PATH` del sistema.

También puedes indicar una ubicación personalizada usando el argumento
`ejecutable_dot` de `dibujar_automata`. La búsqueda automática prioriza `PATH`
y luego la carpeta portátil. La exportación DOT funciona aunque Graphviz falte.

## Generar los ejemplos

Desde la raíz:

```powershell
python -m ejemplos.dibujar
```

El ejemplo procesa `(a|b)*abb` y escribe nueve archivos dentro de
`salidas/ejemplo/`: AFN, AFD y AFD mínimo, cada uno como `.dot`, `.svg` y `.png`.
Si falta Graphviz, primero se generan los tres DOT y después se informa el error.
Los archivos existentes con esos nombres se reemplazan. La carpeta `salidas/`
está excluida de Git porque sus archivos se pueden regenerar.

Para dibujar una expresión diferente:

```python
from automatas import afn_a_afd, dibujar_automata, minimizar_afd, regex_a_afn

afn = regex_a_afn("(a|b)*abb")
afd = afn_a_afd(afn)
minimo = minimizar_afd(afd)

dibujar_automata(afn, "salidas/personal/afn.svg", "AFN - Thompson")
dibujar_automata(afd, "salidas/personal/afd.svg", "AFD - Subconjuntos")
dibujar_automata(minimo, "salidas/personal/minimo.png", "AFD mínimo - Hopcroft")
```

La ruta devuelta es un objeto `Path`. Las carpetas se crean automáticamente.

## Formatos y significado visual

| Formato | Uso | ¿Requiere Graphviz? |
| --- | --- | --- |
| DOT | Texto editable que describe estados y transiciones | No |
| SVG | Dibujo vectorial para ampliar sin perder nitidez | Sí |
| PNG | Imagen para capturas y presentaciones | Sí |

- Una flecha desde un punto externo identifica el estado inicial.
- Un doble círculo y un relleno verde identifican los estados de aceptación.
- Los demás estados se dibujan como círculos con relleno azul claro.
- `ε` marca las transiciones que no consumen entrada.
- Varios símbolos entre el mismo origen y destino comparten una flecha.
- Un espacio literal aparece como `' '`; una coma literal aparece como `','`.
- Los ciclos, estados aislados y sumideros se dibujan si existen en el autómata.

Los estados conservan sus identificadores como etiquetas `q0`, `q1`, etcétera;
también se admiten identificadores negativos o no consecutivos. El dibujo no
elimina estados ni completa transiciones: representa el objeto recibido.

La generación de DOT ordena los estados, aristas y etiquetas para producir texto
reproducible. La distribución exacta del dibujo puede variar según la versión
de Graphviz y las fuentes disponibles. SVG usa el formato oficial de
[salida de Graphviz](https://graphviz.org/docs/outputs/svg/).

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas comprueban los estados, finales, ramificaciones, caracteres especiales
y que el autómata no cambie. Con Graphviz instalado, además generan imágenes
reales, analizan el SVG y verifican los nodos, flechas y etiquetas; también
comprueban que los PNG tengan cabecera y dimensiones válidas. Las pruebas de
renderizado real se omiten explícitamente si Graphviz no está disponible.

Se revisaron visualmente los tres dibujos de `(a|b)*abb`. Si Graphviz falla o
supera el límite de tiempo, se informa un error y no se reemplaza el archivo
anterior con una salida incompleta del renderizador.

La sintaxis del archivo DOT está documentada en la
[referencia oficial](https://graphviz.org/doc/info/lang.html).

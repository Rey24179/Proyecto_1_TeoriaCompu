"""Exportación fiel a DOT, manejo de errores y renderizado real con Graphviz."""

from copy import deepcopy
from pathlib import Path
import struct
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

from automatas import AFD, AFN, EPSILON, automata_a_dot, dibujar_automata
from automatas import afn_a_afd, minimizar_afd, regex_a_afn
from automatas.visualizacion import _buscar_dot


class TestExportacionDOT(unittest.TestCase):
    def test_incluye_estados_aislados_inicio_y_finales(self):
        afn = AFN({-3, 9, 12}, {"a"}, 9, {-3}, {(9, "a"): {-3, 9}})
        dot = automata_a_dot(afn)
        self.assertIn('s0 [label="q-3", shape=doublecircle', dot)
        self.assertIn('s1 [label="q9", shape=circle', dot)
        self.assertIn('s2 [label="q12", shape=circle', dot)
        self.assertIn('__inicio -> s1;', dot)
        self.assertIn('s1 -> s0 [label="a"]', dot)
        self.assertIn('s1 -> s1 [label="a"]', dot)

    def test_agrupa_simbolos_y_conserva_las_ramas_del_afn(self):
        afn = AFN(
            {0, 1, 2}, {"a", "b"}, 0, {1, 2},
            {(0, "a"): {1, 2}, (0, "b"): {1}, (0, EPSILON): {1}},
        )
        dot = automata_a_dot(afn)
        self.assertIn('s0 -> s1 [label="a, b, ε"]', dot)
        self.assertIn('s0 -> s2 [label="a"]', dot)
        self.assertEqual(dot.count('shape=doublecircle'), 2)

    def test_un_estado_puede_ser_inicial_y_final(self):
        dot = automata_a_dot(AFD({7}, set(), 7, {7}))
        self.assertIn('__inicio -> s0;', dot)
        self.assertIn('s0 [label="q7", shape=doublecircle', dot)

    def test_sin_finales_no_agrega_estados_de_aceptacion(self):
        self.assertNotIn('doublecircle', automata_a_dot(AFD({0}, set(), 0, set())))

    def test_no_inventa_transiciones_para_destinos_vacios(self):
        dot = automata_a_dot(AFN({0}, {"a"}, 0, set(), {(0, "a"): set()}))
        self.assertEqual(dot.count(' -> '), 1)  # Solo la flecha de inicio.

    def test_protege_comillas_y_barras_en_titulos(self):
        titulo = 'Prueba "literal" \\N\nsiguiente'
        dot = automata_a_dot(AFD({0}, set(), 0, {0}), titulo)
        self.assertIn('label="Prueba \\"literal\\" \\\\N\\nsiguiente"', dot)

    def test_hace_visibles_espacios_y_caracteres_de_control(self):
        afd = AFD({0, 1}, {" ", "\t", "\n", ",", "\x00"}, 0, {1}, {
            (0, simbolo): 1 for simbolo in (" ", "\t", "\n", ",", "\x00")
        })
        dot = automata_a_dot(afd)
        self.assertIn("' '", dot)
        self.assertIn("','", dot)
        self.assertIn("\\\\t", dot)
        self.assertIn("\\\\n", dot)
        self.assertNotIn("\x00", dot)

    def test_resultado_reproducible_y_sin_mutaciones(self):
        afn = regex_a_afn("(a|b)*abb")
        copia = deepcopy(afn)
        copia.transiciones = dict(reversed(list(copia.transiciones.items())))
        self.assertEqual(automata_a_dot(afn), automata_a_dot(copia))
        self.assertEqual(afn, copia)

    def test_rechaza_tipo_ajeno_y_automata_inconsistente(self):
        with self.assertRaises(TypeError):
            automata_a_dot("a*")
        afd = AFD({0}, {"a"}, 0, set())
        afd.transiciones[(0, "a")] = 99
        with self.assertRaises(ValueError):
            automata_a_dot(afd)


class TestArchivosVisualizacion(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)
        self.afn = regex_a_afn("a|ε")

    def test_guarda_dot_utf8_y_crea_carpetas_sin_graphviz(self):
        ruta = self.carpeta / "subcarpeta" / "afn.dot"
        with patch('automatas.visualizacion._buscar_dot') as buscar:
            self.assertEqual(dibujar_automata(self.afn, ruta), ruta)
            buscar.assert_not_called()
        self.assertEqual(ruta.read_text(encoding="utf-8"), automata_a_dot(self.afn))

    def test_rechaza_extension_no_soportada_sin_crear_archivos(self):
        with self.assertRaises(ValueError):
            dibujar_automata(self.afn, self.carpeta / "nueva" / "afn.jpg")
        self.assertFalse((self.carpeta / "nueva").exists())

    def test_falta_de_graphviz_da_un_error_util(self):
        with patch('automatas.visualizacion._buscar_dot', return_value=None):
            with self.assertRaisesRegex(FileNotFoundError, 'Graphviz'):
                dibujar_automata(self.afn, self.carpeta / "afn.svg")
        self.assertFalse((self.carpeta / "afn.svg").exists())

    def test_error_de_renderizado_conserva_el_archivo_existente(self):
        ruta = self.carpeta / "afn.svg"
        ruta.write_text("contenido anterior", encoding="utf-8")
        error = subprocess.CalledProcessError(1, ["dot"], stderr=b"error de prueba")
        with patch('automatas.visualizacion.subprocess.run', side_effect=error):
            with self.assertRaisesRegex(RuntimeError, 'error de prueba'):
                dibujar_automata(self.afn, ruta, ejecutable_dot="dot")
        self.assertEqual(ruta.read_text(encoding="utf-8"), "contenido anterior")

    def test_timeout_y_salida_vacia_se_reportan_como_errores(self):
        with patch('automatas.visualizacion.subprocess.run', side_effect=subprocess.TimeoutExpired("dot", 30)):
            with self.assertRaisesRegex(RuntimeError, '30 segundos'):
                dibujar_automata(self.afn, self.carpeta / "afn.svg", ejecutable_dot="dot")
        with patch('automatas.visualizacion.subprocess.run', return_value=subprocess.CompletedProcess("dot", 0, b"", b"")):
            with self.assertRaisesRegex(RuntimeError, 'sin producir'):
                dibujar_automata(self.afn, self.carpeta / "afn.svg", ejecutable_dot="dot")

    def test_ejecutable_inexistente_tiene_mensaje_explicito(self):
        with self.assertRaisesRegex(FileNotFoundError, 'ejecutable de Graphviz'):
            dibujar_automata(self.afn, self.carpeta / "afn.svg", ejecutable_dot=self.carpeta / "inexistente.exe")


class TestRenderizadoGraphviz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dot = _buscar_dot()
        if cls.dot is None:
            raise unittest.SkipTest("Graphviz no instalado: se omiten las pruebas de renderizado real.")

    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)
        self.ns = {"svg": "http://www.w3.org/2000/svg"}

    def test_svg_representa_todos_los_estados_y_aristas_de_los_tres_automatas(self):
        afn = regex_a_afn("(a|b)*abb")
        afd = afn_a_afd(afn)
        for nombre, automata in (("afn", afn), ("afd", afd), ("minimo", minimizar_afd(afd))):
            with self.subTest(nombre=nombre):
                ruta = dibujar_automata(automata, self.carpeta / f"{nombre}.svg", ejecutable_dot=self.dot)
                svg = ElementTree.parse(ruta)
                nodos = svg.findall(".//svg:g[@class='node']", self.ns)
                aristas = svg.findall(".//svg:g[@class='edge']", self.ns)
                self.assertEqual(len(nodos), len(automata.estados) + 1)
                etiquetas = {t.text for nodo in nodos for t in nodo.findall('svg:text', self.ns)}
                self.assertEqual(etiquetas, {f"q{q}" for q in automata.estados})
                finales = sum(len(nodo.findall('svg:ellipse', self.ns)) == 2 for nodo in nodos)
                self.assertEqual(finales, len(automata.estados_aceptacion))
                ids = {q: f"s{i}" for i, q in enumerate(sorted(automata.estados))}
                esperadas = {f"__inicio->{ids[automata.estado_inicial]}"}
                for (origen, _), destino in automata.transiciones.items():
                    destinos = destino if isinstance(automata, AFN) else {destino}
                    esperadas.update(f"{ids[origen]}->{ids[q]}" for q in destinos)
                self.assertEqual({a.find('svg:title', self.ns).text for a in aristas}, esperadas)

    def test_etiquetas_especiales_no_se_interpretan_como_codigo(self):
        simbolos = {'"', "\\", "<", "&", ",", " ", "\n"}
        afn = AFN({0, 1}, simbolos, 0, {1}, {(0, s): {1} for s in simbolos})
        titulo = 'Texto "literal" <&> \\N; intruso -> otro'
        ruta = dibujar_automata(afn, self.carpeta / "especial.svg", titulo, ejecutable_dot=self.dot)
        svg = ElementTree.parse(ruta)
        textos = [t.text for t in svg.findall('.//svg:text', self.ns)]
        self.assertIn(titulo, textos)
        self.assertEqual(len(svg.findall(".//svg:g[@class='node']", self.ns)), 3)

    def test_dibuja_un_unico_estado_inicial_y_final(self):
        afd = AFD({0}, set(), 0, {0})
        ruta = dibujar_automata(afd, self.carpeta / "vacio.svg", ejecutable_dot=self.dot)
        svg = ElementTree.parse(ruta)
        self.assertEqual(len(svg.findall(".//svg:g[@class='edge']", self.ns)), 1)
        self.assertEqual(len(svg.findall(".//svg:g[@class='node']", self.ns)), 2)

    def test_png_es_una_imagen_con_dimensiones_validas(self):
        ruta = dibujar_automata(regex_a_afn("a|ε"), self.carpeta / "afn.png", ejecutable_dot=self.dot)
        datos = ruta.read_bytes()
        self.assertEqual(datos[:8], b"\x89PNG\r\n\x1a\n")
        ancho, alto = struct.unpack(">II", datos[16:24])
        self.assertGreater(ancho, 0)
        self.assertGreater(alto, 0)


if __name__ == "__main__":
    unittest.main()

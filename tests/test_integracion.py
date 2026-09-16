"""Procesamiento de archivos, operaciones seleccionadas e interfaz de consola."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from automatas import analizar_archivo, analizar_expresion, leer_expresiones
from main import main


class TestAnalisis(unittest.TestCase):
    def test_selecciona_solo_los_resultados_solicitados(self):
        casos = {
            "postfix": [], "afn": ["afn"], "afd": ["afd"],
            "minimo": ["afd_minimo"], "directo": ["afd_directo"],
            "todo": ["afn", "afd", "afd_minimo"],
        }
        for operacion, nombres in casos.items():
            with self.subTest(operacion=operacion):
                resultado = analizar_expresion("ab", operacion)
                self.assertEqual(resultado.postfix, "ab.")
                self.assertEqual(list(resultado.automatas), nombres)

    def test_simula_los_cuatro_automatas(self):
        resultado = analizar_expresion("(a|b)*abb", incluir_directo=True)
        self.assertEqual(len(resultado.automatas), 4)
        self.assertEqual(set(resultado.simular("abb").values()), {True})
        self.assertEqual(set(resultado.simular("aba").values()), {False})

    def test_rechaza_configuraciones_invalidas(self):
        with self.assertRaises(ValueError):
            analizar_expresion("a", "desconocida")
        with self.assertRaises(ValueError):
            analizar_expresion("a", "afn", incluir_directo=True)


class TestArchivosYConsola(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.carpeta = Path(self.temporal.name)

    def ejecutar(self, argumentos):
        salida, errores = StringIO(), StringIO()
        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = main(argumentos)
        return codigo, salida.getvalue(), errores.getvalue()

    def test_utf8_bom_lineas_vacias_y_numeracion_original(self):
        ruta = self.carpeta / "expresiones.txt"
        ruta.write_text("a*\n\n  ε \n\t\nñ\n", encoding="utf-8-sig")
        self.assertEqual(leer_expresiones(ruta), [(1, "a*"), (3, "  ε "), (5, "ñ")])

    def test_continua_despues_de_una_expresion_invalida(self):
        ruta = self.carpeta / "expresiones.txt"
        ruta.write_text("a*\n\n(a|b\nab\n", encoding="utf-8")
        lineas = analizar_archivo(ruta, incluir_directo=True)
        self.assertEqual([linea.numero for linea in lineas], [1, 3, 4])
        self.assertIsNone(lineas[0].error)
        self.assertIsNotNone(lineas[1].error)
        self.assertIsNone(lineas[1].resultado)
        self.assertEqual(set(lineas[2].resultado.simular("ab").values()), {True})

    def test_archivo_inexistente_y_utf8_invalido(self):
        with self.assertRaises(FileNotFoundError):
            leer_expresiones(self.carpeta / "no_existe.txt")
        ruta = self.carpeta / "invalido.txt"
        ruta.write_bytes(b"\xff\xfe")
        codigo, _, errores = self.ejecutar(["--archivo", str(ruta)])
        self.assertEqual(codigo, 1)
        self.assertIn("Error", errores)

    def test_archivo_vacio(self):
        ruta = self.carpeta / "vacio.txt"
        ruta.write_text("\n \t\n", encoding="utf-8")
        codigo, salida, errores = self.ejecutar(["--archivo", str(ruta)])
        self.assertEqual(codigo, 0)
        self.assertIn("no contiene", salida)
        self.assertEqual(errores, "")

    def test_consola_varias_cadenas_y_todos_los_automatas(self):
        codigo, salida, errores = self.ejecutar([
            "--regex", "(a|b)*abb", "--cadena", "abb", "--cadena", "aba", "--directo",
        ])
        self.assertEqual(codigo, 0)
        self.assertEqual(errores, "")
        self.assertEqual(salida.count(": ACEPTADA"), 4)
        self.assertEqual(salida.count(": RECHAZADA"), 4)

    def test_postfix_no_construye_automatas(self):
        codigo, salida, _ = self.ejecutar(["--regex", "ab", "--operacion", "postfix"])
        self.assertEqual(codigo, 0)
        self.assertIn("Postfix: ab.", salida)
        self.assertNotIn("estados;", salida)

    def test_cadena_vacia_por_defecto_y_explicita(self):
        for extra in ([], ["--cadena="]):
            codigo, salida, _ = self.ejecutar(["--regex", "a?", *extra])
            self.assertEqual(codigo, 0)
            self.assertIn("Cadena '':", salida)
            self.assertEqual(salida.count(": ACEPTADA"), 3)

    def test_muestra_tablas_completas(self):
        codigo, salida, _ = self.ejecutar(["--regex", "a", "--operacion", "afn", "--detalles"])
        self.assertEqual(codigo, 0)
        self.assertIn("Alfabeto: ['a']", salida)
        self.assertIn("q0 --'a'--> q1", salida)

    def test_error_de_sintaxis_es_error_no_rechazo_de_cadena(self):
        codigo, salida, errores = self.ejecutar(["--regex", "a|"])
        self.assertEqual(codigo, 1)
        self.assertEqual(salida, "")
        self.assertIn("operando", errores)

    def test_dibujos_de_archivo_tienen_carpetas_por_linea(self):
        ruta = self.carpeta / "expresiones.txt"
        ruta.write_text("a\n(a\n\na\n", encoding="utf-8")
        destino = self.carpeta / "dibujos"
        codigo, salida, errores = self.ejecutar([
            "--archivo", str(ruta), "--cadena", "a", "--dibujar", "--formato", "dot",
            "--salida", str(destino), "--directo",
        ])
        self.assertEqual(codigo, 1)
        self.assertIn("Error en línea 2", errores)
        self.assertIn("Línea 4", salida)
        for numero in (1, 4):
            self.assertEqual(len(list((destino / f"linea_{numero:03d}").glob("*.dot"))), 4)
        self.assertFalse((destino / "linea_002").exists())

    def test_menu_acepta_literales_que_empiezan_con_guion(self):
        with patch('builtins.input', side_effect=["2", "-a", "-a", "0"]):
            codigo, salida, errores = self.ejecutar([])
        self.assertEqual(codigo, 0)
        self.assertIn("ACEPTADA", salida)
        self.assertEqual(errores, "")

    def test_menu_maneja_opcion_invalida_y_fin_de_entrada(self):
        with patch('builtins.input', side_effect=["x", EOFError]):
            codigo, salida, _ = self.ejecutar([])
        self.assertEqual(codigo, 0)
        self.assertIn("Opción inválida", salida)

    def test_programa_real_con_salida_utf8(self):
        raiz = Path(__file__).resolve().parents[1]
        proceso = subprocess.run(
            [sys.executable, str(raiz / "main.py"), "--regex", "a|ε", "--cadena=", "--directo"],
            cwd=raiz, capture_output=True, text=True, encoding="utf-8", timeout=15,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Expresión: a|ε", proceso.stdout)
        self.assertEqual(proceso.stdout.count(": ACEPTADA"), 4)


if __name__ == "__main__":
    unittest.main()

"""Casos de precedencia, concatenación y errores de sintaxis del conversor."""

import unittest

from automatas import infix_a_postfix, insertar_concatenacion


class TestConcatenacion(unittest.TestCase):
    def test_inserta_puntos_entre_operandos(self):
        casos = {
            "abc": "a.b.c",
            "a(b|c)": "a.(b|c)",
            "(a|b)c": "(a|b).c",
            "(a)(b)": "(a).(b)",
            "a*b+c?d": "a*.b+.c?.d",
            "a*(b)": "a*.(b)",
            "(a|b)*abb": "(a|b)*.a.b.b",
            "εa": "ε.a",
            "aε": "a.ε",
        }
        for infix, esperado in casos.items():
            with self.subTest(infix=infix):
                self.assertEqual(insertar_concatenacion(infix), esperado)

    def test_conserva_concatenacion_explicita_y_operadores(self):
        for infix in ("a.b", "a.(b|c)", "a|b", "(a|b)*", "a+?", "ε"):
            with self.subTest(infix=infix):
                self.assertEqual(insertar_concatenacion(infix), infix)

    def test_combina_concatenacion_explicita_e_implicita(self):
        self.assertEqual(insertar_concatenacion("ab.c(d)"), "a.b.c.(d)")

    def test_ignora_espacios_sin_crear_literales(self):
        self.assertEqual(
            insertar_concatenacion(" \t ( a | b ) * \n a b b\r"),
            "(a|b)*.a.b.b",
        )


class TestPostfix(unittest.TestCase):
    def test_operandos_individuales(self):
        for infix in ("a", "5", "ε", "ñ", "_", "-", ","):
            with self.subTest(infix=infix):
                self.assertEqual(infix_a_postfix(infix), infix)

    def test_concatena_antes_de_unir(self):
        casos = {"a|bc": "abc.|", "ab|c": "ab.c|", "ab|cd": "ab.cd.|"}
        for infix, esperado in casos.items():
            with self.subTest(infix=infix):
                self.assertEqual(infix_a_postfix(infix), esperado)

    def test_binarios_asociativos_por_la_izquierda(self):
        self.assertEqual(infix_a_postfix("abc"), "ab.c.")
        self.assertEqual(infix_a_postfix("a|b|c"), "ab|c|")

    def test_parentesis_cambian_la_agrupacion(self):
        casos = {
            "(a|b)c": "ab|c.",
            "a(b|c)": "abc|.",
            "a|(b|c)": "abc||",
            "((a))": "a",
            "((a|b)c)*": "ab|c.*",
        }
        for infix, esperado in casos.items():
            with self.subTest(infix=infix):
                self.assertEqual(infix_a_postfix(infix), esperado)

    def test_unarios_tienen_mayor_precedencia(self):
        casos = {
            "a*": "a*",
            "a+": "a+",
            "a?": "a?",
            "ab*": "ab*.",
            "a|bc*": "abc*.|",
            "(ab)+c?": "ab.+c?.",
            "(a|b)*abb": "ab|*a.b.b.",
        }
        for infix, esperado in casos.items():
            with self.subTest(infix=infix):
                self.assertEqual(infix_a_postfix(infix), esperado)

    def test_unarios_consecutivos_se_aplican_en_orden(self):
        self.assertEqual(infix_a_postfix("a*?+b"), "a*?+b.")
        self.assertEqual(infix_a_postfix("(a|b)**"), "ab|**")

    def test_epsilon_se_conserva_como_operando(self):
        self.assertEqual(infix_a_postfix("(a|ε)b*"), "aε|b*.")
        self.assertEqual(infix_a_postfix("εε"), "εε.")
        self.assertEqual(infix_a_postfix("ε*"), "ε*")

    def test_concatenacion_explicita_e_implicita_son_equivalentes(self):
        self.assertEqual(infix_a_postfix("ab.c"), "ab.c.")
        self.assertEqual(infix_a_postfix("a.b.c"), "ab.c.")

    def test_ignora_espacios_en_blanco(self):
        self.assertEqual(infix_a_postfix("\t (a | b)* \n a b b "), "ab|*a.b.b.")

    def test_procesa_grupos_profundos_sin_recursion(self):
        infix = "(" * 2000 + "a" + ")" * 2000
        self.assertEqual(infix_a_postfix(infix), "a")


class TestSintaxisInvalida(unittest.TestCase):
    def comprobar_invalidas(self, expresiones):
        for funcion in (insertar_concatenacion, infix_a_postfix):
            for expresion in expresiones:
                with self.subTest(funcion=funcion.__name__, expresion=expresion):
                    with self.assertRaises(ValueError):
                        funcion(expresion)

    def test_rechaza_expresiones_y_grupos_vacios(self):
        self.comprobar_invalidas(("", " \t\n", "()", "( )", "a()", "()a", "(())"))

    def test_rechaza_operandos_faltantes(self):
        self.comprobar_invalidas(
            ("|a", ".a", "a|", "a.", "a||b", "a..b", "a.|b", "a|.b",
             "(a|)", "(|a)", "(a.)", "a(|b)")
        )

    def test_rechaza_unarios_sin_operando(self):
        self.comprobar_invalidas(("*a", "+", "?a", "a|*b", "a.*", "(*)", "a(+b)"))

    def test_rechaza_parentesis_desbalanceados(self):
        self.comprobar_invalidas(("(", ")", "(a", "a)", "((a)", "(a))", ")(a"))

    def test_rechaza_sintaxis_no_soportada(self):
        self.comprobar_invalidas(
            (r"a\*", "[a-z]", "a]", "a{2,3}", "a}", "^a", "a$", "a\x00b", "a\x07")
        )

    def test_error_indica_posicion_en_la_expresion_original(self):
        with self.assertRaisesRegex(ValueError, "posición 5"):
            infix_a_postfix(" a| *b")
        with self.assertRaisesRegex(ValueError, "posición 3"):
            infix_a_postfix("  ( a")


if __name__ == "__main__":
    unittest.main()

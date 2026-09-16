"""Construcción de fragmentos y aceptación del flujo infix -> postfix -> AFN."""

from itertools import product
import re
import unittest

from automatas import EPSILON, infix_a_postfix, postfix_a_afn, regex_a_afn, simular_afn


class TestThompson(unittest.TestCase):
    def test_literal_produce_dos_estados_y_una_transicion(self):
        afn = postfix_a_afn("a")
        self.assertEqual(afn.estados, {0, 1})
        self.assertEqual(afn.estado_inicial, 0)
        self.assertEqual(afn.estados_aceptacion, {1})
        self.assertEqual(afn.alfabeto, {"a"})
        self.assertEqual(afn.transiciones, {(0, "a"): {1}})

    def test_epsilon_no_se_agrega_al_alfabeto(self):
        afn = postfix_a_afn(EPSILON)
        self.assertEqual(afn.alfabeto, set())
        self.assertEqual(afn.transiciones, {(0, EPSILON): {1}})

    def test_fragmentos_conservan_los_extremos_de_thompson(self):
        for expresion in ("ab", "a|b", "a*", "a+", "a?", "(a|b)*abb", "(ε*)*"):
            with self.subTest(expresion=expresion):
                afn = regex_a_afn(expresion)
                afn.validar()
                self.assertEqual(len(afn.estados_aceptacion), 1)
                self.assertTrue(all(
                    afn.estado_inicial not in destinos
                    for destinos in afn.transiciones.values()
                ))
                self.assertTrue(all(
                    origen not in afn.estados_aceptacion
                    for origen, _ in afn.transiciones
                ))

    def test_union_conserva_ambas_ramas_epsilon(self):
        afn = regex_a_afn("a|b")
        self.assertEqual(len(afn.transiciones[(afn.estado_inicial, EPSILON)]), 2)

    def test_extrae_solo_los_literales_del_alfabeto(self):
        self.assertEqual(regex_a_afn("(a|ε)b*ñ?").alfabeto, {"a", "b", "ñ"})

    def test_entrada_infix_y_postfix_producen_el_mismo_afn(self):
        expresion = "(a|b)*abb"
        self.assertEqual(regex_a_afn(expresion), postfix_a_afn(infix_a_postfix(expresion)))

    def test_construcciones_independientes_y_reproducibles(self):
        primero = regex_a_afn("a")
        segundo = regex_a_afn("a")
        self.assertEqual(primero, segundo)
        primero.transiciones[(0, "a")].clear()
        primero.estados.add(99)
        self.assertEqual(segundo.transiciones[(0, "a")], {1})
        self.assertEqual(segundo.estados, {0, 1})

    def test_postfix_ignora_espacios(self):
        self.assertEqual(postfix_a_afn(" a b | \n * "), postfix_a_afn("ab|*"))

    def test_rechaza_postfix_invalido(self):
        for postfix in (
            "", " \t", "*", "+", "?", ".", "|", "a|", "ab", "ab*",
            "ab..", "a|b", "(a)", "a[", "a]", "a{", "a}", "a^", "a$",
            "a\\", "a\x00",
        ):
            with self.subTest(postfix=postfix):
                with self.assertRaises(ValueError):
                    postfix_a_afn(postfix)

    def test_error_postfix_indica_posicion_original(self):
        with self.assertRaisesRegex(ValueError, "posición 4"):
            postfix_a_afn(" a |")
        with self.assertRaisesRegex(ValueError, "posición 4"):
            postfix_a_afn(" a [")

    def test_rechaza_infix_invalido_antes_de_construir(self):
        for expresion in ("a|", "(ab", "()", "[a-z]"):
            with self.subTest(expresion=expresion):
                with self.assertRaises(ValueError):
                    regex_a_afn(expresion)


class TestLenguajesThompson(unittest.TestCase):
    def test_aceptacion_y_rechazo_por_operador(self):
        casos = [
            ("a", ["a"], ["", "aa", "b"]),
            ("ε", [""], ["a", "ε"]),
            ("ab", ["ab"], ["", "a", "b", "ba", "aba"]),
            ("a|b", ["a", "b"], ["", "ab", "ba", "c"]),
            ("a*", ["", "a", "aaaa"], ["b", "ab"]),
            ("a+", ["a", "aaa"], ["", "b", "ab"]),
            ("a?", ["", "a"], ["aa", "b"]),
            ("(a|b)*abb", ["abb", "aabb", "babb", "abababb"], ["", "ab", "abba", "abcabb"]),
            ("(ε|a)b?", ["", "a", "b", "ab"], ["aa", "bb", "ba", "ε"]),
            ("ñ_?", ["ñ", "ñ_"], ["", "_", "ñ__"]),
            ("-,", ["-,"], ["", ",-"]),
        ]
        for expresion, aceptadas, rechazadas in casos:
            afn = regex_a_afn(expresion)
            for cadena in aceptadas:
                with self.subTest(expresion=expresion, cadena=cadena, acepta=True):
                    self.assertTrue(simular_afn(afn, cadena))
            for cadena in rechazadas:
                with self.subTest(expresion=expresion, cadena=cadena, acepta=False):
                    self.assertFalse(simular_afn(afn, cadena))

    def test_unarios_sobre_operandos_que_aceptan_vacio(self):
        for expresion in ("ε*", "ε+", "ε?", "(ε*)*"):
            with self.subTest(expresion=expresion):
                afn = regex_a_afn(expresion)
                self.assertTrue(simular_afn(afn, ""))
                self.assertFalse(simular_afn(afn, "a"))
        for expresion in ("(a?)+", "a*?+", "(a*)*"):
            afn = regex_a_afn(expresion)
            for cadena in ("", "a", "aaa"):
                with self.subTest(expresion=expresion, cadena=cadena):
                    self.assertTrue(simular_afn(afn, cadena))
            self.assertFalse(simular_afn(afn, "b"))

    def test_cadena_larga_sin_recursion(self):
        afn = regex_a_afn("a*")
        self.assertTrue(simular_afn(afn, "a" * 2000))
        self.assertFalse(simular_afn(afn, "a" * 2000 + "b"))

    def test_coincide_con_un_motor_independiente_en_cadenas_cortas(self):
        # re se usa solo como referencia de prueba, nunca en la implementación.
        # Las expresiones de referencia traducen explícitamente epsilon y puntos.
        casos = [
            ("(a|b)*abb", "(a|b)*abb"),
            ("(ab)+c?", "(ab)+c?"),
            ("(a|ε)b*", "(a|)b*"),
            ("a.(b|c)*", "a(b|c)*"),
            ("a?b+c*", "a?b+c*"),
            ("a*?+", "((a*)?)+"),
            ("(a?)+", "(a?)+"),
            ("ab|bc", "ab|bc"),
        ]
        cadenas = [
            "".join(letras)
            for longitud in range(5)
            for letras in product("abc", repeat=longitud)
        ]
        for expresion, referencia in casos:
            afn = regex_a_afn(expresion)
            patron = re.compile(referencia)
            for cadena in cadenas:
                with self.subTest(expresion=expresion, cadena=cadena):
                    self.assertEqual(
                        simular_afn(afn, cadena), patron.fullmatch(cadena) is not None
                    )


if __name__ == "__main__":
    unittest.main()

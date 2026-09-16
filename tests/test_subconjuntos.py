"""Construcción determinista y equivalencia entre AFN y AFD."""

from copy import deepcopy
from itertools import product
import unittest

from automatas import AFN, EPSILON, afn_a_afd, regex_a_afn, simular_afd, simular_afn


class TestSubconjuntos(unittest.TestCase):
    def test_tabla_con_epsilon_ramas_y_estado_inaccesible(self):
        afn = AFN(
            estados={10, 20, 30, 40, 50, 99},
            alfabeto={"a", "b"},
            estado_inicial=10,
            estados_aceptacion={50, 99},
            transiciones={
                (10, EPSILON): {20},
                (20, "a"): {20, 30},
                (30, EPSILON): {40},
                (40, "b"): {50},
                (50, "b"): {50},
                (99, "a"): {99},
            },
        )
        afd = afn_a_afd(afn)
        # 0 = {10,20}, 1 = {20,30,40}, 2 = vacío, 3 = {50}.
        self.assertEqual(afd.estados, {0, 1, 2, 3})
        self.assertEqual(afd.estado_inicial, 0)
        self.assertEqual(afd.estados_aceptacion, {3})
        self.assertEqual(afd.transiciones, {
            (0, "a"): 1, (0, "b"): 2,
            (1, "a"): 1, (1, "b"): 3,
            (2, "a"): 2, (2, "b"): 2,
            (3, "a"): 2, (3, "b"): 3,
        })

    def test_subconjunto_vacio_es_un_sumidero_no_final(self):
        afd = afn_a_afd(regex_a_afn("a"))
        self.assertEqual(afd.estados, {0, 1, 2})
        self.assertEqual(afd.estados_aceptacion, {1})
        self.assertEqual(afd.transiciones, {(0, "a"): 1, (1, "a"): 2, (2, "a"): 2})

    def test_no_agrega_sumidero_si_no_es_alcanzable(self):
        afn = AFN({7}, {"a", "b"}, 7, {7}, {(7, "a"): {7}, (7, "b"): {7}})
        afd = afn_a_afd(afn)
        self.assertEqual(afd.estados, {0})
        self.assertEqual(afd.estados_aceptacion, {0})
        self.assertEqual(afd.transiciones, {(0, "a"): 0, (0, "b"): 0})

    def test_reutiliza_un_subconjunto_alcanzado_por_distintos_simbolos(self):
        afn = AFN(
            {0, 1}, {"a", "b"}, 0, {1},
            {(0, "a"): {1}, (0, "b"): {1}, (1, "a"): {1}, (1, "b"): {1}},
        )
        afd = afn_a_afd(afn)
        self.assertEqual(afd.estados, {0, 1})
        self.assertEqual(afd.transiciones[(0, "a")], afd.transiciones[(0, "b")])

    def test_ciclos_epsilon_y_alfabeto_vacio(self):
        afn = AFN({4, 8}, set(), 4, {8}, {(4, EPSILON): {8}, (8, EPSILON): {4}})
        afd = afn_a_afd(afn)
        self.assertEqual(afd.estados, {0})
        self.assertEqual(afd.alfabeto, set())
        self.assertEqual(afd.estados_aceptacion, {0})
        self.assertEqual(afd.transiciones, {})

    def test_lenguaje_vacio_con_y_sin_alfabeto(self):
        for alfabeto in (set(), {"a", "b"}):
            with self.subTest(alfabeto=alfabeto):
                afn = AFN({10}, alfabeto, 10, set())
                afd = afn_a_afd(afn)
                self.assertEqual(afd.estados_aceptacion, set())
                self.assertEqual(len(afd.estados), 2 if alfabeto else 1)
                self.assertFalse(simular_afd(afd, ""))

    def test_varios_finales_y_aceptacion_del_subconjunto_inicial(self):
        afn = AFN(
            {0, 1, 2}, {"a", "b"}, 0, {0, 1, 2},
            {(0, "a"): {1}, (0, "b"): {2}},
        )
        afd = afn_a_afd(afn)
        self.assertEqual(afd.estados_aceptacion, {0, 1, 2})
        self.assertTrue(simular_afd(afd, ""))
        self.assertTrue(simular_afd(afd, "a"))
        self.assertTrue(simular_afd(afd, "b"))
        self.assertFalse(simular_afd(afd, "ab"))

    def test_conserva_el_alfabeto_aunque_un_simbolo_no_tenga_transiciones(self):
        afn = AFN({0, 1}, {"a", "b", "c"}, 0, {1}, {(0, "a"): {1}})
        afd = afn_a_afd(afn)
        self.assertEqual(afd.alfabeto, afn.alfabeto)
        self.assertNotIn(EPSILON, afd.alfabeto)
        for estado in afd.estados:
            for simbolo in afd.alfabeto:
                self.assertIn((estado, simbolo), afd.transiciones)
                self.assertIn(afd.transiciones[(estado, simbolo)], afd.estados)

    def test_conversion_no_modifica_ni_comparte_datos_con_el_afn(self):
        afn = regex_a_afn("(a|b)*abb")
        copia = deepcopy(afn)
        afd = afn_a_afd(afn)
        self.assertEqual(afn, copia)
        afd.estados.clear()
        afd.alfabeto.add("x")
        afd.estados_aceptacion.clear()
        afd.transiciones.clear()
        self.assertEqual(afn, copia)

    def test_numeracion_reproducible_sin_depender_del_orden_de_transiciones(self):
        afn = regex_a_afn("(a|b)*abb")
        copia = deepcopy(afn)
        copia.transiciones = dict(reversed(list(copia.transiciones.items())))
        self.assertEqual(afn_a_afd(afn), afn_a_afd(copia))
        self.assertEqual(afn_a_afd(afn), afn_a_afd(afn))

    def test_rechaza_un_afn_modificado_incorrectamente(self):
        afn = regex_a_afn("a")
        afn.transiciones[(afn.estado_inicial, "a")] = {99}
        with self.assertRaises(ValueError):
            afn_a_afd(afn)


class TestEquivalenciaAFNyAFD(unittest.TestCase):
    def test_lenguajes_de_regex_sobre_todas_las_cadenas_cortas(self):
        expresiones = (
            "a", "ε", "ab", "a|b", "a*", "a+", "a?", "(a|b)*abb",
            "(ab)+c?", "(a|ε)b*", "a.(b|c)*", "a?b+c*", "a*?+", "(a?)+",
            "ab|bc", "(ε*)*", "ε+", "a?b?c?",
        )
        cadenas = [
            "".join(letras)
            for longitud in range(6)
            for letras in product("abc", repeat=longitud)
        ]
        for expresion in expresiones:
            afn = regex_a_afn(expresion)
            afd = afn_a_afd(afn)
            for cadena in cadenas:
                with self.subTest(expresion=expresion, cadena=cadena):
                    self.assertEqual(simular_afn(afn, cadena), simular_afd(afd, cadena))

    def test_acepta_exactamente_cadenas_que_terminan_en_abb(self):
        afd = afn_a_afd(regex_a_afn("(a|b)*abb"))
        for longitud in range(8):
            for letras in product("ab", repeat=longitud):
                cadena = "".join(letras)
                with self.subTest(cadena=cadena):
                    self.assertEqual(simular_afd(afd, cadena), cadena.endswith("abb"))

    def test_literales_unicode_y_espacios_se_conservan(self):
        afn = AFN({10, 20, 30}, {"ñ", " "}, 10, {30}, {(10, "ñ"): {20}, (20, " "): {30}})
        afd = afn_a_afd(afn)
        for cadena, esperado in (("ñ ", True), ("ñ", False), (" ñ", False), ("", False)):
            with self.subTest(cadena=cadena):
                self.assertEqual(simular_afn(afn, cadena), esperado)
                self.assertEqual(simular_afd(afd, cadena), esperado)


if __name__ == "__main__":
    unittest.main()

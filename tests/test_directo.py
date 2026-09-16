"""Aceptación y construcción directa sin AFN intermedio."""

from collections import deque
from itertools import product
import unittest

from automatas import afn_a_afd, regex_a_afd_directo, regex_a_afn, simular_afd


class TestDirecto(unittest.TestCase):
    def test_tabla_conocida_para_sufijo_abb(self):
        afd = regex_a_afd_directo("(a|b)*abb")
        self.assertEqual(afd.estados, {0, 1, 2, 3})
        self.assertEqual(afd.estados_aceptacion, {3})
        self.assertEqual(afd.transiciones, {
            (0, "a"): 1, (0, "b"): 0,
            (1, "a"): 1, (1, "b"): 2,
            (2, "a"): 1, (2, "b"): 3,
            (3, "a"): 1, (3, "b"): 0,
        })

    def test_equivalencia_exacta_con_subconjuntos(self):
        expresiones = (
            "ε", "a", "ab", "a|b", "a*", "a+", "a?", "(a|b)*abb", "(ab)+c?",
            "(a|ε)b*", "a?b+c*", "a*?+", "(a?)+", "(ε*)*", "ε+", "a?b?c?",
            "(a|b)+(ba|ε)", "#", "#a#", "ñ_?", "aεb", "(εa|aε)?", "(a|a)*",
        )
        for expresion in expresiones:
            with self.subTest(expresion=expresion):
                referencia = afn_a_afd(regex_a_afn(expresion))
                directo = regex_a_afd_directo(expresion)
                directo.validar()
                self.assertEqual(directo.alfabeto, referencia.alfabeto)
                inicial = (referencia.estado_inicial, directo.estado_inicial)
                visitados = {inicial}
                pendientes = deque([inicial])
                while pendientes:
                    a, b = pendientes.popleft()
                    self.assertEqual(a in referencia.estados_aceptacion, b in directo.estados_aceptacion)
                    for simbolo in referencia.alfabeto:
                        destino = (referencia.transiciones[(a, simbolo)], directo.transiciones[(b, simbolo)])
                        if destino not in visitados:
                            visitados.add(destino)
                            pendientes.append(destino)

    def test_marcador_no_reserva_el_literal_numeral(self):
        afd = regex_a_afd_directo("#a#")
        self.assertEqual(afd.alfabeto, {"#", "a"})
        self.assertTrue(simular_afd(afd, "#a#"))
        self.assertFalse(simular_afd(afd, "a"))

    def test_acepta_cadena_vacia_segun_anulabilidad(self):
        for expresion in ("ε", "ε+", "a?", "(a?)+", "(a|ε)b*", "a*?+"):
            with self.subTest(expresion=expresion):
                self.assertTrue(simular_afd(regex_a_afd_directo(expresion), ""))
        for expresion in ("a", "a+", "ab?", "εa"):
            with self.subTest(expresion=expresion):
                self.assertFalse(simular_afd(regex_a_afd_directo(expresion), ""))

    def test_apariciones_repetidas_son_posiciones_distintas(self):
        afd = regex_a_afd_directo("aaa")
        for longitud in range(6):
            self.assertEqual(simular_afd(afd, "a" * longitud), longitud == 3)

    def test_alfabeto_vacio_y_sumidero(self):
        vacio = regex_a_afd_directo("ε")
        self.assertEqual(vacio.estados, {0})
        self.assertEqual(vacio.transiciones, {})
        afd = regex_a_afd_directo("a")
        self.assertEqual(len(afd.estados), 3)
        self.assertEqual(len(afd.transiciones), 3)

    def test_rechaza_sintaxis_invalida(self):
        for expresion in ("", "a|", "(ab", "()", "[ab]"):
            with self.subTest(expresion=expresion):
                with self.assertRaises(ValueError):
                    regex_a_afd_directo(expresion)

    def test_lenguaje_conocido_de_cadenas_que_terminan_en_abb(self):
        afd = regex_a_afd_directo("(a|b)*abb")
        for longitud in range(7):
            for letras in product("ab", repeat=longitud):
                cadena = "".join(letras)
                self.assertEqual(simular_afd(afd, cadena), cadena.endswith("abb"))


if __name__ == "__main__":
    unittest.main()

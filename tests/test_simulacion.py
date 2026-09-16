"""Cierre epsilon, movimientos y simulación sobre AFN definidos a mano."""

from copy import deepcopy
import unittest

from automatas import AFN, EPSILON, cierre_epsilon, mover, simular_afn


class TestOperacionesAFN(unittest.TestCase):
    def setUp(self):
        self.afn = AFN(
            estados={10, 20, 30, 40, 50, 60},
            alfabeto={"a"},
            estado_inicial=10,
            estados_aceptacion={60},
            transiciones={
                (10, EPSILON): {20, 30},
                (20, EPSILON): {10},
                (30, EPSILON): {40},
                (20, "a"): {50},
                (40, "a"): {40, 50},
                (50, EPSILON): {60},
            },
        )

    def test_cierre_sigue_ramas_y_termina_ante_ciclos(self):
        self.assertEqual(cierre_epsilon(self.afn, {10}), {10, 20, 30, 40})

    def test_cierre_incluye_todos_los_estados_iniciales(self):
        self.assertEqual(cierre_epsilon(self.afn, frozenset({10, 50})), self.afn.estados)
        self.assertEqual(cierre_epsilon(self.afn, {60}), {60})
        self.assertEqual(cierre_epsilon(self.afn, set()), set())

    def test_cierre_no_modifica_el_conjunto_recibido(self):
        origenes = {10}
        cierre = cierre_epsilon(self.afn, origenes)
        self.assertEqual(origenes, {10})
        cierre.clear()
        self.assertEqual(origenes, {10})

    def test_mover_une_destinos_sin_calcular_cierre(self):
        self.assertEqual(mover(self.afn, {20, 40}, "a"), {40, 50})
        self.assertEqual(mover(self.afn, {10}, "a"), set())

    def test_mover_no_consume_epsilon_ni_simbolos_ajenos(self):
        self.assertEqual(mover(self.afn, {10}, EPSILON), set())
        self.assertEqual(mover(self.afn, {40}, "b"), set())
        self.assertEqual(mover(self.afn, set(), "a"), set())

    def test_mover_devuelve_un_conjunto_independiente(self):
        mover(self.afn, frozenset({40}), "a").clear()
        self.assertEqual(self.afn.transiciones[(40, "a")], {40, 50})

    def test_operaciones_rechazan_estados_inexistentes(self):
        with self.assertRaises(ValueError):
            cierre_epsilon(self.afn, {99})
        with self.assertRaises(ValueError):
            mover(self.afn, {99}, "a")

    def test_simulacion_usa_cierre_antes_y_despues_de_consumir(self):
        self.assertTrue(simular_afn(self.afn, "a"))
        self.assertTrue(simular_afn(self.afn, "aa"))
        self.assertFalse(simular_afn(self.afn, ""))
        self.assertFalse(simular_afn(self.afn, "b"))

    def test_simulacion_no_modifica_el_automata(self):
        copia = deepcopy(self.afn)
        for cadena in ("", "a", "aa", "b"):
            simular_afn(self.afn, cadena)
        self.assertEqual(self.afn, copia)

    def test_simulacion_detecta_un_automata_modificado_incorrectamente(self):
        self.afn.transiciones[(10, "a")] = {99}
        with self.assertRaises(ValueError):
            simular_afn(self.afn, "a")


class TestSimulacionAFN(unittest.TestCase):
    def test_explora_todas_las_ramas_y_consume_la_cadena_completa(self):
        afn = AFN(
            {0, 1, 2, 3}, {"a", "b", "c"}, 0, {3},
            {(0, "a"): {1, 2}, (1, "b"): {3}, (2, "c"): {3}},
        )
        for cadena in ("ab", "ac"):
            with self.subTest(cadena=cadena):
                self.assertTrue(simular_afn(afn, cadena))
        for cadena in ("", "a", "abc", "aba", "cab"):
            with self.subTest(cadena=cadena):
                self.assertFalse(simular_afn(afn, cadena))

    def test_vacio_se_acepta_si_el_cierre_inicial_contiene_un_final(self):
        afn = AFN({0, 1}, set(), 0, {1}, {(0, EPSILON): {1}, (1, EPSILON): {0}})
        self.assertTrue(simular_afn(afn, ""))
        self.assertFalse(simular_afn(afn, EPSILON))

    def test_estado_inicial_final_sin_transiciones(self):
        afn = AFN({0}, {"a"}, 0, {0})
        self.assertTrue(simular_afn(afn, ""))
        self.assertFalse(simular_afn(afn, "a"))

    def test_automata_sin_finales_rechaza(self):
        afn = AFN({0}, {"a"}, 0, set(), {(0, "a"): {0}})
        self.assertFalse(simular_afn(afn, ""))
        self.assertFalse(simular_afn(afn, "aaa"))

    def test_conserva_los_espacios_de_la_cadena(self):
        afn = AFN({0, 1}, {" "}, 0, {1}, {(0, " "): {1}})
        self.assertTrue(simular_afn(afn, " "))
        self.assertFalse(simular_afn(afn, ""))
        self.assertFalse(simular_afn(afn, "  "))

    def test_cadena_larga_de_transiciones_epsilon_sin_recursion(self):
        afn = AFN(
            set(range(2001)), set(), 0, {2000},
            {(estado, EPSILON): {estado + 1} for estado in range(2000)},
        )
        self.assertTrue(simular_afn(afn, ""))


if __name__ == "__main__":
    unittest.main()

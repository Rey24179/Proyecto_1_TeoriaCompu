"""Equivalencia y minimalidad verificadas con recorridos de pares de estados."""

from collections import deque
from copy import deepcopy
from itertools import combinations, product
from random import Random
import unittest

from automatas import AFD, afn_a_afd, minimizar_afd, regex_a_afn, simular_afd, simular_afn


class TestHopcroft(unittest.TestCase):
    def comprobar_resultado(self, original, minimo):
        """Comprueba estructura, equivalencia exacta y estados distinguibles."""
        minimo.validar()
        self.assertEqual(original.alfabeto, minimo.alfabeto)
        self.assertEqual(minimo.estado_inicial, 0)
        self.assertEqual(minimo.estados, set(range(len(minimo.estados))))
        for estado in minimo.estados:
            for simbolo in minimo.alfabeto:
                self.assertIn((estado, simbolo), minimo.transiciones)

        # Equivalencia exacta: recorrer el producto de ambos autómatas.
        # None representa el rechazo permanente de una transición parcial.
        inicial = (original.estado_inicial, minimo.estado_inicial)
        visitados = {inicial}
        pendientes = deque([inicial])
        while pendientes:
            izquierdo, derecho = pendientes.popleft()
            self.assertEqual(
                izquierdo in original.estados_aceptacion,
                derecho in minimo.estados_aceptacion,
                f"Aceptación diferente en el par {(izquierdo, derecho)}",
            )
            for simbolo in original.alfabeto:
                pareja = (
                    original.transiciones.get((izquierdo, simbolo)),
                    minimo.transiciones[(derecho, simbolo)],
                )
                if pareja not in visitados:
                    visitados.add(pareja)
                    pendientes.append(pareja)
        self.assertEqual({derecho for _, derecho in visitados}, minimo.estados)

        # Minimalidad: cada pareja de estados debe admitir una continuación
        # que acepte desde uno y rechace desde el otro. No usa particiones.
        for pareja_inicial in combinations(sorted(minimo.estados), 2):
            pendientes = deque([pareja_inicial])
            visitados = {pareja_inicial}
            distinguibles = False
            while pendientes:
                izquierdo, derecho = pendientes.popleft()
                if (izquierdo in minimo.estados_aceptacion) != (
                    derecho in minimo.estados_aceptacion
                ):
                    distinguibles = True
                    break
                for simbolo in minimo.alfabeto:
                    pareja = (
                        minimo.transiciones[(izquierdo, simbolo)],
                        minimo.transiciones[(derecho, simbolo)],
                    )
                    if pareja not in visitados:
                        visitados.add(pareja)
                        pendientes.append(pareja)
            self.assertTrue(distinguibles, f"Estados equivalentes: {pareja_inicial}")

    def test_reduce_el_afd_de_subconjuntos_a_un_minimo_conocido(self):
        afd = afn_a_afd(regex_a_afn("(a|b)*abb"))
        minimo = minimizar_afd(afd)
        self.assertEqual(len(afd.estados), 5)
        self.assertEqual(len(minimo.estados), 4)
        self.assertEqual(minimo.estados_aceptacion, {3})
        self.assertEqual(minimo.transiciones, {
            (0, "a"): 1, (0, "b"): 0,
            (1, "a"): 1, (1, "b"): 2,
            (2, "a"): 1, (2, "b"): 3,
            (3, "a"): 1, (3, "b"): 0,
        })
        self.comprobar_resultado(afd, minimo)

    def test_une_finales_equivalentes(self):
        afd = AFD(
            {0, 1, 2}, {"a", "b"}, 0, {1, 2},
            {(0, "a"): 1, (0, "b"): 2, (1, "a"): 1, (1, "b"): 2,
             (2, "a"): 1, (2, "b"): 2},
        )
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 2)
        self.comprobar_resultado(afd, minimo)

    def test_elimina_estados_inaccesibles(self):
        afd = AFD({0, 8, 9}, {"a"}, 0, {0, 9}, {(0, "a"): 0, (8, "a"): 9, (9, "a"): 8})
        minimo = minimizar_afd(afd)
        self.assertEqual(minimo, AFD({0}, {"a"}, 0, {0}, {(0, "a"): 0}))
        self.comprobar_resultado(afd, minimo)

    def test_completa_tabla_parcial_sin_reutilizar_un_final_inaccesible(self):
        afd = AFD({0, 1, 2}, {"a"}, 0, {1, 2}, {(0, "a"): 1})
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 3)
        self.assertTrue(simular_afd(minimo, "a"))
        self.assertFalse(simular_afd(minimo, "aa"))
        self.comprobar_resultado(afd, minimo)

    def test_un_afd_parcial_puede_necesitar_mas_estados_al_completarse(self):
        afd = AFD({0}, {"a"}, 0, {0})
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 2)
        self.assertEqual(minimo.estados_aceptacion, {0})
        self.comprobar_resultado(afd, minimo)

    def test_fusiona_un_sumidero_nuevo_con_un_estado_muerto_existente(self):
        afd = AFD({0, 1}, {"a", "b"}, 0, {0}, {(0, "a"): 1, (1, "a"): 1})
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 2)
        self.comprobar_resultado(afd, minimo)

    def test_lenguaje_vacio_se_reduce_a_un_solo_estado(self):
        afd = AFD({0, 1, 2}, {"a", "b"}, 0, set(), {(0, "a"): 1, (1, "a"): 2})
        minimo = minimizar_afd(afd)
        self.assertEqual(minimo, AFD({0}, {"a", "b"}, 0, set(), {(0, "a"): 0, (0, "b"): 0}))
        self.comprobar_resultado(afd, minimo)

    def test_todos_finales_en_un_afd_completo(self):
        afd = AFD({0, 1}, {"a"}, 0, {0, 1}, {(0, "a"): 1, (1, "a"): 0})
        minimo = minimizar_afd(afd)
        self.assertEqual(minimo, AFD({0}, {"a"}, 0, {0}, {(0, "a"): 0}))
        self.comprobar_resultado(afd, minimo)

    def test_todos_finales_en_un_afd_parcial_no_implica_lenguaje_universal(self):
        afd = AFD({0, 1}, {"a"}, 0, {0, 1}, {(0, "a"): 1})
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 3)
        self.comprobar_resultado(afd, minimo)

    def test_alfabeto_vacio(self):
        for finales in (set(), {-3}, {8}):
            with self.subTest(finales=finales):
                afd = AFD({-3, 8}, set(), -3, finales)
                minimo = minimizar_afd(afd)
                self.assertEqual(minimo.estados, {0})
                self.assertEqual(minimo.transiciones, {})
                self.comprobar_resultado(afd, minimo)

    def test_distingue_estados_que_requieren_varias_rondas(self):
        # Se necesitan 12 letras 'a' para alcanzar el único estado final.
        afd = AFD(set(range(13)), {"a"}, 0, {12}, {(q, "a"): q + 1 for q in range(12)})
        minimo = minimizar_afd(afd)
        self.assertEqual(len(minimo.estados), 14)
        self.comprobar_resultado(afd, minimo)

    def test_no_modifica_ni_comparte_datos_con_el_original(self):
        afd = afn_a_afd(regex_a_afn("(a|b)*abb"))
        copia = deepcopy(afd)
        minimo = minimizar_afd(afd)
        self.assertEqual(afd, copia)
        minimo.estados.clear()
        minimo.alfabeto.add("x")
        minimo.estados_aceptacion.clear()
        minimo.transiciones.clear()
        self.assertEqual(afd, copia)

    def test_resultado_canonico_e_idempotente(self):
        afd = afn_a_afd(regex_a_afn("(a|b)*abb"))
        renombrar = {q: 100 - 7 * q for q in afd.estados}
        renombrado = AFD(
            set(renombrar.values()), set(afd.alfabeto), renombrar[afd.estado_inicial],
            {renombrar[q] for q in afd.estados_aceptacion},
            {(renombrar[q], a): renombrar[r] for (q, a), r in reversed(list(afd.transiciones.items()))},
        )
        minimo = minimizar_afd(afd)
        self.assertEqual(minimo, minimizar_afd(renombrado))
        self.assertEqual(minimo, minimizar_afd(minimo))

    def test_rechaza_un_afd_modificado_incorrectamente(self):
        afd = AFD({0}, {"a"}, 0, {0})
        afd.transiciones[(0, "a")] = 99
        with self.assertRaises(ValueError):
            minimizar_afd(afd)

    def test_todos_los_afd_parciales_de_dos_estados_y_dos_simbolos(self):
        claves = [(0, "a"), (0, "b"), (1, "a"), (1, "b")]
        for destinos in product((None, 0, 1), repeat=4):
            transiciones = {clave: destino for clave, destino in zip(claves, destinos) if destino is not None}
            for finales in (set(), {0}, {1}, {0, 1}):
                with self.subTest(destinos=destinos, finales=finales):
                    afd = AFD({0, 1}, {"a", "b"}, 0, finales, transiciones)
                    self.comprobar_resultado(afd, minimizar_afd(afd))

    def test_afd_generados_con_semilla_fija(self):
        generador = Random(2026)
        for caso in range(100):
            estados = [3 * q - 7 for q in range(generador.randint(1, 8))]
            afd = AFD(
                set(estados), {"a", "b", "c"}, generador.choice(estados),
                {q for q in estados if generador.random() < 0.5},
                {(q, a): generador.choice(estados) for q in estados for a in "abc"
                 if generador.random() < 0.8},
            )
            with self.subTest(caso=caso):
                minimo = minimizar_afd(afd)
                self.comprobar_resultado(afd, minimo)
                self.assertEqual(minimo, minimizar_afd(minimo))

    def test_flujo_completo_conserva_aceptacion_y_minimalidad(self):
        for expresion in ("ε", "a", "a*", "a+", "a?", "(a|b)*", "(a|b)*abb", "(ab)+c?", "(a|ε)b*", "a*?+"):
            afn = regex_a_afn(expresion)
            afd = afn_a_afd(afn)
            minimo = minimizar_afd(afd)
            with self.subTest(expresion=expresion):
                self.comprobar_resultado(afd, minimo)
            for longitud in range(5):
                for letras in product("abc", repeat=longitud):
                    cadena = "".join(letras)
                    with self.subTest(expresion=expresion, cadena=cadena):
                        self.assertEqual(simular_afn(afn, cadena), simular_afd(minimo, cadena))


if __name__ == "__main__":
    unittest.main()

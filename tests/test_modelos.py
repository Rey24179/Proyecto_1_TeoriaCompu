"""Comprueba las reglas estructurales que usarán los algoritmos posteriores."""

import unittest

from automatas import AFD, AFN, EPSILON


class TestModelos(unittest.TestCase):
    def test_afn_permite_epsilon_y_varios_destinos(self):
        afn = AFN(
            estados={0, 1, 2},
            alfabeto={"a"},
            estado_inicial=0,
            estados_aceptacion={2},
            transiciones={(0, EPSILON): {1}, (1, "a"): {1, 2}},
        )
        afn.validar()

    def test_afd_permite_una_tabla_parcial(self):
        afd = AFD(
            estados={0, 1},
            alfabeto={"a", "b"},
            estado_inicial=0,
            estados_aceptacion={1},
            transiciones={(0, "a"): 1},
        )
        afd.validar()

    def test_permite_alfabeto_vacio_y_estado_inicial_final(self):
        for modelo in (AFN, AFD):
            with self.subTest(modelo=modelo.__name__):
                modelo({0}, set(), 0, {0}).validar()

    def test_permite_automata_sin_estados_de_aceptacion(self):
        for modelo in (AFN, AFD):
            with self.subTest(modelo=modelo.__name__):
                modelo({0}, {"a"}, 0, set()).validar()

    def test_rechaza_componentes_inconsistentes(self):
        casos = [
            {"estados": set()},
            {"estado_inicial": 99},
            {"estados_aceptacion": {99}},
            {"alfabeto": {EPSILON}},
            {"alfabeto": {""}},
            {"alfabeto": {"ab"}},
        ]
        for modelo in (AFN, AFD):
            for cambios in casos:
                with self.subTest(modelo=modelo.__name__, cambios=cambios):
                    datos = dict(
                        estados={0, 1},
                        alfabeto={"a"},
                        estado_inicial=0,
                        estados_aceptacion={1},
                    )
                    datos.update(cambios)
                    with self.assertRaises(ValueError):
                        modelo(**datos)

    def test_afn_rechaza_transiciones_invalidas(self):
        for transiciones in (
            {(99, "a"): {1}},
            {(0, "a"): {1, 99}},
            {(0, "b"): {1}},
            {(0, EPSILON): {99}},
        ):
            with self.subTest(transiciones=transiciones):
                with self.assertRaises(ValueError):
                    AFN({0, 1}, {"a"}, 0, {1}, transiciones)

    def test_afd_rechaza_transiciones_invalidas(self):
        for transiciones in (
            {(99, "a"): 1},
            {(0, "a"): 99},
            {(0, "b"): 1},
            {(0, EPSILON): 1},
        ):
            with self.subTest(transiciones=transiciones):
                with self.assertRaises(ValueError):
                    AFD({0, 1}, {"a"}, 0, {1}, transiciones)

    def test_validar_detecta_cambios_inconsistentes(self):
        for modelo in (AFN, AFD):
            with self.subTest(modelo=modelo.__name__):
                automata = modelo({0, 1}, {"a"}, 0, {1})
                automata.estados.remove(1)
                with self.assertRaises(ValueError):
                    automata.validar()

    def test_las_tablas_por_defecto_son_independientes(self):
        afn_a = AFN({0, 1}, {"a"}, 0, {1})
        afn_b = AFN({0, 1}, {"a"}, 0, {1})
        afn_a.transiciones[(0, "a")] = {1}
        self.assertEqual(afn_b.transiciones, {})

        afd_a = AFD({0, 1}, {"a"}, 0, {1})
        afd_b = AFD({0, 1}, {"a"}, 0, {1})
        afd_a.transiciones[(0, "a")] = 1
        self.assertEqual(afd_b.transiciones, {})


if __name__ == "__main__":
    unittest.main()

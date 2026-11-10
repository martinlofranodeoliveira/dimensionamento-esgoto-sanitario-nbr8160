from __future__ import annotations

import unittest
from fractions import Fraction

from esgoto_sanitario_nbr8160.constants import (
    TABELA_APARELHOS_SANITARIOS_NBR8160,
    TABELA_RAMAIS_ESGOTO_NBR8160,
    TABELA_TUBOS_QUEDA_NBR8160,
    TABELA_COLETOR_PREDIAL_NBR8160,
    TABELA_COLUNA_VENTILACAO_NBR8160,
    DECLIVIDADE_MINIMA_DN_ATE_75,
    DECLIVIDADE_MINIMA_DN_A_PARTIR_100,
    FECHO_HIDRICO_MINIMO_MM,
    DISTANCIA_MAXIMA_INSPECAO_M,
    DIMENSAO_MINIMA_INSPECAO_MM,
)


class TestConstants(unittest.TestCase):
    def test_aparelhos_sanitarios_existencia_e_tipos(self) -> None:
        self.assertIn("bacia_sanitaria_caixa", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("bacia_sanitaria_valvula", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("lavatorio_residencial", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("chuveiro_residencial", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("pia_cozinha_residencial", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("tanque_lavar_roupa", TABELA_APARELHOS_SANITARIOS_NBR8160)
        self.assertIn("maquina_lavar_roupa", TABELA_APARELHOS_SANITARIOS_NBR8160)

    def test_aparelhos_sem_float_e_valores_validos(self) -> None:
        for chave, dados in TABELA_APARELHOS_SANITARIOS_NBR8160.items():
            uhc = dados["uhc"]
            dn = dados["dn_minimo"]
            self.assertIsInstance(uhc, Fraction, f"UHC de {chave} deve ser Fraction")
            self.assertIsInstance(dn, int, f"DN de {chave} deve ser int")
            self.assertGreater(uhc, Fraction(0, 1))
            self.assertGreaterEqual(dn, 40)
            self.assertNotIsInstance(uhc, float)
            self.assertNotIsInstance(dn, float)

    def test_bacia_sanitaria_dn_minimo_100(self) -> None:
        bacia_cx = TABELA_APARELHOS_SANITARIOS_NBR8160["bacia_sanitaria_caixa"]
        bacia_val = TABELA_APARELHOS_SANITARIOS_NBR8160["bacia_sanitaria_valvula"]
        self.assertEqual(bacia_cx["dn_minimo"], 100)
        self.assertEqual(bacia_val["dn_minimo"], 100)
        self.assertEqual(bacia_cx["uhc"], Fraction(6, 1))
        self.assertEqual(bacia_val["uhc"], Fraction(32, 1))

    def test_tabela_ramais_esgoto(self) -> None:
        self.assertEqual(len(TABELA_RAMAIS_ESGOTO_NBR8160), 4)
        dns = [dn for _, dn in TABELA_RAMAIS_ESGOTO_NBR8160]
        uhcs = [uhc for uhc, _ in TABELA_RAMAIS_ESGOTO_NBR8160]
        self.assertEqual(dns, [40, 50, 75, 100])
        self.assertEqual(uhcs, [3, 6, 22, 160])

    def test_tabela_tubos_queda(self) -> None:
        self.assertIn(50, TABELA_TUBOS_QUEDA_NBR8160)
        self.assertIn(75, TABELA_TUBOS_QUEDA_NBR8160)
        self.assertIn(100, TABELA_TUBOS_QUEDA_NBR8160)
        self.assertIn(150, TABELA_TUBOS_QUEDA_NBR8160)
        self.assertEqual(TABELA_TUBOS_QUEDA_NBR8160[100]["ate_3_pav"], 240)
        self.assertEqual(TABELA_TUBOS_QUEDA_NBR8160[100]["mais_3_pav"], 500)

    def test_tabela_coletor_predial(self) -> None:
        self.assertIn(100, TABELA_COLETOR_PREDIAL_NBR8160)
        self.assertIn(150, TABELA_COLETOR_PREDIAL_NBR8160)
        tabela_100 = TABELA_COLETOR_PREDIAL_NBR8160[100]
        self.assertEqual(tabela_100[Fraction(1, 100)], 180)
        self.assertEqual(tabela_100[Fraction(2, 100)], 250)

    def test_tabela_coluna_ventilacao(self) -> None:
        self.assertIn(100, TABELA_COLUNA_VENTILACAO_NBR8160)
        faixas = TABELA_COLUNA_VENTILACAO_NBR8160[100]
        self.assertTrue(len(faixas) > 0)
        for uhc_lim, dn_v in faixas:
            self.assertIsInstance(uhc_lim, int)
            self.assertIsInstance(dn_v, int)

    def test_constantes_normativas_especiais(self) -> None:
        self.assertEqual(DECLIVIDADE_MINIMA_DN_ATE_75, Fraction(2, 100))
        self.assertEqual(DECLIVIDADE_MINIMA_DN_A_PARTIR_100, Fraction(1, 100))
        self.assertEqual(FECHO_HIDRICO_MINIMO_MM, 50)
        self.assertEqual(DISTANCIA_MAXIMA_INSPECAO_M, Fraction(25, 1))
        self.assertEqual(DIMENSAO_MINIMA_INSPECAO_MM, 600)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from fractions import Fraction

from esgoto_sanitario_nbr8160.models import (
    AparelhoSanitario,
    RamalDescarga,
    RamalEsgoto,
    TuboQueda,
    ColunaVentilacao,
    ColetorPredial,
    CaixaGordura,
    CaixaInspecao,
    CaixaSifonada,
    ProjetoEsgoto,
)
from esgoto_sanitario_nbr8160.calculator import (
    obter_info_aparelho,
    dimensionar_ramal_descarga,
    dimensionar_ramal_esgoto,
    dimensionar_tubo_queda,
    dimensionar_coluna_ventilacao,
    dimensionar_coletor_predial,
    verificar_caixa_gordura,
    verificar_caixa_inspecao,
    dimensionar_sistema_esgoto,
)


class TestCalculator(unittest.TestCase):
    def test_obter_info_aparelho(self) -> None:
        info_bacia = obter_info_aparelho("bacia_sanitaria_caixa")
        self.assertEqual(info_bacia["dn_minimo"], 100)
        self.assertEqual(info_bacia["uhc"], Fraction(6, 1))

        info_lav = obter_info_aparelho("lavatorio_residencial")
        self.assertEqual(info_lav["dn_minimo"], 40)
        self.assertEqual(info_lav["uhc"], Fraction(1, 1))

        with self.assertRaises(KeyError):
            obter_info_aparelho("aparelho_inexistente")

    def test_dimensionar_ramal_descarga(self) -> None:
        ap = AparelhoSanitario("BS-01", "bacia_sanitaria_caixa", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=100)
        res = dimensionar_ramal_descarga(rd)
        self.assertTrue(res.atende_norma)
        self.assertEqual(res.dn_minimo_norma, 100)
        self.assertEqual(res.dn_adotado, 100)

        # Diâmetro insuficiente
        rd_invalido = RamalDescarga("RD-02", ap, dn_adotado_mm=75)
        res_inv = dimensionar_ramal_descarga(rd_invalido)
        self.assertFalse(res_inv.atende_norma)

    def test_dimensionar_ramal_esgoto_capacidade_e_declividade(self) -> None:
        ap1 = AparelhoSanitario("LV", "lavatorio_residencial", 1)  # 1 UHC
        ap2 = AparelhoSanitario("CH", "chuveiro_residencial", 1)   # 2 UHC
        # Total = 3 UHC -> Tabela 3: até 3 UHC -> DN 40
        re = RamalEsgoto(
            "RE-01",
            aparelhos=[ap1, ap2],
            declividade_m_m=Fraction(2, 100),
        )
        res = dimensionar_ramal_esgoto(re)
        self.assertEqual(res.total_uhc, Fraction(3, 1))
        self.assertEqual(res.dn_calculado, 40)
        self.assertEqual(res.dn_adotado, 40)
        self.assertTrue(res.atende_norma)

        # Declividade insuficiente para DN 40 (mínimo 2%)
        re_dec_inv = RamalEsgoto(
            "RE-02",
            aparelhos=[ap1, ap2],
            dn_adotado_mm=40,
            declividade_m_m=Fraction(1, 100),
        )
        res_dec_inv = dimensionar_ramal_esgoto(re_dec_inv)
        self.assertFalse(res_dec_inv.atende_declividade)
        self.assertFalse(res_dec_inv.atende_norma)

    def test_ramal_esgoto_regra_bacia_e_gordura(self) -> None:
        # Ramal com bacia sanitária exige obrigatoriamente DN 100
        ap_bs = AparelhoSanitario("BS", "bacia_sanitaria_caixa", 1)  # 6 UHC
        re_bs = RamalEsgoto("RE-BS", aparelhos=[ap_bs], declividade_m_m=Fraction(2, 100))
        res_bs = dimensionar_ramal_esgoto(re_bs)
        self.assertEqual(res_bs.dn_calculado, 100)

        # Ramal de pia de cozinha exige no mínimo DN 50
        ap_pia = AparelhoSanitario("PC", "pia_cozinha_residencial", 1)  # 3 UHC (3 caberia em DN 40, mas pia exige 50)
        re_pia = RamalEsgoto("RE-PC", aparelhos=[ap_pia], declividade_m_m=Fraction(2, 100))
        res_pia = dimensionar_ramal_esgoto(re_pia)
        self.assertEqual(res_pia.dn_calculado, 50)

    def test_dimensionar_tubo_queda_pavimentos(self) -> None:
        # 17 UHC em prédio de até 3 pavimentos
        re = RamalEsgoto(
            "RE",
            aparelhos=[
                AparelhoSanitario("BS", "bacia_sanitaria_caixa", 2), # 12 UHC
                AparelhoSanitario("LV", "lavatorio_residencial", 5), # 5 UHC
            ],
            recebe_bacia=True,
        )
        tq3 = TuboQueda("TQ-01", ramais_contribuintes=[re], numero_pavimentos=3)
        res3 = dimensionar_tubo_queda(tq3)
        self.assertEqual(res3.dn_calculado, 100)
        self.assertTrue(res3.atende_norma)

        # Prédio com mais de 3 pavimentos e carga alta
        re_grande = RamalEsgoto(
            "RE-G",
            aparelhos=[
                AparelhoSanitario("BS", "bacia_sanitaria_valvula", 10), # 320 UHC
            ],
            recebe_bacia=True,
        )
        tq_alto = TuboQueda("TQ-02", ramais_contribuintes=[re_grande], numero_pavimentos=10)
        res_alto = dimensionar_tubo_queda(tq_alto)
        # 320 UHC em >3 pavimentos: DN 100 suporta até 500 UHC
        self.assertEqual(res_alto.dn_calculado, 100)
        self.assertEqual(res_alto.capacidade_uhc_admissivel, 500)

    def test_dimensionar_coluna_ventilacao(self) -> None:
        cv = ColunaVentilacao("CV-01", "TQ-01", comprimento_m=Fraction(15, 1))
        res = dimensionar_coluna_ventilacao(cv, dn_tubo_queda=100, uhc_ventilada=Fraction(30, 1))
        self.assertEqual(res.dn_calculado, 50)
        self.assertTrue(res.atende_norma)

        # Carga alta no TQ 100 exige DN 100 de ventilação
        res_alta = dimensionar_coluna_ventilacao(cv, dn_tubo_queda=100, uhc_ventilada=Fraction(200, 1))
        self.assertEqual(res_alta.dn_calculado, 100)

    def test_dimensionar_coletor_predial(self) -> None:
        col = ColetorPredial(
            "CP-01",
            uhc_adicional_direta=Fraction(100, 1),
            declividade_m_m=Fraction(1, 100),
        )
        res = dimensionar_coletor_predial(col, total_uhc=Fraction(100, 1))
        self.assertEqual(res.dn_calculado, 100)
        self.assertEqual(res.capacidade_uhc_tabela, 180)
        self.assertTrue(res.atende_norma)

        # Declividade menor que 0,5% é reprovada
        col_ruim = ColetorPredial(
            "CP-02",
            uhc_adicional_direta=Fraction(100, 1),
            declividade_m_m=Fraction(3, 1000), # 0,3%
        )
        res_ruim = dimensionar_coletor_predial(col_ruim, total_uhc=Fraction(100, 1))
        self.assertFalse(res_ruim.atende_norma)

    def test_verificar_caixas(self) -> None:
        cg_simples = CaixaGordura("CG-01", tipo="simples", volume_retencao_L=Fraction(18, 1))
        res_cg = verificar_caixa_gordura(cg_simples)
        self.assertTrue(res_cg.atende_norma)

        cg_dupla = CaixaGordura("CG-02", tipo="dupla", volume_retencao_L=Fraction(120, 1), diametro_mm=400)
        res_cgd = verificar_caixa_gordura(cg_dupla)
        self.assertTrue(res_cgd.atende_norma)

        ci_ok = CaixaInspecao("CI-01", largura_mm=600, comprimento_mm=600, distancia_montante_m=Fraction(20, 1))
        res_ci = verificar_caixa_inspecao(ci_ok)
        self.assertTrue(res_ci.atende_norma)

        ci_longe = CaixaInspecao("CI-02", largura_mm=600, comprimento_mm=600, distancia_montante_m=Fraction(28, 1))
        res_longe = verificar_caixa_inspecao(ci_longe)
        self.assertFalse(res_longe.atende_norma)

    def test_caixa_gordura_especial_por_refeicoes(self) -> None:
        # Especial para restaurantes / cozinhas industriais: V = 2 * N + 20
        # Para 100 refeições: V = 200 + 20 = 220 L
        cg_esp = CaixaGordura(
            "CG-RESTAURANTE",
            tipo="especial",
            numero_refeicoes=100,
            volume_retencao_L=Fraction(250, 1),
            diametro_mm=600,
        )
        res_esp = verificar_caixa_gordura(cg_esp)
        self.assertTrue(res_esp.atende_norma)
        self.assertEqual(res_esp.volume_retencao_calculado_L, Fraction(220, 1))

        # Se volume adotado for menor que 220 L
        cg_esp_insuf = CaixaGordura(
            "CG-RESTAURANTE-PEQ",
            tipo="especial",
            numero_refeicoes=100,
            volume_retencao_L=Fraction(200, 1),
            diametro_mm=600,
        )
        res_esp_insuf = verificar_caixa_gordura(cg_esp_insuf)
        self.assertFalse(res_esp_insuf.atende_norma)

    def test_tubo_queda_capacidade_excedida(self) -> None:
        tq_pequeno = TuboQueda(
            "TQ-PEQ",
            numero_pavimentos=5,
            dn_adotado_mm=50, # DN 50 suporta máx 24 UHC em >3 pav
        )
        res = dimensionar_tubo_queda(tq_pequeno, carga_uhc_direta=Fraction(30, 1))
        self.assertFalse(res.atende_norma)
        self.assertGreater(res.taxa_ocupacao_uhc, Fraction(1, 1))

    def test_coletor_predial_capacidade_excedida(self) -> None:
        col = ColetorPredial(
            "CP-SOBRECARREGADO",
            dn_adotado_mm=100, # DN 100 a 1% suporta 180 UHC
            declividade_m_m=Fraction(1, 100),
        )
        res = dimensionar_coletor_predial(col, total_uhc=Fraction(250, 1))
        self.assertFalse(res.atende_norma)

    def test_dimensionar_sistema_completo(self) -> None:
        ap = AparelhoSanitario("BS", "bacia_sanitaria_caixa", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=100)
        re = RamalEsgoto("RE-01", aparelhos=[ap], dn_adotado_mm=100, declividade_m_m=Fraction(2, 100), recebe_bacia=True)
        tq = TuboQueda("TQ-01", ramais_contribuintes=[re], numero_pavimentos=2, dn_adotado_mm=100)
        cv = ColunaVentilacao("CV-01", "TQ-01", dn_adotado_mm=50, comprimento_m=Fraction(8, 1))
        cp = ColetorPredial("CP-01", tubos_queda_contribuintes=["TQ-01"], dn_adotado_mm=100, declividade_m_m=Fraction(1, 100))
        cg = CaixaGordura("CG-01", tipo="simples", volume_retencao_L=Fraction(18, 1))
        ci = CaixaInspecao("CI-01", distancia_montante_m=Fraction(10, 1))

        proj = ProjetoEsgoto(
            identificacao="Residencial Teste",
            ramais_descarga=[rd],
            ramais_esgoto=[re],
            tubos_queda=[tq],
            coluna_ventilacao=cv,
            coletor_predial=cp,
            caixa_gordura=cg,
            caixas_inspecao=[ci],
        )

        res = dimensionar_sistema_esgoto(proj)
        self.assertTrue(res.atende_geral)
        self.assertEqual(res.total_uhc_geral, Fraction(6, 1))
        self.assertTrue(all(res.conformidades.values()))
        self.assertIn("ABNT NBR 8160:1999", res.norma)


if __name__ == "__main__":
    unittest.main()

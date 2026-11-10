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
    ResultadoRamalDescarga,
    ResultadoRamalEsgoto,
    ResultadoTuboQueda,
    ResultadoColunaVentilacao,
    ResultadoColetorPredial,
    ResultadoCaixaGordura,
    ResultadoCaixaInspecao,
    ResultadoProjetoEsgoto,
)


class TestModels(unittest.TestCase):
    def test_aparelho_sanitario_valido(self) -> None:
        ap = AparelhoSanitario("LV-01", "lavatorio_residencial", 2)
        self.assertEqual(ap.identificacao, "LV-01")
        self.assertEqual(ap.tipo_aparelho, "lavatorio_residencial")
        self.assertEqual(ap.quantidade, 2)

    def test_aparelho_sanitario_quantidade_invalida(self) -> None:
        with self.assertRaises(ValueError):
            AparelhoSanitario("LV-01", "lavatorio_residencial", 0)
        with self.assertRaises(ValueError):
            AparelhoSanitario("LV-01", "lavatorio_residencial", -1)

    def test_ramal_descarga(self) -> None:
        ap = AparelhoSanitario("BS-01", "bacia_sanitaria_caixa", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=100)
        self.assertEqual(rd.identificacao, "RD-01")
        self.assertEqual(rd.dn_adotado_mm, 100)
        self.assertEqual(rd.aparelho.tipo_aparelho, "bacia_sanitaria_caixa")

    def test_ramal_esgoto_validacoes(self) -> None:
        re = RamalEsgoto(
            "RE-01",
            declividade_m_m=Fraction(2, 100),
            comprimento_m=Fraction(4, 1),
        )
        self.assertEqual(re.identificacao, "RE-01")

        with self.assertRaises(ValueError):
            RamalEsgoto("RE-02", declividade_m_m=Fraction(0, 100))
        with self.assertRaises(ValueError):
            RamalEsgoto("RE-03", comprimento_m=Fraction(-1, 1))

    def test_tubo_queda_validacoes(self) -> None:
        tq = TuboQueda("TQ-01", numero_pavimentos=3, altura_m=Fraction(9, 1))
        self.assertEqual(tq.numero_pavimentos, 3)

        with self.assertRaises(ValueError):
            TuboQueda("TQ-02", numero_pavimentos=0)
        with self.assertRaises(ValueError):
            TuboQueda("TQ-03", altura_m=Fraction(0, 1))

    def test_coluna_ventilacao_validacoes(self) -> None:
        cv = ColunaVentilacao("CV-01", "TQ-01", comprimento_m=Fraction(10, 1))
        self.assertEqual(cv.tubo_queda_associado, "TQ-01")

        with self.assertRaises(ValueError):
            ColunaVentilacao("CV-02", "TQ-01", comprimento_m=Fraction(-5, 1))

    def test_coletor_predial_validacoes(self) -> None:
        cp = ColetorPredial("CP-01", declividade_m_m=Fraction(1, 100), comprimento_m=Fraction(15, 1))
        self.assertEqual(cp.identificacao, "CP-01")

        with self.assertRaises(ValueError):
            ColetorPredial("CP-02", declividade_m_m=Fraction(0, 100))
        with self.assertRaises(ValueError):
            ColetorPredial("CP-03", comprimento_m=Fraction(0, 1))

    def test_caixas_e_dispositivos(self) -> None:
        cg = CaixaGordura("CG-01", tipo="simples", volume_retencao_L=Fraction(18, 1))
        self.assertEqual(cg.tipo, "simples")
        self.assertEqual(cg.volume_retencao_L, Fraction(18, 1))

        ci = CaixaInspecao("CI-01", largura_mm=600, comprimento_mm=600)
        self.assertEqual(ci.largura_mm, 600)
        self.assertEqual(ci.comprimento_mm, 600)

        cs = CaixaSifonada("CS-01", fecho_hidrico_mm=50)
        self.assertEqual(cs.fecho_hidrico_mm, 50)
        self.assertEqual(cs.dn_saida_mm, 50)

    def test_caixa_gordura_especial_atributos(self) -> None:
        cg = CaixaGordura("CG-ESP", tipo="especial", numero_refeicoes=150, volume_retencao_L=Fraction(320, 1))
        self.assertEqual(cg.numero_refeicoes, 150)
        self.assertEqual(cg.volume_retencao_L, Fraction(320, 1))

    def test_resultado_projeto_esgoto(self) -> None:
        res = ResultadoProjetoEsgoto(
            identificacao="Projeto Teste",
            norma="ABNT NBR 8160:1999",
            total_uhc_geral=Fraction(12, 1),
            resultados_ramais_descarga=[],
            resultados_ramais_esgoto=[],
            resultados_tubos_queda=[],
            resultado_coluna_ventilacao=None,
            resultado_coletor_predial=None,
            resultado_caixa_gordura=None,
            resultados_caixas_inspecao=[],
            atende_geral=True,
            conformidades={"ramais": True},
            alertas=[],
            recomendacoes=["Tudo ok"],
        )
        self.assertTrue(res.atende_geral)
        self.assertEqual(res.total_uhc_geral, Fraction(12, 1))


if __name__ == "__main__":
    unittest.main()

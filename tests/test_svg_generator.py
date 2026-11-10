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
from esgoto_sanitario_nbr8160.calculator import dimensionar_sistema_esgoto
from esgoto_sanitario_nbr8160.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    def test_gerar_painel_svg_estrutura_e_conteudo(self) -> None:
        ap = AparelhoSanitario("BS", "bacia_sanitaria_caixa", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=100)
        re = RamalEsgoto("RE-01", aparelhos=[ap], dn_adotado_mm=100, declividade_m_m=Fraction(2, 100), recebe_bacia=True)
        tq = TuboQueda("TQ-01", ramais_contribuintes=[re], numero_pavimentos=2, dn_adotado_mm=100)
        cv = ColunaVentilacao("CV-01", "TQ-01", dn_adotado_mm=50, comprimento_m=Fraction(8, 1))
        cp = ColetorPredial("CP-01", tubos_queda_contribuintes=["TQ-01"], dn_adotado_mm=100, declividade_m_m=Fraction(1, 100))
        cg = CaixaGordura("CG-01", tipo="simples", volume_retencao_L=Fraction(18, 1))
        ci = CaixaInspecao("CI-01", distancia_montante_m=Fraction(10, 1))

        proj = ProjetoEsgoto(
            identificacao="Residencial & Comercial Bela Vista",
            ramais_descarga=[rd],
            ramais_esgoto=[re],
            tubos_queda=[tq],
            coluna_ventilacao=cv,
            coletor_predial=cp,
            caixa_gordura=cg,
            caixas_inspecao=[ci],
        )
        res = dimensionar_sistema_esgoto(proj)
        svg = gerar_painel_svg(res)

        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ABNT NBR 8160:1999", svg)
        self.assertIn("Residencial &amp; Comercial Bela Vista", svg)
        self.assertIn("SISTEMA CONFORME NBR 8160", svg)
        self.assertIn("#10b981", svg)

    def test_gerar_painel_svg_reprovado(self) -> None:
        ap = AparelhoSanitario("BS", "bacia_sanitaria_caixa", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=50) # Incorreto para bacia
        proj = ProjetoEsgoto("Projeto Falho", ramais_descarga=[rd])
        res = dimensionar_sistema_esgoto(proj)
        svg = gerar_painel_svg(res)

        self.assertIn("RESTRIÇÃO / NÃO CONFORME", svg)
        self.assertIn("#ef4444", svg)


if __name__ == "__main__":
    unittest.main()

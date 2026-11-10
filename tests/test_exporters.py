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
from esgoto_sanitario_nbr8160.exporters import (
    sanitizar_campo_csv,
    formatar_fracao_decimal,
    exportar_csv,
    gerar_relatorio_memorial,
)


class TestExporters(unittest.TestCase):
    def test_sanitizar_campo_csv_protecao_formulas(self) -> None:
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+SOMAR(A1:A10)"), "'+SOMAR(A1:A10)")
        self.assertEqual(sanitizar_campo_csv("-100"), "'-100")
        self.assertEqual(sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(sanitizar_campo_csv("\rret"), "'\rret")
        self.assertEqual(sanitizar_campo_csv("Texto Seguro"), "Texto Seguro")
        self.assertEqual(sanitizar_campo_csv(100), "100")

    def test_formatar_fracao_decimal(self) -> None:
        self.assertEqual(formatar_fracao_decimal(Fraction(5, 1)), "5")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 2), 1), "0,5")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 2), 2), "0,50")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 4), 2), "0,25")
        self.assertEqual(formatar_fracao_decimal(Fraction(3, 100), 2), "0,03")

    def test_exportar_csv(self) -> None:
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
        csv_conteudo = exportar_csv(res)

        self.assertIn("Tipo de Trecho;Identificação", csv_conteudo)
        self.assertIn("Ramal de Descarga;RD-01", csv_conteudo)
        self.assertIn("Ramal de Esgoto;RE-01", csv_conteudo)
        self.assertIn("Tubo de Queda (TQ);TQ-01", csv_conteudo)
        self.assertIn("Coluna de Ventilação;CV-01", csv_conteudo)
        self.assertIn("Coletor Predial;CP-01", csv_conteudo)
        self.assertIn("Caixa de Gordura;CG-01", csv_conteudo)
        self.assertIn("Caixa de Inspeção;CI-01", csv_conteudo)

    def test_gerar_relatorio_memorial(self) -> None:
        ap = AparelhoSanitario("LV", "lavatorio_residencial", 1)
        rd = RamalDescarga("RD-01", ap, dn_adotado_mm=40)
        re = RamalEsgoto("RE-01", aparelhos=[ap], dn_adotado_mm=40, declividade_m_m=Fraction(2, 100))
        proj = ProjetoEsgoto("Projeto Memorial", ramais_descarga=[rd], ramais_esgoto=[re])
        res = dimensionar_sistema_esgoto(proj)
        memorial = gerar_relatorio_memorial(res)

        self.assertIn("LOFRANO TECNOLOGIA", memorial)
        self.assertIn("ABNT NBR 8160:1999", memorial)
        self.assertIn("Projeto Memorial", memorial)
        self.assertIn("RAMAIS DE DESCARGA", memorial)
        self.assertIn("RAMAIS DE ESGOTO HORIZONTAIS", memorial)
        self.assertIn("SÍNTESE DE CONFORMIDADE", memorial)


if __name__ == "__main__":
    unittest.main()

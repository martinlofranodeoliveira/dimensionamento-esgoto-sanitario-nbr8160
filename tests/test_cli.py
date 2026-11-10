from __future__ import annotations

import os
import tempfile
import unittest
from fractions import Fraction

from esgoto_sanitario_nbr8160.cli import parse_fracao_cli, main


class TestCLI(unittest.TestCase):
    def test_parse_fracao_cli(self) -> None:
        self.assertEqual(parse_fracao_cli("5"), Fraction(5, 1))
        self.assertEqual(parse_fracao_cli("2.5"), Fraction(25, 10))
        self.assertEqual(parse_fracao_cli("2,5"), Fraction(25, 10))
        self.assertEqual(parse_fracao_cli("3/4"), Fraction(3, 4))

    def test_cli_versao(self) -> None:
        codigo = main(["versao"])
        self.assertEqual(codigo, 0)

    def test_cli_aparelhos(self) -> None:
        codigo = main(["aparelhos"])
        self.assertEqual(codigo, 0)

    def test_cli_tabelas(self) -> None:
        codigo = main(["tabelas"])
        self.assertEqual(codigo, 0)

    def test_cli_dimensionar_rapido_ramal(self) -> None:
        codigo = main(["dimensionar", "--tipo-trecho", "ramal", "--uhc", "6", "--dn", "50", "--declividade", "2.0"])
        self.assertEqual(codigo, 0)

    def test_cli_dimensionar_rapido_tq(self) -> None:
        codigo = main(["dimensionar", "--tipo-trecho", "tq", "--uhc", "30", "--pavimentos", "2", "--dn", "75"])
        self.assertEqual(codigo, 0)

    def test_cli_dimensionar_rapido_coletor(self) -> None:
        codigo = main(["dimensionar", "--tipo-trecho", "coletor", "--uhc", "120", "--dn", "100", "--declividade", "1.0"])
        self.assertEqual(codigo, 0)

    def test_cli_dimensionar_rapido_ventilacao(self) -> None:
        codigo = main(["dimensionar", "--tipo-trecho", "ventilacao", "--uhc", "40", "--dn", "50"])
        self.assertEqual(codigo, 0)

    def test_cli_dimensionar_arquivo_e_saidas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            json_out = os.path.join(tmpdir, "out.json")
            csv_out = os.path.join(tmpdir, "out.csv")
            txt_out = os.path.join(tmpdir, "out.txt")
            svg_out = os.path.join(tmpdir, "out.svg")

            codigo = main([
                "dimensionar",
                "--arquivo", "examples/apartamento_residencial.json",
                "--saida-json", json_out,
                "--saida-csv", csv_out,
                "--saida-relatorio", txt_out,
                "--painel-svg", svg_out,
            ])
            self.assertEqual(codigo, 0)
            self.assertTrue(os.path.exists(json_out))
            self.assertTrue(os.path.exists(csv_out))
            self.assertTrue(os.path.exists(txt_out))
            self.assertTrue(os.path.exists(svg_out))


if __name__ == "__main__":
    unittest.main()

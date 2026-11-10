from __future__ import annotations

import os
import unittest
from pathlib import Path

import esgoto_sanitario_nbr8160


class TestPackaging(unittest.TestCase):
    def test_versao(self) -> None:
        self.assertEqual(esgoto_sanitario_nbr8160.__version__, "1.0.0")

    def test_py_typed_presente(self) -> None:
        pacote_dir = Path(esgoto_sanitario_nbr8160.__file__).parent
        py_typed = pacote_dir / "py.typed"
        self.assertTrue(py_typed.exists(), "Arquivo de tipagem py.typed ausente no pacote.")

    def test_simbolos_publicos_exportados(self) -> None:
        simbolos_esperados = [
            "__version__",
            "AparelhoSanitario",
            "RamalDescarga",
            "RamalEsgoto",
            "TuboQueda",
            "ColunaVentilacao",
            "ColetorPredial",
            "CaixaGordura",
            "CaixaInspecao",
            "CaixaSifonada",
            "ProjetoEsgoto",
            "ResultadoProjetoEsgoto",
            "dimensionar_sistema_esgoto",
            "exportar_csv",
            "gerar_relatorio_memorial",
            "gerar_painel_svg",
        ]
        for s in simbolos_esperados:
            self.assertTrue(hasattr(esgoto_sanitario_nbr8160, s), f"Símbolo {s} não exportado no pacote.")


if __name__ == "__main__":
    unittest.main()

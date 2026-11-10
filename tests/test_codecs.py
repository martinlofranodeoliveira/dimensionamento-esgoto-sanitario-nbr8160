from __future__ import annotations

import json
import os
import tempfile
import unittest
from fractions import Fraction

from esgoto_sanitario_nbr8160.codecs import (
    serializar_fracao,
    deserializar_fracao,
    converter_para_dict,
    verificar_profundidade,
    carregar_json_canonico,
    salvar_json_canonico,
    deserializar_projeto,
)
from esgoto_sanitario_nbr8160.models import (
    AparelhoSanitario,
    RamalDescarga,
    RamalEsgoto,
    ProjetoEsgoto,
)


class TestCodecs(unittest.TestCase):
    def test_fracao_serializacao_deserializacao(self) -> None:
        f = Fraction(3, 4)
        d = serializar_fracao(f)
        self.assertEqual(d, {"num": 3, "den": 4})
        self.assertEqual(deserializar_fracao(d), f)
        self.assertEqual(deserializar_fracao(5), Fraction(5, 1))
        self.assertEqual(deserializar_fracao("3/2"), Fraction(3, 2))

    def test_rejeicao_float_no_json(self) -> None:
        json_invalido = '{"uhc": 3.14}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_invalido)
        self.assertIn("Ponto flutuante IEEE-754", str(ctx.exception))

    def test_rejeicao_chaves_duplicadas(self) -> None:
        json_duplicado = '{"identificacao": "A", "identificacao": "B"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_duplicado)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeicao_bom(self) -> None:
        com_bom = "\ufeff" + '{"identificacao": "Projeto"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(com_bom)
        self.assertIn("BOM UTF-8", str(ctx.exception))

    def test_limite_profundidade(self) -> None:
        profundo: dict = {}
        atual = profundo
        for _ in range(35):
            atual["filho"] = {}
            atual = atual["filho"]

        with self.assertRaises(ValueError) as ctx:
            verificar_profundidade(profundo, 1, 32)
        self.assertIn("Profundidade máxima", str(ctx.exception))

    def test_salvar_e_carregar_arquivo_canonico(self) -> None:
        dados = {
            "projeto": "Residencial",
            "uhc": {"num": 10, "den": 1},
            "aparelhos": ["bacia", "lavatorio"],
        }
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            salvar_json_canonico(tmp_path, dados)
            carregado = carregar_json_canonico(tmp_path)
            self.assertEqual(carregado["projeto"], "Residencial")
            self.assertEqual(carregado["uhc"]["num"], 10)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_deserializar_projeto_completo(self) -> None:
        dados_dict = {
            "identificacao": "Edifício Alfa",
            "ramais_descarga": [
                {
                    "identificacao": "RD-01",
                    "aparelho": {
                        "identificacao": "Lavatório",
                        "tipo_aparelho": "lavatorio_residencial",
                        "quantidade": 1,
                    },
                    "dn_adotado_mm": 40,
                }
            ],
            "ramais_esgoto": [
                {
                    "identificacao": "RE-01",
                    "aparelhos": [
                        {
                            "identificacao": "Lavatório",
                            "tipo_aparelho": "lavatorio_residencial",
                            "quantidade": 1,
                        }
                    ],
                    "dn_adotado_mm": 40,
                    "declividade_m_m": {"num": 2, "den": 100},
                    "comprimento_m": {"num": 3, "den": 1},
                }
            ],
        }
        proj = deserializar_projeto(dados_dict)
        self.assertEqual(proj.identificacao, "Edifício Alfa")
        self.assertEqual(len(proj.ramais_descarga), 1)
        self.assertEqual(len(proj.ramais_esgoto), 1)
        self.assertEqual(proj.ramais_esgoto[0].declividade_m_m, Fraction(2, 100))


if __name__ == "__main__":
    unittest.main()

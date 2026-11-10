from __future__ import annotations

"""Pacote de dimensionamento hidráulico e sanitário de sistemas prediais de esgoto e ventilação segundo a ABNT NBR 8160:1999.

Desenvolvido por LOFRANO TECNOLOGIA.
Aritmética 100% exata (Zero Float) com Frações e inteiros.
"""

__version__ = "1.0.0"
__author__ = "Martin Lofrano de Oliveira / LOFRANO TECNOLOGIA"
__license__ = "MIT"

from esgoto_sanitario_nbr8160.constants import (
    TABELA_APARELHOS_SANITARIOS_NBR8160,
    TABELA_RAMAIS_ESGOTO_NBR8160,
    TABELA_TUBOS_QUEDA_NBR8160,
    TABELA_COLETOR_PREDIAL_NBR8160,
    TABELA_COLUNA_VENTILACAO_NBR8160,
    DISTANCIA_MAXIMA_VENTILACAO_NBR8160,
    DECLIVIDADE_MINIMA_DN_ATE_75,
    DECLIVIDADE_MINIMA_DN_A_PARTIR_100,
    FECHO_HIDRICO_MINIMO_MM,
)
from esgoto_sanitario_nbr8160.models import (
    AparelhoSanitario,
    RamalDescarga,
    RamalEsgoto,
    TuboQueda,
    ColetorPredial,
    ColunaVentilacao,
    CaixaGordura,
    CaixaInspecao,
    CaixaSifonada,
    ProjetoEsgoto,
    ResultadoRamalDescarga,
    ResultadoRamalEsgoto,
    ResultadoTuboQueda,
    ResultadoColetorPredial,
    ResultadoColunaVentilacao,
    ResultadoCaixaGordura,
    ResultadoCaixaInspecao,
    ResultadoProjetoEsgoto,
)
from esgoto_sanitario_nbr8160.calculator import (
    dimensionar_ramal_descarga,
    dimensionar_ramal_esgoto,
    dimensionar_tubo_queda,
    dimensionar_coletor_predial,
    dimensionar_coluna_ventilacao,
    verificar_caixa_gordura,
    verificar_caixa_inspecao,
    dimensionar_sistema_esgoto,
)
from esgoto_sanitario_nbr8160.exporters import (
    exportar_csv,
    gerar_relatorio_memorial,
    formatar_fracao_decimal,
)
from esgoto_sanitario_nbr8160.svg_generator import gerar_painel_svg

__all__ = [
    "__version__",
    "TABELA_APARELHOS_SANITARIOS_NBR8160",
    "TABELA_RAMAIS_ESGOTO_NBR8160",
    "TABELA_TUBOS_QUEDA_NBR8160",
    "TABELA_COLETOR_PREDIAL_NBR8160",
    "TABELA_COLUNA_VENTILACAO_NBR8160",
    "DISTANCIA_MAXIMA_VENTILACAO_NBR8160",
    "DECLIVIDADE_MINIMA_DN_ATE_75",
    "DECLIVIDADE_MINIMA_DN_A_PARTIR_100",
    "FECHO_HIDRICO_MINIMO_MM",
    "AparelhoSanitario",
    "RamalDescarga",
    "RamalEsgoto",
    "TuboQueda",
    "ColetorPredial",
    "ColunaVentilacao",
    "CaixaGordura",
    "CaixaInspecao",
    "CaixaSifonada",
    "ProjetoEsgoto",
    "ResultadoRamalDescarga",
    "ResultadoRamalEsgoto",
    "ResultadoTuboQueda",
    "ResultadoColetorPredial",
    "ResultadoColunaVentilacao",
    "ResultadoCaixaGordura",
    "ResultadoCaixaInspecao",
    "ResultadoProjetoEsgoto",
    "dimensionar_ramal_descarga",
    "dimensionar_ramal_esgoto",
    "dimensionar_tubo_queda",
    "dimensionar_coletor_predial",
    "dimensionar_coluna_ventilacao",
    "verificar_caixa_gordura",
    "verificar_caixa_inspecao",
    "dimensionar_sistema_esgoto",
    "exportar_csv",
    "gerar_relatorio_memorial",
    "formatar_fracao_decimal",
    "gerar_painel_svg",
]

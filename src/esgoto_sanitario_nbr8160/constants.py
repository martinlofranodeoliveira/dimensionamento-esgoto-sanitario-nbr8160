from __future__ import annotations

from fractions import Fraction
from typing import Dict, Any, List, Tuple

# Declividades mínimas normativas (ABNT NBR 8160:1999 item 4.2.3)
DECLIVIDADE_MINIMA_DN_ATE_75 = Fraction(2, 100)        # 2,0% para tubos de DN <= 75 mm
DECLIVIDADE_MINIMA_DN_A_PARTIR_100 = Fraction(1, 100)  # 1,0% para tubos de DN >= 100 mm

# Fecho hídrico mínimo para desconectores e caixas sifonadas (NBR 8160 item 4.1.4)
FECHO_HIDRICO_MINIMO_MM = 50  # 50 mm

# Diâmetro mínimo do Coletor Predial (NBR 8160 item 4.2.4.2)
DN_MINIMO_COLETOR_PREDIAL = 100  # DN 100 mm

# Tabela 1 e Tabela 2 da ABNT NBR 8160:1999
# Unidades de Hunter de Contribuição (UHC) e Diâmetro Nominal Mínimo dos Ramais de Descarga
TABELA_APARELHOS_SANITARIOS_NBR8160: Dict[str, Dict[str, Any]] = {
    "bacia_sanitaria_caixa": {
        "nome": "Bacia sanitária com caixa acoplada",
        "uhc": Fraction(6, 1),
        "dn_minimo": 100,
        "tipo_efluente": "fecal",
    },
    "bacia_sanitaria_valvula": {
        "nome": "Bacia sanitária com válvula de descarga",
        "uhc": Fraction(32, 1),
        "dn_minimo": 100,
        "tipo_efluente": "fecal",
    },
    "banheira_residencial": {
        "nome": "Banheira residencial",
        "uhc": Fraction(2, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "bebedouro": {
        "nome": "Bebedouro",
        "uhc": Fraction(1, 2), # 0,5 UHC
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "bide": {
        "nome": "Bidê",
        "uhc": Fraction(1, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "chuveiro_residencial": {
        "nome": "Chuveiro residencial",
        "uhc": Fraction(2, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "chuveiro_coletivo": {
        "nome": "Chuveiro coletivo",
        "uhc": Fraction(4, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "lavatorio_residencial": {
        "nome": "Lavatório residencial",
        "uhc": Fraction(1, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "lavatorio_coletivo": {
        "nome": "Lavatório coletivo",
        "uhc": Fraction(2, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "maquina_lavar_louca": {
        "nome": "Máquina de lavar louça residencial",
        "uhc": Fraction(2, 1),
        "dn_minimo": 50,
        "tipo_efluente": "gorduroso",
    },
    "maquina_lavar_roupa": {
        "nome": "Máquina de lavar roupa residencial",
        "uhc": Fraction(3, 1),
        "dn_minimo": 50,
        "tipo_efluente": "secundario",
    },
    "mictorio_descarga_auto": {
        "nome": "Mictório com descarga contínua ou automática",
        "uhc": Fraction(2, 1),
        "dn_minimo": 50,
        "tipo_efluente": "primario",
    },
    "mictorio_valvula": {
        "nome": "Mictório com válvula de descarga",
        "uhc": Fraction(6, 1),
        "dn_minimo": 50,
        "tipo_efluente": "primario",
    },
    "pia_cozinha_residencial": {
        "nome": "Pia de cozinha residencial",
        "uhc": Fraction(3, 1),
        "dn_minimo": 50,
        "tipo_efluente": "gorduroso",
    },
    "pia_cozinha_triturador": {
        "nome": "Pia de cozinha com triturador de lixo",
        "uhc": Fraction(4, 1),
        "dn_minimo": 50,
        "tipo_efluente": "gorduroso",
    },
    "tanque_lavar_roupa": {
        "nome": "Tanque de lavar roupas",
        "uhc": Fraction(3, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "ralo_seco": {
        "nome": "Ralo seco",
        "uhc": Fraction(1, 1),
        "dn_minimo": 40,
        "tipo_efluente": "secundario",
    },
    "ralo_sifonado": {
        "nome": "Ralo sifonado",
        "uhc": Fraction(2, 1),
        "dn_minimo": 50,
        "tipo_efluente": "secundario",
    },
}

# Tabela 3 da ABNT NBR 8160:1999
# Dimensionamento de Ramais de Esgoto (Horizontais)
# (limite_maximo_uhc, dn_minimo)
TABELA_RAMAIS_ESGOTO_NBR8160: List[Tuple[int, int]] = [
    (3, 40),
    (6, 50),
    (22, 75),
    (160, 100),
]

# Tabela 4 da ABNT NBR 8160:1999
# Dimensionamento de Tubos de Queda (TQ - Verticais)
TABELA_TUBOS_QUEDA_NBR8160: Dict[int, Dict[str, int]] = {
    50: {
        "ate_3_pav": 10,
        "mais_3_pav": 24,
        "max_por_pav": 6,
    },
    75: {
        "ate_3_pav": 30,
        "mais_3_pav": 60,
        "max_por_pav": 16,
    },
    100: {
        "ate_3_pav": 240,
        "mais_3_pav": 500,
        "max_por_pav": 90,
    },
    150: {
        "ate_3_pav": 960,
        "mais_3_pav": 2000,
        "max_por_pav": 350,
    },
}

# Tabela 6 da ABNT NBR 8160:1999
# Dimensionamento de Subcoletores e Coletor Predial
# Capacidade máxima de UHC em função do DN e da declividade
TABELA_COLETOR_PREDIAL_NBR8160: Dict[int, Dict[Fraction, int]] = {
    100: {
        Fraction(5, 1000): 135,   # 0,5%
        Fraction(1, 100): 180,    # 1,0%
        Fraction(15, 1000): 216,  # 1,5%
        Fraction(2, 100): 250,    # 2,0%
        Fraction(4, 100): 350,    # 4,0%
    },
    150: {
        Fraction(5, 1000): 700,
        Fraction(1, 100): 1000,
        Fraction(15, 1000): 1250,
        Fraction(2, 100): 1500,
        Fraction(4, 100): 2100,
    },
    200: {
        Fraction(5, 1000): 1400,
        Fraction(1, 100): 2000,
        Fraction(15, 1000): 2500,
        Fraction(2, 100): 3000,
        Fraction(4, 100): 4200,
    },
    250: {
        Fraction(5, 1000): 2500,
        Fraction(1, 100): 3600,
        Fraction(15, 1000): 4500,
        Fraction(2, 100): 5400,
        Fraction(4, 100): 7600,
    },
    300: {
        Fraction(5, 1000): 3900,
        Fraction(1, 100): 5600,
        Fraction(15, 1000): 7000,
        Fraction(2, 100): 8400,
        Fraction(4, 100): 12000,
    },
}

# Distância máxima (em metros) do desconector ao tubo de ventilação (NBR 8160 Tabela 7)
DISTANCIA_MAXIMA_VENTILACAO_NBR8160: Dict[int, Fraction] = {
    40: Fraction(10, 10),  # 1,00 m
    50: Fraction(12, 10),  # 1,20 m
    75: Fraction(18, 10),  # 1,80 m
    100: Fraction(24, 10), # 2,40 m
}

# Tabela 5 da ABNT NBR 8160:1999
# Dimensionamento de Colunas de Ventilação (DN mínimo em mm por DN do TQ e UHC)
TABELA_COLUNA_VENTILACAO_NBR8160: Dict[int, List[Tuple[int, int]]] = {
    50: [
        (12, 50),
        (24, 50),
    ],
    75: [
        (21, 50),
        (60, 75),
    ],
    100: [
        (43, 50),
        (140, 75),
        (500, 100),
    ],
    150: [
        (320, 75),
        (2000, 100),
    ],
}

# Caixas de inspeção e limpeza (NBR 8160 item 4.2.5.2)
DISTANCIA_MAXIMA_INSPECAO_M: Fraction = Fraction(25, 1)  # 25,00 m
DIMENSAO_MINIMA_INSPECAO_MM: int = 600                  # 600x600 mm


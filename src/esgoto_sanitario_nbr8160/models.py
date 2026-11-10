from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class AparelhoSanitario:
    """Aparelho sanitário com contribuição de esgoto segundo a NBR 8160."""
    identificacao: str
    tipo_aparelho: str
    quantidade: int = 1

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("Quantidade de aparelhos deve ser estritamente positiva.")


@dataclass(frozen=True)
class RamalDescarga:
    """Tubulação que recebe diretamente os efluentes de um aparelho sanitário."""
    identificacao: str
    aparelho: AparelhoSanitario
    dn_adotado_mm: Optional[int] = None


@dataclass(frozen=True)
class RamalEsgoto:
    """Tubulação horizontal que recebe efluentes de ramais de descarga ou caixas sifonadas."""
    identificacao: str
    aparelhos: List[AparelhoSanitario] = field(default_factory=list)
    dn_adotado_mm: Optional[int] = None
    declividade_m_m: Fraction = Fraction(2, 100)  # Padrão 2,0%
    comprimento_m: Fraction = Fraction(3, 1)
    recebe_bacia: bool = False
    recebe_gordura: bool = False

    def __post_init__(self) -> None:
        if self.declividade_m_m <= 0:
            raise ValueError("Declividade do ramal deve ser estritamente positiva.")
        if self.comprimento_m <= 0:
            raise ValueError("Comprimento do ramal deve ser positivo.")


@dataclass(frozen=True)
class TuboQueda:
    """Tubulação vertical (prumada) que recebe efluentes de ramais de esgoto de um ou mais pavimentos."""
    identificacao: str
    ramais_contribuintes: List[RamalEsgoto] = field(default_factory=list)
    numero_pavimentos: int = 1
    dn_adotado_mm: Optional[int] = None
    altura_m: Fraction = Fraction(3, 1)

    def __post_init__(self) -> None:
        if self.numero_pavimentos <= 0:
            raise ValueError("Número de pavimentos deve ser maior ou igual a 1.")
        if self.altura_m <= 0:
            raise ValueError("Altura do tubo de queda deve ser positiva.")


@dataclass(frozen=True)
class ColunaVentilacao:
    """Coluna vertical de ventilação secundária que prolonga a ventilação do sistema de esgoto."""
    identificacao: str
    tubo_queda_associado: str
    dn_adotado_mm: Optional[int] = None
    comprimento_m: Fraction = Fraction(10, 1)

    def __post_init__(self) -> None:
        if self.comprimento_m <= 0:
            raise ValueError("Comprimento da coluna de ventilação deve ser positivo.")


@dataclass(frozen=True)
class ColetorPredial:
    """Trecho de tubulação horizontal no térreo/subsolo que conduz o esgoto até a rede pública ou fossa."""
    identificacao: str
    tubos_queda_contribuintes: List[str] = field(default_factory=list)
    uhc_adicional_direta: Fraction = Fraction(0, 1)
    dn_adotado_mm: Optional[int] = None
    declividade_m_m: Fraction = Fraction(1, 100)  # Padrão 1,0%
    comprimento_m: Fraction = Fraction(15, 1)

    def __post_init__(self) -> None:
        if self.declividade_m_m <= 0:
            raise ValueError("Declividade do coletor predial deve ser positiva.")
        if self.comprimento_m <= 0:
            raise ValueError("Comprimento do coletor predial deve ser positivo.")


@dataclass(frozen=True)
class CaixaGordura:
    """Dispositivo para retenção de gorduras provenientes de pias de cozinha."""
    identificacao: str
    tipo: str = "simples"  # "pequena", "simples", "dupla", "especial"
    numero_cozinhas: int = 1
    numero_refeicoes: int = 0
    diametro_mm: int = 300
    volume_retencao_L: Fraction = Fraction(18, 1)


@dataclass(frozen=True)
class CaixaInspecao:
    """Caixa de inspeção e limpeza para mudanças de direção e trechos longos."""
    identificacao: str
    largura_mm: int = 600
    comprimento_mm: int = 600
    profundidade_m: Fraction = Fraction(8, 10)  # 0,80 m
    distancia_montante_m: Fraction = Fraction(12, 1)


@dataclass(frozen=True)
class CaixaSifonada:
    """Caixa com desconector e fecho hídrico para coleta de águas secundárias."""
    identificacao: str
    fecho_hidrico_mm: int = 50
    dn_saida_mm: int = 50
    numero_entradas: int = 3


@dataclass(frozen=True)
class ProjetoEsgoto:
    """Entrada completa para dimensionamento de sistema predial de esgoto sanitário."""
    identificacao: str
    ramais_descarga: List[RamalDescarga] = field(default_factory=list)
    ramais_esgoto: List[RamalEsgoto] = field(default_factory=list)
    tubos_queda: List[TuboQueda] = field(default_factory=list)
    coluna_ventilacao: Optional[ColunaVentilacao] = None
    coletor_predial: Optional[ColetorPredial] = None
    caixa_gordura: Optional[CaixaGordura] = None
    caixas_inspecao: List[CaixaInspecao] = field(default_factory=list)
    caixa_sifonada: Optional[CaixaSifonada] = None


@dataclass(frozen=True)
class ResultadoRamalDescarga:
    """Resultado do dimensionamento do ramal de descarga."""
    identificacao: str
    aparelho: str
    uhc_unitaria: Fraction
    uhc_total: Fraction
    dn_minimo_norma: int
    dn_adotado: int
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoRamalEsgoto:
    """Resultado do dimensionamento do ramal de esgoto."""
    identificacao: str
    total_uhc: Fraction
    dn_calculado: int
    dn_adotado: int
    declividade_m_m: Fraction
    declividade_minima_norma: Fraction
    atende_diametro: bool
    atende_declividade: bool
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoTuboQueda:
    """Resultado do dimensionamento do tubo de queda."""
    identificacao: str
    total_uhc: Fraction
    numero_pavimentos: int
    dn_calculado: int
    dn_adotado: int
    capacidade_uhc_admissivel: int
    taxa_ocupacao_uhc: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoColunaVentilacao:
    """Resultado do dimensionamento da coluna de ventilação."""
    identificacao: str
    tubo_queda_associado: str
    uhc_ventilada: Fraction
    dn_calculado: int
    dn_adotado: int
    comprimento_m: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoColetorPredial:
    """Resultado do dimensionamento do coletor predial."""
    identificacao: str
    total_uhc: Fraction
    dn_calculado: int
    dn_adotado: int
    declividade_m_m: Fraction
    capacidade_uhc_tabela: int
    taxa_ocupacao_uhc: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoCaixaGordura:
    """Resultado de verificação da caixa de gordura."""
    identificacao: str
    tipo: str
    volume_retencao_calculado_L: Fraction
    volume_retencao_adotado_L: Fraction
    diametro_adotado_mm: int
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoCaixaInspecao:
    """Resultado de verificação da caixa de inspeção."""
    identificacao: str
    largura_mm: int
    comprimento_mm: int
    distancia_montante_m: Fraction
    distancia_maxima_norma_m: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoProjetoEsgoto:
    """Resultado consolidado do dimensionamento predial de esgoto e ventilação."""
    identificacao: str
    norma: str
    total_uhc_geral: Fraction
    resultados_ramais_descarga: List[ResultadoRamalDescarga]
    resultados_ramais_esgoto: List[ResultadoRamalEsgoto]
    resultados_tubos_queda: List[ResultadoTuboQueda]
    resultado_coluna_ventilacao: Optional[ResultadoColunaVentilacao]
    resultado_coletor_predial: Optional[ResultadoColetorPredial]
    resultado_caixa_gordura: Optional[ResultadoCaixaGordura]
    resultados_caixas_inspecao: List[ResultadoCaixaInspecao]
    atende_geral: bool
    conformidades: Dict[str, bool]
    alertas: List[str]
    recomendacoes: List[str]

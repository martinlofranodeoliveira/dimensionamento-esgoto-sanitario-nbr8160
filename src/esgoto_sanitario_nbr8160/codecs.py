from __future__ import annotations

import json
from fractions import Fraction
from typing import Any, Dict, List, Optional

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


def _rejeitar_float(valor: str) -> None:
    raise ValueError(
        f"Ponto flutuante IEEE-754 '{valor}' detectado no JSON. "
        "O padrão LOFRANO TECNOLOGIA exige Zero Float (inteiros ou frações exatas com 'num' e 'den')."
    )


def _par_sem_duplicatas(pares: List[tuple[str, Any]]) -> Dict[str, Any]:
    resultado: Dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada detectada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def serializar_fracao(f: Fraction) -> Dict[str, int]:
    """Serializa uma fração em representação exata canônica."""
    return {"num": f.numerator, "den": f.denominator}


def deserializar_fracao(d: Any) -> Fraction:
    """Deserializa um valor em Fraction sem admitir float."""
    if isinstance(d, Fraction):
        return d
    if isinstance(d, int):
        return Fraction(d, 1)
    if isinstance(d, dict) and "num" in d and "den" in d:
        if not isinstance(d["num"], int) or not isinstance(d["den"], int):
            raise ValueError("Numerador e denominador devem ser inteiros.")
        return Fraction(d["num"], d["den"])
    if isinstance(d, str):
        if "/" in d:
            partes = d.split("/")
            if len(partes) == 2:
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        return Fraction(d)
    raise ValueError(f"Formato inválido para fração: {d}")


def converter_para_dict(obj: Any) -> Any:
    """Converte estruturas de dados e dataclasses em dicionários canônicos sem float."""
    if isinstance(obj, Fraction):
        return serializar_fracao(obj)
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    if isinstance(obj, float):
        raise ValueError(f"Valor float {obj} detectado durante serialização canônica.")
    if isinstance(obj, list):
        return [converter_para_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): converter_para_dict(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}
    if hasattr(obj, "__dataclass_fields__"):
        res: Dict[str, Any] = {}
        for campo in obj.__dataclass_fields__:
            val = getattr(obj, campo)
            res[campo] = converter_para_dict(val)
        return res
    raise TypeError(f"Tipo não serializável para JSON canônico: {type(obj)}")


def verificar_profundidade(obj: Any, nivel_atual: int = 1, max_nivel: int = 32) -> None:
    """Garante que o JSON não exceda o limite de 32 níveis de profundidade."""
    if nivel_atual > max_nivel:
        raise ValueError(f"Profundidade máxima de aninhamento ({max_nivel}) excedida.")
    if isinstance(obj, dict):
        for v in obj.values():
            verificar_profundidade(v, nivel_atual + 1, max_nivel)
    elif isinstance(obj, list):
        for item in obj:
            verificar_profundidade(item, nivel_atual + 1, max_nivel)


def carregar_json_canonico(texto_ou_caminho: str) -> Dict[str, Any]:
    """Carrega dados JSON com garantias estritas: sem BOM, sem floats, sem chaves duplicadas."""
    if "\n" not in texto_ou_caminho and (texto_ou_caminho.endswith(".json") or len(texto_ou_caminho) < 256):
        import os
        if os.path.exists(texto_ou_caminho):
            with open(texto_ou_caminho, "rb") as f:
                bytes_conteudo = f.read()
                if bytes_conteudo.startswith(b"\xef\xbb\xbf"):
                    raise ValueError("BOM UTF-8 não permitido no padrão canônico.")
                texto = bytes_conteudo.decode("utf-8")
        else:
            texto = texto_ou_caminho
    else:
        texto = texto_ou_caminho

    if texto.startswith("\ufeff"):
        raise ValueError("BOM UTF-8 não permitido no padrão canônico.")

    dados = json.loads(
        texto,
        parse_float=_rejeitar_float,
        object_pairs_hook=_par_sem_duplicatas,
    )
    verificar_profundidade(dados, 1, 32)
    return dados


def salvar_json_canonico(caminho: str, dados: Any) -> None:
    """Salva dados em formato JSON canônico formatado e determinístico."""
    dict_puro = converter_para_dict(dados)
    verificar_profundidade(dict_puro, 1, 32)
    texto = json.dumps(
        dict_puro,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
        f.write("\n")


def deserializar_projeto(dados: Dict[str, Any]) -> ProjetoEsgoto:
    """Reconstrói um objeto ProjetoEsgoto a partir de um dicionário deserializado."""
    identificacao = dados.get("identificacao", "Projeto de Esgoto")

    # Ramais de descarga
    ramais_descarga: List[RamalDescarga] = []
    if "ramais_descarga" in dados and isinstance(dados["ramais_descarga"], list):
        for rd in dados["ramais_descarga"]:
            ap = rd["aparelho"]
            aparelho = AparelhoSanitario(
                identificacao=ap.get("identificacao", "Aparelho"),
                tipo_aparelho=ap["tipo_aparelho"],
                quantidade=int(ap.get("quantidade", 1)),
            )
            ramais_descarga.append(
                RamalDescarga(
                    identificacao=rd.get("identificacao", "RD"),
                    aparelho=aparelho,
                    dn_adotado_mm=int(rd["dn_adotado_mm"]) if "dn_adotado_mm" in rd and rd["dn_adotado_mm"] is not None else None,
                )
            )

    # Ramais de esgoto
    ramais_esgoto: List[RamalEsgoto] = []
    if "ramais_esgoto" in dados and isinstance(dados["ramais_esgoto"], list):
        for re in dados["ramais_esgoto"]:
            aps: List[AparelhoSanitario] = []
            if "aparelhos" in re and isinstance(re["aparelhos"], list):
                for ap in re["aparelhos"]:
                    aps.append(
                        AparelhoSanitario(
                            identificacao=ap.get("identificacao", "Aparelho"),
                            tipo_aparelho=ap["tipo_aparelho"],
                            quantidade=int(ap.get("quantidade", 1)),
                        )
                    )
            ramais_esgoto.append(
                RamalEsgoto(
                    identificacao=re.get("identificacao", "RE"),
                    aparelhos=aps,
                    dn_adotado_mm=int(re["dn_adotado_mm"]) if "dn_adotado_mm" in re and re["dn_adotado_mm"] is not None else None,
                    declividade_m_m=deserializar_fracao(re.get("declividade_m_m", {"num": 2, "den": 100})),
                    comprimento_m=deserializar_fracao(re.get("comprimento_m", {"num": 3, "den": 1})),
                    recebe_bacia=bool(re.get("recebe_bacia", False)),
                    recebe_gordura=bool(re.get("recebe_gordura", False)),
                )
            )

    # Tubos de queda
    tubos_queda: List[TuboQueda] = []
    if "tubos_queda" in dados and isinstance(dados["tubos_queda"], list):
        for tq in dados["tubos_queda"]:
            rms: List[RamalEsgoto] = []
            if "ramais_contribuintes" in tq and isinstance(tq["ramais_contribuintes"], list):
                for re in tq["ramais_contribuintes"]:
                    aps_tq: List[AparelhoSanitario] = []
                    if "aparelhos" in re and isinstance(re["aparelhos"], list):
                        for ap in re["aparelhos"]:
                            aps_tq.append(
                                AparelhoSanitario(
                                    identificacao=ap.get("identificacao", "Aparelho"),
                                    tipo_aparelho=ap["tipo_aparelho"],
                                    quantidade=int(ap.get("quantidade", 1)),
                                )
                            )
                    rms.append(
                        RamalEsgoto(
                            identificacao=re.get("identificacao", "RE"),
                            aparelhos=aps_tq,
                            dn_adotado_mm=int(re["dn_adotado_mm"]) if "dn_adotado_mm" in re and re["dn_adotado_mm"] is not None else None,
                            declividade_m_m=deserializar_fracao(re.get("declividade_m_m", {"num": 2, "den": 100})),
                            comprimento_m=deserializar_fracao(re.get("comprimento_m", {"num": 3, "den": 1})),
                            recebe_bacia=bool(re.get("recebe_bacia", False)),
                            recebe_gordura=bool(re.get("recebe_gordura", False)),
                        )
                    )
            tubos_queda.append(
                TuboQueda(
                    identificacao=tq.get("identificacao", "TQ"),
                    ramais_contribuintes=rms,
                    numero_pavimentos=int(tq.get("numero_pavimentos", 1)),
                    dn_adotado_mm=int(tq["dn_adotado_mm"]) if "dn_adotado_mm" in tq and tq["dn_adotado_mm"] is not None else None,
                    altura_m=deserializar_fracao(tq.get("altura_m", {"num": 3, "den": 1})),
                )
            )

    # Coluna de ventilação
    coluna_v: Optional[ColunaVentilacao] = None
    if "coluna_ventilacao" in dados and dados["coluna_ventilacao"] is not None:
        dcv = dados["coluna_ventilacao"]
        coluna_v = ColunaVentilacao(
            identificacao=dcv.get("identificacao", "CV"),
            tubo_queda_associado=dcv.get("tubo_queda_associado", "TQ"),
            dn_adotado_mm=int(dcv["dn_adotado_mm"]) if "dn_adotado_mm" in dcv and dcv["dn_adotado_mm"] is not None else None,
            comprimento_m=deserializar_fracao(dcv.get("comprimento_m", {"num": 10, "den": 1})),
        )

    # Coletor predial
    coletor_p: Optional[ColetorPredial] = None
    if "coletor_predial" in dados and dados["coletor_predial"] is not None:
        dcp = dados["coletor_predial"]
        coletor_p = ColetorPredial(
            identificacao=dcp.get("identificacao", "CP"),
            tubos_queda_contribuintes=list(dcp.get("tubos_queda_contribuintes", [])),
            uhc_adicional_direta=deserializar_fracao(dcp.get("uhc_adicional_direta", {"num": 0, "den": 1})),
            dn_adotado_mm=int(dcp["dn_adotado_mm"]) if "dn_adotado_mm" in dcp and dcp["dn_adotado_mm"] is not None else None,
            declividade_m_m=deserializar_fracao(dcp.get("declividade_m_m", {"num": 1, "den": 100})),
            comprimento_m=deserializar_fracao(dcp.get("comprimento_m", {"num": 15, "den": 1})),
        )

    # Caixa de gordura
    caixa_g: Optional[CaixaGordura] = None
    if "caixa_gordura" in dados and dados["caixa_gordura"] is not None:
        dcg = dados["caixa_gordura"]
        caixa_g = CaixaGordura(
            identificacao=dcg.get("identificacao", "CG"),
            tipo=dcg.get("tipo", "simples"),
            numero_cozinhas=int(dcg.get("numero_cozinhas", 1)),
            numero_refeicoes=int(dcg.get("numero_refeicoes", 0)),
            diametro_mm=int(dcg.get("diametro_mm", 300)),
            volume_retencao_L=deserializar_fracao(dcg.get("volume_retencao_L", {"num": 18, "den": 1})),
        )

    # Caixas de inspeção
    caixas_inspecao: List[CaixaInspecao] = []
    if "caixas_inspecao" in dados and isinstance(dados["caixas_inspecao"], list):
        for ci in dados["caixas_inspecao"]:
            caixas_inspecao.append(
                CaixaInspecao(
                    identificacao=ci.get("identificacao", "CI"),
                    largura_mm=int(ci.get("largura_mm", 600)),
                    comprimento_mm=int(ci.get("comprimento_mm", 600)),
                    profundidade_m=deserializar_fracao(ci.get("profundidade_m", {"num": 8, "den": 10})),
                    distancia_montante_m=deserializar_fracao(ci.get("distancia_montante_m", {"num": 12, "den": 1})),
                )
            )

    # Caixa sifonada
    caixa_s: Optional[CaixaSifonada] = None
    if "caixa_sifonada" in dados and dados["caixa_sifonada"] is not None:
        dcs = dados["caixa_sifonada"]
        caixa_s = CaixaSifonada(
            identificacao=dcs.get("identificacao", "CS"),
            fecho_hidrico_mm=int(dcs.get("fecho_hidrico_mm", 50)),
            dn_saida_mm=int(dcs.get("dn_saida_mm", 50)),
            numero_entradas=int(dcs.get("numero_entradas", 3)),
        )

    return ProjetoEsgoto(
        identificacao=identificacao,
        ramais_descarga=ramais_descarga,
        ramais_esgoto=ramais_esgoto,
        tubos_queda=tubos_queda,
        coluna_ventilacao=coluna_v,
        coletor_predial=coletor_p,
        caixa_gordura=caixa_g,
        caixas_inspecao=caixas_inspecao,
        caixa_sifonada=caixa_s,
    )

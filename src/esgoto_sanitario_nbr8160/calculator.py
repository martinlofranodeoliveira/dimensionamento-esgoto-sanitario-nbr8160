from __future__ import annotations

from fractions import Fraction
from typing import Optional, List, Dict, Tuple, Any

from esgoto_sanitario_nbr8160.constants import (
    TABELA_APARELHOS_SANITARIOS_NBR8160,
    TABELA_RAMAIS_ESGOTO_NBR8160,
    TABELA_TUBOS_QUEDA_NBR8160,
    TABELA_COLETOR_PREDIAL_NBR8160,
    TABELA_COLUNA_VENTILACAO_NBR8160,
    DISTANCIA_MAXIMA_VENTILACAO_NBR8160,
    DECLIVIDADE_MINIMA_DN_ATE_75,
    DECLIVIDADE_MINIMA_DN_A_PARTIR_100,
    DN_MINIMO_COLETOR_PREDIAL,
    FECHO_HIDRICO_MINIMO_MM,
)
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


def obter_info_aparelho(tipo_aparelho: str) -> Dict[str, Any]:
    """Recupera dados normativos de um aparelho sanitário cadastrado."""
    chave = tipo_aparelho.strip().lower()
    if chave not in TABELA_APARELHOS_SANITARIOS_NBR8160:
        raise KeyError(
            f"Aparelho sanitário '{tipo_aparelho}' não cadastrado. "
            f"Opções disponíveis: {', '.join(sorted(TABELA_APARELHOS_SANITARIOS_NBR8160.keys()))}"
        )
    return TABELA_APARELHOS_SANITARIOS_NBR8160[chave]


def dimensionar_ramal_descarga(ramal: RamalDescarga) -> ResultadoRamalDescarga:
    """Dimensiona e verifica o ramal de descarga de um aparelho sanitário segundo Tabela 1 e 2 da NBR 8160."""
    info = obter_info_aparelho(ramal.aparelho.tipo_aparelho)
    uhc_unitaria = info["uhc"]
    uhc_total = uhc_unitaria * Fraction(ramal.aparelho.quantidade, 1)
    dn_minimo = info["dn_minimo"]

    dn_adotado = ramal.dn_adotado_mm if ramal.dn_adotado_mm is not None else dn_minimo
    atende_norma = dn_adotado >= dn_minimo

    obs: List[str] = []
    if not atende_norma:
        obs.append(
            f"Diâmetro adotado (DN {dn_adotado}) inferior ao mínimo normativo (DN {dn_minimo}) para {info['nome']}."
        )
    else:
        obs.append(
            f"Ramal de descarga DN {dn_adotado} atende à NBR 8160 ({uhc_total} UHC)."
        )

    return ResultadoRamalDescarga(
        identificacao=ramal.identificacao,
        aparelho=info["nome"],
        uhc_unitaria=uhc_unitaria,
        uhc_total=uhc_total,
        dn_minimo_norma=dn_minimo,
        dn_adotado=dn_adotado,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_ramal_esgoto(
    ramal: RamalEsgoto, carga_uhc_direta: Optional[Fraction] = None
) -> ResultadoRamalEsgoto:
    """Dimensiona e verifica ramal de esgoto horizontal por soma de UHC e declividade (Tabela 3 NBR 8160)."""
    total_uhc = Fraction(0, 1) if carga_uhc_direta is None else carga_uhc_direta
    tem_bacia = ramal.recebe_bacia
    tem_gordura = ramal.recebe_gordura
    maior_dn_descarga = 40

    if carga_uhc_direta is None:
        for ap in ramal.aparelhos:
            info = obter_info_aparelho(ap.tipo_aparelho)
            total_uhc += info["uhc"] * Fraction(ap.quantidade, 1)
            if "bacia" in ap.tipo_aparelho:
                tem_bacia = True
            if "pia" in ap.tipo_aparelho or "maquina_lavar_louca" in ap.tipo_aparelho:
                tem_gordura = True
            if info["dn_minimo"] > maior_dn_descarga:
                maior_dn_descarga = info["dn_minimo"]

    # Determinação do DN mínimo por UHC
    dn_calculado = 100
    for limite_uhc, dn in TABELA_RAMAIS_ESGOTO_NBR8160:
        if total_uhc <= limite_uhc:
            dn_calculado = dn
            break

    # Regras normativas especiais
    if tem_bacia and dn_calculado < 100:
        dn_calculado = 100
    if tem_gordura and dn_calculado < 50:
        dn_calculado = 50
    if dn_calculado < maior_dn_descarga:
        dn_calculado = maior_dn_descarga

    dn_adotado = ramal.dn_adotado_mm if ramal.dn_adotado_mm is not None else dn_calculado

    # Declividade mínima normativa
    if dn_adotado <= 75:
        declividade_minima = DECLIVIDADE_MINIMA_DN_ATE_75  # 2,0%
    else:
        declividade_minima = DECLIVIDADE_MINIMA_DN_A_PARTIR_100  # 1,0%

    atende_diametro = dn_adotado >= dn_calculado
    atende_declividade = ramal.declividade_m_m >= declividade_minima
    atende_norma = atende_diametro and atende_declividade

    obs: List[str] = []
    if not atende_diametro:
        obs.append(
            f"Diâmetro adotado (DN {dn_adotado}) inferior ao mínimo exigido (DN {dn_calculado}) para {float(total_uhc):.1f} UHC."
        )
    if not atende_declividade:
        obs.append(
            f"Declividade adotada ({float(ramal.declividade_m_m * 100):.2f}%) inferior ao mínimo normativo de {float(declividade_minima * 100):.2f}% (NBR 8160 item 4.2.3)."
        )
    if tem_bacia:
        obs.append("Ramal recebe efluente de bacia sanitária (DN mínimo 100 obrigatório).")
    if tem_gordura:
        obs.append("Ramal recebe efluente de cozinha/gordura (deve ser direcionado à caixa de gordura).")
    if atende_norma:
        obs.append(
            f"Ramal de esgoto DN {dn_adotado} atende à NBR 8160 com declividade de {float(ramal.declividade_m_m * 100):.2f}%."
        )

    return ResultadoRamalEsgoto(
        identificacao=ramal.identificacao,
        total_uhc=total_uhc,
        dn_calculado=dn_calculado,
        dn_adotado=dn_adotado,
        declividade_m_m=ramal.declividade_m_m,
        declividade_minima_norma=declividade_minima,
        atende_diametro=atende_diametro,
        atende_declividade=atende_declividade,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_tubo_queda(
    tubo_queda: TuboQueda, carga_uhc_direta: Optional[Fraction] = None
) -> ResultadoTuboQueda:
    """Dimensiona e verifica tubo de queda vertical segundo Tabela 4 da NBR 8160."""
    total_uhc = Fraction(0, 1) if carga_uhc_direta is None else carga_uhc_direta
    maior_dn_ramal = 40
    tem_bacia = False

    if carga_uhc_direta is None:
        for ramal in tubo_queda.ramais_contribuintes:
            res_r = dimensionar_ramal_esgoto(ramal)
            total_uhc += res_r.total_uhc
            if res_r.dn_adotado > maior_dn_ramal:
                maior_dn_ramal = res_r.dn_adotado
            if ramal.recebe_bacia or any("bacia" in ap.tipo_aparelho for ap in ramal.aparelhos):
                tem_bacia = True

    chave_predio = "ate_3_pav" if tubo_queda.numero_pavimentos <= 3 else "mais_3_pav"

    # Selecionar DN na Tabela 4
    dn_calculado = 150
    capacidade_tabela = 2000
    for dn in sorted(TABELA_TUBOS_QUEDA_NBR8160.keys()):
        cap = TABELA_TUBOS_QUEDA_NBR8160[dn][chave_predio]
        if total_uhc <= cap:
            dn_calculado = dn
            capacidade_tabela = cap
            break

    # Regras normativas
    if tem_bacia and dn_calculado < 100:
        dn_calculado = 100
        capacidade_tabela = TABELA_TUBOS_QUEDA_NBR8160[100][chave_predio]
    if dn_calculado < maior_dn_ramal:
        dn_calculado = maior_dn_ramal
        if dn_calculado in TABELA_TUBOS_QUEDA_NBR8160:
            capacidade_tabela = TABELA_TUBOS_QUEDA_NBR8160[dn_calculado][chave_predio]

    dn_adotado = tubo_queda.dn_adotado_mm if tubo_queda.dn_adotado_mm is not None else dn_calculado
    if dn_adotado in TABELA_TUBOS_QUEDA_NBR8160:
        capacidade_adotada = TABELA_TUBOS_QUEDA_NBR8160[dn_adotado][chave_predio]
    else:
        capacidade_adotada = capacidade_tabela

    atende_norma = dn_adotado >= dn_calculado and total_uhc <= capacidade_adotada
    taxa_ocupacao = total_uhc / Fraction(capacidade_adotada, 1) if capacidade_adotada > 0 else Fraction(1, 1)

    obs: List[str] = []
    if not atende_norma:
        obs.append(
            f"Tubo de queda DN {dn_adotado} insuficiente para {float(total_uhc):.1f} UHC (Capacidade: {capacidade_adotada} UHC)."
        )
    else:
        obs.append(
            f"Tubo de queda DN {dn_adotado} atende à NBR 8160 ({tubo_queda.numero_pavimentos} pavimentos, ocupação de {float(taxa_ocupacao * 100):.1f}%)."
        )

    return ResultadoTuboQueda(
        identificacao=tubo_queda.identificacao,
        total_uhc=total_uhc,
        numero_pavimentos=tubo_queda.numero_pavimentos,
        dn_calculado=dn_calculado,
        dn_adotado=dn_adotado,
        capacidade_uhc_admissivel=capacidade_adotada,
        taxa_ocupacao_uhc=taxa_ocupacao,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_coluna_ventilacao(
    coluna: ColunaVentilacao, dn_tubo_queda: int, uhc_ventilada: Fraction
) -> ResultadoColunaVentilacao:
    """Dimensiona e verifica a coluna de ventilação secundária segundo Tabela 5 da NBR 8160."""
    tabela_tq = TABELA_COLUNA_VENTILACAO_NBR8160.get(dn_tubo_queda, [(500, 100)])

    dn_calculado = 100
    for limite_uhc, dn_v in tabela_tq:
        if uhc_ventilada <= limite_uhc:
            dn_calculado = dn_v
            break

    dn_adotado = coluna.dn_adotado_mm if coluna.dn_adotado_mm is not None else dn_calculado
    atende_norma = dn_adotado >= dn_calculado

    obs: List[str] = []
    if not atende_norma:
        obs.append(
            f"Coluna de ventilação DN {dn_adotado} inferior ao mínimo exigido (DN {dn_calculado}) para TQ DN {dn_tubo_queda}."
        )
    else:
        obs.append(
            f"Coluna de ventilação DN {dn_adotado} atende à NBR 8160 (comprimento {float(coluna.comprimento_m):.1f} m)."
        )

    return ResultadoColunaVentilacao(
        identificacao=coluna.identificacao,
        tubo_queda_associado=coluna.tubo_queda_associado,
        uhc_ventilada=uhc_ventilada,
        dn_calculado=dn_calculado,
        dn_adotado=dn_adotado,
        comprimento_m=coluna.comprimento_m,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_coletor_predial(
    coletor: ColetorPredial, total_uhc: Fraction
) -> ResultadoColetorPredial:
    """Dimensiona e verifica subcoletor ou coletor predial segundo Tabela 6 da NBR 8160."""
    declividade = coletor.declividade_m_m

    dn_calculado = 300
    capacidade_tabela = 12000

    for dn in sorted(TABELA_COLETOR_PREDIAL_NBR8160.keys()):
        tabela_dn = TABELA_COLETOR_PREDIAL_NBR8160[dn]
        # Pega a capacidade para a declividade mais próxima menor ou igual
        decls = sorted(tabela_dn.keys())
        dec_ref = decls[0]
        for d in decls:
            if declividade >= d:
                dec_ref = d
        cap = tabela_dn[dec_ref]
        if total_uhc <= cap:
            dn_calculado = dn
            capacidade_tabela = cap
            break

    if dn_calculado < DN_MINIMO_COLETOR_PREDIAL:
        dn_calculado = DN_MINIMO_COLETOR_PREDIAL

    dn_adotado = coletor.dn_adotado_mm if coletor.dn_adotado_mm is not None else dn_calculado
    if dn_adotado in TABELA_COLETOR_PREDIAL_NBR8160:
        tabela_dn = TABELA_COLETOR_PREDIAL_NBR8160[dn_adotado]
        decls = sorted(tabela_dn.keys())
        dec_ref = decls[0]
        for d in decls:
            if declividade >= d:
                dec_ref = d
        capacidade_adotada = tabela_dn[dec_ref]
    else:
        capacidade_adotada = capacidade_tabela

    atende_declividade = declividade >= Fraction(5, 1000) # mínimo 0,5%
    atende_diametro = dn_adotado >= dn_calculado and dn_adotado >= DN_MINIMO_COLETOR_PREDIAL
    atende_capacidade = total_uhc <= capacidade_adotada
    atende_norma = atende_declividade and atende_diametro and atende_capacidade

    taxa_ocupacao = total_uhc / Fraction(capacidade_adotada, 1) if capacidade_adotada > 0 else Fraction(1, 1)

    obs: List[str] = []
    if not atende_declividade:
        obs.append(
            f"Declividade ({float(declividade * 100):.2f}%) inferior ao mínimo de 0,50% para coletores prediais."
        )
    if not atende_diametro:
        obs.append(
            f"Diâmetro adotado (DN {dn_adotado}) inferior ao mínimo exigido (DN {dn_calculado})."
        )
    if not atende_capacidade:
        obs.append(
            f"Carga de {float(total_uhc):.1f} UHC excede a capacidade do coletor DN {dn_adotado} ({capacidade_adotada} UHC)."
        )
    if atende_norma:
        obs.append(
            f"Coletor predial DN {dn_adotado} atende à NBR 8160 (i={float(declividade * 100):.2f}%, ocupação de {float(taxa_ocupacao * 100):.1f}%)."
        )

    return ResultadoColetorPredial(
        identificacao=coletor.identificacao,
        total_uhc=total_uhc,
        dn_calculado=dn_calculado,
        dn_adotado=dn_adotado,
        declividade_m_m=declividade,
        capacidade_uhc_tabela=capacidade_adotada,
        taxa_ocupacao_uhc=taxa_ocupacao,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def verificar_caixa_gordura(caixa: CaixaGordura) -> ResultadoCaixaGordura:
    """Verifica dimensionamento da caixa de gordura conforme NBR 8160 item 4.2.5.1."""
    tipo = caixa.tipo.strip().lower()

    if tipo in ("pequena", "simples"):
        vol_min = Fraction(18, 1)
        diam_min = 300
    elif tipo == "dupla":
        vol_min = Fraction(120, 1)
        diam_min = 400
    elif tipo == "especial":
        # V = 2 * N_refeicoes + 20 L
        n_ref = max(caixa.numero_refeicoes, 20)
        vol_min = Fraction(2 * n_ref + 20, 1)
        diam_min = 600
    else:
        vol_min = Fraction(18, 1)
        diam_min = 300

    atende_vol = caixa.volume_retencao_L >= vol_min
    atende_diam = caixa.diametro_mm >= diam_min
    atende_norma = atende_vol and atende_diam

    obs: List[str] = []
    if not atende_vol:
        obs.append(
            f"Volume de retenção ({float(caixa.volume_retencao_L):.1f} L) inferior ao mínimo normativo de {float(vol_min):.1f} L."
        )
    if not atende_diam:
        obs.append(
            f"Diâmetro ({caixa.diametro_mm} mm) inferior ao mínimo de {diam_min} mm para caixa de gordura {tipo}."
        )
    if atende_norma:
        obs.append(
            f"Caixa de gordura tipo {tipo.upper()} (Vol={float(caixa.volume_retencao_L):.1f} L) atende à NBR 8160."
        )

    return ResultadoCaixaGordura(
        identificacao=caixa.identificacao,
        tipo=tipo,
        volume_retencao_calculado_L=vol_min,
        volume_retencao_adotado_L=caixa.volume_retencao_L,
        diametro_adotado_mm=caixa.diametro_mm,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def verificar_caixa_inspecao(caixa: CaixaInspecao) -> ResultadoCaixaInspecao:
    """Verifica dimensionamento e espaçamento da caixa de inspeção conforme NBR 8160 item 4.2.5.2."""
    dist_max = Fraction(25, 1)  # Máximo 25 metros entre caixas

    atende_dist = caixa.distancia_montante_m <= dist_max
    atende_dim = caixa.largura_mm >= 600 and caixa.comprimento_mm >= 600
    atende_norma = atende_dist and atende_dim

    obs: List[str] = []
    if not atende_dist:
        obs.append(
            f"Distância a montante ({float(caixa.distancia_montante_m):.1f} m) excede o limite normativo de 25,0 m (NBR 8160 item 4.2.5.2)."
        )
    if not atende_dim:
        obs.append(
            f"Dimensões em planta ({caixa.largura_mm}x{caixa.comprimento_mm} mm) inferiores ao mínimo de 600x600 mm para profundidade até 1,0 m."
        )
    if atende_norma:
        obs.append(
            f"Caixa de inspeção {caixa.largura_mm}x{caixa.comprimento_mm} mm atende à NBR 8160 (distância {float(caixa.distancia_montante_m):.1f} m)."
        )

    return ResultadoCaixaInspecao(
        identificacao=caixa.identificacao,
        largura_mm=caixa.largura_mm,
        comprimento_mm=caixa.comprimento_mm,
        distancia_montante_m=caixa.distancia_montante_m,
        distancia_maxima_norma_m=dist_max,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_sistema_esgoto(projeto: ProjetoEsgoto) -> ResultadoProjetoEsgoto:
    """Realiza o dimensionamento sanitário e verificação completa de um sistema predial de esgoto."""
    # 1. Ramais de descarga
    res_descarga: List[ResultadoRamalDescarga] = []
    for rd in projeto.ramais_descarga:
        res_descarga.append(dimensionar_ramal_descarga(rd))

    # 2. Ramais de esgoto
    res_esgoto: List[ResultadoRamalEsgoto] = []
    for re in projeto.ramais_esgoto:
        res_esgoto.append(dimensionar_ramal_esgoto(re))

    # 3. Tubos de queda
    res_tq: List[ResultadoTuboQueda] = []
    total_uhc_tqs = Fraction(0, 1)
    for tq in projeto.tubos_queda:
        rtq = dimensionar_tubo_queda(tq)
        res_tq.append(rtq)
        total_uhc_tqs += rtq.total_uhc

    # 4. Coluna de ventilação
    res_cv: Optional[ResultadoColunaVentilacao] = None
    if projeto.coluna_ventilacao is not None:
        # Encontra o TQ associado
        dn_tq_ref = 100
        for rtq in res_tq:
            if rtq.identificacao == projeto.coluna_ventilacao.tubo_queda_associado:
                dn_tq_ref = rtq.dn_adotado
                break
        res_cv = dimensionar_coluna_ventilacao(
            projeto.coluna_ventilacao,
            dn_tubo_queda=dn_tq_ref,
            uhc_ventilada=total_uhc_tqs,
        )

    # 5. Coletor predial
    res_cp: Optional[ResultadoColetorPredial] = None
    total_uhc_geral = total_uhc_tqs
    if projeto.coletor_predial is not None:
        total_uhc_geral += projeto.coletor_predial.uhc_adicional_direta
        res_cp = dimensionar_coletor_predial(projeto.coletor_predial, total_uhc_geral)

    # 6. Caixa de gordura
    res_cg: Optional[ResultadoCaixaGordura] = None
    if projeto.caixa_gordura is not None:
        res_cg = verificar_caixa_gordura(projeto.caixa_gordura)

    # 7. Caixas de inspeção
    res_ci: List[ResultadoCaixaInspecao] = []
    for ci in projeto.caixas_inspecao:
        res_ci.append(verificar_caixa_inspecao(ci))

    # Conformidades e Alertas
    conformidades: Dict[str, bool] = {
        "ramais_descarga": all(r.atende_norma for r in res_descarga) if res_descarga else True,
        "ramais_esgoto": all(r.atende_norma for r in res_esgoto) if res_esgoto else True,
        "tubos_queda": all(r.atende_norma for r in res_tq) if res_tq else True,
    }
    alertas: List[str] = []
    recomendacoes: List[str] = []

    if res_cv is not None:
        conformidades["coluna_ventilacao"] = res_cv.atende_norma
        if not res_cv.atende_norma:
            alertas.extend(res_cv.observacoes)

    if res_cp is not None:
        conformidades["coletor_predial"] = res_cp.atende_norma
        if not res_cp.atende_norma:
            alertas.extend(res_cp.observacoes)

    if res_cg is not None:
        conformidades["caixa_gordura"] = res_cg.atende_norma
        if not res_cg.atende_norma:
            alertas.extend(res_cg.observacoes)

    if res_ci:
        conformidades["caixas_inspecao"] = all(r.atende_norma for r in res_ci)
        for r in res_ci:
            if not r.atende_norma:
                alertas.extend(r.observacoes)

    # Caixa sifonada
    if projeto.caixa_sifonada is not None:
        if projeto.caixa_sifonada.fecho_hidrico_mm >= FECHO_HIDRICO_MINIMO_MM:
            recomendacoes.append(
                f"Caixa sifonada com fecho hídrico de {projeto.caixa_sifonada.fecho_hidrico_mm} mm: barreira perfeita contra gases fétidos."
            )
        else:
            alertas.append(
                f"Caixa sifonada com fecho hídrico ({projeto.caixa_sifonada.fecho_hidrico_mm} mm) inferior ao mínimo normativo de 50 mm."
            )
            conformidades["caixa_sifonada"] = False

    atende_geral = all(conformidades.values())
    if atende_geral and not alertas:
        recomendacoes.append(
            "Sistema predial de esgoto sanitário e ventilação integralmente aprovado segundo os critérios da ABNT NBR 8160:1999."
        )

    return ResultadoProjetoEsgoto(
        identificacao=projeto.identificacao,
        norma="ABNT NBR 8160:1999",
        total_uhc_geral=total_uhc_geral,
        resultados_ramais_descarga=res_descarga,
        resultados_ramais_esgoto=res_esgoto,
        resultados_tubos_queda=res_tq,
        resultado_coluna_ventilacao=res_cv,
        resultado_coletor_predial=res_cp,
        resultado_caixa_gordura=res_cg,
        resultados_caixas_inspecao=res_ci,
        atende_geral=atende_geral,
        conformidades=conformidades,
        alertas=alertas,
        recomendacoes=recomendacoes,
    )

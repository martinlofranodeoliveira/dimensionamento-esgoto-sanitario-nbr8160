from __future__ import annotations

import csv
import io
from fractions import Fraction
from typing import Any, List

from esgoto_sanitario_nbr8160.models import ResultadoProjetoEsgoto

CARACTERES_INJECAO_CSV = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: Any) -> str:
    """Sanitiza campos contra injeção de fórmulas CSV mantendo integridade."""
    texto = str(valor)
    if texto.startswith(CARACTERES_INJECAO_CSV):
        return "'" + texto
    return texto


def formatar_fracao_decimal(f: Fraction, casas: int = 2) -> str:
    """Converte fração em representação decimal exata com vírgula padrão pt-BR."""
    if f.denominator == 1:
        return str(f.numerator)
    fator = 10 ** casas
    val_inteiro = round((f.numerator * fator) / f.denominator)
    sinal = "-" if val_inteiro < 0 else ""
    val_abs = abs(val_inteiro)
    parte_int = val_abs // fator
    parte_dec = str(val_abs % fator).zfill(casas)
    return f"{sinal}{parte_int},{parte_dec}"


def exportar_csv(resultado: ResultadoProjetoEsgoto) -> str:
    """Exporta planilha técnica em formato CSV com proteção contra injeção de fórmulas."""
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # Cabeçalho
    escritor.writerow([
        sanitizar_campo_csv("Tipo de Trecho"),
        sanitizar_campo_csv("Identificação"),
        sanitizar_campo_csv("Carga de Contribuição"),
        sanitizar_campo_csv("DN Calculado / Mínimo"),
        sanitizar_campo_csv("DN Adotado"),
        sanitizar_campo_csv("Declividade / Parâmetro"),
        sanitizar_campo_csv("Capacidade / Limite"),
        sanitizar_campo_csv("Conformidade NBR 8160"),
    ])

    # Ramais de descarga
    for rd in resultado.resultados_ramais_descarga:
        escritor.writerow([
            sanitizar_campo_csv("Ramal de Descarga"),
            sanitizar_campo_csv(rd.identificacao),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rd.uhc_total, 1)} UHC ({rd.aparelho})"),
            sanitizar_campo_csv(f"DN {rd.dn_minimo_norma}"),
            sanitizar_campo_csv(f"DN {rd.dn_adotado}"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("CONFORME" if rd.atende_norma else "NÃO CONFORME"),
        ])

    # Ramais de esgoto
    for re in resultado.resultados_ramais_esgoto:
        escritor.writerow([
            sanitizar_campo_csv("Ramal de Esgoto"),
            sanitizar_campo_csv(re.identificacao),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(re.total_uhc, 1)} UHC"),
            sanitizar_campo_csv(f"DN {re.dn_calculado}"),
            sanitizar_campo_csv(f"DN {re.dn_adotado}"),
            sanitizar_campo_csv(f"i = {formatar_fracao_decimal(re.declividade_m_m * 100, 2)}%"),
            sanitizar_campo_csv(f"Min: {formatar_fracao_decimal(re.declividade_minima_norma * 100, 2)}%"),
            sanitizar_campo_csv("CONFORME" if re.atende_norma else "NÃO CONFORME"),
        ])

    # Tubos de queda
    for tq in resultado.resultados_tubos_queda:
        escritor.writerow([
            sanitizar_campo_csv("Tubo de Queda (TQ)"),
            sanitizar_campo_csv(tq.identificacao),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(tq.total_uhc, 1)} UHC ({tq.numero_pavimentos} pav)"),
            sanitizar_campo_csv(f"DN {tq.dn_calculado}"),
            sanitizar_campo_csv(f"DN {tq.dn_adotado}"),
            sanitizar_campo_csv(f"Ocupação: {formatar_fracao_decimal(tq.taxa_ocupacao_uhc * 100, 1)}%"),
            sanitizar_campo_csv(f"Máx: {tq.capacidade_uhc_admissivel} UHC"),
            sanitizar_campo_csv("CONFORME" if tq.atende_norma else "NÃO CONFORME"),
        ])

    # Coluna de ventilação
    if resultado.resultado_coluna_ventilacao is not None:
        rcv = resultado.resultado_coluna_ventilacao
        escritor.writerow([
            sanitizar_campo_csv("Coluna de Ventilação"),
            sanitizar_campo_csv(rcv.identificacao),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rcv.uhc_ventilada, 1)} UHC ventilada"),
            sanitizar_campo_csv(f"DN {rcv.dn_calculado}"),
            sanitizar_campo_csv(f"DN {rcv.dn_adotado}"),
            sanitizar_campo_csv(f"Comp: {formatar_fracao_decimal(rcv.comprimento_m, 1)} m"),
            sanitizar_campo_csv(f"Assoc: {rcv.tubo_queda_associado}"),
            sanitizar_campo_csv("CONFORME" if rcv.atende_norma else "NÃO CONFORME"),
        ])

    # Coletor predial
    if resultado.resultado_coletor_predial is not None:
        rcp = resultado.resultado_coletor_predial
        escritor.writerow([
            sanitizar_campo_csv("Coletor Predial"),
            sanitizar_campo_csv(rcp.identificacao),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rcp.total_uhc, 1)} UHC"),
            sanitizar_campo_csv(f"DN {rcp.dn_calculado}"),
            sanitizar_campo_csv(f"DN {rcp.dn_adotado}"),
            sanitizar_campo_csv(f"i = {formatar_fracao_decimal(rcp.declividade_m_m * 100, 2)}%"),
            sanitizar_campo_csv(f"Máx: {rcp.capacidade_uhc_tabela} UHC"),
            sanitizar_campo_csv("CONFORME" if rcp.atende_norma else "NÃO CONFORME"),
        ])

    # Caixa de gordura
    if resultado.resultado_caixa_gordura is not None:
        rcg = resultado.resultado_caixa_gordura
        escritor.writerow([
            sanitizar_campo_csv("Caixa de Gordura"),
            sanitizar_campo_csv(rcg.identificacao),
            sanitizar_campo_csv(f"Tipo {rcg.tipo.upper()}"),
            sanitizar_campo_csv(f"D = {rcg.diametro_adotado_mm} mm"),
            sanitizar_campo_csv(f"Vol = {formatar_fracao_decimal(rcg.volume_retencao_adotado_L, 1)} L"),
            sanitizar_campo_csv(f"Min: {formatar_fracao_decimal(rcg.volume_retencao_calculado_L, 1)} L"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("CONFORME" if rcg.atende_norma else "NÃO CONFORME"),
        ])

    # Caixas de inspeção
    for rci in resultado.resultados_caixas_inspecao:
        escritor.writerow([
            sanitizar_campo_csv("Caixa de Inspeção"),
            sanitizar_campo_csv(rci.identificacao),
            sanitizar_campo_csv(f"{rci.largura_mm}x{rci.comprimento_mm} mm"),
            sanitizar_campo_csv("Min 600x600 mm"),
            sanitizar_campo_csv(f"Dist: {formatar_fracao_decimal(rci.distancia_montante_m, 1)} m"),
            sanitizar_campo_csv(f"Máx: {formatar_fracao_decimal(rci.distancia_maxima_norma_m, 1)} m"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("CONFORME" if rci.atende_norma else "NÃO CONFORME"),
        ])

    return saida.getvalue()


def gerar_relatorio_memorial(resultado: ResultadoProjetoEsgoto) -> str:
    """Gera o Memorial de Cálculo Técnico completo em texto puro formatado em pt-BR."""
    linhas: List[str] = []
    div = "=" * 80
    subdiv = "-" * 80

    linhas.append(div)
    linhas.append("       LOFRANO TECNOLOGIA - ENGENHARIA SANITÁRIA E HIDRÁULICA PREDIAL")
    linhas.append("         MEMORIAL DE CÁLCULO NORMATIVO - ABNT NBR 8160:1999 (ESGOTO)")
    linhas.append(div)
    linhas.append(f"Projeto: {resultado.identificacao}")
    linhas.append(f"Norma Regulamentadora: {resultado.norma}")
    linhas.append(f"Carga Total Acumulada: {formatar_fracao_decimal(resultado.total_uhc_geral, 1)} UHC")
    linhas.append(f"Status Geral de Aprovação: {'APROVADO' if resultado.atende_geral else 'COM RESTRIÇÕES / NÃO CONFORME'}")
    linhas.append(subdiv)

    # 1. Ramais de Descarga
    if resultado.resultados_ramais_descarga:
        linhas.append("1. RAMAIS DE DESCARGA (TABELAS 1 E 2 NBR 8160)")
        for rd in resultado.resultados_ramais_descarga:
            linhas.append(
                f"  - [{rd.identificacao}] {rd.aparelho}: {formatar_fracao_decimal(rd.uhc_total, 1)} UHC | "
                f"DN Mínimo: {rd.dn_minimo_norma} mm | DN Adotado: {rd.dn_adotado} mm -> "
                f"{'CONFORME' if rd.atende_norma else 'NÃO CONFORME'}"
            )
        linhas.append("")

    # 2. Ramais de Esgoto
    if resultado.resultados_ramais_esgoto:
        linhas.append("2. RAMAIS DE ESGOTO HORIZONTAIS (TABELA 3 NBR 8160)")
        for re in resultado.resultados_ramais_esgoto:
            linhas.append(
                f"  - [{re.identificacao}] Carga: {formatar_fracao_decimal(re.total_uhc, 1)} UHC | "
                f"DN Calculado: {re.dn_calculado} mm | DN Adotado: {re.dn_adotado} mm | "
                f"Declividade: {formatar_fracao_decimal(re.declividade_m_m * 100, 2)}% (Mínimo: {formatar_fracao_decimal(re.declividade_minima_norma * 100, 2)}%) -> "
                f"{'CONFORME' if re.atende_norma else 'NÃO CONFORME'}"
            )
            for obs in re.observacoes:
                linhas.append(f"    * {obs}")
        linhas.append("")

    # 3. Tubos de Queda
    if resultado.resultados_tubos_queda:
        linhas.append("3. TUBOS DE QUEDA VERTICAIS / PRUMADAS (TABELA 4 NBR 8160)")
        for tq in resultado.resultados_tubos_queda:
            linhas.append(
                f"  - [{tq.identificacao}] {tq.numero_pavimentos} Pavimentos | Carga: {formatar_fracao_decimal(tq.total_uhc, 1)} UHC | "
                f"DN Adotado: {tq.dn_adotado} mm | Capacidade: {tq.capacidade_uhc_admissivel} UHC "
                f"(Ocupação: {formatar_fracao_decimal(tq.taxa_ocupacao_uhc * 100, 1)}%) -> "
                f"{'CONFORME' if tq.atende_norma else 'NÃO CONFORME'}"
            )
            for obs in tq.observacoes:
                linhas.append(f"    * {obs}")
        linhas.append("")

    # 4. Coluna de Ventilação
    if resultado.resultado_coluna_ventilacao is not None:
        rcv = resultado.resultado_coluna_ventilacao
        linhas.append("4. COLUNA DE VENTILAÇÃO SECUNDÁRIA (TABELA 5 NBR 8160)")
        linhas.append(f"  - Prumada: {rcv.identificacao} (Associada ao TQ: {rcv.tubo_queda_associado})")
        linhas.append(f"  - Carga Ventilada: {formatar_fracao_decimal(rcv.uhc_ventilada, 1)} UHC | Comprimento: {formatar_fracao_decimal(rcv.comprimento_m, 1)} m")
        linhas.append(f"  - DN Mínimo Normativo: {rcv.dn_calculado} mm | DN Adotado: {rcv.dn_adotado} mm")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rcv.atende_norma else 'NÃO CONFORME'}")
        for obs in rcv.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")

    # 5. Coletor Predial
    if resultado.resultado_coletor_predial is not None:
        rcp = resultado.resultado_coletor_predial
        linhas.append("5. SUBCOLETORES E COLETOR PREDIAL (TABELA 6 NBR 8160)")
        linhas.append(f"  - Coletor: {rcp.identificacao}")
        linhas.append(f"  - Carga Total Conduzida: {formatar_fracao_decimal(rcp.total_uhc, 1)} UHC")
        linhas.append(f"  - Diâmetro Adotado: DN {rcp.dn_adotado} mm (Mínimo: {rcp.dn_calculado} mm)")
        linhas.append(f"  - Declividade de Instalação: {formatar_fracao_decimal(rcp.declividade_m_m * 100, 2)}% (Mínimo: 1,0%)")
        linhas.append(f"  - Capacidade Admissível: {rcp.capacidade_uhc_tabela} UHC (Ocupação: {formatar_fracao_decimal(rcp.taxa_ocupacao_uhc * 100, 1)}%)")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rcp.atende_norma else 'NÃO CONFORME'}")
        for obs in rcp.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")

    # 6. Dispositivos e Caixas
    linhas.append("6. CAIXAS DE GORDURA, INSPEÇÃO E DESCONECTORES")
    if resultado.resultado_caixa_gordura is not None:
        rcg = resultado.resultado_caixa_gordura
        linhas.append(f"  - Caixa de Gordura: {rcg.identificacao} (Tipo {rcg.tipo.upper()})")
        linhas.append(f"    * Diâmetro: {rcg.diametro_adotado_mm} mm | Volume Adotado: {formatar_fracao_decimal(rcg.volume_retencao_adotado_L, 1)} L (Mínimo: {formatar_fracao_decimal(rcg.volume_retencao_calculado_L, 1)} L)")
        linhas.append(f"    * Status: {'CONFORME' if rcg.atende_norma else 'NÃO CONFORME'}")

    for rci in resultado.resultados_caixas_inspecao:
        linhas.append(f"  - Caixa de Inspeção: {rci.identificacao} ({rci.largura_mm}x{rci.comprimento_mm} mm)")
        linhas.append(f"    * Distância a montante: {formatar_fracao_decimal(rci.distancia_montante_m, 1)} m (Máximo permitido: {formatar_fracao_decimal(rci.distancia_maxima_norma_m, 1)} m)")
        linhas.append(f"    * Status: {'CONFORME' if rci.atende_norma else 'NÃO CONFORME'}")
    linhas.append("")

    # 7. Síntese e Recomendações
    linhas.append("7. SÍNTESE DE CONFORMIDADE E RECOMENDAÇÕES EXECUTIVAS")
    for k, v in resultado.conformidades.items():
        linhas.append(f"  - Componente [{k}]: {'APROVADO' if v else 'REPROVADO'}")
    if resultado.alertas:
        linhas.append("  ALERTAS DE PROJETO:")
        for al in resultado.alertas:
            linhas.append(f"    [!] {al}")
    if resultado.recomendacoes:
        linhas.append("  RECOMENDAÇÕES EXECUTIVAS:")
        for rec in resultado.recomendacoes:
            linhas.append(f"    [*] {rec}")

    linhas.append(div)
    linhas.append("LOFRANO TECNOLOGIA - Soluções Determinísticas e Engenharia Confiável.")
    linhas.append(div)
    return "\n".join(linhas)

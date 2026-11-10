from __future__ import annotations

import html
from fractions import Fraction
from typing import Optional

from esgoto_sanitario_nbr8160.models import ResultadoProjetoEsgoto
from esgoto_sanitario_nbr8160.exporters import formatar_fracao_decimal


def gerar_painel_svg(resultado: ResultadoProjetoEsgoto) -> str:
    """Gera um painel técnico vetorial SVG 1440x900 profissional e atraente."""
    status_cor = "#10b981" if resultado.atende_geral else "#ef4444"
    status_texto = "SISTEMA CONFORME NBR 8160" if resultado.atende_geral else "RESTRIÇÃO / NÃO CONFORME"

    total_uhc_str = formatar_fracao_decimal(resultado.total_uhc_geral, 1)
    qtd_ramais_desc = len(resultado.resultados_ramais_descarga)
    qtd_ramais_esg = len(resultado.resultados_ramais_esgoto)
    qtd_tq = len(resultado.resultados_tubos_queda)

    # TQ Principal
    tq_principal = resultado.resultados_tubos_queda[0] if resultado.resultados_tubos_queda else None
    tq_dn = f"DN {tq_principal.dn_adotado}" if tq_principal else "-"
    tq_ocup = f"{formatar_fracao_decimal(tq_principal.taxa_ocupacao_uhc * 100, 1)}%" if tq_principal else "-"
    tq_cap = f"{tq_principal.capacidade_uhc_admissivel} UHC" if tq_principal else "-"

    # Coletor Predial
    cp = resultado.resultado_coletor_predial
    cp_dn = f"DN {cp.dn_adotado}" if cp else "-"
    cp_dec = f"{formatar_fracao_decimal(cp.declividade_m_m * 100, 2)}%" if cp else "-"
    cp_ocup = f"{formatar_fracao_decimal(cp.taxa_ocupacao_uhc * 100, 1)}%" if cp else "-"

    # Coluna de Ventilação
    cv = resultado.resultado_coluna_ventilacao
    cv_dn = f"DN {cv.dn_adotado}" if cv else "-"
    cv_comp = f"{formatar_fracao_decimal(cv.comprimento_m, 1)} m" if cv else "-"

    # Caixa de Gordura
    cg = resultado.resultado_caixa_gordura
    cg_vol = f"{formatar_fracao_decimal(cg.volume_retencao_adotado_L, 0)} L" if cg else "-"
    cg_tipo = cg.tipo.upper() if cg else "-"

    # Caixas de Inspeção
    qtd_ci = len(resultado.resultados_caixas_inspecao)

    id_proj = html.escape(resultado.identificacao)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900">
  <defs>
    <!-- Gradientes de Fundo -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.95" />
    </linearGradient>
    <linearGradient id="blueCardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#0369a1" stop-opacity="0.10" />
    </linearGradient>
    <linearGradient id="pipeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="50%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <linearGradient id="ventGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669" />
      <stop offset="50%" stop-color="#34d399" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <linearGradient id="fixtureGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc" />
      <stop offset="100%" stop-color="#cbd5e1" />
    </linearGradient>
    <linearGradient id="chamberGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#475569" />
      <stop offset="100%" stop-color="#334155" />
    </linearGradient>

    <!-- Filtro de Sombra -->
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Fundo Principal -->
  <rect width="1440" height="900" fill="url(#bgGrad)" />

  <!-- Grid Sutil de Engenharia -->
  <g opacity="0.05" stroke="#38bdf8" stroke-width="1">
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" />
    </pattern>
    <rect width="1440" height="900" fill="url(#grid)" />
  </g>

  <!-- ==================== CABEÇALHO ==================== -->
  <g transform="translate(40, 26)">
    <!-- Logo Badge -->
    <rect x="0" y="0" width="180" height="32" rx="6" fill="#0284c7" fill-opacity="0.2" stroke="#38bdf8" stroke-width="1.5" />
    <text x="90" y="21" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" letter-spacing="1.5" text-anchor="middle">LOFRANO TECNOLOGIA</text>

    <!-- Título e Subtítulo -->
    <text x="195" y="22" fill="#ffffff" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700">DIMENSIONAMENTO DE ESGOTO SANITÁRIO E VENTILAÇÃO</text>
    <text x="195" y="42" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12">ABNT NBR 8160:1999 — Projeto e Execução de Sistemas Prediais de Esgoto Sanitário</text>

    <!-- Badge de Identificação do Projeto -->
    <rect x="880" y="2" width="230" height="34" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1" />
    <text x="895" y="18" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">PROJETO:</text>
    <text x="895" y="30" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600">{id_proj}</text>

    <!-- Badge de Status Geral -->
    <rect x="1125" y="2" width="275" height="34" rx="6" fill="{status_cor}" fill-opacity="0.15" stroke="{status_cor}" stroke-width="1.5" />
    <circle cx="1145" cy="19" r="6" fill="{status_cor}" />
    <text x="1160" y="23" fill="{status_cor}" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700">{status_texto}</text>
  </g>

  <!-- ==================== CARTÕES SUPERIORES (KPIs) ==================== -->
  <g transform="translate(40, 85)">
    <!-- Cartão 1: Total UHC -->
    <rect x="0" y="0" width="256" height="88" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <text x="20" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">CARGA TOTAL DE ESGOTO</text>
    <text x="20" y="58" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">{total_uhc_str}</text>
    <text x="150" y="58" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="13">UHC acumuladas</text>
    <text x="20" y="76" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">{qtd_ramais_desc} aparelhos / {qtd_ramais_esg} ramais</text>

    <!-- Cartão 2: Tubo de Queda (TQ) -->
    <rect x="276" y="0" width="256" height="88" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <text x="296" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">TUBO DE QUEDA (PRUMADA)</text>
    <text x="296" y="58" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">{tq_dn}</text>
    <text x="410" y="58" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700">η = {tq_ocup}</text>
    <text x="296" y="76" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">Capacidade máx: {tq_cap} (Tab. 4)</text>

    <!-- Cartão 3: Coletor Predial -->
    <rect x="552" y="0" width="256" height="88" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <text x="572" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">COLETOR PREDIAL / SAÍDA</text>
    <text x="572" y="58" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">{cp_dn}</text>
    <text x="686" y="58" fill="#f59e0b" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">i = {cp_dec}</text>
    <text x="572" y="76" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">Ocupação: {cp_ocup} (Tab. 6)</text>

    <!-- Cartão 4: Ventilação Secundária -->
    <rect x="828" y="0" width="256" height="88" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <text x="848" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">COLUNA DE VENTILAÇÃO</text>
    <text x="848" y="58" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">{cv_dn}</text>
    <text x="962" y="58" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="13">H = {cv_comp}</text>
    <text x="848" y="76" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">Proteção de fecho hídrico (Tab. 5)</text>

    <!-- Cartão 5: Caixas de Gordura & Inspeção -->
    <rect x="1104" y="0" width="256" height="88" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <text x="1124" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">CAIXAS & DISPOSITIVOS</text>
    <text x="1124" y="58" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="800">CG {cg_vol}</text>
    <text x="1260" y="58" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="13">{qtd_ci} CI(s)</text>
    <text x="1124" y="76" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">Tipo {cg_tipo} • CI máx 25 m</text>
  </g>

  <!-- ==================== CORPO CENTRAL: ESQUEMA TÉCNICO VETORIAL ==================== -->
  <g transform="translate(40, 190)">
    <!-- Painel do Esquema Isométrico / Elevação Sanitária -->
    <rect x="0" y="0" width="810" height="660" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />

    <!-- Barra de Título do Esquema -->
    <rect x="0" y="0" width="810" height="42" rx="10" fill="#1e293b" />
    <text x="20" y="26" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">ESQUEMA ELEVAÇÃO HIDRÁULICO-SANITÁRIO E VENTILAÇÃO</text>
    <text x="560" y="26" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Desconector / Fecho Hídrico h ≥ 50 mm</text>

    <!-- Linhas de Pavimento (Piso / Lajes) -->
    <!-- Cobertura (y=90) -->
    <line x1="60" y1="90" x2="750" y2="90" stroke="#475569" stroke-dasharray="4 4" stroke-width="1.5" />
    <text x="65" y="82" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">COBERTURA / TELHADO (+6,00 m)</text>

    <!-- Pavimento Superior (y=260) -->
    <line x1="60" y1="260" x2="750" y2="260" stroke="#475569" stroke-width="2" />
    <text x="65" y="252" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">PAVIMENTO SUPERIOR (+3,00 m) — BANHEIRO</text>

    <!-- Pavimento Térreo (y=440) -->
    <line x1="60" y1="440" x2="750" y2="440" stroke="#475569" stroke-width="2" />
    <text x="65" y="432" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">PAVIMENTO TÉRREO (0,00 m) — COZINHA E ÁREA DE SERVIÇO</text>

    <!-- Subsolo / Fundação (y=610) -->
    <line x1="60" y1="610" x2="750" y2="610" stroke="#334155" stroke-width="2" />
    <text x="65" y="602" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">LEITO ENTERRADO / COLETOR PREDIAL (-0,80 m)</text>

    <!-- ================= TUBULAÇÕES VERTICAIS ================= -->
    <!-- Coluna de Ventilação CV-01 (Verde) x=370 -->
    <!-- Terminal de Ventilação na Cobertura -->
    <path d="M 360 40 L 380 40 L 375 25 L 365 25 Z" fill="#34d399" />
    <line x1="370" y1="40" x2="370" y2="520" stroke="url(#ventGrad)" stroke-width="6" stroke-linecap="round" />
    <!-- Identificação CV -->
    <rect x="330" y="52" width="80" height="20" rx="4" fill="#064e3b" stroke="#059669" stroke-width="1" />
    <text x="370" y="66" fill="#34d399" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">CV {cv_dn}</text>

    <!-- Tubo de Queda TQ-01 (Azul) x=430 -->
    <!-- Prolongamento de ventilação primária acima da cobertura -->
    <line x1="430" y1="40" x2="430" y2="90" stroke="#0284c7" stroke-width="10" stroke-linecap="round" />
    <path d="M 420 40 L 440 40 L 435 25 L 425 25 Z" fill="#38bdf8" />
    <!-- TQ descendo até o subsolo -->
    <line x1="430" y1="90" x2="430" y2="530" stroke="url(#pipeGrad)" stroke-width="12" stroke-linecap="round" />
    <!-- Identificação TQ -->
    <rect x="445" y="110" width="90" height="22" rx="4" fill="#0c4a6e" stroke="#0284c7" stroke-width="1" />
    <text x="490" y="125" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">TQ {tq_dn}</text>

    <!-- Conexão de Alívio / Ventilação na Base (CV conecta ao TQ no térreo) -->
    <path d="M 370 510 C 370 525, 410 525, 430 520" fill="none" stroke="#10b981" stroke-width="5" />
    <text x="345" y="540" fill="#34d399" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Pé da Coluna de Ventilação</text>

    <!-- ================= PAVIMENTO SUPERIOR: BANHEIRO ================= -->
    <!-- Bacia Sanitária (BS) x=140, y=230 -->
    <rect x="120" y="210" width="30" height="40" rx="4" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <ellipse cx="135" cy="240" rx="14" ry="10" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5" />
    <text x="135" y="200" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">BS</text>
    <text x="135" y="188" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" text-anchor="middle">6 UHC / DN 100</text>
    <!-- Ramal de Descarga BS direto ao TQ -->
    <path d="M 135 250 L 135 258 L 430 258" fill="none" stroke="#0284c7" stroke-width="8" />
    <text x="270" y="252" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600">Ramal DN 100 (i=2%)</text>

    <!-- Lavatório (LV) x=210, y=215 -->
    <rect x="200" y="215" width="22" height="18" rx="3" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <text x="211" y="205" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600" text-anchor="middle">LV</text>
    <!-- Ramal LV até a Caixa Sifonada -->
    <path d="M 211 233 L 211 248 L 260 248" fill="none" stroke="#38bdf8" stroke-width="3" />
    <text x="211" y="195" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" text-anchor="middle">1 UHC / DN 40</text>

    <!-- Chuveiro (CH) x=290, y=215 -->
    <circle cx="290" cy="215" r="8" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <line x1="284" y1="223" x2="284" y2="230" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2 1" />
    <line x1="290" y1="223" x2="290" y2="230" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2 1" />
    <line x1="296" y1="223" x2="296" y2="230" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2 1" />
    <text x="290" y="202" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600" text-anchor="middle">CH</text>
    <!-- Ralo / Caixa Sifonada do Banheiro x=265, y=245 -->
    <rect x="255" y="240" width="20" height="16" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5" />
    <text x="265" y="270" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" text-anchor="middle">CS 100x50</text>
    <!-- Ligação CS até Ramal de Esgoto -->
    <path d="M 275 248 L 320 248 L 320 258" fill="none" stroke="#0284c7" stroke-width="5" />

    <!-- Ramal de Ventilação Secundária no Pav. Superior ligando ao CV -->
    <path d="M 320 248 L 320 180 L 370 180" fill="none" stroke="#10b981" stroke-width="3" stroke-dasharray="3 3" />
    <text x="325" y="174" fill="#34d399" font-family="'Segoe UI', Roboto, sans-serif" font-size="8">Ventilação DN 50</text>

    <!-- ================= PAVIMENTO TÉRREO: COZINHA E LAVANDERIA ================= -->
    <!-- Pia de Cozinha (PC) x=130, y=390 -->
    <rect x="115" y="385" width="35" height="25" rx="3" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <rect x="120" y="390" width="25" height="15" rx="2" fill="#94a3b8" />
    <text x="132" y="375" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">PC</text>
    <text x="132" y="363" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" text-anchor="middle">3 UHC / DN 50 (Gordura)</text>

    <!-- Caixa de Gordura (CG) Externa/Térreo x=190, y=440 -->
    <rect x="175" y="440" width="40" height="35" rx="4" fill="#475569" stroke="#f59e0b" stroke-width="2" />
    <text x="195" y="462" fill="#fbbf24" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="700" text-anchor="middle">CG</text>
    <text x="195" y="488" fill="#fbbf24" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" text-anchor="middle">{cg_vol}</text>
    <!-- Tubulação PC -> CG -->
    <path d="M 132 410 L 132 445 L 175 445" fill="none" stroke="#f59e0b" stroke-width="4" />
    <text x="135" y="435" fill="#fbbf24" font-family="'Segoe UI', Roboto, sans-serif" font-size="8">DN 50 (Exclusivo)</text>

    <!-- Tanque (TQ) e Máquina de Lavar (MLR) x=280 e x=330, y=390 -->
    <rect x="270" y="388" width="22" height="22" rx="3" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <text x="281" y="380" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600" text-anchor="middle">TQ</text>
    <rect x="315" y="385" width="26" height="26" rx="4" fill="url(#fixtureGrad)" stroke="#64748b" stroke-width="1.5" />
    <circle cx="328" cy="398" r="7" fill="#94a3b8" />
    <text x="328" y="378" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600" text-anchor="middle">MLR</text>

    <!-- Ramal de Esgoto Térreo conectando ao Tubo de Queda -->
    <path d="M 281 410 L 281 435 L 430 435" fill="none" stroke="#0284c7" stroke-width="6" />
    <path d="M 328 411 L 328 435" fill="none" stroke="#0284c7" stroke-width="4" />
    <text x="345" y="430" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8">Ramal DN 75 (i=2%)</text>

    <!-- ================= SUBSOLO / LEITO EXTERNO ================= -->
    <!-- Curva do TQ no pé da coluna (com ângulo de 45° ou duas de 45°) -->
    <path d="M 430 530 C 430 570, 445 580, 480 580" fill="none" stroke="url(#pipeGrad)" stroke-width="10" />
    <text x="445" y="565" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8">2 curvas de 45°</text>

    <!-- Saída da Caixa de Gordura conectando à Caixa de Inspeção -->
    <path d="M 215 460 L 530 460 L 530 580" fill="none" stroke="#f59e0b" stroke-width="5" />
    <text x="240" y="475" fill="#fbbf24" font-family="'Segoe UI', Roboto, sans-serif" font-size="8">Efluente tratado CG (DN 75 / 100)</text>

    <!-- Caixa de Inspeção CI-01 x=510, y=560 -->
    <rect x="500" y="560" width="55" height="45" rx="4" fill="url(#chamberGrad)" stroke="#38bdf8" stroke-width="2" />
    <line x1="500" y1="565" x2="555" y2="565" stroke="#94a3b8" stroke-width="2" />
    <text x="527" y="588" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">CI-01</text>
    <text x="527" y="600" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" text-anchor="middle">600x600</text>

    <!-- Coletor Predial CP-01 saindo da CI-01 em direção à rede pública -->
    <path d="M 555 585 L 750 595" fill="none" stroke="url(#pipeGrad)" stroke-width="10" stroke-linecap="round" />
    <!-- Seta de Fluxo -->
    <polygon points="750,595 738,589 738,601" fill="#38bdf8" />
    <text x="610" y="578" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">COLETOR PREDIAL {cp_dn}</text>
    <text x="610" y="612" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Declividade: {cp_dec} • Destino: Rede Pública</text>

    <!-- LEGENDA TÉCNICA DO DIAGRAMA -->
    <rect x="20" y="525" width="200" height="115" rx="6" fill="#0f172a" fill-opacity="0.9" stroke="#334155" stroke-width="1" />
    <text x="30" y="543" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">CONVENÇÃO GRÁFICA</text>
    <!-- Tubo de Esgoto Primário -->
    <line x1="30" y1="558" x2="60" y2="558" stroke="#0284c7" stroke-width="6" />
    <text x="68" y="562" fill="#e2e8f0" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Esgoto Primário / Bacia</text>
    <!-- Esgoto Secundário / Ramal -->
    <line x1="30" y1="576" x2="60" y2="576" stroke="#38bdf8" stroke-width="3" />
    <text x="68" y="580" fill="#e2e8f0" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Esgoto Secundário</text>
    <!-- Ventilação Secundária -->
    <line x1="30" y1="594" x2="60" y2="594" stroke="#10b981" stroke-width="3" stroke-dasharray="3 3" />
    <text x="68" y="598" fill="#e2e8f0" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Ventilação NBR 8160</text>
    <!-- Gordura -->
    <line x1="30" y1="612" x2="60" y2="612" stroke="#f59e0b" stroke-width="4" />
    <text x="68" y="616" fill="#e2e8f0" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">Águas Gordurosas (CG)</text>
  </g>

  <!-- ==================== COLUNA LATERAL DIREITA: TABELAS DE VERIFICAÇÃO ==================== -->
  <g transform="translate(870, 190)">
    <!-- Painel 1: Tabela de Ramais de Esgoto -->
    <rect x="0" y="0" width="530" height="320" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="0" y="0" width="530" height="38" rx="10" fill="#1e293b" />
    <text x="18" y="24" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700">VERIFICAÇÃO DE RAMAIS DE DESCARGA E ESGOTO</text>

    <!-- Cabeçalho da Tabela -->
    <text x="18" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">TRECHO / ELEMENTO</text>
    <text x="175" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">CARGA</text>
    <text x="245" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">DN CÁLC</text>
    <text x="325" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">DN ADOT</text>
    <text x="405" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">DECLIV.</text>
    <text x="480" y="55" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">STATUS</text>
    <line x1="18" y1="62" x2="512" y2="62" stroke="#334155" stroke-width="1" />
"""

    # Gerar linhas da tabela de ramais
    y_tab = 82
    linhas_ramais = list(resultado.resultados_ramais_esgoto)[:6]
    for r in linhas_ramais:
        status_item_cor = "#10b981" if r.atende_norma else "#ef4444"
        status_item_txt = "OK" if r.atende_norma else "ERRO"
        uhc_txt = formatar_fracao_decimal(r.total_uhc, 1) + " UHC"
        dec_txt = formatar_fracao_decimal(r.declividade_m_m * 100, 1) + "%"

        svg += f"""
    <text x="18" y="{y_tab}" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">{html.escape(r.identificacao[:22])}</text>
    <text x="175" y="{y_tab}" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">{uhc_txt}</text>
    <text x="245" y="{y_tab}" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">DN {r.dn_calculado}</text>
    <text x="325" y="{y_tab}" fill="#ffffff" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">DN {r.dn_adotado}</text>
    <text x="405" y="{y_tab}" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">{dec_txt}</text>
    <rect x="475" y="{y_tab - 11}" width="38" height="15" rx="3" fill="{status_item_cor}" fill-opacity="0.2" />
    <text x="494" y="{y_tab}" fill="{status_item_cor}" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="700" text-anchor="middle">{status_item_txt}</text>
    <line x1="18" y1="{y_tab + 7}" x2="512" y2="{y_tab + 7}" stroke="#1e293b" stroke-width="1" />
"""
        y_tab += 26

    # Se sobrarem linhas, preencher até 6
    if len(linhas_ramais) < 4:
        for rd in resultado.resultados_ramais_descarga[:4 - len(linhas_ramais)]:
            status_item_cor = "#10b981" if rd.atende_norma else "#ef4444"
            status_item_txt = "OK" if rd.atende_norma else "ERRO"
            uhc_txt = formatar_fracao_decimal(rd.uhc_total, 1) + " UHC"
            svg += f"""
    <text x="18" y="{y_tab}" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">{html.escape(rd.identificacao[:22])}</text>
    <text x="175" y="{y_tab}" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">{uhc_txt}</text>
    <text x="245" y="{y_tab}" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">DN {rd.dn_minimo_norma}</text>
    <text x="325" y="{y_tab}" fill="#ffffff" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">DN {rd.dn_adotado}</text>
    <text x="405" y="{y_tab}" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">Descarga</text>
    <rect x="475" y="{y_tab - 11}" width="38" height="15" rx="3" fill="{status_item_cor}" fill-opacity="0.2" />
    <text x="494" y="{y_tab}" fill="{status_item_cor}" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="700" text-anchor="middle">{status_item_txt}</text>
    <line x1="18" y1="{y_tab + 7}" x2="512" y2="{y_tab + 7}" stroke="#1e293b" stroke-width="1" />
"""
            y_tab += 26

    # Painel 2: Prumadas, Coletor e Caixas de Inspeção
    svg += f"""
    <!-- Painel 2: Prumadas, Coletor e Caixas de Inspeção -->
    <rect x="0" y="340" width="530" height="320" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="0" y="340" width="530" height="38" rx="10" fill="#1e293b" />
    <text x="18" y="364" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700">PRUMADAS, VENTILAÇÃO E DISPOSITIVOS ESPECIAIS</text>

    <!-- Checklist e Verificações Normativas NBR 8160 -->
    <g transform="translate(18, 395)">
      <!-- Item 1: Tubo de Queda -->
      <circle cx="8" cy="6" r="4" fill="#10b981" />
      <text x="22" y="10" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Tubo de Queda (TQ):</text>
      <text x="170" y="10" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{tq_dn} (Capacidade: {tq_cap} | Ocupação: {tq_ocup})</text>

      <!-- Item 2: Coluna de Ventilação -->
      <circle cx="8" cy="36" r="4" fill="#10b981" />
      <text x="22" y="40" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Ventilação Secundária:</text>
      <text x="170" y="40" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{cv_dn} contínua com terminal na cobertura</text>

      <!-- Item 3: Fecho Hídrico -->
      <circle cx="8" cy="66" r="4" fill="#10b981" />
      <text x="22" y="70" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Fecho Hídrico Mínimo:</text>
      <text x="170" y="70" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">h ≥ 50 mm em todos os desconectores (item 4.2.4.1)</text>

      <!-- Item 4: Coletor Predial -->
      <circle cx="8" cy="96" r="4" fill="#10b981" />
      <text x="22" y="100" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Coletor Predial:</text>
      <text x="170" y="100" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{cp_dn} com i={cp_dec} (Mínimo DN 100 e 1,0%)</text>

      <!-- Item 5: Caixa de Gordura -->
      <circle cx="8" cy="126" r="4" fill="#10b981" />
      <text x="22" y="130" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Caixa de Gordura:</text>
      <text x="170" y="130" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Tipo {cg_tipo} com retenção de {cg_vol} (exclusiva de pias)</text>

      <!-- Item 6: Caixas de Inspeção -->
      <circle cx="8" cy="156" r="4" fill="#10b981" />
      <text x="22" y="160" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Caixas de Inspeção:</text>
      <text x="170" y="160" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Dimensões 600x600 mm, distâncias ≤ 25,0 m</text>

      <!-- Item 7: Declividades Mínimas -->
      <circle cx="8" cy="186" r="4" fill="#10b981" />
      <text x="22" y="190" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600">Declividades Mínimas:</text>
      <text x="170" y="190" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">2,0% para DN ≤ 75 mm; 1,0% para DN ≥ 100 mm</text>
    </g>

    <!-- Box de Garantia Zero Float -->
    <rect x="18" y="580" width="494" height="40" rx="6" fill="#0284c7" fill-opacity="0.15" stroke="#0284c7" stroke-width="1" />
    <text x="265" y="605" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" text-anchor="middle">GARANTIA TÉCNICA: MOTOR DETERMINÍSTICO ZERO FLOAT (FRAÇÕES RACIONAIS)</text>
  </g>

  <!-- ==================== RODAPÉ ==================== -->
  <g transform="translate(40, 868)">
    <line x1="0" y1="0" x2="1360" y2="0" stroke="#334155" stroke-width="1" />
    <text x="0" y="18" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">LOFRANO TECNOLOGIA • Engenharia Sanitária e Hidráulica Predial • ABNT NBR 8160:1999 • Código Aberto MIT</text>
    <text x="1360" y="18" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" text-anchor="end">Cálculo Racional e Determinístico sem Aproximação IEEE-754</text>
  </g>
</svg>"""
    return svg

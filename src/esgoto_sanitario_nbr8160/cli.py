from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from typing import Optional, List

from esgoto_sanitario_nbr8160 import __version__
from esgoto_sanitario_nbr8160.constants import (
    TABELA_APARELHOS_SANITARIOS_NBR8160,
    TABELA_RAMAIS_ESGOTO_NBR8160,
    TABELA_TUBOS_QUEDA_NBR8160,
    TABELA_COLETOR_PREDIAL_NBR8160,
    TABELA_COLUNA_VENTILACAO_NBR8160,
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
)
from esgoto_sanitario_nbr8160.calculator import (
    dimensionar_sistema_esgoto,
    dimensionar_ramal_esgoto,
    dimensionar_tubo_queda,
    dimensionar_coletor_predial,
    dimensionar_coluna_ventilacao,
)
from esgoto_sanitario_nbr8160.codecs import (
    carregar_json_canonico,
    salvar_json_canonico,
    deserializar_projeto,
)
from esgoto_sanitario_nbr8160.exporters import (
    exportar_csv,
    gerar_relatorio_memorial,
    formatar_fracao_decimal,
)
from esgoto_sanitario_nbr8160.svg_generator import gerar_painel_svg


def parse_fracao_cli(texto: str) -> Fraction:
    """Converte string recebida na linha de comando em Fraction sem admitir float."""
    t = texto.strip().replace(",", ".")
    if "/" in t:
        partes = t.split("/")
        if len(partes) == 2:
            return Fraction(int(partes[0].strip()), int(partes[1].strip()))
    if "." in t:
        partes = t.split(".")
        if len(partes) == 2:
            num = int(partes[0] + partes[1])
            den = 10 ** len(partes[1])
            return Fraction(num, den)
    return Fraction(int(t), 1)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="esgoto-sanitario",
        description="Dimensionamento de sistemas prediais de esgoto sanitário e ventilação segundo a ABNT NBR 8160:1999. LOFRANO TECNOLOGIA.",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: dimensionar
    p_dim = subparsers.add_parser("dimensionar", help="Dimensiona e verifica componentes prediais de esgoto")
    p_dim.add_argument("--arquivo", "-a", type=str, help="Caminho do arquivo JSON de projeto")
    p_dim.add_argument("--tipo-trecho", "-t", type=str, choices=["ramal", "tq", "coletor", "ventilacao"], help="Tipo de trecho individual")
    p_dim.add_argument("--uhc", type=str, help="Unidades de Hunter de Contribuição (ex: 6 ou 32)")
    p_dim.add_argument("--dn", type=int, help="DN adotado em mm (ex: 40, 50, 75, 100, 150)")
    p_dim.add_argument("--declividade", type=str, default="2.0", help="Declividade em %% (padrão: 2.0%% para ramal, 1.0%% para coletor)")
    p_dim.add_argument("--pavimentos", type=int, default=1, help="Número de pavimentos para tubo de queda (padrão: 1)")
    p_dim.add_argument("--comprimento", type=str, default="10.0", help="Comprimento em metros (padrão: 10.0 m)")
    
    # Saídas
    p_dim.add_argument("--saida-json", "-j", type=str, help="Caminho para salvar resultado consolidado em JSON")
    p_dim.add_argument("--saida-csv", "-c", type=str, help="Caminho para salvar planilha estruturada em CSV")
    p_dim.add_argument("--saida-relatorio", "-r", type=str, help="Caminho para salvar memorial descritivo em TXT")
    p_dim.add_argument("--painel-svg", "-s", type=str, help="Caminho para gerar e salvar painel técnico em SVG")

    # Comando: aparelhos
    subparsers.add_parser("aparelhos", help="Lista aparelhos sanitários padronizados, UHC e DN mínimo da NBR 8160")

    # Comando: tabelas
    subparsers.add_parser("tabelas", help="Exibe as tabelas normativas oficiais da ABNT NBR 8160:1999")

    # Comando: versao
    subparsers.add_parser("versao", help="Exibe a versão do pacote")

    return parser


def comando_aparelhos() -> int:
    print("=" * 80)
    print("TABELA 1 & 2 — CONTRIBUIÇÃO DE ESGOTO POR APARELHO SANITÁRIO (ABNT NBR 8160)")
    print("=" * 80)
    print(f"{'Identificador':<28} | {'Nome':<30} | {'UHC':<5} | {'DN Mín':<6}")
    print("-" * 80)
    for chave, dados in sorted(TABELA_APARELHOS_SANITARIOS_NBR8160.items()):
        nome = dados["nome"]
        uhc = formatar_fracao_decimal(dados["uhc"], 1)
        dn = dados["dn_minimo"]
        print(f"{chave:<28} | {nome:<30} | {uhc:<5} | DN {dn}")
    print("=" * 80)
    print("Nota: Bacia sanitária exige obrigatoriamente DN mínimo de 100 mm.")
    return 0


def comando_tabelas() -> int:
    print("=" * 80)
    print("TABELAS NORMATIVAS DA ABNT NBR 8160:1999")
    print("=" * 80)
    print("\n1. TABELA 3 — DIMENSIONAMENTO DE RAMAIS DE ESGOTO")
    print("-" * 50)
    print(f"{'Capacidade Máxima (UHC)':<25} | {'Diâmetro Mínimo (DN)':<20}")
    print("-" * 50)
    for uhc_max, dn in TABELA_RAMAIS_ESGOTO_NBR8160:
        print(f"Até {uhc_max:<21} UHC | DN {dn}")
    print("Declividade mínima: 2,0% para DN <= 75 mm; 1,0% para DN >= 100 mm.")

    print("\n2. TABELA 4 — DIMENSIONAMENTO DE TUBOS DE QUEDA (PRUMADAS)")
    print("-" * 65)
    print(f"{'DN':<8} | {'Até 3 Pavimentos (UHC)':<25} | {'Mais de 3 Pavimentos (UHC)'}")
    print("-" * 65)
    for dn, dic in sorted(TABELA_TUBOS_QUEDA_NBR8160.items()):
        u3 = dic["ate_3_pav"]
        umais = dic["mais_3_pav"]
        print(f"DN {dn:<5} | até {u3:<21} UHC | até {umais} UHC")

    print("\n3. TABELA 6 — DIMENSIONAMENTO DE SUBCOLETORES E COLETOR PREDIAL")
    print("-" * 75)
    print(f"{'DN':<8} | {'i=0,5%':<10} | {'i=1,0%':<10} | {'i=1,5%':<10} | {'i=2,0%':<10} | {'i=4,0%'}")
    print("-" * 75)
    for dn, dic_dec in sorted(TABELA_COLETOR_PREDIAL_NBR8160.items()):
        u05 = dic_dec.get(Fraction(5, 1000), "-")
        u10 = dic_dec.get(Fraction(1, 100), "-")
        u15 = dic_dec.get(Fraction(15, 1000), "-")
        u20 = dic_dec.get(Fraction(2, 100), "-")
        u40 = dic_dec.get(Fraction(4, 100), "-")
        print(f"DN {dn:<5} | {str(u05):<10} | {str(u10):<10} | {str(u15):<10} | {str(u20):<10} | {str(u40)}")
    print("Nota: Coletor predial possui diâmetro mínimo absoluto de DN 100 e declividade mínima de 1,0%.")
    return 0


def executar_dimensionamento_cli(args: argparse.Namespace) -> int:
    if args.arquivo:
        # Carregar via arquivo JSON
        dados = carregar_json_canonico(args.arquivo)
        projeto = deserializar_projeto(dados)
        resultado = dimensionar_sistema_esgoto(projeto)
    elif args.tipo_trecho and args.uhc:
        # Modo rápido via linha de comando
        uhc = parse_fracao_cli(args.uhc)
        dec = parse_fracao_cli(args.declividade) / 100
        comp = parse_fracao_cli(args.comprimento)

        if args.tipo_trecho == "ramal":
            ramal = RamalEsgoto(
                identificacao="Ramal Rápido",
                aparelhos=[],
                dn_adotado_mm=args.dn,
                declividade_m_m=dec,
                comprimento_m=comp,
            )
            res_r = dimensionar_ramal_esgoto(ramal, carga_uhc_direta=uhc)
            print("=" * 60)
            print(f"DIMENSIONAMENTO DE RAMAL DE ESGOTO ({formatar_fracao_decimal(uhc, 1)} UHC)")
            print("=" * 60)
            print(f"DN Calculado (Norma): DN {res_r.dn_calculado}")
            print(f"DN Adotado:           DN {res_r.dn_adotado}")
            print(f"Declividade Adotada:  {formatar_fracao_decimal(res_r.declividade_m_m * 100, 2)}%")
            print(f"Declividade Mínima:   {formatar_fracao_decimal(res_r.declividade_minima_norma * 100, 2)}%")
            print(f"Status NBR 8160:      {'CONFORME' if res_r.atende_norma else 'NÃO CONFORME'}")
            for obs in res_r.observacoes:
                print(f" - {obs}")
            return 0 if res_r.atende_norma else 1

        elif args.tipo_trecho == "tq":
            tq = TuboQueda(
                identificacao="TQ Rápido",
                ramais_contribuintes=[],
                numero_pavimentos=args.pavimentos,
                dn_adotado_mm=args.dn,
                altura_m=comp,
            )
            res_t = dimensionar_tubo_queda(tq, carga_uhc_direta=uhc)
            print("=" * 60)
            print(f"DIMENSIONAMENTO DE TUBO DE QUEDA ({formatar_fracao_decimal(uhc, 1)} UHC - {args.pavimentos} pav)")
            print("=" * 60)
            print(f"DN Calculado:         DN {res_t.dn_calculado}")
            print(f"DN Adotado:           DN {res_t.dn_adotado}")
            print(f"Capacidade Máxima:    {res_t.capacidade_uhc_admissivel} UHC")
            print(f"Taxa de Ocupação:     {formatar_fracao_decimal(res_t.taxa_ocupacao_uhc * 100, 1)}%")
            print(f"Status NBR 8160:      {'CONFORME' if res_t.atende_norma else 'NÃO CONFORME'}")
            for obs in res_t.observacoes:
                print(f" - {obs}")
            return 0 if res_t.atende_norma else 1

        elif args.tipo_trecho == "coletor":
            col = ColetorPredial(
                identificacao="Coletor Rápido",
                uhc_adicional_direta=uhc,
                dn_adotado_mm=args.dn,
                declividade_m_m=dec,
                comprimento_m=comp,
            )
            res_c = dimensionar_coletor_predial(col, total_uhc=uhc)
            print("=" * 60)
            print(f"DIMENSIONAMENTO DE COLETOR PREDIAL ({formatar_fracao_decimal(uhc, 1)} UHC)")
            print("=" * 60)
            print(f"DN Calculado:         DN {res_c.dn_calculado}")
            print(f"DN Adotado:           DN {res_c.dn_adotado}")
            print(f"Declividade:          {formatar_fracao_decimal(res_c.declividade_m_m * 100, 2)}%")
            print(f"Capacidade Tab. 6:    {res_c.capacidade_uhc_tabela} UHC")
            print(f"Taxa de Ocupação:     {formatar_fracao_decimal(res_c.taxa_ocupacao_uhc * 100, 1)}%")
            print(f"Status NBR 8160:      {'CONFORME' if res_c.atende_norma else 'NÃO CONFORME'}")
            for obs in res_c.observacoes:
                print(f" - {obs}")
            return 0 if res_c.atende_norma else 1

        elif args.tipo_trecho == "ventilacao":
            cv = ColunaVentilacao(
                identificacao="CV Rápida",
                tubo_queda_associado="TQ",
                dn_adotado_mm=args.dn,
                comprimento_m=comp,
            )
            res_v = dimensionar_coluna_ventilacao(cv, dn_tubo_queda=100, uhc_ventilada=uhc)
            print("=" * 60)
            print(f"DIMENSIONAMENTO DE COLUNA DE VENTILAÇÃO ({formatar_fracao_decimal(uhc, 1)} UHC)")
            print("=" * 60)
            print(f"DN Calculado:         DN {res_v.dn_calculado}")
            print(f"DN Adotado:           DN {res_v.dn_adotado}")
            print(f"Comprimento:          {formatar_fracao_decimal(res_v.comprimento_m, 1)} m")
            print(f"Status NBR 8160:      {'CONFORME' if res_v.atende_norma else 'NÃO CONFORME'}")
            for obs in res_v.observacoes:
                print(f" - {obs}")
            return 0 if res_v.atende_norma else 1
        else:
            print("Tipo de trecho não suportado.")
            return 1
    else:
        print("Erro: Forneça um arquivo JSON (--arquivo) ou defina --tipo-trecho e --uhc.")
        return 1

    # Saídas
    relatorio = gerar_relatorio_memorial(resultado)
    if args.saida_relatorio:
        with open(args.saida_relatorio, "w", encoding="utf-8") as f:
            f.write(relatorio)
        print(f"Memorial descritivo salvo em: {args.saida_relatorio}")
    else:
        print(relatorio)

    if args.saida_json:
        salvar_json_canonico(args.saida_json, resultado)
        print(f"Resultado JSON canônico salvo em: {args.saida_json}")

    if args.saida_csv:
        csv_texto = exportar_csv(resultado)
        with open(args.saida_csv, "w", encoding="utf-8") as f:
            f.write(csv_texto)
        print(f"Planilha CSV salva em: {args.saida_csv}")

    if args.painel_svg:
        svg_conteudo = gerar_painel_svg(resultado)
        with open(args.painel_svg, "w", encoding="utf-8") as f:
            f.write(svg_conteudo)
        print(f"Painel técnico SVG salvo em: {args.painel_svg}")

    return 0 if resultado.atende_geral else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = criar_parser()
    args = parser.parse_args(argv)

    if args.comando == "aparelhos":
        return comando_aparelhos()
    elif args.comando == "tabelas":
        return comando_tabelas()
    elif args.comando == "versao":
        print(f"esgoto-sanitario v{__version__} — ABNT NBR 8160:1999 (LOFRANO TECNOLOGIA)")
        return 0
    elif args.comando == "dimensionar":
        return executar_dimensionamento_cli(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

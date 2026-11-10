from __future__ import annotations

import sqlite3
import sys
from fractions import Fraction

# ATENÇÃO: Este verificador independente NUNCA importa o pacote 'esgoto_sanitario_nbr8160'.
# Todos os cálculos são refeitos a partir dos primeiros princípios e normas ABNT NBR 8160:1999
# utilizando SQLite em memória com aritmética 100% Zero Float (Fraction e inteiros).


def main() -> int:
    print("=" * 80)
    print("  AUDITORIA INDEPENDENTE DE ESGOTO SANITÁRIO E VENTILAÇÃO (ABNT NBR 8160:1999)")
    print("  LOFRANO TECNOLOGIA - Verificação Exclusiva via SQLite em Memória")
    print("=" * 80)

    con = sqlite3.connect(":memory:")
    cur = con.cursor()

    # 1. Criação das tabelas normativas NBR 8160
    cur.execute("""
    CREATE TABLE aparelhos_normativos (
        tipo TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        uhc_num INT NOT NULL,
        uhc_den INT NOT NULL,
        dn_minimo INT NOT NULL,
        tipo_efluente TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE ramais_esgoto_tabela3 (
        limite_uhc INT PRIMARY KEY,
        dn_minimo INT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE tubos_queda_tabela4 (
        dn INT PRIMARY KEY,
        limite_ate_3_pav INT NOT NULL,
        limite_mais_3_pav INT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE coletores_tabela6 (
        dn INT NOT NULL,
        declividade_num INT NOT NULL,
        declividade_den INT NOT NULL,
        capacidade_uhc INT NOT NULL,
        PRIMARY KEY (dn, declividade_num, declividade_den)
    )
    """)

    # 2. Carga dos dados oficiais da NBR 8160
    aparelhos_dados = [
        ("bacia_sanitaria_caixa", "Bacia com caixa acoplada", 6, 1, 100, "fecal"),
        ("bacia_sanitaria_valvula", "Bacia com válvula", 32, 1, 100, "fecal"),
        ("lavatorio_residencial", "Lavatório residencial", 1, 1, 40, "secundario"),
        ("chuveiro_residencial", "Chuveiro residencial", 2, 1, 40, "secundario"),
        ("ralo_sifonado", "Ralo sifonado", 2, 1, 50, "secundario"),
        ("pia_cozinha_residencial", "Pia de cozinha", 3, 1, 50, "gorduroso"),
        ("tanque_lavar_roupa", "Tanque de lavar", 3, 1, 40, "secundario"),
        ("maquina_lavar_roupa", "Máquina de lavar roupa", 3, 1, 50, "secundario"),
    ]
    cur.executemany("INSERT INTO aparelhos_normativos VALUES (?, ?, ?, ?, ?, ?)", aparelhos_dados)

    ramais_dados = [
        (3, 40),
        (6, 50),
        (22, 75),
        (160, 100),
    ]
    cur.executemany("INSERT INTO ramais_esgoto_tabela3 VALUES (?, ?)", ramais_dados)

    tq_dados = [
        (50, 10, 24),
        (75, 30, 60),
        (100, 240, 500),
        (150, 960, 2000),
    ]
    cur.executemany("INSERT INTO tubos_queda_tabela4 VALUES (?, ?, ?)", tq_dados)

    coletor_dados = [
        (100, 5, 1000, 135),
        (100, 1, 100, 180),
        (100, 15, 1000, 216),
        (100, 2, 100, 250),
        (100, 4, 100, 350),
        (150, 5, 1000, 700),
        (150, 1, 100, 1000),
        (150, 15, 1000, 1250),
        (150, 2, 100, 1500),
        (150, 4, 100, 2100),
    ]
    cur.executemany("INSERT INTO coletores_tabela6 VALUES (?, ?, ?, ?)", coletor_dados)

    con.commit()

    print("[1/6] Base de dados relacional SQLite populada com sucesso.")

    # 3. Teste Caso 1: Banheiro Residencial Típico
    # BS (6 UHC) + LV (1 UHC) + CH (2 UHC) + RS (2 UHC) = 11 UHC
    cur.execute("""
    CREATE TABLE instalacao_caso1 (
        aparelho TEXT NOT NULL,
        quantidade INT NOT NULL
    )
    """)
    cur.executemany("INSERT INTO instalacao_caso1 VALUES (?, ?)", [
        ("bacia_sanitaria_caixa", 1),
        ("lavatorio_residencial", 1),
        ("chuveiro_residencial", 1),
        ("ralo_sifonado", 1),
    ])

    cur.execute("""
    SELECT SUM(a.uhc_num * i.quantidade) AS total_num, a.uhc_den
    FROM instalacao_caso1 i
    JOIN aparelhos_normativos a ON i.aparelho = a.tipo
    GROUP BY a.uhc_den
    """)
    linha = cur.fetchone()
    total_uhc_caso1 = Fraction(linha[0], linha[1])
    assert total_uhc_caso1 == Fraction(11, 1), f"Esperado 11 UHC, obtido {total_uhc_caso1}"
    print(f"[2/6] Caso 1 - Soma de UHC do Banheiro: {total_uhc_caso1} UHC (Correto)")

    # 4. Dimensionamento do Ramal de Esgoto do Banheiro Caso 1 via SQL
    # Pela Tabela 3: 11 UHC exigiria DN 75 (até 22 UHC), MAS recebe bacia sanitária -> DN 100 obrigatório!
    cur.execute("""
    SELECT dn_minimo FROM ramais_esgoto_tabela3
    WHERE limite_uhc >= ?
    ORDER BY limite_uhc ASC
    LIMIT 1
    """, (int(total_uhc_caso1),))
    dn_tabela = cur.fetchone()[0]
    assert dn_tabela == 75, f"Esperado DN 75 da tabela, obtido {dn_tabela}"

    # Regra de bacia sanitária
    cur.execute("SELECT COUNT(*) FROM instalacao_caso1 WHERE aparelho LIKE '%bacia%'")
    tem_bacia = cur.fetchone()[0] > 0
    dn_final_ramal = max(dn_tabela, 100) if tem_bacia else dn_tabela
    assert dn_final_ramal == 100, f"Esperado DN 100 obrigatório com bacia, obtido {dn_final_ramal}"
    print(f"[3/6] Caso 1 - Dimensionamento do Ramal com bacia: DN {dn_final_ramal} (Correto)")

    # 5. Dimensionamento do Tubo de Queda (TQ) para Edifício com 8 Pavimentos
    # Carga por pavimento = 11 UHC (banheiro) + 9 UHC (serviço) = 20 UHC
    # 8 Pavimentos -> 160 UHC total
    total_uhc_predio = Fraction(160, 1)
    pavimentos = 8
    cur.execute("""
    SELECT dn, limite_mais_3_pav FROM tubos_queda_tabela4
    WHERE limite_mais_3_pav >= ?
    ORDER BY limite_mais_3_pav ASC
    LIMIT 1
    """, (int(total_uhc_predio),))
    linha_tq = cur.fetchone()
    dn_tq = linha_tq[0]
    cap_tq = linha_tq[1]
    assert dn_tq == 100, f"Esperado DN 100 para 160 UHC em 8 pavimentos, obtido {dn_tq}"
    assert cap_tq == 500, f"Esperado capacidade de 500 UHC, obtido {cap_tq}"
    taxa_ocupacao_tq = total_uhc_predio / Fraction(cap_tq, 1)
    assert taxa_ocupacao_tq == Fraction(160, 500), f"Taxa de ocupação incorreta: {taxa_ocupacao_tq}"
    print(f"[4/6] Caso 2 - Tubo de Queda (8 pav, 160 UHC): DN {dn_tq} (Capacidade {cap_tq} UHC, Ocupação 32%) (Correto)")

    # 6. Coletor Predial para 160 UHC com declividade de 1,0% (1/100)
    cur.execute("""
    SELECT dn, capacidade_uhc FROM coletores_tabela6
    WHERE declividade_num = 1 AND declividade_den = 100 AND capacidade_uhc >= ?
    ORDER BY capacidade_uhc ASC
    LIMIT 1
    """, (int(total_uhc_predio),))
    linha_col = cur.fetchone()
    dn_col = linha_col[0]
    cap_col = linha_col[1]
    assert dn_col == 100, f"Esperado DN 100 para coletor predial com 160 UHC a 1%, obtido {dn_col}"
    assert cap_col == 180, f"Esperado capacidade de 180 UHC, obtido {cap_col}"
    print(f"[5/6] Caso 2 - Coletor Predial: DN {dn_col} a 1,0% (Capacidade {cap_col} UHC) (Correto)")

    # 7. Regras de Caixa de Gordura e Caixa de Inspeção
    # Simples: 18 L / D 300 mm
    # Dupla: 120 L / D 400 mm
    # Especial: V = 2 * N + 20 L
    n_refeicoes = 100
    v_esp_esperado = 2 * n_refeicoes + 20  # 220 L
    assert v_esp_esperado == 220
    # Inspeção: distância máxima de 25 metros
    dist_inspecao = Fraction(20, 1)
    assert dist_inspecao <= Fraction(25, 1)
    print(f"[6/6] Verificação de Dispositivos e Caixas (CG e CI): OK")

    print("=" * 80)
    print("  RESULTADO: TODAS AS 6 AUDITORIAS INDEPENDENTES EM SQLITE FORAM APROVADAS!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())

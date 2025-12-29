#!/usr/bin/env python3
"""
Scrape Contabilizei - Extrai dados da plataforma Contabilizei

Este script fornece funcoes para processar e salvar dados extraidos
da plataforma Contabilizei via browser automation (claude-in-chrome).

O scraping real e feito pelo agente usando ferramentas MCP.
Este script processa os dados extraidos e salva no banco SQLite.

Uso pelo agente:
1. Agente navega na Contabilizei via browser automation
2. Extrai dados (faturamento, impostos)
3. Chama save_contabilizei_data() para salvar no banco
"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple

# Import database functions
try:
    from finance_db import (
        add_pj_revenue, add_pj_tax, add_pj_expense,
        get_pj_monthly_summary, get_consolidated_summary
    )
except ImportError:
    from scripts.finance_db import (
        add_pj_revenue, add_pj_tax, add_pj_expense,
        get_pj_monthly_summary, get_consolidated_summary
    )


def parse_brazilian_currency(value_str: str) -> float:
    """
    Converte string de moeda brasileira para float.
    Exemplos:
        "R$ 36.427,14" -> 36427.14
        "36.427,14" -> 36427.14
        "166,98" -> 166.98
    """
    if not value_str:
        return 0.0

    # Remove "R$" e espacos
    cleaned = value_str.replace("R$", "").strip()

    # Remove pontos de milhar e troca virgula por ponto
    cleaned = cleaned.replace(".", "").replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_month_name(month_name: str) -> int:
    """Converte nome do mes para numero."""
    months = {
        "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
    }
    return months.get(month_name.lower(), 0)


def parse_competencia(text: str) -> Tuple[int, int]:
    """
    Extrai ano e mes de texto de competencia.
    Exemplos:
        "Competencia - Nov/2025" -> (2025, 11)
        "Novembro 2025" -> (2025, 11)
    """
    # Tenta formato "Mes/Ano"
    match = re.search(r"(\w+)/(\d{4})", text)
    if match:
        month_str, year_str = match.groups()
        month_map = {
            "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
            "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
        }
        month = month_map.get(month_str.lower()[:3], 0)
        return int(year_str), month

    # Tenta formato "Mes Ano"
    match = re.search(r"(\w+)\s+(\d{4})", text)
    if match:
        month_str, year_str = match.groups()
        month = parse_month_name(month_str)
        return int(year_str), month

    return 0, 0


def save_contabilizei_data(
    faturamento: float = None,
    faturamento_mes: int = None,
    faturamento_ano: int = None,
    imposto: float = None,
    imposto_mes: int = None,
    imposto_ano: int = None,
    imposto_vencimento: str = None,
    prolabore: float = None,
    contabilizei_fee: float = None
) -> Dict:
    """
    Salva dados extraidos da Contabilizei no banco de dados.

    Args:
        faturamento: Valor do faturamento bruto
        faturamento_mes: Mes do faturamento
        faturamento_ano: Ano do faturamento
        imposto: Valor do imposto Simples Nacional
        imposto_mes: Mes de competencia do imposto
        imposto_ano: Ano de competencia do imposto
        imposto_vencimento: Data de vencimento (YYYY-MM-DD)
        prolabore: Valor do pro-labore mensal
        contabilizei_fee: Mensalidade da Contabilizei

    Returns:
        Dict com resultados das operacoes
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "operations": []
    }

    # Salvar faturamento
    if faturamento and faturamento_mes and faturamento_ano:
        result = add_pj_revenue(
            faturamento_ano,
            faturamento_mes,
            faturamento,
            "contabilizei",
            f"Faturamento {faturamento_mes}/{faturamento_ano} - Importado via scraping"
        )
        results["operations"].append({
            "type": "faturamento",
            "year": faturamento_ano,
            "month": faturamento_mes,
            "value": faturamento,
            "status": result.get("status")
        })

    # Salvar imposto
    if imposto and imposto_mes and imposto_ano:
        result = add_pj_tax(
            imposto_ano,
            imposto_mes,
            "simples",
            imposto,
            imposto_vencimento,
            "pending"
        )
        results["operations"].append({
            "type": "imposto_simples",
            "year": imposto_ano,
            "month": imposto_mes,
            "value": imposto,
            "due_date": imposto_vencimento,
            "status": result.get("status")
        })

    # Salvar despesas fixas (mesmo mes do faturamento)
    expense_year = faturamento_ano or imposto_ano or datetime.now().year
    expense_month = faturamento_mes or imposto_mes or datetime.now().month

    if prolabore:
        result = add_pj_expense(expense_year, expense_month, "prolabore", prolabore)
        results["operations"].append({
            "type": "prolabore",
            "year": expense_year,
            "month": expense_month,
            "value": prolabore,
            "status": result.get("status")
        })

    if contabilizei_fee:
        result = add_pj_expense(expense_year, expense_month, "contabilizei", contabilizei_fee)
        results["operations"].append({
            "type": "contabilizei_fee",
            "year": expense_year,
            "month": expense_month,
            "value": contabilizei_fee,
            "status": result.get("status")
        })

    return results


def get_sync_status(year: int, month: int) -> Dict:
    """
    Retorna status de sincronizacao do mes.

    Returns:
        Dict com dados PJ e se precisa sincronizar
    """
    pj = get_pj_monthly_summary(year, month)

    return {
        "year": year,
        "month": month,
        "has_revenue": pj["gross_revenue"] > 0,
        "has_taxes": pj["total_taxes"] > 0,
        "gross_revenue": pj["gross_revenue"],
        "total_taxes": pj["total_taxes"],
        "net_revenue": pj["net_revenue"],
        "synced_at": pj.get("synced_at"),
        "needs_sync": pj["gross_revenue"] == 0
    }


def format_sync_report(year: int, month: int) -> str:
    """
    Gera relatorio de sincronizacao para exibicao.
    """
    pj = get_pj_monthly_summary(year, month)
    cons = get_consolidated_summary(year, month)

    month_names = ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    report = f"""
=== SINCRONIZACAO CONTABILIZEI ===
Periodo: {month_names[month]} {year}
Atualizado: {datetime.now().strftime("%d/%m/%Y %H:%M")}

EMPRESA (PJ):
  Faturamento Bruto: R$ {pj['gross_revenue']:,.2f}
  Simples Nacional:  R$ {pj['total_taxes']:,.2f} ({pj['effective_tax_rate']:.1f}%)
  Receita Liquida:   R$ {pj['net_revenue']:,.2f}

CONSOLIDADO (PJ + PF):
  Renda Total:       R$ {cons['total_income']:,.2f}
  Gastos Variaveis:  R$ {cons['pf_expenses']:,.2f}
  Poupanca:          R$ {cons['savings']:,.2f} ({cons['savings_rate']:.1f}%)
"""
    return report


# ==================== CLI ====================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python scrape_contabilizei.py <comando>")
        print("Comandos: status, report, test")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        status = get_sync_status(year, month)
        print(f"\n=== Status {month}/{year} ===")
        print(f"Faturamento: {'✓' if status['has_revenue'] else '✗'} R$ {status['gross_revenue']:,.2f}")
        print(f"Impostos: {'✓' if status['has_taxes'] else '✗'} R$ {status['total_taxes']:,.2f}")
        print(f"Sincronizado: {status['synced_at'] or 'Nunca'}")
        print(f"Precisa sync: {'Sim' if status['needs_sync'] else 'Nao'}")

    elif cmd == "report":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        print(format_sync_report(year, month))

    elif cmd == "test":
        # Teste das funcoes de parse
        print("Testando parse de moeda:")
        tests = ["R$ 36.427,14", "36.427,14", "166,98", "R$ 1.927,34"]
        for t in tests:
            print(f"  {t} -> {parse_brazilian_currency(t)}")

        print("\nTestando parse de competencia:")
        tests = ["Competencia - Nov/2025", "Dezembro 2025", "Jan/2026"]
        for t in tests:
            print(f"  {t} -> {parse_competencia(t)}")

    else:
        print(f"Comando desconhecido: {cmd}")

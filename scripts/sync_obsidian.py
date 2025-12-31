#!/usr/bin/env python3
"""
Obsidian Sync Module
Sincroniza dados do SQLite com arquivos Obsidian para uso com Dataview.
Tambem sincroniza com Excel Dashboard.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Handle both direct execution and module import
try:
    from scripts.finance_db import (
        get_categories,
        get_transactions,
        get_monthly_summary,
        get_active_installments,
        get_pj_monthly_summary,
        get_pj_yearly_summary,
        get_consolidated_summary,
        generate_installment_transactions
    )
    from scripts.sync_excel import sync_dashboard as sync_excel_dashboard
except ImportError:
    from finance_db import (
        get_categories,
        get_transactions,
        get_monthly_summary,
        get_active_installments,
        get_pj_monthly_summary,
        get_pj_yearly_summary,
        get_consolidated_summary,
        generate_installment_transactions
    )
    try:
        from sync_excel import sync_dashboard as sync_excel_dashboard
    except ImportError:
        sync_excel_dashboard = None

# Paths
BASE_PATH = Path(__file__).parent.parent
TRACKING_PATH = BASE_PATH / "tracking"
DATA_PATH = BASE_PATH / "data"

MONTH_NAMES = [
    "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


def generate_dashboard(year: int, month: int) -> str:
    """Gera dashboard principal com dados do banco."""
    summary = get_monthly_summary(year, month)
    installments = get_active_installments()

    # Calcular totais
    total_spent = summary["total_spent"]
    total_budget = summary["total_budget"]
    savings_rate = summary["savings_rate"]

    # Categorias criticas
    critical = [c for c in summary["categories"] if c["status"] == "critical"]
    warning = [c for c in summary["categories"] if c["status"] == "warning"]

    dashboard = f"""---
tipo: dashboard
ano: {year}
mes: {month}
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# Dashboard Financeiro {year}

> Sincronizado automaticamente em: `= this.atualizado`

## Mes Atual: {MONTH_NAMES[month]} {year}

### KPIs Principais

```dataview
TABLE WITHOUT ID
  metrica as "Metrica",
  valor as "Valor",
  meta as "Meta",
  status as "Status"
FROM "tracking/data"
WHERE tipo = "kpi" AND ano = {year} AND mes = {month}
```

| Metrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Gastos Variaveis | R$ {total_spent:,.0f} | R$ {total_budget:,.0f} | {"OK" if total_spent <= total_budget else "Acima"} |
| Taxa Poupanca | {savings_rate:.0f}% | 28% | {"OK" if savings_rate >= 25 else "Atencao"} |
| Categorias Criticas | {len(critical)} | 0 | {"OK" if len(critical) == 0 else "Critico"} |

### Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
"""

    for cat in summary["categories"]:
        icon = cat["icon"]
        name = cat["category"].title()
        spent = cat["total"]
        budget = cat["budget"]
        pct = cat["percent"]
        status_icon = "OK" if cat["status"] == "ok" else ("Atencao" if cat["status"] == "warning" else "Critico")
        dashboard += f"| {icon} {name} | R$ {spent:,.0f} | R$ {budget:,.0f} | {pct:.0f}% | {status_icon} |\n"

    dashboard += f"""
### Distribuicao 50/30/20

| Categoria | Ideal | Atual | Status |
|-----------|-------|-------|--------|
| Necessidades (50%) | R$ 27.500 | *calcular* | - |
| Desejos (30%) | R$ 16.500 | *calcular* | - |
| Poupanca (20%) | R$ 11.000 | R$ {55000 - total_spent:,.0f} | {"OK" if savings_rate >= 20 else "Atencao"} |

---

## Alertas Ativos

"""

    if critical:
        for c in critical:
            excess = c["total"] - c["budget"]
            dashboard += f"- **CRITICO**: {c['icon']} {c['category'].title()} excedeu R$ {excess:,.0f} ({c['percent']:.0f}% do budget)\n"

    if warning:
        for c in warning:
            dashboard += f"- **Atencao**: {c['icon']} {c['category'].title()} em {c['percent']:.0f}% do budget\n"

    if not critical and not warning:
        dashboard += "- Nenhum alerta ativo\n"

    dashboard += f"""
---

## Parcelamentos Ativos

| Descricao | Parcela | Valor | Termina |
|-----------|---------|-------|---------|
"""

    for inst in installments[:10]:
        dashboard += f"| {inst['description'][:25]} | {inst['current_installment']}/{inst['total_installments']} | R$ {inst['installment_amount']:,.0f} | {inst['end_date']} |\n"

    if len(installments) > 10:
        dashboard += f"\n*... e mais {len(installments) - 10} parcelamentos*\n"

    dashboard += f"""
---

## Links Rapidos

- [[2026/{MONTH_NAMES[month]}|Detalhamento {MONTH_NAMES[month]}]]
- [[../obra/Plano-Obra-2026|Plano de Obra]]
- [[../obra/Checklist-Etapas|Checklist Obra]]

---

## Proximas Acoes

"""

    if critical:
        for i, c in enumerate(critical, 1):
            dashboard += f"{i}. [ ] Revisar gastos de {c['category'].title()}\n"

    dashboard += f"{len(critical) + 1}. [ ] Sincronizar fatura BB\n"
    dashboard += f"{len(critical) + 2}. [ ] Atualizar parcelamentos\n"

    return dashboard


def generate_monthly_detail(year: int, month: int) -> str:
    """Gera arquivo de detalhamento mensal."""
    summary = get_monthly_summary(year, month)
    transactions = get_transactions(year=year, month=month, limit=500)

    total_spent = summary["total_spent"]

    detail = f"""---
tipo: mensal
ano: {year}
mes: {month}
mes_nome: {MONTH_NAMES[month]}
total_gasto: {total_spent}
total_transacoes: {len(transactions)}
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# {MONTH_NAMES[month]} {year} - Detalhamento

> Fonte: SQLite Database
> Ultima sincronizacao: `= this.atualizado`

## Resumo do Mes

| Metrica | Valor |
|---------|-------|
| Receita Liquida | R$ 55.000 |
| Total Variaveis | R$ {total_spent:,.0f} |
| Taxa Poupanca | {summary['savings_rate']:.1f}% |

---

## Gastos por Categoria

"""

    for cat in summary["categories"]:
        if cat["total"] > 0:
            detail += f"### {cat['icon']} {cat['category'].title()}\n\n"
            detail += f"**Budget**: R$ {cat['budget']:,.0f} | **Gasto**: R$ {cat['total']:,.0f} | **Status**: {cat['status'].upper()}\n\n"

            # Transacoes desta categoria
            cat_txs = [t for t in transactions if t.get("category_name") == cat["category"]]
            if cat_txs:
                detail += "| Data | Descricao | Valor |\n"
                detail += "|------|-----------|-------|\n"
                for tx in cat_txs[:10]:
                    detail += f"| {tx['date']} | {tx['description'][:30]} | R$ {abs(tx['amount']):,.2f} |\n"
                if len(cat_txs) > 10:
                    detail += f"\n*... e mais {len(cat_txs) - 10} transacoes*\n"
            detail += "\n"

    detail += f"""---

## Todas as Transacoes ({len(transactions)} registros)

| Data | Descricao | Categoria | Valor |
|------|-----------|-----------|-------|
"""

    for tx in transactions[:50]:
        cat_name = tx.get("category_name", "N/A")
        detail += f"| {tx['date']} | {tx['description'][:25]} | {cat_name} | R$ {abs(tx['amount']):,.2f} |\n"

    if len(transactions) > 50:
        detail += f"\n*... e mais {len(transactions) - 50} transacoes*\n"

    return detail


def generate_category_file(category: Dict, year: int) -> str:
    """Gera arquivo de categoria com historico."""
    name = category["name"]
    icon = category["icon"]
    budget = category["budget_monthly"]

    content = f"""---
tipo: categoria
nome: {name}
budget: {budget}
icon: {icon}
---

# {icon} {name.title()}

**Budget Mensal**: R$ {budget:,.0f}

## Historico {year}

```dataview
TABLE WITHOUT ID
  mes_nome as "Mes",
  sum(amount) as "Total",
  round(sum(amount) / {budget} * 100) + "%" as "% Budget"
FROM "tracking/{year}"
WHERE contains(categorias, "{name}")
GROUP BY mes
```

## Transacoes Recentes

```dataview
TABLE WITHOUT ID
  date as "Data",
  description as "Descricao",
  amount as "Valor"
FROM "tracking/transacoes"
WHERE categoria = "{name}"
SORT date DESC
LIMIT 20
```
"""
    return content


def sync_categories(year: int):
    """Sincroniza paginas de categoria."""
    categories = get_categories()
    cat_path = TRACKING_PATH / "categorias"
    cat_path.mkdir(parents=True, exist_ok=True)

    for cat in categories:
        # Get yearly data for this category
        yearly_data = []
        for month in range(1, 13):
            summary = get_monthly_summary(year, month)
            cat_data = next((c for c in summary["categories"] if c["category"] == cat["name"]), None)
            if cat_data:
                yearly_data.append({
                    "month": month,
                    "total": cat_data["total"],
                    "budget": cat_data["budget"],
                    "percent": cat_data["percent"]
                })

        content = generate_category_page(cat, yearly_data)
        file_path = cat_path / f"{cat['name'].title()}.md"
        file_path.write_text(content, encoding="utf-8")

    print(f"  {len(categories)} categorias atualizadas")


def generate_category_page(category: Dict, yearly_data: List[Dict]) -> str:
    """Gera pagina de categoria com dados do ano."""
    name = category["name"]
    icon = category["icon"]
    budget = category["budget_monthly"]

    total_spent = sum(m["total"] for m in yearly_data)
    budget_annual = budget * 12

    content = f"""---
tipo: categoria
nome: {name}
icon: {icon}
budget_mensal: {budget}
---

# {icon} {name.title()}

## Budget Mensal: R$ {budget:,.0f}

---

## Historico 2026

| Mes | Gasto | Budget | % | Status |
|-----|-------|--------|---|--------|
"""

    for m in yearly_data:
        month_name = MONTH_NAMES[m["month"]]
        status = "OK" if m["percent"] <= 90 else ("Atencao" if m["percent"] <= 110 else "Critico")
        if m["total"] > 0:
            content += f"| {month_name} | R$ {m['total']:,.0f} | R$ {budget:,.0f} | {m['percent']:.0f}% | {status} |\n"
        else:
            content += f"| {month_name} | - | R$ {budget:,.0f} | - | - |\n"

    content += f"""
---

## Acumulado Anual

| Metrica | Valor |
|---------|-------|
| Total Gasto | R$ {total_spent:,.0f} |
| Budget Anual | R$ {budget_annual:,.0f} |
| Media Mensal | R$ {total_spent / max(1, len([m for m in yearly_data if m['total'] > 0])):,.0f} |
| % Utilizado | {(total_spent / budget_annual * 100) if budget_annual > 0 else 0:.0f}% |

---

## Links

- [[../Dashboard-Mensal|Dashboard]]
- [[../_Index|Home]]
"""
    return content


def sync_pj(year: int):
    """Sincroniza dados da empresa (PJ) para Obsidian."""
    empresa_path = TRACKING_PATH / "empresa"
    empresa_path.mkdir(parents=True, exist_ok=True)

    # Get yearly summary
    yearly = get_pj_yearly_summary(year)

    # Generate Dashboard-PJ.md
    dashboard_pj = f"""---
tipo: dashboard-pj
ano: {year}
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# Dashboard Empresa (PJ)

> Fonte: Contabilizei (app.contabilizei.com.br)
> Ultima sincronizacao: `= this.atualizado`

---

## Dados da Empresa

| Campo | Valor |
|-------|-------|
| Razao Social | KARL ALVES HACKEL CONSULTORIA EM TECNOLOGIA |
| CNPJ | 49.436.696/0001-92 |
| Regime Tributario | Simples Nacional |
| Inscricao Municipal | 75835193 |
| Contabilidade | Contabilizei |

---

## Faturamento {year}

| Mes | Faturamento | Simples | Liquido |
|-----|-------------|---------|---------|
"""

    # Add monthly data
    for m in range(1, 13):
        pj_month = get_pj_monthly_summary(year, m)
        fat = pj_month.get("gross_revenue", 0)
        simples = pj_month.get("total_taxes", 0)  # Use total_taxes instead of simples_tax
        liquido = pj_month.get("net_revenue", 0)
        if fat > 0 or simples > 0:
            dashboard_pj += f"| {MONTH_NAMES[m]} | R$ {fat:,.0f} | R$ {simples:,.0f} | R$ {liquido:,.0f} |\n"

    # Add totals
    total_fat = yearly.get("total_revenue", 0)
    total_tax = yearly.get("total_taxes", 0)
    total_net = total_fat - total_tax

    dashboard_pj += f"""
---

## Impostos a Pagar

| Guia | Competencia | Vencimento | Valor | Status |
|------|-------------|------------|-------|--------|
| DARF Unificado | Nov/{year} | 30/12/{year} | R$ 166,98 | Pendente |
| Simples Nacional | Dez/{year} | 20/01/{year+1} | A calcular | Futuro |

---

## Despesas Fixas Mensais

| Tipo | Valor | Observacao |
|------|-------|------------|
| Pro-labore | R$ 1.518,00 | Salario do socio |
| INSS (11%) | R$ 166,98 | Sobre pro-labore |
| Contabilizei | R$ 191,90 | Mensalidade |

---

## Resumo Anual {year}

| Metrica | Valor |
|---------|-------|
| Faturamento Total | R$ {total_fat:,.0f} |
| Impostos Total | R$ {total_tax:,.0f} |
| Taxa Efetiva | {yearly.get('effective_rate', 0):.1f}% |

---

## Links

- [[../Dashboard-Mensal|Dashboard Pessoal]]
- [[../_Index|Home]]
- [[Faturamento-{year}|Historico Faturamento]]
- [[Impostos-{year}|Historico Impostos]]
"""

    dashboard_path = empresa_path / "Dashboard-PJ.md"
    dashboard_path.write_text(dashboard_pj, encoding="utf-8")
    print(f"  Dashboard PJ atualizado: {dashboard_path}")

    # Generate Faturamento-{year}.md
    faturamento = f"""---
tipo: faturamento-pj
ano: {year}
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# Faturamento PJ {year}

> Historico de faturamento da empresa
> Fonte: Contabilizei

---

## Resumo Anual

| Metrica | Valor |
|---------|-------|
| Faturamento Total | R$ {total_fat:,.0f} |
| Media Mensal | R$ {total_fat / max(1, yearly.get('months_with_revenue', 1)):,.0f} |

---

## Faturamento Mensal

| Mes | Faturamento | Notas Emitidas | Observacao |
|-----|-------------|----------------|------------|
"""

    for m in range(1, 13):
        pj_month = get_pj_monthly_summary(year, m)
        fat = pj_month.get("gross_revenue", 0)
        if fat > 0:
            faturamento += f"| {MONTH_NAMES[m]} | R$ {fat:,.2f} | - | - |\n"
        else:
            faturamento += f"| {MONTH_NAMES[m]} | - | - | - |\n"

    faturamento += f"""
---

## Links

- [[Dashboard-PJ|Dashboard PJ]]
- [[Impostos-{year}|Impostos {year}]]
"""

    faturamento_path = empresa_path / f"Faturamento-{year}.md"
    faturamento_path.write_text(faturamento, encoding="utf-8")
    print(f"  Faturamento atualizado: {faturamento_path}")

    # Generate Impostos-{year}.md
    impostos = f"""---
tipo: impostos-pj
ano: {year}
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# Impostos PJ {year}

> Historico de impostos (Simples Nacional)
> Regime: Simples Nacional - Anexo III (Servicos)

---

## Resumo Anual

| Metrica | Valor |
|---------|-------|
| Total Impostos | R$ {total_tax:,.2f} |
| Taxa Efetiva Media | {yearly.get('effective_rate', 0):.1f}% |
| Faixa Simples | Anexo III |

---

## Impostos por Mes (Competencia)

| Competencia | Base | Aliquota | Valor | Vencimento | Status |
|-------------|------|----------|-------|------------|--------|
"""

    for m in range(1, 13):
        pj_month = get_pj_monthly_summary(year, m)
        fat = pj_month.get("gross_revenue", 0)
        simples = pj_month.get("total_taxes", 0)  # Use total_taxes
        if fat > 0 or simples > 0:
            rate = (simples / fat * 100) if fat > 0 else 0
            venc = f"20/{m+1:02d}/{year}" if m < 12 else f"20/01/{year+1}"
            impostos += f"| {MONTH_NAMES[m]} | R$ {fat:,.0f} | {rate:.2f}% | R$ {simples:,.2f} | {venc} | Pago |\n"
        else:
            impostos += f"| {MONTH_NAMES[m]} | - | - | - | - | - |\n"

    impostos += f"""
---

## Como Funciona o Simples Nacional

O Simples Nacional e calculado sobre o faturamento bruto:

1. **Anexo III** - Servicos (consultoria, PM)
2. **Aliquota** varia conforme faturamento acumulado 12 meses
3. **Vencimento**: Dia 20 do mes seguinte a competencia
4. **Pagamento**: Via DARF Unificado

---

## Links

- [[Dashboard-PJ|Dashboard PJ]]
- [[Faturamento-{year}|Faturamento {year}]]
"""

    impostos_path = empresa_path / f"Impostos-{year}.md"
    impostos_path.write_text(impostos, encoding="utf-8")
    print(f"  Impostos atualizado: {impostos_path}")


def sync_to_obsidian(year: int, month: int):
    """Sincroniza todos os dados para Obsidian."""
    print(f"Sincronizando {MONTH_NAMES[month]} {year}...")

    # Criar diretorios
    year_path = TRACKING_PATH / str(year)
    year_path.mkdir(parents=True, exist_ok=True)

    # Gerar Dashboard
    dashboard = generate_dashboard(year, month)
    dashboard_path = TRACKING_PATH / "Dashboard-Mensal.md"
    dashboard_path.write_text(dashboard, encoding="utf-8")
    print(f"  Dashboard atualizado: {dashboard_path}")

    # Gerar detalhamento mensal
    detail = generate_monthly_detail(year, month)
    month_path = year_path / f"{MONTH_NAMES[month]}.md"
    month_path.write_text(detail, encoding="utf-8")
    print(f"  Mensal atualizado: {month_path}")

    # Gerar JSON para queries externas
    summary = get_monthly_summary(year, month)
    json_path = DATA_PATH / f"summary_{year}_{month:02d}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  JSON exportado: {json_path}")

    # Sincronizar categorias
    sync_categories(year)

    print("Sincronizacao Obsidian concluida!")
    return summary


def sync_all(year: int, month: int):
    """Sincronizacao completa: SQLite -> Obsidian + Excel."""
    print(f"\n{'='*50}")
    print(f"SINCRONIZACAO COMPLETA - {MONTH_NAMES[month]} {year}")
    print(f"{'='*50}\n")

    # 0. Gerar transacoes de parcelamentos para o mes
    print("[0/4] Gerando transacoes de parcelamentos...")
    inst_result = generate_installment_transactions(year, month)
    print(f"  Parcelamentos: {inst_result['created']} criados, {inst_result['skipped']} ja existentes")

    # 1. Sync Obsidian PF
    print("\n[1/4] Sincronizando Obsidian (PF)...")
    summary = sync_to_obsidian(year, month)

    # 2. Sync PJ
    print("\n[2/4] Sincronizando Obsidian (PJ)...")
    sync_pj(year)

    # 3. Sync Excel
    print("\n[3/4] Sincronizando Excel...")
    if sync_excel_dashboard:
        sync_excel_dashboard(year, month)
    else:
        print("  sync_excel nao disponivel")

    # Get consolidated summary
    consolidated = get_consolidated_summary(year, month)

    print(f"\n{'='*50}")
    print("SINCRONIZACAO COMPLETA!")
    print(f"  Gastos PF: R$ {summary['total_spent']:,.2f}")
    print(f"  Taxa poupanca PF: {summary['savings_rate']:.1f}%")
    print(f"  Receita PJ: R$ {consolidated.get('pj_net_revenue', 0):,.2f}")
    print(f"  Total Disponivel: R$ {consolidated.get('total_income', 55000):,.2f}")
    print(f"{'='*50}\n")

    return summary


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python sync_obsidian.py <comando> [ano] [mes]")
        print("Comandos:")
        print("  sync     - Sincroniza Obsidian (PF)")
        print("  syncpj   - Sincroniza Obsidian (PJ/Empresa)")
        print("  syncall  - Sincroniza Obsidian (PF + PJ) + Excel")
        print("  dashboard - Gera dashboard")
        print("  monthly  - Gera detalhamento mensal")
        sys.exit(1)

    cmd = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month

    if cmd == "sync":
        sync_to_obsidian(year, month)
    elif cmd == "syncall":
        sync_all(year, month)
    elif cmd == "syncpj":
        sync_pj(year)
    elif cmd == "dashboard":
        print(generate_dashboard(year, month))
    elif cmd == "monthly":
        print(generate_monthly_detail(year, month))
    else:
        print(f"Comando desconhecido: {cmd}")

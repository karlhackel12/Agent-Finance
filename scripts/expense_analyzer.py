#!/usr/bin/env python3
"""
Expense Analyzer Module
Analisa padroes de gastos, detecta anomalias e sugere otimizacoes.
"""

import json
import statistics
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from finance_db import (
    get_categories,
    get_transactions,
    get_monthly_summary,
    get_active_installments
)

# Paths
BASE_PATH = Path(__file__).parent.parent
TRACKING_PATH = BASE_PATH / "tracking"

# Configuracao
INCOME = 55000  # Renda mensal liquida
SAVINGS_TARGET = 0.28  # Meta de poupanca (28%)

MONTH_NAMES = [
    "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


@dataclass
class CategoryAnalysis:
    """Analise de uma categoria."""
    name: str
    icon: str
    spent: float
    budget: float
    percent: float
    status: str
    daily_average: float
    transaction_count: int
    largest_transaction: Optional[Dict] = None
    trend: str = "stable"  # up, down, stable


@dataclass
class MonthAnalysis:
    """Analise completa do mes."""
    year: int
    month: int
    total_spent: float
    total_budget: float
    savings_rate: float
    daily_average: float
    days_elapsed: int
    days_remaining: int
    projected_total: float
    categories: List[CategoryAnalysis] = field(default_factory=list)
    top_transactions: List[Dict] = field(default_factory=list)
    anomalies: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ExpenseAnalyzer:
    """Analisador de despesas."""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.summary = get_monthly_summary(year, month)
        self.transactions = get_transactions(year=year, month=month, limit=500)
        self.categories = get_categories()
        self.installments = get_active_installments()

        # Calcular dias
        today = date.today()
        if year == today.year and month == today.month:
            self.days_elapsed = today.day
        else:
            # Mes passado - todos os dias
            import calendar
            self.days_elapsed = calendar.monthrange(year, month)[1]

        import calendar
        self.days_in_month = calendar.monthrange(year, month)[1]
        self.days_remaining = self.days_in_month - self.days_elapsed

    def full_analysis(self) -> MonthAnalysis:
        """Executa analise completa do mes."""
        total_spent = self.summary["total_spent"]
        total_budget = self.summary["total_budget"]

        # Calcular metricas
        daily_average = total_spent / max(self.days_elapsed, 1)
        projected_total = total_spent + (daily_average * self.days_remaining)
        savings_rate = (INCOME - total_spent) / INCOME * 100

        # Analisar categorias
        categories = self._analyze_categories()

        # Top transacoes
        top_transactions = self._get_top_transactions(10)

        # Detectar anomalias
        anomalies = self._detect_anomalies()

        # Gerar recomendacoes
        recommendations = self._generate_recommendations(categories, savings_rate)

        return MonthAnalysis(
            year=self.year,
            month=self.month,
            total_spent=total_spent,
            total_budget=total_budget,
            savings_rate=savings_rate,
            daily_average=daily_average,
            days_elapsed=self.days_elapsed,
            days_remaining=self.days_remaining,
            projected_total=projected_total,
            categories=categories,
            top_transactions=top_transactions,
            anomalies=anomalies,
            recommendations=recommendations
        )

    def _analyze_categories(self) -> List[CategoryAnalysis]:
        """Analisa cada categoria."""
        analyses = []

        for cat in self.summary["categories"]:
            # Transacoes da categoria
            cat_txs = [t for t in self.transactions if t.get("category_name") == cat["category"]]

            daily_avg = cat["total"] / max(self.days_elapsed, 1)

            largest = None
            if cat_txs:
                largest = max(cat_txs, key=lambda t: abs(t["amount"]))

            analyses.append(CategoryAnalysis(
                name=cat["category"],
                icon=cat["icon"],
                spent=cat["total"],
                budget=cat["budget"],
                percent=cat["percent"],
                status=cat["status"],
                daily_average=daily_avg,
                transaction_count=len(cat_txs),
                largest_transaction=largest,
                trend=self._calculate_trend(cat["category"])
            ))

        return sorted(analyses, key=lambda a: a.spent, reverse=True)

    def _calculate_trend(self, category: str) -> str:
        """Calcula tendencia da categoria (placeholder para comparacao com mes anterior)."""
        # TODO: Implementar quando houver dados historicos
        return "stable"

    def _get_top_transactions(self, limit: int = 10) -> List[Dict]:
        """Retorna as maiores transacoes."""
        sorted_txs = sorted(self.transactions, key=lambda t: abs(t["amount"]), reverse=True)
        return sorted_txs[:limit]

    def _detect_anomalies(self) -> List[Dict]:
        """Detecta transacoes anomalas."""
        anomalies = []

        if len(self.transactions) < 5:
            return anomalies

        # Calcular estatisticas
        amounts = [abs(t["amount"]) for t in self.transactions]
        mean = statistics.mean(amounts)
        stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0

        # Transacoes acima de 2 desvios padrao
        threshold = mean + (2 * stdev)

        for tx in self.transactions:
            if abs(tx["amount"]) > threshold:
                anomalies.append({
                    "transaction": tx,
                    "reason": "valor_atipico",
                    "threshold": threshold,
                    "description": f"Valor R$ {abs(tx['amount']):,.0f} e muito acima da media (R$ {mean:,.0f})"
                })

        return anomalies

    def _generate_recommendations(self, categories: List[CategoryAnalysis], savings_rate: float) -> List[str]:
        """Gera recomendacoes baseadas na analise."""
        recommendations = []

        # Categorias criticas
        critical = [c for c in categories if c.status == "critical"]
        if critical:
            for cat in critical[:3]:
                excess = cat.spent - cat.budget
                recommendations.append(
                    f"URGENTE: Reduzir {cat.icon} {cat.name.title()} - excedeu R$ {excess:,.0f}"
                )

        # Taxa de poupanca
        if savings_rate < SAVINGS_TARGET * 100:
            diff = (SAVINGS_TARGET * 100) - savings_rate
            amount = INCOME * diff / 100
            recommendations.append(
                f"Aumentar poupanca: cortar R$ {amount:,.0f} para atingir meta de {SAVINGS_TARGET*100:.0f}%"
            )

        # Categorias com espaco
        for cat in categories:
            if cat.percent < 50 and cat.budget > 500:
                space = cat.budget - cat.spent
                recommendations.append(
                    f"MARGEM: {cat.icon} {cat.name.title()} tem R$ {space:,.0f} disponivel"
                )
                break

        # Parcelamentos
        total_installments = sum(i["installment_amount"] for i in self.installments)
        if total_installments > 3000:
            recommendations.append(
                f"Parcelamentos comprometem R$ {total_installments:,.0f}/mes - evitar novas compras parceladas"
            )

        return recommendations[:5]  # Limitar a 5 recomendacoes

    def get_savings_suggestions(self) -> List[Dict]:
        """Retorna sugestoes especificas de economia."""
        suggestions = []

        # Categorias acima do budget
        for cat in self.summary["categories"]:
            if cat["percent"] > 100:
                excess = cat["total"] - cat["budget"]
                suggestions.append({
                    "category": cat["category"],
                    "icon": cat["icon"],
                    "type": "reduce_excess",
                    "amount": excess,
                    "message": f"Reduzir R$ {excess:,.0f} em {cat['category'].title()}"
                })

        # Transacoes grandes opcionais (lazer, compras)
        optional_categories = ["lazer", "compras"]
        for tx in self.transactions:
            if tx.get("category_name") in optional_categories and abs(tx["amount"]) > 500:
                suggestions.append({
                    "category": tx.get("category_name"),
                    "type": "large_optional",
                    "amount": abs(tx["amount"]),
                    "message": f"Transacao opcional: {tx['description'][:30]} - R$ {abs(tx['amount']):,.0f}"
                })

        return suggestions

    def project_month_end(self) -> Dict:
        """Projeta situacao no fim do mes."""
        analysis = self.full_analysis()

        projected_savings = INCOME - analysis.projected_total
        projected_rate = projected_savings / INCOME * 100

        # Projetar por categoria
        category_projections = []
        for cat in analysis.categories:
            projected = cat.spent + (cat.daily_average * self.days_remaining)
            will_exceed = projected > cat.budget
            category_projections.append({
                "category": cat.name,
                "icon": cat.icon,
                "current": cat.spent,
                "projected": projected,
                "budget": cat.budget,
                "will_exceed": will_exceed,
                "excess": max(0, projected - cat.budget)
            })

        return {
            "current_spent": analysis.total_spent,
            "projected_spent": analysis.projected_total,
            "projected_savings": projected_savings,
            "projected_savings_rate": projected_rate,
            "days_remaining": self.days_remaining,
            "daily_average": analysis.daily_average,
            "on_track": projected_rate >= SAVINGS_TARGET * 100,
            "categories": category_projections
        }

    def generate_report(self) -> str:
        """Gera relatorio completo em Markdown."""
        analysis = self.full_analysis()
        projection = self.project_month_end()

        report = f"""# Analise de Gastos - {MONTH_NAMES[self.month]} {self.year}

> Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}

## Resumo Executivo

| Metrica | Valor |
|---------|-------|
| Total Gasto | R$ {analysis.total_spent:,.0f} |
| Budget Total | R$ {analysis.total_budget:,.0f} |
| Media Diaria | R$ {analysis.daily_average:,.0f} |
| Taxa Poupanca | {analysis.savings_rate:.1f}% |
| Dias Restantes | {analysis.days_remaining} |

## Projecao de Fechamento

| Metrica | Projetado |
|---------|-----------|
| Gasto Total | R$ {projection['projected_spent']:,.0f} |
| Poupanca | R$ {projection['projected_savings']:,.0f} |
| Taxa Poupanca | {projection['projected_savings_rate']:.1f}% |
| Meta Atingida | {"Sim" if projection['on_track'] else "Nao"} |

## Analise por Categoria

| Categoria | Gasto | Budget | % | Transacoes | Status |
|-----------|-------|--------|---|------------|--------|
"""

        for cat in analysis.categories:
            status_icon = {"ok": "OK", "warning": "ATENCAO", "critical": "CRITICO"}[cat.status]
            report += f"| {cat.icon} {cat.name.title()} | R$ {cat.spent:,.0f} | R$ {cat.budget:,.0f} | {cat.percent:.0f}% | {cat.transaction_count} | {status_icon} |\n"

        report += f"""
## Top 10 Maiores Gastos

| # | Data | Descricao | Categoria | Valor |
|---|------|-----------|-----------|-------|
"""

        for i, tx in enumerate(analysis.top_transactions, 1):
            cat_name = tx.get("category_name", "N/A")
            report += f"| {i} | {tx['date']} | {tx['description'][:25]} | {cat_name} | R$ {abs(tx['amount']):,.0f} |\n"

        if analysis.anomalies:
            report += f"""
## Anomalias Detectadas

"""
            for anomaly in analysis.anomalies:
                tx = anomaly["transaction"]
                report += f"- **{tx['description'][:30]}**: {anomaly['description']}\n"

        report += f"""
## Recomendacoes

"""

        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"

        return report

    def save_to_obsidian(self):
        """Salva analise no Obsidian."""
        report = self.generate_report()
        path = TRACKING_PATH / str(self.year) / f"Analise-{MONTH_NAMES[self.month]}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        print(f"Analise salva em: {path}")


def analyze(year: int, month: int):
    """Funcao conveniente para analise rapida."""
    analyzer = ExpenseAnalyzer(year, month)
    analysis = analyzer.full_analysis()

    print(f"\n=== Analise {MONTH_NAMES[month]} {year} ===\n")

    print("RESUMO")
    print(f"  Total gasto: R$ {analysis.total_spent:,.2f}")
    print(f"  Media diaria: R$ {analysis.daily_average:,.2f}")
    print(f"  Dias restantes: {analysis.days_remaining}")
    print(f"  Projecao mes: R$ {analysis.projected_total:,.0f}")
    print(f"  Taxa poupanca: {analysis.savings_rate:.1f}%")

    critical = [c for c in analysis.categories if c.status == "critical"]
    warning = [c for c in analysis.categories if c.status == "warning"]

    if critical or warning:
        print("\nCATEGORIAS CRITICAS")
        for cat in critical:
            print(f"  {cat.icon} {cat.name.title()}: {cat.percent:.0f}% budget (CRITICO)")
        for cat in warning:
            print(f"  {cat.icon} {cat.name.title()}: {cat.percent:.0f}% budget (ATENCAO)")

    print("\nTOP 5 MAIORES GASTOS")
    for i, tx in enumerate(analysis.top_transactions[:5], 1):
        print(f"  {i}. {tx['description'][:30]}: R$ {abs(tx['amount']):,.0f}")

    if analysis.recommendations:
        print("\nRECOMENDAÇÕES")
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python expense_analyzer.py <comando> [ano] [mes]")
        print("Comandos: analyze, trends, savings, projection, report, save")
        sys.exit(1)

    cmd = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month

    analyzer = ExpenseAnalyzer(year, month)

    if cmd == "analyze":
        analyze(year, month)
    elif cmd == "savings":
        suggestions = analyzer.get_savings_suggestions()
        print(f"\n=== Sugestoes de Economia ===\n")
        for s in suggestions:
            print(f"  {s['icon']} {s['message']}")
    elif cmd == "projection":
        proj = analyzer.project_month_end()
        print(f"\n=== Projecao {MONTH_NAMES[month]} {year} ===\n")
        print(f"  Gasto atual: R$ {proj['current_spent']:,.0f}")
        print(f"  Projecao: R$ {proj['projected_spent']:,.0f}")
        print(f"  Poupanca: R$ {proj['projected_savings']:,.0f} ({proj['projected_savings_rate']:.1f}%)")
        print(f"  Meta: {'ATINGIDA' if proj['on_track'] else 'NAO ATINGIDA'}")
    elif cmd == "report":
        print(analyzer.generate_report())
    elif cmd == "save":
        analyzer.save_to_obsidian()
    else:
        print(f"Comando desconhecido: {cmd}")

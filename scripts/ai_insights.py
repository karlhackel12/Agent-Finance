#!/usr/bin/env python3
"""
AI Insights Module
Analise preditiva, deteccao de padroes e recomendacoes personalizadas.
"""

import json
import math
import random
import statistics
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

from finance_db import (
    get_categories,
    get_transactions,
    get_monthly_summary,
    get_active_installments
)

# Configuracao do usuario - Dados reais do CLAUDE.md
USER_PROFILE = {
    "income": 55000,           # Renda mensal liquida (R$ 55-60k)
    "income_usd": 12000,       # Renda bruta USD
    "exchange_rate": 6.00,     # Taxa cambio base
    "savings_target": 0.35,    # Meta de poupanca (35% - agressivo)
    "emergency_fund_months": 24,  # Meses de reserva de emergencia
    "emergency_target_2025": 240000,  # Tier 1 reserve
    "emergency_target_2026": 480000,  # Tier 2 reserve
    "retirement_year": 2035,   # Ano alvo independencia financeira
    "retirement_target": 7700000,  # Patrimonio alvo
    "passive_income_target": 21700,  # Renda passiva mensal alvo
    "current_assets": 30000,   # Patrimonio atual estimado (inicio 2026)
    "expected_return": 0.11,   # Retorno anual esperado (11%)
    "inflation": 0.045,        # Inflacao anual (4.5%)
    "net_worth_2025": 365000,  # Meta patrimonio 2025
    "net_worth_2026": 800000,  # Meta patrimonio 2026
    "net_worth_2030": 4000000, # Meta patrimonio 2030
    # Compromissos fixos mensais
    "fixed_commitments": {
        "home_loan": 7500,
        "car_subscription": 3200,
        "health_insurance": 1300,
        "work_subscriptions": 661,
        "streaming": 350,
    },
    "total_fixed": 13011,      # Total fixos mensais
}

# Paths
BASE_PATH = Path(__file__).parent.parent

MONTH_NAMES = [
    "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


class TrendDirection(Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class Prediction:
    """Previsao de gasto."""
    category: str
    predicted_amount: float
    confidence: float  # 0-1
    trend: TrendDirection
    factors: List[str]


@dataclass
class Pattern:
    """Padrao detectado."""
    type: str  # seasonal, recurring, anomaly, trend
    description: str
    confidence: float
    data: Dict


@dataclass
class Scenario:
    """Cenario what-if."""
    name: str
    changes: Dict[str, float]  # categoria -> mudanca %
    projected_savings: float
    projected_savings_rate: float
    impact_description: str


@dataclass
class Goal:
    """Meta financeira."""
    name: str
    target_amount: float
    current_amount: float
    deadline: str
    monthly_required: float
    on_track: bool
    progress_percent: float


class SpendingPredictor:
    """Modelo de previsao de gastos."""

    def __init__(self, history_months: int = 6):
        self.history_months = history_months
        self.category_history: Dict[str, List[float]] = defaultdict(list)
        self._load_history()

    def _load_history(self):
        """Carrega historico de gastos."""
        today = date.today()

        for i in range(self.history_months):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1

            try:
                summary = get_monthly_summary(year, month)
                for cat in summary["categories"]:
                    self.category_history[cat["category"]].append(cat["total"])
            except:
                pass

    def predict_category(self, category: str) -> Prediction:
        """Preve gasto de uma categoria para proximo mes."""
        history = self.category_history.get(category, [])

        if len(history) < 2:
            # Sem historico suficiente, usar budget
            cats = get_categories()
            cat_info = next((c for c in cats if c["name"] == category), None)
            budget = cat_info["budget_monthly"] if cat_info else 1000

            return Prediction(
                category=category,
                predicted_amount=budget,
                confidence=0.3,
                trend=TrendDirection.STABLE,
                factors=["Sem historico suficiente, usando budget como base"]
            )

        # Calcular media e tendencia
        mean = statistics.mean(history)

        # Tendencia simples (ultimos 3 vs anteriores)
        if len(history) >= 4:
            recent = statistics.mean(history[:3])
            older = statistics.mean(history[3:])
            trend_pct = (recent - older) / older if older > 0 else 0
        else:
            trend_pct = 0

        # Determinar direcao
        if trend_pct > 0.1:
            trend = TrendDirection.UP
            predicted = mean * 1.1
        elif trend_pct < -0.1:
            trend = TrendDirection.DOWN
            predicted = mean * 0.9
        else:
            trend = TrendDirection.STABLE
            predicted = mean

        # Fatores explicativos
        factors = []
        if trend == TrendDirection.UP:
            factors.append(f"Tendencia de alta: +{trend_pct*100:.0f}% nos ultimos meses")
        elif trend == TrendDirection.DOWN:
            factors.append(f"Tendencia de queda: {trend_pct*100:.0f}% nos ultimos meses")

        # Confianca baseada em variabilidade
        if len(history) >= 3:
            cv = statistics.stdev(history) / mean if mean > 0 else 1
            confidence = max(0.3, min(0.9, 1 - cv))
        else:
            confidence = 0.5

        return Prediction(
            category=category,
            predicted_amount=predicted,
            confidence=confidence,
            trend=trend,
            factors=factors
        )

    def predict_all(self) -> Dict[str, Prediction]:
        """Preve gastos de todas as categorias."""
        categories = get_categories()
        predictions = {}

        for cat in categories:
            predictions[cat["name"]] = self.predict_category(cat["name"])

        return predictions

    def predict_total(self) -> Tuple[float, float]:
        """Preve gasto total e taxa de poupanca."""
        predictions = self.predict_all()
        total = sum(p.predicted_amount for p in predictions.values())
        savings_rate = (USER_PROFILE["income"] - total) / USER_PROFILE["income"]
        return total, savings_rate


class PatternDetector:
    """Detector de padroes em gastos."""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.transactions = get_transactions(year=year, month=month, limit=500)
        self.summary = get_monthly_summary(year, month)

    def detect_all(self) -> List[Pattern]:
        """Detecta todos os padroes."""
        patterns = []
        patterns.extend(self._detect_recurring())
        patterns.extend(self._detect_day_patterns())
        patterns.extend(self._detect_category_concentration())
        patterns.extend(self._detect_large_purchases())
        return patterns

    def _detect_recurring(self) -> List[Pattern]:
        """Detecta gastos recorrentes."""
        patterns = []

        # Agrupar por descricao similar
        desc_amounts = defaultdict(list)
        for tx in self.transactions:
            # Simplificar descricao
            desc = tx["description"].split("*")[0].strip().upper()
            desc_amounts[desc].append(abs(tx["amount"]))

        for desc, amounts in desc_amounts.items():
            if len(amounts) >= 2:
                # Verificar se valores sao similares (recorrente)
                if len(set(amounts)) == 1 or (max(amounts) - min(amounts)) / max(amounts) < 0.1:
                    patterns.append(Pattern(
                        type="recurring",
                        description=f"Gasto recorrente detectado: {desc}",
                        confidence=0.8,
                        data={
                            "merchant": desc,
                            "amount": amounts[0],
                            "frequency": len(amounts)
                        }
                    ))

        return patterns

    def _detect_day_patterns(self) -> List[Pattern]:
        """Detecta padroes por dia da semana."""
        patterns = []

        day_spending = defaultdict(float)
        day_count = defaultdict(int)

        for tx in self.transactions:
            try:
                tx_date = datetime.strptime(tx["date"], "%Y-%m-%d")
                day_name = tx_date.strftime("%A")
                day_spending[day_name] += abs(tx["amount"])
                day_count[day_name] += 1
            except:
                pass

        if day_spending:
            max_day = max(day_spending, key=day_spending.get)
            max_amount = day_spending[max_day]
            avg = sum(day_spending.values()) / len(day_spending)

            if max_amount > avg * 1.5:
                patterns.append(Pattern(
                    type="day_pattern",
                    description=f"Gastos concentrados em {max_day}: R$ {max_amount:,.0f}",
                    confidence=0.7,
                    data={
                        "day": max_day,
                        "amount": max_amount,
                        "average": avg
                    }
                ))

        return patterns

    def _detect_category_concentration(self) -> List[Pattern]:
        """Detecta concentracao excessiva em categorias."""
        patterns = []
        total = self.summary["total_spent"]

        for cat in self.summary["categories"]:
            if total > 0:
                pct = cat["total"] / total * 100
                if pct > 40:
                    patterns.append(Pattern(
                        type="concentration",
                        description=f"{cat['icon']} {cat['category'].title()} representa {pct:.0f}% dos gastos",
                        confidence=0.9,
                        data={
                            "category": cat["category"],
                            "percent": pct,
                            "amount": cat["total"]
                        }
                    ))

        return patterns

    def _detect_large_purchases(self) -> List[Pattern]:
        """Detecta compras grandes atipicas."""
        patterns = []

        if len(self.transactions) < 5:
            return patterns

        amounts = [abs(tx["amount"]) for tx in self.transactions]
        mean = statistics.mean(amounts)
        stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0

        for tx in self.transactions:
            if abs(tx["amount"]) > mean + 2 * stdev:
                patterns.append(Pattern(
                    type="large_purchase",
                    description=f"Compra atipica: {tx['description'][:30]} - R$ {abs(tx['amount']):,.0f}",
                    confidence=0.85,
                    data={
                        "transaction": tx,
                        "zscore": (abs(tx["amount"]) - mean) / stdev if stdev > 0 else 0
                    }
                ))

        return patterns


class ScenarioSimulator:
    """Simulador de cenarios what-if."""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.summary = get_monthly_summary(year, month)
        self.base_spending = self.summary["total_spent"]
        self.income = USER_PROFILE["income"]

    def simulate(self, changes: Dict[str, float]) -> Scenario:
        """
        Simula cenario com mudancas percentuais por categoria.
        changes: {"alimentacao": -20, "lazer": -50} significa -20% em alimentacao, -50% em lazer
        """
        new_spending = 0
        impact_parts = []

        for cat in self.summary["categories"]:
            cat_name = cat["category"]
            original = cat["total"]

            if cat_name in changes:
                change_pct = changes[cat_name]
                new_amount = original * (1 + change_pct / 100)
                diff = new_amount - original
                new_spending += new_amount

                if abs(diff) > 10:
                    direction = "reduzir" if diff < 0 else "aumentar"
                    impact_parts.append(f"{cat['icon']} {cat_name}: {direction} R$ {abs(diff):,.0f}")
            else:
                new_spending += original

        projected_savings = self.income - new_spending
        projected_rate = projected_savings / self.income * 100

        return Scenario(
            name="Cenario Personalizado",
            changes=changes,
            projected_savings=projected_savings,
            projected_savings_rate=projected_rate,
            impact_description="; ".join(impact_parts) if impact_parts else "Sem mudancas"
        )

    def preset_scenarios(self) -> List[Scenario]:
        """Retorna cenarios pre-definidos."""
        scenarios = []

        # Cenario 1: Corte agressivo
        scenarios.append(self.simulate({
            "alimentacao": -20,
            "lazer": -50,
            "compras": -30
        }))
        scenarios[-1].name = "Corte Agressivo"

        # Cenario 2: Corte moderado
        scenarios.append(self.simulate({
            "alimentacao": -10,
            "lazer": -20,
            "compras": -15
        }))
        scenarios[-1].name = "Corte Moderado"

        # Cenario 3: Foco em categorias criticas
        critical = [c["category"] for c in self.summary["categories"] if c["status"] == "critical"]
        if critical:
            changes = {cat: -30 for cat in critical}
            scenarios.append(self.simulate(changes))
            scenarios[-1].name = "Foco em Categorias Criticas"

        # Cenario 4: Meta de 30% poupanca
        target_savings = self.income * 0.30
        current_savings = self.income - self.base_spending
        needed_cut = target_savings - current_savings

        if needed_cut > 0:
            # Distribuir corte proporcionalmente
            changes = {}
            for cat in self.summary["categories"]:
                if cat["total"] > 0:
                    cut_pct = (needed_cut / self.base_spending) * 100
                    changes[cat["category"]] = -cut_pct
            scenarios.append(self.simulate(changes))
            scenarios[-1].name = "Meta 30% Poupanca"

        return scenarios


class GoalTracker:
    """Acompanhamento de metas financeiras."""

    def __init__(self):
        self.goals: List[Goal] = []
        self._init_default_goals()

    def _init_default_goals(self):
        """Inicializa metas reais do usuario baseadas em CLAUDE.md."""
        today = date.today()
        current = USER_PROFILE["current_assets"]

        # Meta 1: Reserva Tier 1 (6 meses = R$ 240k)
        self.goals.append(self._create_goal(
            name="Reserva Tier 1 (6 meses)",
            target=USER_PROFILE["emergency_target_2025"],
            current=current * 0.5,  # 50% do patrimonio em reserva
            deadline="2025-12-31"
        ))

        # Meta 2: Patrimonio 2026
        self.goals.append(self._create_goal(
            name="Patrimonio 2026",
            target=USER_PROFILE["net_worth_2026"],
            current=current,
            deadline="2026-12-31"
        ))

        # Meta 3: Reserva Tier 2 (24 meses = R$ 480k)
        self.goals.append(self._create_goal(
            name="Reserva Tier 2 (24 meses)",
            target=USER_PROFILE["emergency_target_2026"],
            current=current * 0.5,
            deadline="2026-12-31"
        ))

        # Meta 4: Patrimonio 2030
        self.goals.append(self._create_goal(
            name="Patrimonio 2030",
            target=USER_PROFILE["net_worth_2030"],
            current=current,
            deadline="2030-12-31"
        ))

        # Meta 5: Independencia Financeira 2035
        self.goals.append(self._create_goal(
            name="Independencia Financeira 2035",
            target=USER_PROFILE["retirement_target"],
            current=current,
            deadline=f"{USER_PROFILE['retirement_year']}-12-31"
        ))

    def _create_goal(self, name: str, target: float, current: float, deadline: str) -> Goal:
        """Cria uma meta com calculos."""
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            months_remaining = (deadline_date.year - date.today().year) * 12 + \
                              (deadline_date.month - date.today().month)
            months_remaining = max(1, months_remaining)
        except:
            months_remaining = 12

        remaining = target - current
        monthly_required = remaining / months_remaining if remaining > 0 else 0

        # Verificar se esta no caminho
        expected_monthly = USER_PROFILE["income"] * USER_PROFILE["savings_target"]
        on_track = monthly_required <= expected_monthly

        progress = (current / target * 100) if target > 0 else 0

        return Goal(
            name=name,
            target_amount=target,
            current_amount=current,
            deadline=deadline,
            monthly_required=monthly_required,
            on_track=on_track,
            progress_percent=progress
        )

    def project_wealth(self, years: int = 10, simulations: int = 1000) -> Dict:
        """Projeta patrimonio usando Monte Carlo."""
        income = USER_PROFILE["income"]
        savings_rate = USER_PROFILE["savings_target"]
        expected_return = USER_PROFILE["expected_return"]
        inflation = USER_PROFILE["inflation"]
        current = USER_PROFILE["current_assets"]

        # Volatilidade anual (desvio padrao dos retornos)
        volatility = 0.15  # 15% de volatilidade anual

        results = []

        for _ in range(simulations):
            wealth = current
            monthly_savings = income * savings_rate

            for year in range(years):
                # Retorno anual com variacao aleatoria (distribuicao normal)
                annual_return = random.gauss(expected_return, volatility)

                # Adicionar poupanca anual
                annual_savings = monthly_savings * 12

                # Aplicar retorno e adicionar poupanca
                wealth = wealth * (1 + annual_return) + annual_savings

                # Ajustar poupanca pela inflacao
                monthly_savings *= (1 + inflation)

            results.append(wealth)

        results.sort()

        return {
            "years": years,
            "simulations": simulations,
            "current": current,
            "percentile_10": results[int(simulations * 0.10)],
            "percentile_25": results[int(simulations * 0.25)],
            "median": results[int(simulations * 0.50)],
            "percentile_75": results[int(simulations * 0.75)],
            "percentile_90": results[int(simulations * 0.90)],
            "mean": statistics.mean(results),
            "target": USER_PROFILE["retirement_target"],
            "probability_success": sum(1 for r in results if r >= USER_PROFILE["retirement_target"]) / simulations
        }


class RecommendationEngine:
    """Engine de recomendacoes personalizadas."""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.summary = get_monthly_summary(year, month)
        self.predictor = SpendingPredictor()
        self.detector = PatternDetector(year, month)
        self.simulator = ScenarioSimulator(year, month)
        self.goal_tracker = GoalTracker()

    def generate_recommendations(self) -> List[Dict]:
        """Gera recomendacoes personalizadas."""
        recommendations = []

        # 1. Recomendacoes baseadas em budget
        recommendations.extend(self._budget_recommendations())

        # 2. Recomendacoes baseadas em padroes
        recommendations.extend(self._pattern_recommendations())

        # 3. Recomendacoes baseadas em metas
        recommendations.extend(self._goal_recommendations())

        # 4. Recomendacoes de otimizacao
        recommendations.extend(self._optimization_recommendations())

        # Ordenar por prioridade
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

        return recommendations[:10]  # Top 10 recomendacoes

    def _budget_recommendations(self) -> List[Dict]:
        """Recomendacoes baseadas em analise de budget."""
        recs = []

        for cat in self.summary["categories"]:
            if cat["status"] == "critical":
                excess = cat["total"] - cat["budget"]
                recs.append({
                    "type": "budget",
                    "priority": "high",
                    "category": cat["category"],
                    "icon": cat["icon"],
                    "title": f"Reduzir {cat['category'].title()}",
                    "description": f"Categoria excedeu budget em R$ {excess:,.0f}. "
                                   f"Considere revisar gastos nesta area.",
                    "action": f"Cortar R$ {excess:,.0f} em {cat['category']}",
                    "impact": f"Aumenta poupanca em {excess/USER_PROFILE['income']*100:.1f}%"
                })
            elif cat["status"] == "warning" and cat["percent"] > 95:
                remaining = cat["budget"] - cat["total"]
                recs.append({
                    "type": "budget",
                    "priority": "medium",
                    "category": cat["category"],
                    "icon": cat["icon"],
                    "title": f"Atencao com {cat['category'].title()}",
                    "description": f"Categoria em {cat['percent']:.0f}% do budget. "
                                   f"Resta apenas R$ {remaining:,.0f}.",
                    "action": f"Limitar gastos a R$ {remaining:,.0f}",
                    "impact": "Evita estouro de budget"
                })

        return recs

    def _pattern_recommendations(self) -> List[Dict]:
        """Recomendacoes baseadas em padroes detectados."""
        recs = []
        patterns = self.detector.detect_all()

        for pattern in patterns:
            if pattern.type == "recurring":
                recs.append({
                    "type": "pattern",
                    "priority": "low",
                    "title": "Gasto recorrente identificado",
                    "description": pattern.description,
                    "action": "Avaliar necessidade e possibilidade de cancelamento",
                    "impact": f"Potencial economia de R$ {pattern.data.get('amount', 0):,.0f}/mes"
                })
            elif pattern.type == "concentration":
                recs.append({
                    "type": "pattern",
                    "priority": "medium",
                    "title": "Concentracao de gastos",
                    "description": pattern.description,
                    "action": "Diversificar gastos ou revisar categoria",
                    "impact": "Maior controle orcamentario"
                })

        return recs

    def _goal_recommendations(self) -> List[Dict]:
        """Recomendacoes baseadas em metas."""
        recs = []

        for goal in self.goal_tracker.goals:
            if not goal.on_track:
                shortfall = goal.monthly_required - (USER_PROFILE["income"] * USER_PROFILE["savings_target"])
                recs.append({
                    "type": "goal",
                    "priority": "high",
                    "title": f"Meta '{goal.name}' em risco",
                    "description": f"Precisa poupar R$ {goal.monthly_required:,.0f}/mes, "
                                   f"mas meta atual e R$ {USER_PROFILE['income'] * USER_PROFILE['savings_target']:,.0f}.",
                    "action": f"Aumentar poupanca em R$ {shortfall:,.0f}/mes",
                    "impact": f"Atingir {goal.name} ate {goal.deadline}"
                })

        return recs

    def _optimization_recommendations(self) -> List[Dict]:
        """Recomendacoes de otimizacao geral."""
        recs = []

        # Verificar taxa de poupanca
        savings_rate = self.summary["savings_rate"]
        target = USER_PROFILE["savings_target"] * 100

        if savings_rate < target:
            diff = target - savings_rate
            amount = USER_PROFILE["income"] * diff / 100
            recs.append({
                "type": "optimization",
                "priority": "high",
                "title": "Taxa de poupanca abaixo da meta",
                "description": f"Atual: {savings_rate:.1f}%, Meta: {target:.0f}%",
                "action": f"Reduzir gastos em R$ {amount:,.0f}",
                "impact": f"Atingir meta de {target:.0f}% de poupanca"
            })

        # Verificar parcelamentos
        installments = get_active_installments()
        total_installments = sum(i["installment_amount"] for i in installments)

        if total_installments > USER_PROFILE["income"] * 0.1:
            recs.append({
                "type": "optimization",
                "priority": "medium",
                "title": "Alto comprometimento com parcelamentos",
                "description": f"R$ {total_installments:,.0f}/mes em parcelamentos "
                               f"({total_installments/USER_PROFILE['income']*100:.1f}% da renda)",
                "action": "Evitar novas compras parceladas",
                "impact": "Liberar fluxo de caixa futuro"
            })

        return recs


def generate_insights_report(year: int, month: int) -> str:
    """Gera relatorio completo de insights."""
    predictor = SpendingPredictor()
    detector = PatternDetector(year, month)
    simulator = ScenarioSimulator(year, month)
    goal_tracker = GoalTracker()
    engine = RecommendationEngine(year, month)

    predictions = predictor.predict_all()
    patterns = detector.detect_all()
    scenarios = simulator.preset_scenarios()
    goals = goal_tracker.goals
    recommendations = engine.generate_recommendations()
    wealth_projection = goal_tracker.project_wealth(10, 500)

    report = f"""# Insights Financeiros - {MONTH_NAMES[month]} {year}

> Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}
> Powered by AI Insights Engine

---

## Previsao para Proximo Mes

| Categoria | Previsao | Confianca | Tendencia |
|-----------|----------|-----------|-----------|
"""

    for cat_name, pred in predictions.items():
        trend_icon = {"up": "↑", "down": "↓", "stable": "→"}[pred.trend.value]
        report += f"| {cat_name.title()} | R$ {pred.predicted_amount:,.0f} | {pred.confidence*100:.0f}% | {trend_icon} |\n"

    total_pred, rate_pred = predictor.predict_total()
    report += f"\n**Total Previsto**: R$ {total_pred:,.0f} | **Taxa Poupanca Prevista**: {rate_pred*100:.1f}%\n"

    report += f"""
---

## Padroes Detectados

"""

    if patterns:
        for pattern in patterns:
            report += f"- **{pattern.type.title()}**: {pattern.description} (confianca: {pattern.confidence*100:.0f}%)\n"
    else:
        report += "Nenhum padrao significativo detectado.\n"

    report += f"""
---

## Cenarios What-If

| Cenario | Poupanca Projetada | Taxa |
|---------|-------------------|------|
"""

    for scenario in scenarios:
        report += f"| {scenario.name} | R$ {scenario.projected_savings:,.0f} | {scenario.projected_savings_rate:.1f}% |\n"

    report += f"""
---

## Acompanhamento de Metas

| Meta | Progresso | Necessario/Mes | Status |
|------|-----------|----------------|--------|
"""

    for goal in goals:
        status = "No caminho" if goal.on_track else "ATENCAO"
        report += f"| {goal.name} | {goal.progress_percent:.1f}% | R$ {goal.monthly_required:,.0f} | {status} |\n"

    report += f"""
---

## Projecao de Patrimonio (10 anos - Monte Carlo)

| Percentil | Valor Projetado |
|-----------|-----------------|
| Pessimista (10%) | R$ {wealth_projection['percentile_10']:,.0f} |
| Conservador (25%) | R$ {wealth_projection['percentile_25']:,.0f} |
| Mediana (50%) | R$ {wealth_projection['median']:,.0f} |
| Otimista (75%) | R$ {wealth_projection['percentile_75']:,.0f} |
| Muito Otimista (90%) | R$ {wealth_projection['percentile_90']:,.0f} |

**Meta**: R$ {wealth_projection['target']:,.0f}
**Probabilidade de Sucesso**: {wealth_projection['probability_success']*100:.1f}%

---

## Top Recomendacoes

"""

    for i, rec in enumerate(recommendations, 1):
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["priority"]]
        report += f"""### {i}. {priority_icon} {rec['title']}

**{rec['description']}**

- **Acao**: {rec['action']}
- **Impacto**: {rec['impact']}

"""

    return report


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ai_insights.py <comando> [ano] [mes]")
        print("Comandos: report, predict, patterns, scenarios, goals, wealth, recommend")
        sys.exit(1)

    cmd = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month

    if cmd == "report":
        print(generate_insights_report(year, month))

    elif cmd == "predict":
        predictor = SpendingPredictor()
        predictions = predictor.predict_all()
        print(f"\n=== Previsoes para Proximo Mes ===\n")
        for cat, pred in predictions.items():
            print(f"  {cat.title()}: R$ {pred.predicted_amount:,.0f} ({pred.confidence*100:.0f}% confianca)")
        total, rate = predictor.predict_total()
        print(f"\n  TOTAL: R$ {total:,.0f} | Poupanca: {rate*100:.1f}%")

    elif cmd == "patterns":
        detector = PatternDetector(year, month)
        patterns = detector.detect_all()
        print(f"\n=== Padroes Detectados ===\n")
        for pattern in patterns:
            print(f"  [{pattern.type}] {pattern.description}")

    elif cmd == "scenarios":
        simulator = ScenarioSimulator(year, month)
        scenarios = simulator.preset_scenarios()
        print(f"\n=== Cenarios What-If ===\n")
        for scenario in scenarios:
            print(f"  {scenario.name}: R$ {scenario.projected_savings:,.0f} ({scenario.projected_savings_rate:.1f}%)")

    elif cmd == "goals":
        tracker = GoalTracker()
        print(f"\n=== Metas Financeiras ===\n")
        for goal in tracker.goals:
            status = "OK" if goal.on_track else "ATENCAO"
            print(f"  {goal.name}: {goal.progress_percent:.1f}% - {status}")
            print(f"    Necessario: R$ {goal.monthly_required:,.0f}/mes")

    elif cmd == "wealth":
        tracker = GoalTracker()
        projection = tracker.project_wealth(10, 1000)
        print(f"\n=== Projecao de Patrimonio (10 anos) ===\n")
        print(f"  Mediana: R$ {projection['median']:,.0f}")
        print(f"  Probabilidade de sucesso: {projection['probability_success']*100:.1f}%")

    elif cmd == "recommend":
        engine = RecommendationEngine(year, month)
        recs = engine.generate_recommendations()
        print(f"\n=== Top Recomendacoes ===\n")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")
            print(f"     {rec['action']}")

    else:
        print(f"Comando desconhecido: {cmd}")

#!/usr/bin/env python3
"""
Budget Optimizer - AI-powered budget allocation suggestions
Analyzes spending patterns to recommend budget adjustments
"""

import sqlite3
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

DB_PATH = Path(__file__).parent.parent.parent / "data" / "finance.db"

# Import finance_db to ensure database exists with correct schema
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from finance_db import ensure_database_exists
    ensure_database_exists()
except ImportError:
    pass


@dataclass
class BudgetRecommendation:
    """A budget adjustment recommendation."""
    category: str
    current_budget: float
    suggested_budget: float
    change: float
    change_pct: float
    reason: str
    priority: str  # 'high', 'medium', 'low'
    confidence: float


class BudgetOptimizer:
    """
    AI-powered budget optimizer.

    Analyzes historical spending patterns to suggest:
    - Categories where budget is too tight
    - Categories where budget has slack
    - Optimal reallocation strategies
    """

    # Categories considered essential (harder to cut)
    ESSENTIAL_CATEGORIES = {'alimentacao', 'saude', 'transporte', 'casa'}

    # Categories that are discretionary (easier to cut)
    DISCRETIONARY_CATEGORIES = {'lazer', 'compras', 'assinaturas'}

    def __init__(self, analysis_months: int = 6):
        """
        Initialize optimizer.

        Args:
            analysis_months: Number of months to analyze
        """
        self.analysis_months = analysis_months
        self.current_budgets: Dict[str, float] = {}
        self.spending_history: Dict[str, List[float]] = {}
        self.utilization: Dict[str, Dict] = {}

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def load_budgets(self) -> Dict[str, float]:
        """Load current budget allocations from database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, budget_monthly FROM categories")
        rows = cursor.fetchall()
        conn.close()

        self.current_budgets = {row['name']: row['budget_monthly'] for row in rows}
        return self.current_budgets

    def load_spending_history(self) -> Dict[str, List[float]]:
        """Load monthly spending history by category."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                strftime('%Y-%m', t.date) as month,
                c.name as category,
                SUM(ABS(t.amount)) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense'
            AND t.date >= date('now', ?)
            GROUP BY month, c.name
            ORDER BY month
        '''

        cursor.execute(query, (f'-{self.analysis_months} months',))
        rows = cursor.fetchall()
        conn.close()

        # Organize by category
        from collections import defaultdict
        history: Dict[str, List[float]] = defaultdict(list)

        for row in rows:
            history[row['category']].append(row['total'])

        self.spending_history = dict(history)
        return self.spending_history

    def analyze_utilization(self) -> Dict[str, Dict]:
        """
        Analyze budget utilization for each category.

        Returns:
            Dict with category -> utilization stats
        """
        if not self.current_budgets:
            self.load_budgets()
        if not self.spending_history:
            self.load_spending_history()

        for category, budget in self.current_budgets.items():
            history = self.spending_history.get(category, [])

            if not history:
                self.utilization[category] = {
                    'budget': budget,
                    'avg_spending': 0,
                    'utilization_pct': 0,
                    'status': 'no_data',
                    'variance': 0
                }
                continue

            avg_spending = np.mean(history)
            std_spending = np.std(history) if len(history) > 1 else 0
            max_spending = np.max(history)

            if budget > 0:
                utilization_pct = (avg_spending / budget) * 100
            else:
                utilization_pct = 0

            # Determine status
            if utilization_pct > 100:
                status = 'over_budget'
            elif utilization_pct > 80:
                status = 'tight'
            elif utilization_pct < 50:
                status = 'slack'
            else:
                status = 'healthy'

            self.utilization[category] = {
                'budget': budget,
                'avg_spending': round(avg_spending, 2),
                'max_spending': round(max_spending, 2),
                'utilization_pct': round(utilization_pct, 1),
                'status': status,
                'variance': round(std_spending, 2),
                'months_analyzed': len(history)
            }

        return self.utilization

    def identify_slack_categories(self) -> List[Tuple[str, float]]:
        """
        Identify categories with significant budget slack.

        Returns:
            List of (category, slack_amount) sorted by slack
        """
        if not self.utilization:
            self.analyze_utilization()

        slack = []
        for category, stats in self.utilization.items():
            if stats['status'] == 'slack':
                slack_amount = stats['budget'] - stats['avg_spending']
                slack.append((category, slack_amount))

        return sorted(slack, key=lambda x: x[1], reverse=True)

    def identify_tight_categories(self) -> List[Tuple[str, float]]:
        """
        Identify categories that are over budget or tight.

        Returns:
            List of (category, overage_amount) sorted by need
        """
        if not self.utilization:
            self.analyze_utilization()

        tight = []
        for category, stats in self.utilization.items():
            if stats['status'] in ('over_budget', 'tight'):
                # How much more would be comfortable (avg + 1 std)
                needed = stats['avg_spending'] + stats['variance'] - stats['budget']
                if needed > 0:
                    tight.append((category, needed))

        return sorted(tight, key=lambda x: x[1], reverse=True)

    def suggest_reallocations(self) -> List[BudgetRecommendation]:
        """
        Generate budget reallocation recommendations.

        Returns:
            List of BudgetRecommendation objects
        """
        if not self.utilization:
            self.analyze_utilization()

        recommendations = []
        slack_categories = self.identify_slack_categories()
        tight_categories = self.identify_tight_categories()

        # Total available slack
        total_slack = sum(amount for _, amount in slack_categories)

        # Recommendations for tight categories (increase budget)
        for category, needed in tight_categories:
            stats = self.utilization[category]
            is_essential = category in self.ESSENTIAL_CATEGORIES

            # Suggested increase: cover avg spending + 10% buffer
            suggested = stats['avg_spending'] * 1.1
            change = suggested - stats['budget']

            priority = 'high' if is_essential else 'medium'
            confidence = min(0.9, stats['months_analyzed'] / 6)

            if change > 50:  # Only recommend if change is significant
                recommendations.append(BudgetRecommendation(
                    category=category,
                    current_budget=stats['budget'],
                    suggested_budget=round(suggested, 0),
                    change=round(change, 0),
                    change_pct=round((change / stats['budget']) * 100, 1) if stats['budget'] > 0 else 0,
                    reason=f"Média de gastos R$ {stats['avg_spending']:,.0f} excede budget",
                    priority=priority,
                    confidence=round(confidence, 2)
                ))

        # Recommendations for slack categories (decrease budget)
        for category, slack in slack_categories:
            stats = self.utilization[category]
            is_discretionary = category in self.DISCRETIONARY_CATEGORIES

            # Suggested decrease: avg spending + 20% buffer
            suggested = stats['avg_spending'] * 1.2
            change = suggested - stats['budget']  # Will be negative

            priority = 'medium' if is_discretionary else 'low'
            confidence = min(0.85, stats['months_analyzed'] / 6)

            if abs(change) > 100:  # Only recommend if savings are significant
                recommendations.append(BudgetRecommendation(
                    category=category,
                    current_budget=stats['budget'],
                    suggested_budget=round(suggested, 0),
                    change=round(change, 0),
                    change_pct=round((change / stats['budget']) * 100, 1) if stats['budget'] > 0 else 0,
                    reason=f"Utilização média de apenas {stats['utilization_pct']:.0f}%",
                    priority=priority,
                    confidence=round(confidence, 2)
                ))

        # Sort by priority and then by absolute change
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: (priority_order[x.priority], -abs(x.change)))

        return recommendations

    def simulate_scenario(self, scenario: str = 'moderate') -> Dict:
        """
        Simulate different budget scenarios.

        Args:
            scenario: 'aggressive', 'moderate', or 'conservative'

        Returns:
            Simulated budget with projected savings
        """
        if not self.utilization:
            self.analyze_utilization()

        # Scenario parameters
        scenarios = {
            'aggressive': {'reduction': 0.3, 'target_util': 0.7},   # 30% cut, target 70% utilization
            'moderate': {'reduction': 0.15, 'target_util': 0.8},    # 15% cut, target 80% utilization
            'conservative': {'reduction': 0.05, 'target_util': 0.9}  # 5% cut, target 90% utilization
        }

        params = scenarios.get(scenario, scenarios['moderate'])

        current_total = sum(self.current_budgets.values())
        new_budgets = {}
        savings = 0

        for category, budget in self.current_budgets.items():
            stats = self.utilization.get(category, {})
            avg = stats.get('avg_spending', budget)
            is_essential = category in self.ESSENTIAL_CATEGORIES

            if is_essential:
                # Essential: only reduce if very slack
                if stats.get('utilization_pct', 100) < 50:
                    new_budget = max(avg * 1.1, budget * (1 - params['reduction'] * 0.5))
                else:
                    new_budget = budget  # Keep essential budgets
            else:
                # Discretionary: apply reduction
                target = max(avg * 1.1, budget * (1 - params['reduction']))
                new_budget = target

            new_budgets[category] = round(new_budget, 0)
            savings += budget - new_budget

        return {
            'scenario': scenario,
            'current_total': round(current_total, 0),
            'new_total': round(sum(new_budgets.values()), 0),
            'monthly_savings': round(savings, 0),
            'annual_savings': round(savings * 12, 0),
            'budgets': new_budgets,
            'parameters': params
        }

    def generate_recommendations_report(self) -> Dict:
        """
        Generate comprehensive optimization report.

        Returns:
            Complete optimization report
        """
        self.load_budgets()
        self.load_spending_history()
        self.analyze_utilization()

        recommendations = self.suggest_reallocations()

        # Calculate potential savings from recommendations
        total_decrease = sum(r.change for r in recommendations if r.change < 0)
        total_increase = sum(r.change for r in recommendations if r.change > 0)

        return {
            'generated_at': datetime.now().isoformat(),
            'analysis_months': self.analysis_months,
            'current_total_budget': sum(self.current_budgets.values()),
            'utilization': self.utilization,
            'recommendations': [
                {
                    'category': r.category,
                    'current_budget': r.current_budget,
                    'suggested_budget': r.suggested_budget,
                    'change': r.change,
                    'change_pct': r.change_pct,
                    'reason': r.reason,
                    'priority': r.priority,
                    'confidence': r.confidence
                }
                for r in recommendations
            ],
            'summary': {
                'potential_decrease': round(total_decrease, 0),
                'needed_increase': round(total_increase, 0),
                'net_change': round(total_decrease + total_increase, 0),
                'high_priority_count': sum(1 for r in recommendations if r.priority == 'high')
            },
            'scenarios': {
                'aggressive': self.simulate_scenario('aggressive'),
                'moderate': self.simulate_scenario('moderate'),
                'conservative': self.simulate_scenario('conservative')
            }
        }


def main():
    """Run optimizer and print report."""
    print("=" * 60)
    print("BUDGET OPTIMIZER - Otimização de Budget")
    print("=" * 60)

    optimizer = BudgetOptimizer(analysis_months=6)
    report = optimizer.generate_recommendations_report()

    # Print utilization
    print("\n📊 UTILIZAÇÃO POR CATEGORIA:")
    print("-" * 50)
    print(f"{'Categoria':15} {'Budget':>10} {'Média':>10} {'Util%':>8} {'Status'}")
    print("-" * 50)

    for category, stats in sorted(report['utilization'].items()):
        status_icon = {
            'over_budget': '🔴',
            'tight': '🟠',
            'healthy': '🟢',
            'slack': '🔵',
            'no_data': '⚪'
        }.get(stats['status'], '❓')

        print(f"{category:15} R${stats['budget']:>8,.0f} R${stats['avg_spending']:>8,.0f} "
              f"{stats['utilization_pct']:>6.0f}% {status_icon}")

    # Print recommendations
    recommendations = report['recommendations']
    if recommendations:
        print(f"\n💡 RECOMENDAÇÕES ({len(recommendations)}):")
        print("-" * 50)

        for r in recommendations:
            icon = '📈' if r['change'] > 0 else '📉'
            priority_icon = {'high': '❗', 'medium': '⚠️', 'low': 'ℹ️'}[r['priority']]

            print(f"\n{priority_icon} {r['category'].title()}")
            print(f"   {icon} R$ {r['current_budget']:,.0f} → R$ {r['suggested_budget']:,.0f} ({r['change_pct']:+.0f}%)")
            print(f"   Motivo: {r['reason']}")

    # Print summary
    summary = report['summary']
    print("\n📋 RESUMO:")
    print("-" * 50)
    print(f"   Potencial de redução:  R$ {abs(summary['potential_decrease']):,.0f}/mês")
    print(f"   Aumento necessário:    R$ {summary['needed_increase']:,.0f}/mês")
    print(f"   Economia líquida:      R$ {abs(summary['net_change']):,.0f}/mês = R$ {abs(summary['net_change'] * 12):,.0f}/ano")

    # Print scenarios
    print("\n🎯 CENÁRIOS:")
    print("-" * 50)

    for name, scenario in report['scenarios'].items():
        print(f"\n   {name.upper()}:")
        print(f"   Budget atual: R$ {scenario['current_total']:,.0f}")
        print(f"   Budget novo:  R$ {scenario['new_total']:,.0f}")
        print(f"   Economia:     R$ {scenario['monthly_savings']:,.0f}/mês = R$ {scenario['annual_savings']:,.0f}/ano")

    print("\n" + "=" * 60)

    return report


if __name__ == "__main__":
    main()

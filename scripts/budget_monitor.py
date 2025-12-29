#!/usr/bin/env python3
"""
Budget Monitor Module
Sistema de alertas para monitoramento de budget e gastos.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from finance_db import (
    get_categories,
    get_transactions,
    get_monthly_summary,
    get_active_installments
)

# Configuracao de thresholds
THRESHOLDS = {
    "warning": 80,      # 80% do budget
    "exceeded": 100,    # 100% do budget
    "critical": 120,    # 120% do budget
}

# Configuracao de alertas
ALERT_CONFIG = {
    "large_transaction": 1000,  # Transacoes acima deste valor
    "installment_ending_days": 30,  # Dias antes do fim do parcelamento
    "savings_rate_target": 28,  # Meta de taxa de poupanca
}


@dataclass
class Alert:
    """Representa um alerta do sistema."""
    type: str           # budget_warning, budget_exceeded, large_tx, installment, savings
    severity: str       # info, warning, critical
    category: Optional[str]
    message: str
    value: float
    threshold: float
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}
        return f"{icons.get(self.severity, '•')} {self.message}"


class BudgetMonitor:
    """Monitor de budget e alertas financeiros."""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.summary = get_monthly_summary(year, month)
        self.transactions = get_transactions(year=year, month=month, limit=500)
        self.installments = get_active_installments()
        self.alerts: List[Alert] = []

    def check_all(self) -> List[Alert]:
        """Executa todas as verificacoes e retorna alertas."""
        self.alerts = []
        self._check_budget_thresholds()
        self._check_large_transactions()
        self._check_installments()
        self._check_savings_rate()
        self._check_trends()
        return self.alerts

    def _check_budget_thresholds(self):
        """Verifica se categorias estao acima dos thresholds."""
        for cat in self.summary["categories"]:
            pct = cat["percent"]
            name = cat["category"]
            icon = cat["icon"]
            spent = cat["total"]
            budget = cat["budget"]

            if pct >= THRESHOLDS["critical"]:
                excess = spent - budget
                self.alerts.append(Alert(
                    type="budget_critical",
                    severity="critical",
                    category=name,
                    message=f"{icon} {name.title()} CRITICO: {pct:.0f}% do budget (+R$ {excess:,.0f})",
                    value=pct,
                    threshold=THRESHOLDS["critical"],
                    timestamp=datetime.now().isoformat()
                ))
            elif pct >= THRESHOLDS["exceeded"]:
                excess = spent - budget
                self.alerts.append(Alert(
                    type="budget_exceeded",
                    severity="warning",
                    category=name,
                    message=f"{icon} {name.title()} excedeu budget: {pct:.0f}% (+R$ {excess:,.0f})",
                    value=pct,
                    threshold=THRESHOLDS["exceeded"],
                    timestamp=datetime.now().isoformat()
                ))
            elif pct >= THRESHOLDS["warning"]:
                remaining = budget - spent
                self.alerts.append(Alert(
                    type="budget_warning",
                    severity="info",
                    category=name,
                    message=f"{icon} {name.title()} em {pct:.0f}% do budget (resta R$ {remaining:,.0f})",
                    value=pct,
                    threshold=THRESHOLDS["warning"],
                    timestamp=datetime.now().isoformat()
                ))

    def _check_large_transactions(self):
        """Verifica transacoes grandes."""
        threshold = ALERT_CONFIG["large_transaction"]
        for tx in self.transactions:
            if abs(tx["amount"]) >= threshold:
                self.alerts.append(Alert(
                    type="large_transaction",
                    severity="info",
                    category=tx.get("category_name"),
                    message=f"Transacao grande: {tx['description'][:30]} - R$ {abs(tx['amount']):,.0f}",
                    value=abs(tx["amount"]),
                    threshold=threshold,
                    timestamp=datetime.now().isoformat()
                ))

    def _check_installments(self):
        """Verifica parcelamentos terminando em breve."""
        days_threshold = ALERT_CONFIG["installment_ending_days"]
        today = datetime.now().date()

        for inst in self.installments:
            try:
                end_date = datetime.strptime(inst["end_date"], "%Y-%m-%d").date()
                days_remaining = (end_date - today).days

                if 0 < days_remaining <= days_threshold:
                    self.alerts.append(Alert(
                        type="installment_ending",
                        severity="info",
                        category=inst.get("category_name"),
                        message=f"Parcelamento '{inst['description'][:20]}' termina em {days_remaining} dias",
                        value=days_remaining,
                        threshold=days_threshold,
                        timestamp=datetime.now().isoformat()
                    ))
            except (ValueError, TypeError):
                pass

        # Total comprometido com parcelamentos
        total_installments = sum(i["installment_amount"] for i in self.installments)
        if total_installments > 5000:
            self.alerts.append(Alert(
                type="installments_high",
                severity="warning",
                category=None,
                message=f"Total comprometido em parcelamentos: R$ {total_installments:,.0f}/mes",
                value=total_installments,
                threshold=5000,
                timestamp=datetime.now().isoformat()
            ))

    def _check_savings_rate(self):
        """Verifica taxa de poupanca."""
        target = ALERT_CONFIG["savings_rate_target"]
        current = self.summary["savings_rate"]

        if current < 0:
            self.alerts.append(Alert(
                type="savings_negative",
                severity="critical",
                category=None,
                message=f"Taxa de poupanca NEGATIVA: {current:.1f}% (gastando mais que ganha)",
                value=current,
                threshold=0,
                timestamp=datetime.now().isoformat()
            ))
        elif current < target - 10:
            self.alerts.append(Alert(
                type="savings_low",
                severity="warning",
                category=None,
                message=f"Taxa de poupanca baixa: {current:.1f}% (meta: {target}%)",
                value=current,
                threshold=target,
                timestamp=datetime.now().isoformat()
            ))
        elif current < target:
            self.alerts.append(Alert(
                type="savings_below_target",
                severity="info",
                category=None,
                message=f"Taxa de poupanca: {current:.1f}% (meta: {target}%)",
                value=current,
                threshold=target,
                timestamp=datetime.now().isoformat()
            ))

    def _check_trends(self):
        """Verifica tendencias de gastos (compara com mes anterior)."""
        # Por enquanto, apenas um placeholder
        # TODO: Implementar comparacao com mes anterior quando houver dados
        pass

    def get_summary(self) -> Dict:
        """Retorna resumo dos alertas."""
        critical = [a for a in self.alerts if a.severity == "critical"]
        warning = [a for a in self.alerts if a.severity == "warning"]
        info = [a for a in self.alerts if a.severity == "info"]

        return {
            "total": len(self.alerts),
            "critical": len(critical),
            "warning": len(warning),
            "info": len(info),
            "alerts": [a.to_dict() for a in self.alerts]
        }

    def generate_report(self) -> str:
        """Gera relatorio de alertas em Markdown."""
        if not self.alerts:
            self.check_all()

        critical = [a for a in self.alerts if a.severity == "critical"]
        warning = [a for a in self.alerts if a.severity == "warning"]
        info = [a for a in self.alerts if a.severity == "info"]

        report = f"""# Relatorio de Alertas

> Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}
> Periodo: {self.month:02d}/{self.year}

## Resumo

| Severidade | Quantidade |
|------------|------------|
| Critico | {len(critical)} |
| Atencao | {len(warning)} |
| Info | {len(info)} |
| **Total** | **{len(self.alerts)}** |

"""

        if critical:
            report += "## Alertas Criticos\n\n"
            for a in critical:
                report += f"- {a}\n"
            report += "\n"

        if warning:
            report += "## Alertas de Atencao\n\n"
            for a in warning:
                report += f"- {a}\n"
            report += "\n"

        if info:
            report += "## Informacoes\n\n"
            for a in info:
                report += f"- {a}\n"
            report += "\n"

        # Recomendacoes
        report += "## Recomendacoes\n\n"

        if critical:
            report += "1. **Acao imediata**: Revisar categorias criticas e identificar gastos desnecessarios\n"

        exceeded_cats = [a.category for a in self.alerts if a.type == "budget_exceeded" and a.category]
        if exceeded_cats:
            report += f"2. **Revisar**: Categorias {', '.join(exceeded_cats)} estao acima do budget\n"

        if self.summary["savings_rate"] < ALERT_CONFIG["savings_rate_target"]:
            diff = ALERT_CONFIG["savings_rate_target"] - self.summary["savings_rate"]
            report += f"3. **Aumentar poupanca**: Reduzir gastos em R$ {55000 * diff / 100:,.0f} para atingir meta\n"

        return report


def check_alerts(year: int, month: int) -> List[Alert]:
    """Funcao conveniente para verificar alertas."""
    monitor = BudgetMonitor(year, month)
    return monitor.check_all()


def print_alerts(year: int, month: int):
    """Imprime alertas no console."""
    monitor = BudgetMonitor(year, month)
    alerts = monitor.check_all()

    print(f"\n=== Alertas {month:02d}/{year} ===\n")

    if not alerts:
        print("Nenhum alerta ativo!")
        return

    for alert in sorted(alerts, key=lambda a: {"critical": 0, "warning": 1, "info": 2}[a.severity]):
        print(alert)

    print(f"\nTotal: {len(alerts)} alertas")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python budget_monitor.py <comando> [ano] [mes]")
        print("Comandos: check, report, json")
        sys.exit(1)

    cmd = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month

    if cmd == "check":
        print_alerts(year, month)
    elif cmd == "report":
        monitor = BudgetMonitor(year, month)
        monitor.check_all()
        print(monitor.generate_report())
    elif cmd == "json":
        monitor = BudgetMonitor(year, month)
        monitor.check_all()
        print(json.dumps(monitor.get_summary(), indent=2, ensure_ascii=False))
    else:
        print(f"Comando desconhecido: {cmd}")

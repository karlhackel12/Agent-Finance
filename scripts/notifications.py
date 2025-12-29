#!/usr/bin/env python3
"""
Notifications Module
Sistema de notificacoes para alertas financeiros.
Suporta: Console, Arquivo, Telegram (futuro), Pushover (futuro)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Paths
BASE_PATH = Path(__file__).parent.parent
LOGS_PATH = BASE_PATH / "logs"
CONFIG_PATH = BASE_PATH / "config"


@dataclass
class Notification:
    """Representa uma notificacao."""
    title: str
    message: str
    severity: str  # info, warning, critical
    timestamp: str
    source: str  # budget_monitor, expense_analyzer, etc.
    data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data
        }


class NotificationChannel(ABC):
    """Classe base para canais de notificacao."""

    @abstractmethod
    def send(self, notification: Notification) -> bool:
        """Envia uma notificacao."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Verifica se o canal esta configurado."""
        pass


class ConsoleChannel(NotificationChannel):
    """Canal de notificacao para console."""

    def send(self, notification: Notification) -> bool:
        icons = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "critical": "🔴"
        }
        icon = icons.get(notification.severity, "•")
        print(f"{icon} [{notification.source}] {notification.title}")
        print(f"   {notification.message}")
        return True

    def is_configured(self) -> bool:
        return True


class FileChannel(NotificationChannel):
    """Canal de notificacao para arquivo de log."""

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or LOGS_PATH / "notifications.log"

    def send(self, notification: Notification) -> bool:
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                log_entry = {
                    "timestamp": notification.timestamp,
                    "severity": notification.severity,
                    "source": notification.source,
                    "title": notification.title,
                    "message": notification.message
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
            return False

    def is_configured(self) -> bool:
        return True


class ObsidianChannel(NotificationChannel):
    """Canal de notificacao para arquivo Obsidian."""

    def __init__(self, alerts_file: Optional[Path] = None):
        self.alerts_file = alerts_file or BASE_PATH / "tracking" / "Alertas-Ativos.md"

    def send(self, notification: Notification) -> bool:
        try:
            self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

            # Ler conteudo existente ou criar novo
            if self.alerts_file.exists():
                content = self.alerts_file.read_text(encoding="utf-8")
                # Encontrar secao de alertas
                if "## Alertas Recentes" in content:
                    # Inserir apos o cabecalho
                    parts = content.split("## Alertas Recentes")
                    header = parts[0] + "## Alertas Recentes\n\n"
                    rest = parts[1] if len(parts) > 1 else ""
                else:
                    header = content + "\n## Alertas Recentes\n\n"
                    rest = ""
            else:
                header = f"""---
tipo: alertas
atualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

# Alertas Ativos

## Alertas Recentes

"""
                rest = ""

            # Adicionar novo alerta
            icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}
            icon = icons.get(notification.severity, "•")
            new_alert = f"- {icon} **{notification.title}** ({notification.timestamp[:10]})\n  {notification.message}\n\n"

            # Limitar a 20 alertas recentes
            lines = rest.strip().split("\n\n")
            lines = [l for l in lines if l.strip()][:19]
            rest = "\n\n".join(lines)

            content = header + new_alert + rest
            self.alerts_file.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Erro ao atualizar Obsidian: {e}")
            return False

    def is_configured(self) -> bool:
        return True


class TelegramChannel(NotificationChannel):
    """Canal de notificacao para Telegram (placeholder)."""

    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    def send(self, notification: Notification) -> bool:
        if not self.is_configured():
            return False

        # TODO: Implementar envio real via Telegram API
        # import requests
        # url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        # payload = {
        #     "chat_id": self.chat_id,
        #     "text": f"*{notification.title}*\n{notification.message}",
        #     "parse_mode": "Markdown"
        # }
        # response = requests.post(url, json=payload)
        # return response.ok

        print(f"[TELEGRAM] Notificacao seria enviada: {notification.title}")
        return True

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)


class PushoverChannel(NotificationChannel):
    """Canal de notificacao para Pushover (placeholder)."""

    def __init__(self):
        self.user_key = os.environ.get("PUSHOVER_USER_KEY")
        self.api_token = os.environ.get("PUSHOVER_API_TOKEN")

    def send(self, notification: Notification) -> bool:
        if not self.is_configured():
            return False

        # TODO: Implementar envio real via Pushover API
        # import requests
        # url = "https://api.pushover.net/1/messages.json"
        # payload = {
        #     "token": self.api_token,
        #     "user": self.user_key,
        #     "title": notification.title,
        #     "message": notification.message,
        #     "priority": 1 if notification.severity == "critical" else 0
        # }
        # response = requests.post(url, data=payload)
        # return response.ok

        print(f"[PUSHOVER] Notificacao seria enviada: {notification.title}")
        return True

    def is_configured(self) -> bool:
        return bool(self.user_key and self.api_token)


class NotificationManager:
    """Gerenciador de notificacoes."""

    def __init__(self):
        self.channels: List[NotificationChannel] = []

    def add_channel(self, channel: NotificationChannel):
        """Adiciona um canal de notificacao."""
        if channel.is_configured():
            self.channels.append(channel)

    def notify(self, title: str, message: str, severity: str = "info",
               source: str = "system", data: Optional[Dict] = None) -> bool:
        """Envia notificacao para todos os canais configurados."""
        notification = Notification(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now().isoformat(),
            source=source,
            data=data
        )

        success = True
        for channel in self.channels:
            try:
                result = channel.send(notification)
                success = success and result
            except Exception as e:
                print(f"Erro no canal {channel.__class__.__name__}: {e}")
                success = False

        return success

    def notify_alerts(self, alerts: List[Dict], source: str = "budget_monitor"):
        """Envia multiplos alertas."""
        for alert in alerts:
            self.notify(
                title=alert.get("type", "Alert"),
                message=alert.get("message", ""),
                severity=alert.get("severity", "info"),
                source=source,
                data=alert
            )


def get_default_manager() -> NotificationManager:
    """Retorna gerenciador com canais padrao."""
    manager = NotificationManager()
    manager.add_channel(ConsoleChannel())
    manager.add_channel(FileChannel())
    manager.add_channel(ObsidianChannel())
    manager.add_channel(TelegramChannel())
    manager.add_channel(PushoverChannel())
    return manager


def send_budget_alerts(year: int, month: int):
    """Envia alertas de budget via todos os canais."""
    from budget_monitor import BudgetMonitor

    monitor = BudgetMonitor(year, month)
    alerts = monitor.check_all()

    if not alerts:
        print("Nenhum alerta para enviar.")
        return

    manager = get_default_manager()
    for alert in alerts:
        manager.notify(
            title=alert.type.replace("_", " ").title(),
            message=alert.message,
            severity=alert.severity,
            source="budget_monitor"
        )

    print(f"\n{len(alerts)} alertas enviados para {len(manager.channels)} canais.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python notifications.py <comando> [ano] [mes]")
        print("Comandos: test, alerts, status")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        manager = get_default_manager()
        manager.notify(
            title="Teste de Notificacao",
            message="Esta e uma notificacao de teste do sistema financeiro.",
            severity="info",
            source="test"
        )
        print("Notificacao de teste enviada!")

    elif cmd == "alerts":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        send_budget_alerts(year, month)

    elif cmd == "status":
        manager = get_default_manager()
        print("\n=== Status dos Canais ===\n")
        for channel in [ConsoleChannel(), FileChannel(), ObsidianChannel(),
                        TelegramChannel(), PushoverChannel()]:
            status = "Configurado" if channel.is_configured() else "Nao configurado"
            print(f"  {channel.__class__.__name__}: {status}")

    else:
        print(f"Comando desconhecido: {cmd}")

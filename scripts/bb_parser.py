#!/usr/bin/env python3
"""
BB Parser Module
Parseia transacoes extraidas do Banco do Brasil.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Mapeamento de palavras-chave para categorias
CATEGORY_KEYWORDS = {
    "alimentacao": [
        "ifood", "rappi", "uber eats", "restaurante", "lanchonete", "pizzaria",
        "supermercado", "mercado", "padaria", "acougue", "hortifruti",
        "cafe", "cafeteria", "starbucks", "mcdonald", "burger", "subway",
        "outback", "madero", "habib", "giraffas", "bobs", "kfc",
        "pao de acucar", "carrefour", "extra", "dia", "atacadao", "assai",
        "sams club", "costco", "makro", "bretas", "minuto pao",
        # Estabelecimentos locais brasileiros
        "conveniencia", "mercearia", "peixaria", "panificadora", "lanchone",
        "chopp", "bar ", "boteco", "comercio de alim", "alimentacao",
        "feira", "sacolao", "quitanda", "emporio", "delicatessen",
    ],
    "transporte": [
        "uber", "99", "cabify", "lyft", "taxi", "corrida",
        "shell", "ipiranga", "petrobras", "posto br", "posto", "combustivel",
        "estacionamento", "estapar", "zona azul", "sem parar", "conectcar",
        "pedagio", "autoban", "ecovias", "ccr", "arteris",
    ],
    "saude": [
        "farmacia", "drogaria", "drogasil", "droga raia", "pacheco", "pague menos",
        "clinica", "hospital", "laboratorio", "exame", "consulta", "medico",
        "dentista", "fisioterapia", "psicolog", "nutri", "academia", "smartfit",
        "bio ritmo", "bodytech",
    ],
    "assinaturas": [
        "netflix", "spotify", "amazon prime", "disney", "hbo", "star+",
        "apple", "icloud", "google", "microsoft", "adobe", "notion",
        "github", "openai", "claude", "chatgpt", "dropbox", "1password",
        "canva", "figma", "slack", "zoom", "twitch",
    ],
    "compras": [
        "amazon", "mercado livre", "magalu", "magazine luiza", "americanas",
        "submarino", "shopee", "aliexpress", "shein", "casas bahia",
        "ponto frio", "fast shop", "kabum", "pichau", "terabyte",
        "nike", "adidas", "zara", "renner", "riachuelo", "cea",
    ],
    "lazer": [
        "cinema", "cinemark", "cinepolis", "uci", "ingresso", "ticket",
        "steam", "playstation", "xbox", "nintendo", "epic games",
        "show", "teatro", "museu", "parque", "viagem", "hotel",
        "airbnb", "booking", "decolar", "latam", "gol", "azul",
    ],
    "educacao": [
        "udemy", "coursera", "alura", "rocketseat", "origamid",
        "amazon kindle", "livro", "livraria", "saraiva", "cultura",
        "escola", "faculdade", "curso", "certificacao",
    ],
    "casa": [
        "leroy merlin", "telhanorte", "c&c", "ferreira costa",
        "tok stok", "etna", "mobly", "mmartan", "camicado",
        "cobasi", "petz", "petlove",
        "eletricista", "encanador", "pedreiro", "pintor",
        "condominio", "iptu", "agua", "luz", "gas", "internet",
    ],
    "taxas": [
        "iof", "taxa", "tarifa", "anuidade", "seguro", "juros",
        "multa", "cartorio", "despachante", "detran",
    ],
}


@dataclass
class ParsedTransaction:
    """Transacao parseada."""
    date: str
    description: str
    amount: float
    category: str
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    raw_text: str = ""


def categorize_transaction(description: str) -> str:
    """Categoriza transacao baseado em palavras-chave."""
    desc_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category

    return "compras"  # Default


def parse_installment(description: str) -> Tuple[Optional[int], Optional[int]]:
    """Extrai informacao de parcelamento."""
    patterns = [
        r"(\d+)/(\d+)",           # 3/10
        r"(\d+)\s*DE\s*(\d+)",    # 3 DE 10
        r"PARC\s*(\d+)/(\d+)",    # PARC 3/10
        r"PARCELA\s*(\d+)",       # PARCELA 3 (sem total)
    ]

    for pattern in patterns:
        match = re.search(pattern, description.upper())
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return int(groups[0]), int(groups[1])
            elif len(groups) == 1:
                return int(groups[0]), None

    return None, None


def parse_amount(amount_str: str) -> float:
    """Converte string de valor para float."""
    # Remove caracteres nao numericos exceto virgula e ponto
    cleaned = re.sub(r"[^\d,.-]", "", amount_str)

    # Padrao brasileiro: 1.234,56
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")

    try:
        return abs(float(cleaned))
    except ValueError:
        return 0.0


def parse_date(date_str: str) -> str:
    """Converte string de data para formato padrao YYYY-MM-DD."""
    patterns = [
        ("%d/%m/%Y", date_str),
        ("%d/%m/%y", date_str),
        ("%d-%m-%Y", date_str),
        ("%d.%m.%Y", date_str),
    ]

    for fmt, ds in patterns:
        try:
            dt = datetime.strptime(ds.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Se nao conseguiu parsear, retorna o mes atual
    return datetime.now().strftime("%Y-%m-01")


def parse_bb_transactions(raw_data: str) -> List[ParsedTransaction]:
    """
    Parseia texto bruto extraido da fatura BB.

    Formato esperado (cada linha):
    DATA | DESCRICAO | VALOR
    ou
    DATA    DESCRICAO    VALOR

    Exemplo:
    15/01/2026 | IFOOD *RESTAURANTE | R$ 45,90
    """
    transactions = []

    # Separar por linhas
    lines = raw_data.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Tentar diferentes separadores
        parts = None
        for sep in ["|", "\t", "   "]:
            if sep in line:
                parts = [p.strip() for p in line.split(sep) if p.strip()]
                if len(parts) >= 3:
                    break

        if not parts or len(parts) < 3:
            continue

        try:
            # Extrair campos
            date_str = parse_date(parts[0])
            description = parts[1]
            amount = parse_amount(parts[-1])

            if amount == 0:
                continue

            # Categorizar
            category = categorize_transaction(description)

            # Verificar parcelamento
            inst_current, inst_total = parse_installment(description)

            transactions.append(ParsedTransaction(
                date=date_str,
                description=description,
                amount=amount,
                category=category,
                installment_current=inst_current,
                installment_total=inst_total,
                raw_text=line
            ))

        except Exception as e:
            print(f"Erro ao parsear linha: {line} - {e}")
            continue

    return transactions


def import_to_database(transactions: List[ParsedTransaction], source: str = "bb_fatura") -> Dict:
    """Importa transacoes parseadas para o banco."""
    from scripts.finance_db import add_transaction

    results = {
        "inserted": 0,
        "duplicates": 0,
        "errors": 0,
        "total_amount": 0
    }

    for tx in transactions:
        try:
            result = add_transaction(
                date_str=tx.date,
                description=tx.description,
                amount=tx.amount,
                category=tx.category,
                installment_current=tx.installment_current,
                installment_total=tx.installment_total,
                source=source
            )

            if result["status"] == "inserted":
                results["inserted"] += 1
                results["total_amount"] += tx.amount
            elif result["status"] == "duplicate":
                results["duplicates"] += 1

        except Exception as e:
            print(f"Erro ao importar: {tx.description} - {e}")
            results["errors"] += 1

    return results


def generate_import_report(transactions: List[ParsedTransaction]) -> str:
    """Gera relatorio de importacao."""
    if not transactions:
        return "Nenhuma transacao encontrada."

    # Agrupar por categoria
    by_category = {}
    for tx in transactions:
        if tx.category not in by_category:
            by_category[tx.category] = {"count": 0, "total": 0}
        by_category[tx.category]["count"] += 1
        by_category[tx.category]["total"] += tx.amount

    total = sum(tx.amount for tx in transactions)

    report = f"""## Transacoes Extraidas

**Total**: {len(transactions)} transacoes
**Valor Total**: R$ {total:,.2f}

### Por Categoria

| Categoria | Qtd | Total |
|-----------|-----|-------|
"""

    for cat, data in sorted(by_category.items(), key=lambda x: x[1]["total"], reverse=True):
        report += f"| {cat.title()} | {data['count']} | R$ {data['total']:,.2f} |\n"

    return report


if __name__ == "__main__":
    # Teste com dados de exemplo
    sample_data = """
15/01/2026 | IFOOD *RESTAURANTE | R$ 45,90
15/01/2026 | UBER *TRIP | R$ 25,00
15/01/2026 | NETFLIX | R$ 55,90
15/01/2026 | AMAZON BR PARC 3/10 | R$ 120,00
15/01/2026 | SUPERMERCADO EXTRA | R$ 320,00
"""

    transactions = parse_bb_transactions(sample_data)

    print("=== Transacoes Parseadas ===\n")
    for tx in transactions:
        print(f"  {tx.date} | {tx.description[:30]} | R$ {tx.amount:.2f} | {tx.category}")
        if tx.installment_current:
            print(f"    Parcela: {tx.installment_current}/{tx.installment_total}")

    print("\n" + generate_import_report(transactions))

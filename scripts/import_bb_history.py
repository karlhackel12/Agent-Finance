#!/usr/bin/env python3
"""
Import BB History - Importa histórico de faturas BB (Jul-Dez 2025)
"""

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "finance.db"
HISTORY_FILE = PROJECT_ROOT / "data" / "bb_history_2025.txt"

# Mapeamento de categorias BB para categorias do sistema
BB_TO_SYSTEM_CATEGORY = {
    "restaurantes": "alimentacao",
    "supermercados": "alimentacao",
    "saude": "saude",
    "lazer": "lazer",
    "servicos": "compras",  # default, mas assinaturas vão para assinaturas
    "transporte": "transporte",
    "viagens": "lazer",
    "vestuario": "compras",
    "educacao": "educacao",
    "bancos": None,  # Ignorar PicPay transfers
    "outros": "taxas",  # IOF, juros, etc
}

# Assinaturas recorrentes (vão para categoria assinaturas)
SUBSCRIPTION_KEYWORDS = [
    "claude.ai", "openai", "chatgpt", "lovable", "cursor", "zoom",
    "make.com", "anthropic", "manus ai", "notion", "figma", "vercel",
    "replit", "grammarly", "circleback", "emergent", "1password",
    "aqua voice", "perplexity", "invideo", "flowith", "reclaim.ai",
    "cluely", "21st.dev", "taplio", "leapfrog", "of london",
    "float labs", "meetsquad", "anything create", "globo premiere",
    "estadao", "amazon prime", "amazon kindle", "google one",
    "ifood club", "contabilizei", "movida carro", "tavus",
]

# Combustível -> Transporte
FUEL_KEYWORDS = [
    "posto", "combustivel", "gasolina", "etanol", "diesel",
]

# Farmácia -> Saude
PHARMACY_KEYWORDS = [
    "farmacia", "drogaria", "farma", "droga", "raia", "pacheco",
]

# Pet Shop -> Compras
PET_KEYWORDS = [
    "pet", "cobasi", "petz",
]

# Taxas
TAX_KEYWORDS = [
    "iof", "juros", "multa", "taxa", "encargo", "anuidade",
]

# Transações a ignorar
IGNORE_PATTERNS = [
    r"PGTO\. CASH",  # Pagamentos de fatura
    r"#PCV",  # Parcelamentos convertidos
    r"PICPAY\*",  # Transferências PicPay
    r"DEVOLUCAO JUROS",  # Devoluções
    r"PARC\.COMP\.VIST",  # Parcelamento compra à vista
]


def should_ignore(description: str) -> bool:
    """Verifica se transação deve ser ignorada."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, description, re.IGNORECASE):
            return True
    return False


def get_system_category(bb_category: str, description: str) -> Optional[str]:
    """Mapeia categoria BB para categoria do sistema."""
    desc_lower = description.lower()

    # Verificar assinaturas primeiro
    for keyword in SUBSCRIPTION_KEYWORDS:
        if keyword in desc_lower:
            return "assinaturas"

    # Combustível -> Transporte
    for keyword in FUEL_KEYWORDS:
        if keyword in desc_lower:
            return "transporte"

    # Farmácia -> Saude
    for keyword in PHARMACY_KEYWORDS:
        if keyword in desc_lower:
            return "saude"

    # Pet -> Compras
    for keyword in PET_KEYWORDS:
        if keyword in desc_lower:
            return "compras"

    # Taxas
    for keyword in TAX_KEYWORDS:
        if keyword in desc_lower:
            return "taxas"

    # Usar mapeamento padrão
    return BB_TO_SYSTEM_CATEGORY.get(bb_category.lower())


def parse_date(date_str: str, year: int) -> str:
    """Converte data DD/MM para YYYY-MM-DD."""
    try:
        parts = date_str.strip().split("/")
        if len(parts) == 2:
            day, month = int(parts[0]), int(parts[1])
            return f"{year}-{month:02d}-{day:02d}"
    except:
        pass
    return None


def parse_amount(amount_str: str) -> float:
    """Converte valor R$ 1.234,56 para float."""
    cleaned = amount_str.replace("R$", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except:
        return 0.0


def parse_history_file(filepath: Path) -> List[Dict]:
    """Parseia arquivo de histórico BB."""
    transactions = []
    current_month = None
    current_year = 2025
    current_bb_category = None

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Detectar mês
        if line.startswith("=== "):
            month_match = re.search(r"(JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)\s+(\d{4})", line)
            if month_match:
                month_name = month_match.group(1)
                current_year = int(month_match.group(2))
                month_map = {
                    "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9,
                    "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
                }
                current_month = month_map.get(month_name)
            continue

        # Detectar categoria BB
        if line in ["Bancos", "Lazer", "Restaurantes", "Saude", "Servicos",
                    "Supermercados", "Transporte", "Vestuario", "Viagens",
                    "Educacao", "Outros"]:
            current_bb_category = line.lower()
            continue

        # Parsear transação
        # Formato: DD/MM\tDESCRICAO\tR$\tVALOR
        parts = line.split("\t")
        if len(parts) >= 4:
            date_str = parts[0].strip()
            description = parts[1].strip()
            # Valor está nas últimas partes
            amount_str = parts[-1].strip()

            # Ignorar transações específicas
            if should_ignore(description):
                continue

            # Ignorar valores negativos (créditos)
            amount = parse_amount(amount_str)
            if amount <= 0:
                continue

            # Obter categoria do sistema
            system_category = get_system_category(current_bb_category or "servicos", description)
            if system_category is None:
                continue  # Ignorar (ex: PicPay)

            # Parsear data
            date = parse_date(date_str, current_year)
            if not date:
                continue

            transactions.append({
                "date": date,
                "description": description,
                "amount": amount,
                "category": system_category,
                "bb_category": current_bb_category,
                "source": "bb_historico_2025"
            })

    return transactions


def get_category_mapping(cursor) -> Dict[str, int]:
    """Obtém mapeamento nome -> id das categorias."""
    cursor.execute("SELECT id, name FROM categories")
    return {row[1]: row[0] for row in cursor.fetchall()}


def import_to_database(transactions: List[Dict]) -> Dict:
    """Importa transações no banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obter mapeamento de categorias
    category_map = get_category_mapping(cursor)

    results = {
        "inserted": 0,
        "duplicates": 0,
        "errors": 0,
        "by_category": {},
        "by_month": {},
    }

    for tx in transactions:
        try:
            # Obter category_id
            cat_name = tx["category"]
            category_id = category_map.get(cat_name)
            if category_id is None:
                print(f"Categoria não encontrada: {cat_name}")
                results["errors"] += 1
                continue

            # Gerar hash para evitar duplicatas
            import hashlib
            hash_str = f"{tx['date']}|{tx['description']}|{tx['amount']}"
            tx_hash = hashlib.md5(hash_str.encode()).hexdigest()

            # Verificar duplicata
            cursor.execute("""
                SELECT id FROM transactions
                WHERE hash = ?
            """, (tx_hash,))

            if cursor.fetchone():
                results["duplicates"] += 1
                continue

            # Inserir
            cursor.execute("""
                INSERT INTO transactions (date, description, amount, category_id, type, source, hash)
                VALUES (?, ?, ?, ?, 'expense', ?, ?)
            """, (tx["date"], tx["description"], tx["amount"], category_id, tx["source"], tx_hash))

            results["inserted"] += 1

            # Estatísticas
            if cat_name not in results["by_category"]:
                results["by_category"][cat_name] = {"count": 0, "total": 0}
            results["by_category"][cat_name]["count"] += 1
            results["by_category"][cat_name]["total"] += tx["amount"]

            month = tx["date"][:7]
            if month not in results["by_month"]:
                results["by_month"][month] = {"count": 0, "total": 0}
            results["by_month"][month]["count"] += 1
            results["by_month"][month]["total"] += tx["amount"]

        except Exception as e:
            print(f"Erro ao importar {tx['description']}: {e}")
            results["errors"] += 1

    conn.commit()
    conn.close()

    return results


def print_report(results: Dict):
    """Imprime relatório de importação."""
    print("\n" + "=" * 60)
    print("RELATÓRIO DE IMPORTAÇÃO - BB Histórico 2025")
    print("=" * 60)

    print(f"\n📊 Resumo:")
    print(f"   ✅ Inseridas: {results['inserted']}")
    print(f"   ⏭️  Duplicatas: {results['duplicates']}")
    print(f"   ❌ Erros: {results['errors']}")

    print(f"\n📁 Por Categoria:")
    for cat, data in sorted(results["by_category"].items(), key=lambda x: x[1]["total"], reverse=True):
        print(f"   {cat.title():15} {data['count']:4} txs  R$ {data['total']:,.2f}")

    print(f"\n📅 Por Mês:")
    for month, data in sorted(results["by_month"].items()):
        print(f"   {month}  {data['count']:4} txs  R$ {data['total']:,.2f}")

    total = sum(d["total"] for d in results["by_category"].values())
    print(f"\n💰 Total Importado: R$ {total:,.2f}")
    print("=" * 60)


def main():
    """Executa importação."""
    print("🔄 Iniciando importação do histórico BB 2025...")

    if not HISTORY_FILE.exists():
        print(f"❌ Arquivo não encontrado: {HISTORY_FILE}")
        return

    if not DB_PATH.exists():
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return

    # Parsear arquivo
    print(f"📖 Lendo arquivo: {HISTORY_FILE}")
    transactions = parse_history_file(HISTORY_FILE)
    print(f"   Encontradas {len(transactions)} transações válidas")

    # Importar
    print(f"💾 Importando para: {DB_PATH}")
    results = import_to_database(transactions)

    # Relatório
    print_report(results)

    return results


if __name__ == "__main__":
    main()

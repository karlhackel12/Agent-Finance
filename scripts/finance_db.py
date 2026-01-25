#!/usr/bin/env python3
"""
Finance Database Module
Gerencia transacoes, categorias e budgets no SQLite local.

METODOLOGIA DE DATAS:
- O campo 'date' na tabela transactions = DATA DA TRANSAÇÃO (quando a compra foi feita)
- NÃO é a data de pagamento da fatura do cartão
- Exemplo: compra em 20/12 = date='2025-12-20', independente de quando a fatura fecha/paga
- Isso permite análise precisa de quando cada gasto ocorreu
"""

import sqlite3
import hashlib
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent.parent / "data" / "finance.db"


def ensure_database_exists():
    """Verifica se o banco existe com schema correto, se não cria dados demo."""
    need_create = False

    if not DB_PATH.exists():
        need_create = True
    else:
        # Check if schema is correct (has icon and type columns)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT icon FROM categories LIMIT 1")
            cursor.execute("SELECT type FROM transactions LIMIT 1")
            conn.close()
        except sqlite3.OperationalError:
            # Schema is wrong, delete and recreate
            conn.close()
            import os
            os.remove(DB_PATH)
            need_create = True
            print("Old database schema detected, recreating...")

    if need_create:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Import demo data generator
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "data"))
        try:
            from demo_data import create_demo_database
            create_demo_database(str(DB_PATH))
            print("Demo database created for Streamlit Cloud deployment")
        except Exception as e:
            print(f"Error importing demo_data: {e}")
            # Create minimal structure with correct schema (fallback if demo_data fails)
            conn = sqlite3.connect(DB_PATH)
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY, name TEXT UNIQUE, icon TEXT DEFAULT '📦', budget_monthly REAL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY, date TEXT, description TEXT, amount REAL, category_id INTEGER, type TEXT DEFAULT 'expense', source TEXT DEFAULT 'manual'
                );
                CREATE TABLE IF NOT EXISTS installments (
                    id INTEGER PRIMARY KEY, description TEXT, total_amount REAL, installment_amount REAL,
                    total_installments INTEGER, current_installment INTEGER DEFAULT 1, start_date TEXT, end_date TEXT,
                    category_id INTEGER, status TEXT DEFAULT 'active'
                );
                CREATE TABLE IF NOT EXISTS monthly_budgets (
                    id INTEGER PRIMARY KEY, year INTEGER, month INTEGER, category_id INTEGER, budget_amount REAL
                );
                INSERT INTO categories (name, icon, budget_monthly) VALUES
                    ('alimentacao', '🍔', 3500), ('compras', '🛒', 2500), ('casa', '🏠', 500),
                    ('transporte', '🚗', 4000), ('saude', '🏥', 4000), ('assinaturas', '💻', 3500),
                    ('lazer', '🎮', 1500), ('educacao', '📚', 200), ('taxas', '📝', 100),
                    ('esportes', '🎾', 1500), ('obra', '🏗️', 16500);
            """)
            conn.close()
            print("Minimal database created with correct schema")


def get_connection():
    """Retorna conexao com o banco."""
    ensure_database_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_hash(date_str: str, description: str, amount: float) -> str:
    """Gera hash unico para evitar duplicatas com normalizacao robusta."""
    # Normalizar descrição: remover espaços extras, lowercase
    normalized_desc = ' '.join(description.strip().split()).lower()
    # Formatar valor com 2 casas decimais para consistência
    amount_str = f"{abs(amount):.2f}"
    # Usar separador null byte (não aparece em texto normal)
    content = f"{date_str}\x00{normalized_desc}\x00{amount_str}"
    return hashlib.md5(content.encode()).hexdigest()


# ==================== CATEGORIES ====================

def get_categories() -> List[Dict]:
    """Retorna todas as categorias."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_category_by_name(name: str) -> Optional[Dict]:
    """Busca categoria por nome."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE name = ?", (name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_variable_categories() -> List[Dict]:
    """Retorna apenas categorias variáveis (not excluded).

    Categorias variáveis são aquelas incluídas no budget mensal de R$ 19.800:
    alimentacao, transporte, saude, assinaturas, compras, lazer, educacao, casa, taxas
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, icon, budget_monthly
        FROM categories
        WHERE is_excluded = 0
        ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_excluded_categories() -> List[Dict]:
    """Retorna apenas categorias excluídas (obra, esportes).

    Categorias excluídas são rastreadas separadamente e não contam no budget mensal:
    - obra: R$ 16.500/mês (média 2026)
    - esportes: R$ 1.500/mês
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, icon, budget_monthly
        FROM categories
        WHERE is_excluded = 1
        ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== TRANSACTIONS ====================

def add_transaction(
    date_str: str,
    description: str,
    amount: float,
    category: str,
    account: str = "BB Credito",
    type_: str = "expense",
    installment_current: Optional[int] = None,
    installment_total: Optional[int] = None,
    tags: Optional[List[str]] = None,
    source: str = "manual"
) -> Dict:
    """
    Adiciona uma transacao ao banco.
    Retorna a transacao inserida ou None se duplicata.

    Args:
        date_str: Data da TRANSAÇÃO (quando a compra foi feita), formato YYYY-MM-DD.
                  NÃO usar data de pagamento da fatura.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Gerar hash para evitar duplicatas
    tx_hash = generate_hash(date_str, description, amount)

    # Verificar duplicata
    cursor.execute("SELECT id FROM transactions WHERE hash = ?", (tx_hash,))
    if cursor.fetchone():
        conn.close()
        return {"status": "duplicate", "hash": tx_hash}

    # Buscar category_id
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category.lower(),))
    cat_row = cursor.fetchone()
    category_id = cat_row["id"] if cat_row else None

    # Buscar account_id
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account,))
    acc_row = cursor.fetchone()
    account_id = acc_row["id"] if acc_row else None

    # Inserir transacao
    cursor.execute('''
        INSERT INTO transactions
        (date, description, amount, category_id, account_id, type,
         installment_current, installment_total, tags, source, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        date_str, description, amount, category_id, account_id, type_,
        installment_current, installment_total,
        json.dumps(tags) if tags else None, source, tx_hash
    ))

    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "status": "inserted",
        "id": tx_id,
        "hash": tx_hash,
        "date": date_str,
        "description": description,
        "amount": amount,
        "category": category
    }


def get_transactions(
    year: Optional[int] = None,
    month: Optional[int] = None,
    category: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """Busca transacoes com filtros opcionais."""
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon, a.name as account_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE 1=1
    '''
    params = []

    if year:
        query += " AND strftime('%Y', t.date) = ?"
        params.append(str(year))

    if month:
        query += " AND strftime('%m', t.date) = ?"
        params.append(f"{month:02d}")

    if category:
        query += " AND c.name = ?"
        params.append(category.lower())

    query += " ORDER BY t.date DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_monthly_summary(year: int, month: int) -> Dict:
    """Retorna resumo mensal de gastos por categoria."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            c.name as category,
            c.icon,
            c.budget_monthly as budget,
            COALESCE(SUM(ABS(t.amount)), 0) as total
        FROM categories c
        LEFT JOIN transactions t ON t.category_id = c.id
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.type = 'expense'
        GROUP BY c.id
        ORDER BY total DESC
    ''', (str(year), f"{month:02d}"))

    rows = cursor.fetchall()
    conn.close()

    result = {
        "year": year,
        "month": month,
        "categories": [],
        "total_spent": 0,
        "total_budget": 0
    }

    for row in rows:
        cat_data = dict(row)
        cat_data["percent"] = round(cat_data["total"] / cat_data["budget"] * 100, 1) if cat_data["budget"] > 0 else 0
        cat_data["status"] = "ok" if cat_data["percent"] <= 90 else ("warning" if cat_data["percent"] <= 110 else "critical")
        result["categories"].append(cat_data)
        result["total_spent"] += cat_data["total"]
        result["total_budget"] += cat_data["budget"]

    result["savings_rate"] = round((55000 - result["total_spent"]) / 55000 * 100, 1)

    return result


def get_monthly_summary_v2(year: int, month: int) -> Dict:
    """Retorna resumo mensal separando variáveis de excluídas.

    Categorias variáveis (9): alimentacao, transporte, saude, assinaturas,
                             compras, lazer, educacao, casa, taxas
    Categorias excluídas (2): obra, esportes

    A taxa de poupança é calculada APENAS sobre as variáveis.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar variáveis (is_excluded = 0)
    cursor.execute('''
        SELECT
            c.name as category,
            c.icon,
            c.budget_monthly as budget,
            COALESCE(SUM(ABS(t.amount)), 0) as total
        FROM categories c
        LEFT JOIN transactions t ON t.category_id = c.id
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.type = 'expense'
        WHERE c.is_excluded = 0
        GROUP BY c.id
        ORDER BY total DESC
    ''', (str(year), f"{month:02d}"))

    variable_rows = cursor.fetchall()

    # Buscar excluídas (is_excluded = 1)
    cursor.execute('''
        SELECT
            c.name as category,
            c.icon,
            c.budget_monthly as budget,
            COALESCE(SUM(ABS(t.amount)), 0) as total
        FROM categories c
        LEFT JOIN transactions t ON t.category_id = c.id
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.type = 'expense'
        WHERE c.is_excluded = 1
        GROUP BY c.id
        ORDER BY total DESC
    ''', (str(year), f"{month:02d}"))

    excluded_rows = cursor.fetchall()
    conn.close()

    # Processar variáveis
    variables = {
        "categories": [],
        "total": 0,
        "budget": 0
    }

    for row in variable_rows:
        cat_data = dict(row)
        cat_data["percent"] = round(cat_data["total"] / cat_data["budget"] * 100, 1) if cat_data["budget"] > 0 else 0
        cat_data["status"] = "ok" if cat_data["percent"] <= 90 else ("warning" if cat_data["percent"] <= 110 else "critical")
        variables["categories"].append(cat_data)
        variables["total"] += cat_data["total"]
        variables["budget"] += cat_data["budget"]

    # Processar excluídas
    excluded = {
        "categories": [],
        "total": 0,
        "budget": 0
    }

    for row in excluded_rows:
        cat_data = dict(row)
        cat_data["percent"] = round(cat_data["total"] / cat_data["budget"] * 100, 1) if cat_data["budget"] > 0 else 0
        cat_data["status"] = "ok" if cat_data["percent"] <= 90 else ("warning" if cat_data["percent"] <= 110 else "critical")
        excluded["categories"].append(cat_data)
        excluded["total"] += cat_data["total"]
        excluded["budget"] += cat_data["budget"]

    # Taxa de poupança calculada APENAS sobre variáveis
    savings_rate = round((55000 - variables["total"]) / 55000 * 100, 1)

    return {
        "year": year,
        "month": month,
        "variables": variables,
        "excluded": excluded,
        "savings_rate": savings_rate,
        "total_spent": variables["total"] + excluded["total"]
    }


# ==================== INSTALLMENTS ====================

def add_installment(
    description: str,
    total_amount: float,
    total_installments: int,
    start_date: str,
    category: str
) -> Dict:
    """Adiciona um parcelamento."""
    conn = get_connection()
    cursor = conn.cursor()

    installment_amount = total_amount / total_installments

    # Calcular data final
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end_month = start.month + total_installments - 1
    end_year = start.year + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    end_date = f"{end_year}-{end_month:02d}-01"

    # Buscar category_id
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category.lower(),))
    cat_row = cursor.fetchone()
    category_id = cat_row["id"] if cat_row else None

    cursor.execute('''
        INSERT INTO installments
        (description, total_amount, installment_amount, total_installments,
         current_installment, start_date, end_date, category_id)
        VALUES (?, ?, ?, ?, 1, ?, ?, ?)
    ''', (description, total_amount, installment_amount, total_installments,
          start_date, end_date, category_id))

    inst_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": inst_id,
        "description": description,
        "installment_amount": round(installment_amount, 2),
        "total_installments": total_installments,
        "end_date": end_date
    }


def get_active_installments() -> List[Dict]:
    """Retorna parcelamentos ativos."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT i.*, c.name as category_name
        FROM installments i
        LEFT JOIN categories c ON i.category_id = c.id
        WHERE i.status = 'active'
        ORDER BY i.end_date
    ''')

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def generate_installment_transactions(year: int, month: int) -> Dict:
    """
    Gera transações para parcelamentos ativos em um mês específico.
    Isso garante que os parcelamentos "comam" do budget mensal.

    Usa installment_id para prevenir duplicação quando transações
    são importadas manualmente do cartão de crédito.
    """
    conn = get_connection()
    cursor = conn.cursor()

    results = {"created": 0, "skipped": 0, "errors": 0}

    # Buscar parcelamentos ativos
    installments = get_active_installments()

    for inst in installments:
        try:
            start_date = datetime.strptime(inst['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(inst['end_date'], '%Y-%m-%d')
            target_date = datetime(year, month, 1)

            # Verificar se o mês está dentro do período do parcelamento
            if start_date <= target_date <= end_date:
                # Calcular número da parcela para este mês
                months_elapsed = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
                parcela_num = months_elapsed + 1  # Parcelas começam em 1

                if parcela_num > inst['total_installments']:
                    continue

                # ✅ VERIFICAR SE JÁ EXISTE transação com este installment_id no mês
                cursor.execute("""
                    SELECT id FROM transactions
                    WHERE installment_id = ?
                    AND strftime('%Y-%m', date) = ?
                """, (inst['id'], f"{year}-{month:02d}"))

                if cursor.fetchone():
                    results["skipped"] += 1
                    continue  # ✅ Já existe, não duplicar

                # Descrição da transação
                description = f"{inst['description']} {parcela_num}/{inst['total_installments']}"

                # Data da transação (dia 10 do mês)
                tx_date = f"{year}-{month:02d}-10"

                # Hash para evitar duplicatas
                tx_hash = generate_hash(tx_date, description, inst['installment_amount'])

                # Inserir transação com installment_id
                cursor.execute('''
                    INSERT INTO transactions
                    (date, description, amount, category_id, type, source, hash,
                     installment_id, installment_current, installment_total)
                    VALUES (?, ?, ?, ?, 'expense', 'parcelamento', ?, ?, ?, ?)
                ''', (tx_date, description, inst['installment_amount'], inst['category_id'], tx_hash,
                      inst['id'], parcela_num, inst['total_installments']))

                results["created"] += 1

        except Exception as e:
            print(f"Erro ao processar parcelamento {inst['description']}: {e}")
            results["errors"] += 1

    conn.commit()
    conn.close()

    return results


# ==================== REPORTS ====================

def generate_monthly_report(year: int, month: int) -> str:
    """Gera relatorio mensal em Markdown."""
    summary = get_monthly_summary(year, month)
    transactions = get_transactions(year=year, month=month, limit=500)

    month_names = ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    report = f"""# {month_names[month]} {year} - Relatorio Financeiro

> Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}

## Resumo

| Metrica | Valor |
|---------|-------|
| Total Gasto | R$ {summary['total_spent']:,.2f} |
| Budget Total | R$ {summary['total_budget']:,.2f} |
| Taxa Poupanca | {summary['savings_rate']}% |

## Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
"""

    for cat in summary["categories"]:
        status_icon = "🟢" if cat["status"] == "ok" else ("🟡" if cat["status"] == "warning" else "🔴")
        report += f"| {cat['icon']} {cat['category']} | R$ {cat['total']:,.2f} | R$ {cat['budget']:,.2f} | {cat['percent']}% | {status_icon} |\n"

    report += f"""

## Transacoes ({len(transactions)} registros)

| Data | Descricao | Valor | Categoria |
|------|-----------|-------|-----------|
"""

    for tx in transactions[:50]:  # Limitar a 50 no relatorio
        cat_name = tx.get("category_name", "N/A")
        report += f"| {tx['date']} | {tx['description'][:30]} | R$ {abs(tx['amount']):,.2f} | {cat_name} |\n"

    if len(transactions) > 50:
        report += f"\n*... e mais {len(transactions) - 50} transacoes*\n"

    return report


# ==================== PJ (EMPRESA) ====================

def init_pj_tables():
    """Cria tabelas para dados da empresa (PJ) se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de faturamento PJ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pj_revenue (
            id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            gross_revenue REAL NOT NULL,
            currency TEXT DEFAULT 'BRL',
            source TEXT DEFAULT 'contabilizei',
            notes TEXT,
            synced_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
    ''')

    # Tabela de impostos PJ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pj_taxes (
            id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            tax_type TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE,
            paid_date DATE,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month, tax_type)
        )
    ''')

    # Tabela de despesas fixas PJ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pj_expenses (
            id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            expense_type TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month, expense_type)
        )
    ''')

    conn.commit()
    conn.close()


def add_pj_revenue(year: int, month: int, gross_revenue: float, source: str = "contabilizei", notes: str = None) -> Dict:
    """Adiciona ou atualiza faturamento PJ do mês."""
    init_pj_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pj_revenue (year, month, gross_revenue, source, notes, synced_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE SET
            gross_revenue = excluded.gross_revenue,
            source = excluded.source,
            notes = excluded.notes,
            synced_at = excluded.synced_at
    ''', (year, month, gross_revenue, source, notes, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"year": year, "month": month, "gross_revenue": gross_revenue, "status": "saved"}


def add_pj_tax(year: int, month: int, tax_type: str, amount: float, due_date: str = None, status: str = "pending") -> Dict:
    """Adiciona ou atualiza imposto PJ."""
    init_pj_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pj_taxes (year, month, tax_type, amount, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, month, tax_type) DO UPDATE SET
            amount = excluded.amount,
            due_date = excluded.due_date,
            status = excluded.status
    ''', (year, month, tax_type, amount, due_date, status))

    conn.commit()
    conn.close()

    return {"year": year, "month": month, "tax_type": tax_type, "amount": amount, "status": "saved"}


def add_pj_expense(year: int, month: int, expense_type: str, amount: float, notes: str = None) -> Dict:
    """Adiciona ou atualiza despesa fixa PJ."""
    init_pj_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pj_expenses (year, month, expense_type, amount, notes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(year, month, expense_type) DO UPDATE SET
            amount = excluded.amount,
            notes = excluded.notes
    ''', (year, month, expense_type, amount, notes))

    conn.commit()
    conn.close()

    return {"year": year, "month": month, "expense_type": expense_type, "amount": amount, "status": "saved"}


def get_pj_monthly_summary(year: int, month: int) -> Dict:
    """Retorna resumo mensal da empresa (PJ)."""
    init_pj_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar faturamento
    cursor.execute('''
        SELECT gross_revenue, synced_at FROM pj_revenue
        WHERE year = ? AND month = ?
    ''', (year, month))
    rev_row = cursor.fetchone()
    gross_revenue = rev_row["gross_revenue"] if rev_row else 0
    synced_at = rev_row["synced_at"] if rev_row else None

    # Buscar impostos
    cursor.execute('''
        SELECT tax_type, amount, due_date, status FROM pj_taxes
        WHERE year = ? AND month = ?
    ''', (year, month))
    taxes = [dict(row) for row in cursor.fetchall()]
    total_taxes = sum(t["amount"] for t in taxes)

    # Buscar despesas fixas
    cursor.execute('''
        SELECT expense_type, amount FROM pj_expenses
        WHERE year = ? AND month = ?
    ''', (year, month))
    expenses = [dict(row) for row in cursor.fetchall()]
    total_expenses = sum(e["amount"] for e in expenses)

    conn.close()

    # Calcular líquido
    net_revenue = gross_revenue - total_taxes

    return {
        "year": year,
        "month": month,
        "gross_revenue": gross_revenue,
        "taxes": taxes,
        "total_taxes": total_taxes,
        "expenses": expenses,
        "total_expenses": total_expenses,
        "net_revenue": net_revenue,
        "effective_tax_rate": round(total_taxes / gross_revenue * 100, 2) if gross_revenue > 0 else 0,
        "synced_at": synced_at
    }


def get_pj_yearly_summary(year: int) -> Dict:
    """Retorna resumo anual da empresa (PJ)."""
    init_pj_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar todos os meses do ano
    cursor.execute('''
        SELECT month, gross_revenue FROM pj_revenue
        WHERE year = ?
        ORDER BY month
    ''', (year,))
    revenues = {row["month"]: row["gross_revenue"] for row in cursor.fetchall()}

    cursor.execute('''
        SELECT month, SUM(amount) as total FROM pj_taxes
        WHERE year = ?
        GROUP BY month
    ''', (year,))
    taxes = {row["month"]: row["total"] for row in cursor.fetchall()}

    conn.close()

    months = []
    total_gross = 0
    total_taxes = 0

    for m in range(1, 13):
        gross = revenues.get(m, 0)
        tax = taxes.get(m, 0)
        months.append({
            "month": m,
            "gross_revenue": gross,
            "taxes": tax,
            "net_revenue": gross - tax
        })
        total_gross += gross
        total_taxes += tax

    return {
        "year": year,
        "months": months,
        "total_gross": total_gross,
        "total_taxes": total_taxes,
        "total_net": total_gross - total_taxes,
        "avg_monthly_gross": total_gross / 12 if total_gross > 0 else 0,
        "effective_tax_rate": round(total_taxes / total_gross * 100, 2) if total_gross > 0 else 0
    }


def get_consolidated_summary(year: int, month: int) -> Dict:
    """Retorna visão consolidada PF + PJ."""
    pj = get_pj_monthly_summary(year, month)
    pf = get_monthly_summary(year, month)

    # Renda total fixa mensal (PJ líquido é parte da renda)
    TOTAL_INCOME = 55000  # Renda líquida mensal total

    return {
        "year": year,
        "month": month,
        # PJ
        "pj_gross_revenue": pj["gross_revenue"],
        "pj_taxes": pj["total_taxes"],
        "pj_net_revenue": pj["net_revenue"],
        "pj_tax_rate": pj["effective_tax_rate"],
        # PF
        "pf_expenses": pf["total_spent"],
        "pf_budget": pf["total_budget"],
        # Consolidado
        "total_income": TOTAL_INCOME,
        "total_outflow": pf["total_spent"] + pj["total_taxes"],
        "savings": TOTAL_INCOME - pf["total_spent"],
        "savings_rate": round((TOTAL_INCOME - pf["total_spent"]) / TOTAL_INCOME * 100, 1)
    }


# ==================== CLI ====================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python finance_db.py <comando>")
        print("Comandos: categories, summary, transactions, report, pj, consolidated")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "categories":
        for cat in get_categories():
            print(f"{cat['icon']} {cat['name']}: R$ {cat['budget_monthly']}")

    elif cmd == "summary":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        summary = get_monthly_summary(year, month)
        print(f"\n=== {month}/{year} ===")
        print(f"Total Gasto: R$ {summary['total_spent']:,.2f}")
        print(f"Budget: R$ {summary['total_budget']:,.2f}")
        print(f"Taxa Poupanca: {summary['savings_rate']}%")
        print("\nPor categoria:")
        for cat in summary["categories"]:
            status = "✓" if cat["status"] == "ok" else ("⚠" if cat["status"] == "warning" else "✗")
            print(f"  {status} {cat['category']}: R$ {cat['total']:,.2f} / R$ {cat['budget']:,.2f} ({cat['percent']}%)")

    elif cmd == "transactions":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        for tx in get_transactions(year=year, month=month, limit=20):
            print(f"{tx['date']} | R$ {tx['amount']:>10.2f} | {tx['description'][:30]}")

    elif cmd == "report":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        print(generate_monthly_report(year, month))

    elif cmd == "pj":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        pj = get_pj_monthly_summary(year, month)
        print(f"\n=== PJ {month}/{year} ===")
        print(f"Faturamento Bruto: R$ {pj['gross_revenue']:,.2f}")
        print(f"Impostos: R$ {pj['total_taxes']:,.2f} ({pj['effective_tax_rate']}%)")
        print(f"Receita Liquida: R$ {pj['net_revenue']:,.2f}")
        if pj['taxes']:
            print("\nImpostos detalhados:")
            for tax in pj['taxes']:
                status = "✓ Pago" if tax['status'] == 'paid' else "⏳ Pendente"
                print(f"  {tax['tax_type']}: R$ {tax['amount']:,.2f} - {status}")

    elif cmd == "consolidated":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
        cons = get_consolidated_summary(year, month)
        print(f"\n=== CONSOLIDADO {month}/{year} ===")
        print(f"\n📊 RECEITAS:")
        print(f"  PJ Bruto: R$ {cons['pj_gross_revenue']:,.2f}")
        print(f"  (-) Impostos: R$ {cons['pj_taxes']:,.2f}")
        print(f"  PJ Liquido: R$ {cons['pj_net_revenue']:,.2f}")
        print(f"\n💰 DESPESAS PF:")
        print(f"  Gastos Variaveis: R$ {cons['pf_expenses']:,.2f}")
        print(f"  Budget: R$ {cons['pf_budget']:,.2f}")
        print(f"\n📈 RESULTADO:")
        print(f"  Renda Total: R$ {cons['total_income']:,.2f}")
        print(f"  Poupanca: R$ {cons['savings']:,.2f} ({cons['savings_rate']}%)")

    else:
        print(f"Comando desconhecido: {cmd}")

#!/usr/bin/env python3
"""
Setup Real Data
Popula o banco com dados reais do planejamento 2026.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "finance.db"

# Dados reais do planejamento
CATEGORIES = [
    # (name, icon, budget_monthly, color)
    ("alimentacao", "🍔", 3500, "#FF6B6B"),
    ("transporte", "🚗", 1500, "#4ECDC4"),
    ("saude", "🏥", 1500, "#45B7D1"),
    ("assinaturas", "💻", 2011, "#96CEB4"),  # Plano saude + Software + Streaming
    ("compras", "🛒", 5000, "#FFEAA7"),
    ("lazer", "🎮", 2000, "#DDA0DD"),
    ("educacao", "📚", 500, "#98D8C8"),
    ("casa", "🏠", 2000, "#F7DC6F"),
    ("taxas", "📝", 500, "#BB8FCE"),
]

# Compromissos fixos mensais
FIXED_COMMITMENTS = [
    ("Financiamento Imovel", 7500, "moradia", "2045-12-31"),
    ("Assinatura Carro", 3200, "transporte", None),
    ("Contas Casa", 3000, "casa", None),
    ("Plano de Saude", 1300, "saude", None),
    ("Software Trabalho", 661, "assinaturas", None),
    ("Streaming", 350, "assinaturas", None),
]

# Parcelamentos ativos (Janeiro 2026)
INSTALLMENTS = [
    # (description, total_amount, installment_amount, total, current, start_date, end_date, category)
    ("MOVEIS PLANEJADOS", 94000, 9400, 10, 1, "2026-01-01", "2026-10-01", "casa"),
    ("AMAZON BR", 1200, 120, 10, 3, "2024-11-01", "2025-08-01", "compras"),
    ("MAGALU", 850, 85, 10, 4, "2024-10-01", "2025-07-01", "compras"),
    ("MERCADO LIVRE", 2400, 200, 12, 2, "2024-12-01", "2025-11-01", "compras"),
    ("APPLE.COM", 1680, 140, 12, 5, "2024-09-01", "2025-08-01", "assinaturas"),
    ("STEAM", 360, 60, 6, 3, "2024-11-01", "2025-04-01", "lazer"),
    ("UDEMY", 540, 90, 6, 2, "2024-12-01", "2025-05-01", "educacao"),
    ("TOK STOK", 3600, 300, 12, 6, "2024-08-01", "2025-07-01", "casa"),
    ("LEROY MERLIN", 2160, 180, 12, 4, "2024-10-01", "2025-09-01", "casa"),
    ("NIKE", 720, 120, 6, 3, "2024-11-01", "2025-04-01", "compras"),
    ("ALIEXPRESS", 480, 80, 6, 2, "2024-12-01", "2025-05-01", "compras"),
    ("CASAS BAHIA", 1800, 150, 12, 5, "2024-09-01", "2025-08-01", "casa"),
    ("KABUM", 2400, 200, 12, 3, "2024-11-01", "2025-10-01", "compras"),
    ("DROGASIL", 600, 100, 6, 4, "2024-10-01", "2025-03-01", "saude"),
    ("IFOOD MARKET", 420, 70, 6, 2, "2024-12-01", "2025-05-01", "alimentacao"),
    ("SHEIN", 540, 90, 6, 3, "2024-11-01", "2025-04-01", "compras"),
]

# Transacoes exemplo Janeiro 2026 (baseado no Janeiro.md original)
JANUARY_TRANSACTIONS = [
    # Alimentacao
    ("2026-01-02", "IFOOD *RESTAURANTE", 45.90, "alimentacao"),
    ("2026-01-05", "SUPERMERCADO EXTRA", 320.00, "alimentacao"),
    ("2026-01-08", "RAPPI *LANCHES", 38.50, "alimentacao"),
    ("2026-01-10", "PADARIA BENJAMIN", 25.00, "alimentacao"),
    ("2026-01-12", "SUPERMERCADO CARREFOUR", 450.00, "alimentacao"),
    ("2026-01-15", "IFOOD *PIZZA", 65.00, "alimentacao"),
    ("2026-01-18", "RESTAURANTE OUTBACK", 280.00, "alimentacao"),
    ("2026-01-20", "SUPERMERCADO PAO DE ACUCAR", 380.00, "alimentacao"),
    ("2026-01-22", "IFOOD *JAPONES", 120.00, "alimentacao"),
    ("2026-01-25", "SUPERMERCADO EXTRA", 290.00, "alimentacao"),
    ("2026-01-28", "RAPPI *MERCADO", 185.60, "alimentacao"),

    # Transporte
    ("2026-01-03", "UBER *TRIP", 25.00, "transporte"),
    ("2026-01-07", "SHELL COMBUSTIVEIS", 280.00, "transporte"),
    ("2026-01-14", "UBER *TRIP", 32.00, "transporte"),
    ("2026-01-21", "SHELL COMBUSTIVEIS", 290.00, "transporte"),
    ("2026-01-28", "99 *CORRIDA", 18.00, "transporte"),

    # Saude
    ("2026-01-10", "DROGARIA SAO PAULO", 156.00, "saude"),
    ("2026-01-15", "CLINICA MEDICA", 350.00, "saude"),
    ("2026-01-20", "DROGASIL", 89.90, "saude"),

    # Assinaturas
    ("2026-01-01", "NETFLIX", 55.90, "assinaturas"),
    ("2026-01-01", "SPOTIFY", 34.90, "assinaturas"),
    ("2026-01-01", "ICLOUD", 10.90, "assinaturas"),
    ("2026-01-05", "OPENAI", 120.00, "assinaturas"),
    ("2026-01-05", "GITHUB", 25.00, "assinaturas"),
    ("2026-01-05", "CLAUDE PRO", 100.00, "assinaturas"),
    ("2026-01-10", "AMAZON PRIME", 14.90, "assinaturas"),
    ("2026-01-15", "GOOGLE ONE", 35.00, "assinaturas"),

    # Compras
    ("2026-01-12", "AMAZON BR", 450.00, "compras"),
    ("2026-01-15", "MERCADO LIVRE", 320.00, "compras"),
    ("2026-01-20", "MAGALU", 890.00, "compras"),

    # Lazer
    ("2026-01-18", "CINEMARK", 89.00, "lazer"),
    ("2026-01-22", "STEAM", 120.00, "lazer"),
    ("2026-01-25", "SPOTIFY PREMIUM", 21.90, "lazer"),

    # Educacao
    ("2026-01-08", "UDEMY", 89.90, "educacao"),
    ("2026-01-20", "AMAZON KINDLE", 45.00, "educacao"),

    # Casa
    ("2026-01-10", "LEROY MERLIN", 890.00, "casa"),
    ("2026-01-15", "TELHANORTE", 450.00, "casa"),
    ("2026-01-25", "COBASI", 120.00, "casa"),

    # Taxas
    ("2026-01-01", "IOF COMPRA INTERNACIONAL", 45.00, "taxas"),
    ("2026-01-15", "TAXA SERVICO BB", 35.00, "taxas"),
    ("2026-01-20", "ANUIDADE CARTAO", 49.90, "taxas"),
]


def setup_database():
    """Configura o banco com dados reais."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Limpando dados anteriores...")
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM installments")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM accounts")

    print("Inserindo categorias...")
    for name, icon, budget, color in CATEGORIES:
        cursor.execute("""
            INSERT INTO categories (name, icon, budget_monthly, color)
            VALUES (?, ?, ?, ?)
        """, (name, icon, budget, color))

    print("Inserindo conta BB...")
    cursor.execute("""
        INSERT INTO accounts (name, type, bank)
        VALUES ('BB Credito', 'credit_card', 'Banco do Brasil')
    """)

    print("Inserindo parcelamentos...")
    for desc, total, installment, total_inst, current, start, end, category in INSTALLMENTS:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        cat_row = cursor.fetchone()
        cat_id = cat_row[0] if cat_row else None

        cursor.execute("""
            INSERT INTO installments
            (description, total_amount, installment_amount, total_installments,
             current_installment, start_date, end_date, category_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (desc, total, installment, total_inst, current, start, end, cat_id))

    print("Inserindo transacoes de Janeiro 2026...")
    cursor.execute("SELECT id FROM accounts WHERE name = 'BB Credito'")
    account_id = cursor.fetchone()[0]

    import hashlib
    for date_str, desc, amount, category in JANUARY_TRANSACTIONS:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        cat_row = cursor.fetchone()
        cat_id = cat_row[0] if cat_row else None

        tx_hash = hashlib.md5(f"{date_str}|{desc}|{abs(amount)}".encode()).hexdigest()

        cursor.execute("""
            INSERT INTO transactions
            (date, description, amount, category_id, account_id, type, source, hash)
            VALUES (?, ?, ?, ?, ?, 'expense', 'seed', ?)
        """, (date_str, desc, -amount, cat_id, account_id, tx_hash))

    conn.commit()

    # Verificar dados
    cursor.execute("SELECT COUNT(*) FROM categories")
    print(f"Categorias: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM installments")
    print(f"Parcelamentos: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM transactions")
    print(f"Transacoes: {cursor.fetchone()[0]}")

    cursor.execute("SELECT SUM(ABS(amount)) FROM transactions")
    total = cursor.fetchone()[0]
    print(f"Total gastos Janeiro: R$ {total:,.2f}")

    conn.close()
    print("\nDados reais configurados com sucesso!")


if __name__ == "__main__":
    setup_database()

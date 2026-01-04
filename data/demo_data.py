#!/usr/bin/env python3
"""
Demo data generator for Streamlit Cloud deployment
Creates sample data when real database is not available
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_demo_database(db_path: str = "data/finance.db"):
    """Create a demo database with sample data"""

    # Check if database already exists
    if os.path.exists(db_path):
        return False

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT '📦',
            budget_monthly REAL DEFAULT 0,
            is_essential INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            type TEXT DEFAULT 'expense',
            source TEXT DEFAULT 'manual',
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS installments (
            id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            total_amount REAL NOT NULL,
            installment_amount REAL NOT NULL,
            total_installments INTEGER NOT NULL,
            current_installment INTEGER DEFAULT 1,
            start_date TEXT NOT NULL,
            end_date TEXT,
            category_id INTEGER,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS monthly_budgets (
            id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            budget_amount REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            UNIQUE(year, month, category_id)
        );
    """)

    # Insert demo categories with icons
    # Valores atualizados em 2025-12-31 (auditoria completa - ícones alinhados com banco)
    categories = [
        ('alimentacao', '🍔', 3500),
        ('compras', '🛒', 2500),
        ('casa', '🏠', 500),           # Gastos regulares de casa
        ('transporte', '🚗', 4000),    # Movida 3200 + Combustível 800
        ('saude', '🏥', 4000),          # Plano saúde + tratamentos
        ('assinaturas', '💻', 3500),   # Aumentado (trabalho + pessoal)
        ('lazer', '🎮', 1500),
        ('educacao', '📚', 200),
        ('taxas', '📝', 100),
        ('esportes', '🎾', 1500),      # Tênis (PIX Thiago Mariotti)
        ('obra', '🏗️', 16500),          # Construção/móveis - budget médio mensal
    ]

    cursor.executemany(
        "INSERT INTO categories (name, icon, budget_monthly) VALUES (?, ?, ?)",
        categories
    )

    # Insert demo transactions for last 6 months
    transaction_templates = [
        ('alimentacao', ['Supermercado', 'Restaurante', 'Padaria', 'iFood', 'Feira'], (50, 800)),
        ('compras', ['Amazon', 'Magazine Luiza', 'Shopee', 'Mercado Livre'], (30, 500)),
        ('casa', ['Material construção', 'Limpeza', 'Manutenção'], (50, 300)),
        ('transporte', ['Combustível', 'Uber', 'Estacionamento', 'Pedágio'], (30, 200)),
        ('saude', ['Farmácia', 'Consulta médica', 'Exames'], (50, 400)),
        ('assinaturas', ['Netflix', 'Spotify', 'Claude Pro', 'GitHub Copilot', 'iCloud'], (15, 200)),
        ('lazer', ['Cinema', 'Viagem', 'Hobby', 'Jogos'], (30, 300)),
        ('educacao', ['Curso online', 'Livros', 'Udemy'], (50, 200)),
        ('taxas', ['Banco', 'Cartão', 'Impostos'], (20, 100)),
    ]

    # Get category IDs
    cursor.execute("SELECT id, name FROM categories")
    cat_map = {name: id for id, name in cursor.fetchall()}

    # Generate transactions for last 6 months
    today = datetime.now()
    transactions = []

    for month_offset in range(6):
        month_date = today - timedelta(days=30 * month_offset)
        year = month_date.year
        month = month_date.month

        for cat_name, descriptions, amount_range in transaction_templates:
            # Generate 3-8 transactions per category per month
            num_transactions = random.randint(3, 8)
            for _ in range(num_transactions):
                day = random.randint(1, 28)
                date = f"{year}-{month:02d}-{day:02d}"
                desc = random.choice(descriptions)
                amount = round(random.uniform(*amount_range), 2)
                transactions.append((date, desc, amount, cat_map[cat_name], 'demo'))

    cursor.executemany(
        "INSERT INTO transactions (date, description, amount, category_id, source) VALUES (?, ?, ?, ?, ?)",
        transactions
    )

    # Insert real installments data - ATUALIZADO com fatura Dez/2025
    # Formato: (desc, total, parcela, num_parcelas, current_in_dec, start, end, cat)
    # current_installment = parcela que aparece em Dezembro (XX de XX/YY)
    installments = [
        # ============================================
        # OBRA/MÓVEIS (não conta no budget variáveis)
        # ============================================
        # Móveis Planejados - pagamento separado (não no cartão)
        ('MOVEIS PLANEJADOS', 95000, 9500, 10, 1, '2025-12-01', '2026-09-01', cat_map['obra']),
        # Futuros
        ('MESA E CADEIRAS', 16000, 1600, 10, 0, '2026-03-01', '2026-12-01', cat_map['obra']),
        ('ELETRODOMESTICOS', 15000, 2500, 6, 0, '2026-04-01', '2026-09-01', cat_map['obra']),

        # ============================================
        # SAÚDE
        # ============================================
        # DROGARIAS PACHECO - Dez=02/03, termina Jan/26
        ('DROGARIAS PACHECO', 5540.16, 1846.72, 3, 2, '2025-11-01', '2026-01-01', cat_map['saude']),
        # DROGARIA MODERNA - Dez=01/02, termina Jan/26
        ('DROGARIA MODERNA', 475.88, 237.94, 2, 1, '2025-12-01', '2026-01-01', cat_map['saude']),

        # ============================================
        # COMPRAS
        # ============================================
        # AMAZON MARKETPLACE - Dez=03/10, termina Jul/26
        ('AMAZON MARKETPLACE', 8352, 835.20, 10, 3, '2025-10-01', '2026-07-01', cat_map['compras']),
        # MAGALU - Dez=01/10, termina Set/26
        ('MAGALU', 4482.50, 448.25, 10, 1, '2025-12-01', '2026-09-01', cat_map['compras']),
        # SHOPEE FIDCO - Dez=03/12, termina Set/26
        ('SHOPEE FIDCO', 2321.64, 193.47, 12, 3, '2025-10-01', '2026-09-01', cat_map['compras']),
        # VINDI BROIL - Dez=03/10, termina Jul/26
        ('VINDI BROIL', 3590.10, 359.01, 10, 3, '2025-10-01', '2026-07-01', cat_map['compras']),
        # AREDES - Dez=07/08, termina Jan/26
        ('AREDES', 5362.88, 670.36, 8, 7, '2025-06-01', '2026-01-01', cat_map['compras']),
        # OTIQUE - Dez=08/10, termina Fev/26
        ('OTIQUE', 850, 85, 10, 8, '2025-05-01', '2026-02-01', cat_map['compras']),
        # LOVABLE - Dez=03/04, termina Jan/26
        ('LOVABLE', 613.72, 153.43, 4, 3, '2025-10-01', '2026-01-01', cat_map['assinaturas']),
        # MACOPIL - Dez=01/05, termina Abr/26
        ('MACOPIL', 639.05, 127.81, 5, 1, '2025-12-01', '2026-04-01', cat_map['compras']),
        # SHOPEE MEUPUXADOR - Dez=01/05, termina Abr/26
        ('SHOPEE MEUPUXADOR', 587.80, 117.56, 5, 1, '2025-12-01', '2026-04-01', cat_map['compras']),

        # ============================================
        # CASA
        # ============================================
        # CASA CHIESSE 2X - Dez=01/02, termina Jan/26
        ('CASA CHIESSE 2X', 1098, 549, 2, 1, '2025-12-01', '2026-01-01', cat_map['casa']),
        # CASA CHIESSE 5X - Dez=01/05, termina Abr/26
        ('CASA CHIESSE 5X', 815.35, 163.07, 5, 1, '2025-12-01', '2026-04-01', cat_map['casa']),
        # FIRE VERBO - Dez=01/02, termina Jan/26
        ('FIRE VERBO', 440, 220, 2, 1, '2025-12-01', '2026-01-01', cat_map['casa']),

        # ============================================
        # ASSINATURAS
        # ============================================
        # OPENAI CHATGPT - Dez=03/12, termina Set/26
        ('OPENAI CHATGPT', 1308.08, 109.09, 12, 3, '2025-10-01', '2026-09-01', cat_map['assinaturas']),
        # FLOWITH.IO - Dez=01/05, termina Abr/26
        ('FLOWITH.IO', 305.25, 61.05, 5, 1, '2025-12-01', '2026-04-01', cat_map['assinaturas']),
        # TAVUS - Dez=01/05, termina Abr/26
        ('TAVUS', 361.80, 72.36, 5, 1, '2025-12-01', '2026-04-01', cat_map['assinaturas']),
    ]

    cursor.executemany(
        """INSERT INTO installments
           (description, total_amount, installment_amount, total_installments,
            current_installment, start_date, end_date, category_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        installments
    )

    # Gerar transações de parcelamentos para Janeiro 2026
    # Isso garante que os parcelamentos "comam" do budget no dashboard
    from datetime import datetime as dt
    year, month = 2026, 1
    target_date = dt(year, month, 1)

    cursor.execute("SELECT * FROM installments WHERE status = 'active'")
    active_installments = cursor.fetchall()

    for inst in active_installments:
        inst_id, desc, total_amt, inst_amt, total_inst, current_inst, start_date, end_date, cat_id, status = inst

        start = dt.strptime(start_date, '%Y-%m-%d')
        end = dt.strptime(end_date, '%Y-%m-%d')

        if start <= target_date <= end:
            months_elapsed = (target_date.year - start.year) * 12 + (target_date.month - start.month)
            parcela_num = months_elapsed + 1

            if parcela_num <= total_inst:
                tx_desc = f"{desc} {parcela_num}/{total_inst}"
                tx_date = f"{year}-{month:02d}-10"

                cursor.execute('''
                    INSERT INTO transactions (date, description, amount, category_id, type, source)
                    VALUES (?, ?, ?, ?, 'expense', 'parcelamento')
                ''', (tx_date, tx_desc, inst_amt, cat_id))

    conn.commit()
    conn.close()

    return True

if __name__ == "__main__":
    if create_demo_database():
        print("Demo database created successfully!")
    else:
        print("Database already exists, skipping demo data creation.")

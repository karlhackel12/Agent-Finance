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
    categories = [
        ('alimentacao', '🍽️', 4000, 1),
        ('compras', '🛒', 3500, 0),
        ('casa', '🏠', 2000, 1),
        ('transporte', '🚗', 1500, 1),
        ('saude', '💊', 1500, 1),
        ('assinaturas', '📱', 2011, 0),
        ('lazer', '🎮', 1500, 0),
        ('educacao', '📚', 1500, 0),
        ('taxas', '🏦', 1000, 0),
    ]

    cursor.executemany(
        "INSERT INTO categories (name, icon, budget_monthly, is_essential) VALUES (?, ?, ?, ?)",
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

    # Insert real installments data
    installments = [
        # Grandes - Obra/Móveis
        ('MOVEIS PLANEJADOS', 95000, 9500, 10, 2, '2025-12-01', '2026-10-01', cat_map['casa']),
        ('MESA E CADEIRAS', 16000, 1600, 10, 1, '2026-01-01', '2026-10-01', cat_map['casa']),
        ('ELETRODOMESTICOS', 15000, 2500, 6, 0, '2026-09-01', '2027-02-01', cat_map['casa']),
        # Saúde
        ('DROGARIAS PACHECO', 5540, 1846.72, 3, 2, '2025-12-01', '2026-02-01', cat_map['saude']),
        ('DROGARIA MODERNA', 476, 237.94, 2, 1, '2026-01-01', '2026-02-01', cat_map['saude']),
        # Compras
        ('AMAZON MARKETPLACE', 8352, 835.2, 10, 3, '2025-11-01', '2026-08-01', cat_map['compras']),
        ('AREDES', 5363, 670.36, 8, 7, '2025-07-01', '2026-02-01', cat_map['compras']),
        ('MAGALU', 4482, 448.25, 10, 1, '2026-01-01', '2026-10-01', cat_map['compras']),
        ('ALFATEC COMERCIO', 8689, 413.76, 21, 16, '2024-10-01', '2026-06-01', cat_map['compras']),
        ('VINDI BROIL', 3590, 359.01, 10, 3, '2025-11-01', '2026-08-01', cat_map['compras']),
        ('SHOPEE FIDCO', 2322, 193.47, 12, 3, '2025-11-01', '2026-10-01', cat_map['compras']),
        ('LOVABLE', 614, 153.43, 4, 3, '2025-11-01', '2026-02-01', cat_map['compras']),
        ('MACOPIL', 639, 127.81, 5, 1, '2026-01-01', '2026-05-01', cat_map['compras']),
        ('SHOPEE MEUPUXADOR', 588, 117.56, 5, 1, '2026-01-01', '2026-05-01', cat_map['compras']),
        ('MARIA LUIZA', 410, 102.5, 4, 3, '2025-11-01', '2026-02-01', cat_map['compras']),
        ('OTIQUE', 850, 85, 10, 8, '2025-06-01', '2026-03-01', cat_map['compras']),
        # Casa
        ('CASA CHIESSE 2X', 1098, 549, 2, 1, '2026-01-01', '2026-02-01', cat_map['casa']),
        ('CASA CHIESSE 5X', 815, 163.07, 5, 1, '2026-01-01', '2026-05-01', cat_map['casa']),
        ('FIRE VERBO', 440, 220, 2, 1, '2026-01-01', '2026-02-01', cat_map['casa']),
        ('TAVUS', 362, 72.36, 5, 1, '2026-01-01', '2026-05-01', cat_map['compras']),
        ('FLOWITH.IO', 305, 61.05, 5, 1, '2026-01-01', '2026-05-01', cat_map['assinaturas']),
        # Assinaturas
        ('OPENAI CHATGPT', 1309, 109.09, 12, 3, '2025-11-01', '2026-10-01', cat_map['assinaturas']),
    ]

    cursor.executemany(
        """INSERT INTO installments
           (description, total_amount, installment_amount, total_installments,
            current_installment, start_date, end_date, category_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        installments
    )

    conn.commit()
    conn.close()

    return True

if __name__ == "__main__":
    if create_demo_database():
        print("Demo database created successfully!")
    else:
        print("Database already exists, skipping demo data creation.")

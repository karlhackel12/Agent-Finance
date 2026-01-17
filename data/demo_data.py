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

    # Generate demo transactions for months BEFORE Janeiro 2026
    # Janeiro 2026 has real transactions added separately
    transactions = []

    # Generate for Jul-Dez 2025 (6 months before Jan 2026)
    demo_months = [
        (2025, 7), (2025, 8), (2025, 9),
        (2025, 10), (2025, 11), (2025, 12)
    ]

    for year, month in demo_months:
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
        ('VINDI BROIL', 3590.10, 359.01, 10, 3, '2025-10-01', '2026-07-01', cat_map['obra']),
        # AREDES - Dez=07/08, termina Jan/26
        ('AREDES', 5362.88, 670.36, 8, 7, '2025-06-01', '2026-01-01', cat_map['obra']),
        # OTIQUE - Dez=08/10, termina Fev/26
        ('OTIQUE', 850, 85, 10, 8, '2025-05-01', '2026-02-01', cat_map['compras']),
        # LOVABLE - Dez=03/04, termina Jan/26
        ('LOVABLE', 613.72, 153.43, 4, 3, '2025-10-01', '2026-01-01', cat_map['assinaturas']),
        # MACOPIL - Dez=01/05, termina Abr/26
        ('MACOPIL', 639.05, 127.81, 5, 1, '2025-12-01', '2026-04-01', cat_map['obra']),
        # SHOPEE MEUPUXADOR - Dez=01/05, termina Abr/26
        ('SHOPEE MEUPUXADOR', 587.80, 117.56, 5, 1, '2025-12-01', '2026-04-01', cat_map['compras']),

        # ============================================
        # CASA
        # ============================================
        # CASA CHIESSE 2X - Dez=01/02, termina Jan/26
        ('CASA CHIESSE 2X', 1098, 549, 2, 1, '2025-12-01', '2026-01-01', cat_map['obra']),
        # CASA CHIESSE 5X - Dez=01/05, termina Abr/26
        ('CASA CHIESSE 5X', 815.35, 163.07, 5, 1, '2025-12-01', '2026-04-01', cat_map['obra']),
        # FIRE VERBO - Dez=01/02, termina Jan/26
        ('FIRE VERBO', 440, 220, 2, 1, '2025-12-01', '2026-01-01', cat_map['lazer']),

        # RAIA311 - Jan=01/02, termina Fev/26
        ('RAIA311', 1859.42, 929.71, 2, 1, '2026-01-01', '2026-02-01', cat_map['saude']),

        # PICPAY Karl Obra - Jan=01/02
        ('PICPAY OBRA', 1971.26, 985.63, 2, 1, '2026-01-01', '2026-02-01', cat_map['obra']),

        # PICPAY Móveis - Jan=01/02
        ('PICPAY MOVEIS', 10475.86, 5237.93, 2, 1, '2026-01-01', '2026-02-01', cat_map['obra']),

        # EDZCOLLAB4TEA - Jan=01/12
        ('EDZCOLLAB4TEA', 1188.48, 99.04, 12, 1, '2026-01-01', '2026-12-01', cat_map['educacao']),

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

    # Adicionar transações reais de Janeiro 2026 (à vista)
    # Atualizado 2026-01-17 com fatura completa 28/12-16/01
    jan_2026_transactions = [
        # ============================================
        # ALIMENTAÇÃO
        # ============================================
        ('2026-01-02', 'COSECHAS BM', 48.30, cat_map['alimentacao']),
        ('2026-01-02', 'NATANAEL PESCADOS', 263.20, cat_map['alimentacao']),
        ('2026-01-05', 'SUPERMERCADO 365', 146.12, cat_map['alimentacao']),
        ('2026-01-05', 'Pix Karl (reembolso)', 282.00, cat_map['alimentacao']),
        ('2026-01-05', 'KIOSQUE DO ALEMO', 34.70, cat_map['alimentacao']),
        ('2026-01-05', 'IFD*BR (iFood)', 164.66, cat_map['alimentacao']),
        ('2026-01-06', 'IFD*BR (iFood)', 7.95, cat_map['alimentacao']),
        ('2026-01-08', 'A F PEREIRA MERCEARIA', 48.80, cat_map['alimentacao']),
        ('2026-01-08', 'PASTA A MANO', 90.48, cat_map['alimentacao']),
        ('2026-01-08', 'NAGUMO', 338.85, cat_map['alimentacao']),
        ('2026-01-09', 'A F PEREIRA MERCEARIA', 49.00, cat_map['alimentacao']),
        ('2026-01-09', 'PANIFICADORA ACHILES', 94.25, cat_map['alimentacao']),
        ('2026-01-09', 'RESTAURANTE DA LUZIA', 25.00, cat_map['alimentacao']),
        ('2026-01-09', '016 HAMBURGUERIA', 50.00, cat_map['alimentacao']),
        ('2026-01-10', 'iFood', 5.95, cat_map['alimentacao']),
        ('2026-01-10', 'RESTAURANTE DA LUZIA', 75.00, cat_map['alimentacao']),
        ('2026-01-11', 'LANCHONETE DINOSSAUROS', 12.00, cat_map['alimentacao']),
        ('2026-01-12', 'CODEV COMERCIO ALIM', 32.80, cat_map['alimentacao']),
        ('2026-01-14', 'A F PEREIRA MERCEARIA', 24.00, cat_map['alimentacao']),
        ('2026-01-15', 'JIM.COM PADAKA27', 14.00, cat_map['alimentacao']),
        ('2026-01-15', 'RESTAURANTE DA LUZIA', 58.00, cat_map['alimentacao']),
        ('2026-01-16', 'OZIEL BATISTA ALVES', 35.00, cat_map['alimentacao']),
        ('2026-01-16', 'RESTAURANTE DA LUZIA', 65.00, cat_map['alimentacao']),

        # ============================================
        # TRANSPORTE
        # ============================================
        ('2026-01-05', 'POSTO NACOES UNIDAS', 100.00, cat_map['transporte']),
        ('2026-01-06', 'MOVIDA CARRO', 3270.00, cat_map['transporte']),

        # ============================================
        # SAÚDE
        # ============================================
        ('2026-01-02', 'FARMASOUZA', 129.88, cat_map['saude']),
        ('2026-01-06', 'RAIA4154', 152.83, cat_map['saude']),
        ('2026-01-06', 'RAIA311 (1/2)', 929.71, cat_map['saude']),
        ('2026-01-13', 'TAINARA (salão)', 105.00, cat_map['saude']),
        ('2026-01-15', 'DROGARIAS ECONOMIZE', 26.58, cat_map['saude']),
        ('2026-01-15', 'PICPAY*UNIMEDSEGU', 1430.91, cat_map['saude']),

        # ============================================
        # ASSINATURAS
        # ============================================
        ('2026-01-01', 'PPRO *MICROSOFT', 60.00, cat_map['assinaturas']),
        ('2026-01-01', 'REPLIT', 289.39, cat_map['assinaturas']),
        ('2026-01-05', 'Amazon Prime Canais', 14.99, cat_map['assinaturas']),
        ('2026-01-06', 'AQUA VOICE', 56.47, cat_map['assinaturas']),
        ('2026-01-06', 'NOTION LABS', 135.71, cat_map['assinaturas']),
        ('2026-01-06', '21ST.DEV', 113.05, cat_map['assinaturas']),
        ('2026-01-06', 'AMAZON SERVICOS', 19.90, cat_map['assinaturas']),
        ('2026-01-06', 'FLOAT LABS', 101.75, cat_map['assinaturas']),
        ('2026-01-07', 'CLAUDE.AI', 550.00, cat_map['assinaturas']),
        ('2026-01-07', 'PADDLE.NET N8N', 150.00, cat_map['assinaturas']),
        ('2026-01-08', 'EVOSTARTER', 112.26, cat_map['assinaturas']),
        ('2026-01-08', 'Amazon Prime Canais', 44.90, cat_map['assinaturas']),
        ('2026-01-08', 'CLOUDFLARE', 28.02, cat_map['assinaturas']),
        ('2026-01-08', 'CLAUDE.AI', 641.07, cat_map['assinaturas']),
        ('2026-01-08', 'ANTHROPIC', 50.00, cat_map['assinaturas']),
        ('2026-01-08', 'REPLIT', 137.45, cat_map['assinaturas']),
        ('2026-01-08', 'REPLIT', 140.09, cat_map['assinaturas']),
        ('2026-01-09', 'JUSBRASIL', 39.90, cat_map['assinaturas']),
        ('2026-01-10', 'VERCEL', 111.71, cat_map['assinaturas']),
        ('2026-01-10', 'CURSOR AI', 111.71, cat_map['assinaturas']),
        ('2026-01-11', 'RECLAIM.AI', 67.03, cat_map['assinaturas']),
        ('2026-01-12', 'Amazon Prime Canais', 16.90, cat_map['assinaturas']),
        ('2026-01-13', 'Google YouTube Member', 4.99, cat_map['assinaturas']),
        ('2026-01-14', 'Amazon Prime Canais', 19.90, cat_map['assinaturas']),
        ('2026-01-15', 'DOANYTHINGMACHINE', 111.83, cat_map['assinaturas']),
        ('2026-01-15', 'Z-API.IO', 99.99, cat_map['assinaturas']),
        ('2026-01-15', 'Globo Premiere', 59.90, cat_map['assinaturas']),
        ('2026-01-15', 'Amazon Prime Canais', 34.90, cat_map['assinaturas']),
        ('2026-01-15', 'Contabilizei', 369.00, cat_map['assinaturas']),
        ('2026-01-16', 'Contabilizei', 178.43, cat_map['assinaturas']),
        ('2026-01-16', 'Amazon Kindle Unltd', 24.90, cat_map['assinaturas']),

        # ============================================
        # COMPRAS
        # ============================================
        ('2026-01-05', 'AMAZON BR', 141.00, cat_map['compras']),
        ('2026-01-05', 'AMAZON BOOKWIRE', 73.38, cat_map['compras']),
        ('2026-01-06', 'AMAZON MARKETPLACE', 250.90, cat_map['compras']),
        ('2026-01-08', 'EVOSTARTER', 112.26, cat_map['compras']),
        ('2026-01-12', 'ShoppingParkSul', 16.00, cat_map['compras']),

        # ============================================
        # LAZER (inclui Clash Royale)
        # ============================================
        ('2026-01-05', 'Pix MATHAUS', 283.00, cat_map['lazer']),
        ('2026-01-05', 'Pix THOMAS', 283.00, cat_map['lazer']),
        ('2026-01-05', 'Google Clash Royale', 57.90, cat_map['lazer']),
        ('2026-01-07', 'Google Clash Royale', 45.90, cat_map['lazer']),
        ('2026-01-11', 'THAURUS INDUSTRIA', 619.09, cat_map['lazer']),
        ('2026-01-12', 'Google Clash Royale', 24.90, cat_map['lazer']),
        ('2026-01-14', 'Google Clash Royale', 29.90, cat_map['lazer']),
        ('2026-01-14', 'OF London', 46.24, cat_map['lazer']),
        ('2026-01-15', 'Google Clash Royale', 59.90, cat_map['lazer']),
        ('2026-01-15', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-15', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-15', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-16', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-16', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-16', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2026-01-16', 'Google Clash Royale', 18.50, cat_map['lazer']),

        # ============================================
        # CASA
        # ============================================
        ('2026-01-06', 'MY PET BARRA', 273.00, cat_map['casa']),
        ('2026-01-10', 'CONTA VIVO', 120.00, cat_map['casa']),

        # ============================================
        # TAXAS
        # ============================================
        ('2026-01-07', 'IOF compras exterior', 31.30, cat_map['taxas']),
        ('2026-01-07', 'IOF saque Pix', 16.62, cat_map['taxas']),
        ('2026-01-07', 'Juros saque Pix', 98.48, cat_map['taxas']),
        ('2026-01-05', 'Devolução juros', -43.16, cat_map['taxas']),
        ('2026-01-09', 'IOF compras exterior', 3.35, cat_map['taxas']),
        ('2026-01-12', 'IOF compras exterior', 3.17, cat_map['taxas']),
        ('2026-01-14', 'IOF PIX CHOK', 7.50, cat_map['taxas']),
        ('2026-01-14', 'Juros saque Pix', 38.45, cat_map['taxas']),
        ('2026-01-15', 'IOF compras exterior', 1.73, cat_map['taxas']),
        ('2026-01-16', 'Receita Federal', 435.34, cat_map['taxas']),
        ('2026-01-29', 'Serasa Experian', 23.90, cat_map['taxas']),

        # ============================================
        # OBRA (PIX eletricista + parcelamentos móveis)
        # ============================================
        ('2026-01-14', 'PIX CHOK ELETRIC', 1240.00, cat_map['obra']),
        ('2026-01-12', 'PICPAY*Karl A (obra)', 985.63, cat_map['obra']),
        ('2026-01-14', 'PICPAY*Karl A (móveis 1/2)', 5237.93, cat_map['obra']),

        # ============================================
        # EDUCAÇÃO
        # ============================================
        ('2026-01-11', 'EDZCOLLAB4TEA (1/12)', 99.04, cat_map['educacao']),
    ]

    # Transações de Dezembro 2025 (data da transação, não do pagamento)
    dez_2025_transactions = [
        # Alimentação
        ('2025-12-28', 'A F PEREIRA MERCEARIA', 28.00, cat_map['alimentacao']),
        ('2025-12-29', 'IFD*BR (iFood)', 250.49, cat_map['alimentacao']),
        ('2025-12-30', 'SUPERMERCADO PEROLA', 307.36, cat_map['alimentacao']),
        ('2025-12-31', 'POSTO NACOES UNIDAS', 50.00, cat_map['transporte']),
        ('2025-12-31', 'IFD*BR (iFood)', 184.88, cat_map['alimentacao']),
        ('2025-12-31', 'RESTAURANTE PIEMONTE', 38.15, cat_map['alimentacao']),

        # Assinaturas
        ('2025-12-28', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2025-12-28', 'Google Clash Royale', 18.50, cat_map['lazer']),
        ('2025-12-29', 'Amazon Prime Aluguel', 29.90, cat_map['assinaturas']),
        ('2025-12-30', 'FLOWITH.IO', 289.27, cat_map['assinaturas']),
        ('2025-12-29', 'RIVERSIDEFM', 167.13, cat_map['assinaturas']),

        # Taxas
        ('2025-12-30', 'IOF compras exterior', 4.01, cat_map['taxas']),
    ]

    cursor.executemany(
        "INSERT INTO transactions (date, description, amount, category_id, source) VALUES (?, ?, ?, ?, 'real_dez2025')",
        dez_2025_transactions
    )

    cursor.executemany(
        "INSERT INTO transactions (date, description, amount, category_id, source) VALUES (?, ?, ?, ?, 'real_jan2026')",
        jan_2026_transactions
    )

    conn.commit()
    conn.close()

    return True

if __name__ == "__main__":
    if create_demo_database():
        print("Demo database created successfully!")
    else:
        print("Database already exists, skipping demo data creation.")

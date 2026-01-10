#!/usr/bin/env python3
"""
Adiciona transações reais de Janeiro 2026 ao banco de dados
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "finance.db"

def get_category_id(cursor, category_name: str) -> int:
    """Obtém ID da categoria pelo nome."""
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Categoria não encontrada: {category_name}")
    return result[0]

def add_transactions():
    """Adiciona transações de Janeiro 2026."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obter IDs das categorias
    cat_ids = {}
    categories = ['alimentacao', 'transporte', 'saude', 'assinaturas', 'compras',
                  'lazer', 'casa', 'taxas']
    for cat in categories:
        cat_ids[cat] = get_category_id(cursor, cat)

    # Transações de Janeiro 2026 (apenas à vista, parcelamentos já existem)
    transactions = [
        # ========== ALIMENTACAO ==========
        ('2025-12-29', 'A F PEREIRA MERCEARIA', 28.00, cat_ids['alimentacao']),
        ('2025-12-30', 'SUPERMERCADO PEROLA', 307.36, cat_ids['alimentacao']),
        ('2026-01-02', 'COSECHAS BM', 48.30, cat_ids['alimentacao']),
        ('2026-01-02', 'NATANAEL PESCADOS', 263.20, cat_ids['alimentacao']),
        ('2026-01-05', 'SUPERMERCADO 365', 146.12, cat_ids['alimentacao']),
        ('2026-01-05', 'Pix Karl (reembolso alimentação)', 282.00, cat_ids['alimentacao']),
        ('2026-01-08', 'A F PEREIRA MERCEARIA', 48.80, cat_ids['alimentacao']),
        ('2026-01-09', 'A F PEREIRA MERCEARIA', 49.00, cat_ids['alimentacao']),
        # Restaurantes
        ('2025-12-29', 'IFD*BR (iFood)', 250.49, cat_ids['alimentacao']),
        ('2025-12-31', 'IFD*BR (iFood)', 184.88, cat_ids['alimentacao']),
        ('2025-12-31', 'RESTAURANTE PIEMONTE', 38.15, cat_ids['alimentacao']),
        ('2026-01-05', 'KIOSQUE DO ALEMO', 34.70, cat_ids['alimentacao']),
        ('2026-01-05', 'IFD*BR (iFood)', 164.66, cat_ids['alimentacao']),
        ('2026-01-06', 'IFD*BR (iFood)', 7.95, cat_ids['alimentacao']),
        ('2026-01-08', 'PASTA A MANO', 90.48, cat_ids['alimentacao']),
        ('2026-01-09', 'PANIFICADORA ACHILES', 94.25, cat_ids['alimentacao']),
        ('2026-01-09', 'RESTAURANTE DA LUZIA', 25.00, cat_ids['alimentacao']),
        ('2026-01-09', '016 HAMBURGUERIA', 50.00, cat_ids['alimentacao']),
        ('2026-01-10', 'iFood', 5.95, cat_ids['alimentacao']),

        # ========== TRANSPORTE ==========
        ('2025-12-31', 'POSTO NACOES UNIDAS', 50.00, cat_ids['transporte']),
        ('2026-01-05', 'POSTO NACOES UNIDAS', 100.00, cat_ids['transporte']),
        ('2026-01-06', 'MOVIDA CARRO ASSINATURA', 3270.00, cat_ids['transporte']),

        # ========== SAUDE ==========
        ('2026-01-02', 'FARMASOUZA', 129.88, cat_ids['saude']),
        ('2026-01-06', 'RAIA4154', 152.83, cat_ids['saude']),
        ('2026-01-06', 'RAIA311 (1/2)', 929.71, cat_ids['saude']),

        # ========== ASSINATURAS ==========
        ('2025-12-28', 'Google Clash Royale', 18.50, cat_ids['assinaturas']),
        ('2025-12-28', 'Google Clash Royale', 18.50, cat_ids['assinaturas']),
        ('2025-12-29', 'Serasa Experian', 23.90, cat_ids['assinaturas']),
        ('2025-12-29', 'RIVERSIDEFM', 167.13, cat_ids['assinaturas']),
        ('2025-12-29', 'Amazon Prime Aluguel', 29.90, cat_ids['assinaturas']),
        ('2025-12-30', 'FLOWITH.IO', 289.27, cat_ids['assinaturas']),
        ('2026-01-01', 'PPRO *MICROSOFT', 60.00, cat_ids['assinaturas']),
        ('2026-01-01', 'REPLIT', 289.39, cat_ids['assinaturas']),
        ('2026-01-05', 'Google Clash Royale', 57.90, cat_ids['assinaturas']),
        ('2026-01-05', 'Amazon Prime Canais', 14.99, cat_ids['assinaturas']),
        ('2026-01-06', 'AQUA VOICE', 56.47, cat_ids['assinaturas']),
        ('2026-01-06', 'NOTION LABS', 135.71, cat_ids['assinaturas']),
        ('2026-01-06', '21ST.DEV', 113.05, cat_ids['assinaturas']),
        ('2026-01-06', 'AMAZON SERVICOS', 19.90, cat_ids['assinaturas']),
        ('2026-01-06', 'FLOAT LABS (SUPERCUT)', 101.75, cat_ids['assinaturas']),
        ('2026-01-07', 'CLAUDE.AI', 550.00, cat_ids['assinaturas']),
        ('2026-01-07', 'PADDLE.NET* N8N CLOUD', 150.00, cat_ids['assinaturas']),
        ('2026-01-07', 'Google Clash Royale', 45.90, cat_ids['assinaturas']),
        ('2026-01-08', 'EVOSTARTER', 112.26, cat_ids['assinaturas']),
        ('2026-01-08', 'Amazon Prime Canais', 44.90, cat_ids['assinaturas']),
        ('2026-01-08', 'CLOUDFLARE', 28.02, cat_ids['assinaturas']),
        ('2026-01-08', 'CLAUDE.AI', 641.07, cat_ids['assinaturas']),
        ('2026-01-08', 'ANTHROPIC', 50.00, cat_ids['assinaturas']),
        ('2026-01-08', 'REPLIT', 137.45, cat_ids['assinaturas']),
        ('2026-01-08', 'REPLIT', 140.09, cat_ids['assinaturas']),
        ('2026-01-09', 'JUSBRASIL', 39.90, cat_ids['assinaturas']),

        # ========== COMPRAS ==========
        ('2026-01-05', 'AMAZON BR', 141.00, cat_ids['compras']),
        ('2026-01-05', 'AMAZONMKTPLC*BOOKWIRE', 73.38, cat_ids['compras']),
        ('2026-01-06', 'AMAZON MARKETPLACE', 250.90, cat_ids['compras']),

        # ========== LAZER ==========
        ('2026-01-05', 'FIRE VERBO', 240.00, cat_ids['lazer']),
        ('2026-01-05', 'Pix MATHAUS ALVES HACKEL', 283.00, cat_ids['lazer']),
        ('2026-01-05', 'Pix THOMAS ALVES HACKEL', 283.00, cat_ids['lazer']),

        # ========== CASA ==========
        ('2026-01-06', 'MY PET BARRA', 273.00, cat_ids['casa']),
        ('2026-01-10', 'CONTA VIVO', 120.00, cat_ids['casa']),

        # ========== TAXAS ==========
        ('2026-01-07', 'IOF compras exterior', 31.30, cat_ids['taxas']),
        ('2026-01-07', 'IOF saque Pix', 16.62, cat_ids['taxas']),
        ('2026-01-07', 'Juros saque Pix', 98.48, cat_ids['taxas']),
        ('2026-01-05', 'Devolução juros (crédito)', -43.16, cat_ids['taxas']),
    ]

    # Inserir transações
    inserted = 0
    for date, desc, amount, cat_id in transactions:
        try:
            # Verificar duplicata simples (data + descrição + valor)
            cursor.execute("""
                SELECT id FROM transactions
                WHERE date = ? AND description = ? AND amount = ?
            """, (date, desc, amount))

            if cursor.fetchone():
                print(f"⏭️  Duplicata: {date} {desc} R$ {amount:.2f}")
                continue

            tx_type = 'expense' if amount > 0 else 'income'
            cursor.execute("""
                INSERT INTO transactions (date, description, amount, category_id, type, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, desc, amount, cat_id, tx_type, 'manual_jan2026'))

            inserted += 1
            print(f"✅ {date} {desc}: R$ {amount:.2f}")

        except Exception as e:
            print(f"❌ Erro ao inserir {desc}: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Total inserido: {inserted} transações")
    return inserted

if __name__ == "__main__":
    print("🔄 Adicionando transações de Janeiro 2026...\n")
    add_transactions()
    print("\n✅ Concluído! Execute sync_obsidian.py para atualizar os dashboards.")

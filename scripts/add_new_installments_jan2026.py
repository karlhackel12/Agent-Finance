#!/usr/bin/env python3
"""
Adiciona novos parcelamentos encontrados na fatura Janeiro 2026

Parcelamentos novos:
1. LOJAS RENNER - R$ 180,95 × 2 (compras)
2. AMAZON MARKET - R$ 1.399,76 × 2 (compras) - última parcela
3. MARIA LUIZA B - R$ 102,50 × 4 (compras) - última parcela
4. ALFATEC COMER - R$ 413,76 × 21 (compras)
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from finance_db import get_connection, get_category_by_name

def add_months(date_str, months):
    """Adiciona meses a uma data."""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    year = date.year
    month = date.month + months

    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1

    return f"{year:04d}-{month:02d}-{date.day:02d}"

def add_installment(description, total_amount, installment_amount, total_installments,
                   current_installment, start_date, category_name, status='active'):
    """Adiciona um parcelamento ao banco."""
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar category_id
    category = get_category_by_name(category_name)
    if not category:
        print(f"❌ Categoria '{category_name}' não encontrada!")
        return False

    category_id = category['id']

    # Calcular end_date
    months_remaining = total_installments - current_installment
    end_date = add_months(start_date, months_remaining)

    # Inserir parcelamento
    cursor.execute('''
        INSERT INTO installments
        (description, total_amount, installment_amount, total_installments,
         current_installment, start_date, end_date, category_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        description, total_amount, installment_amount, total_installments,
        current_installment, start_date, end_date, category_id, status
    ))

    conn.commit()
    conn.close()

    return True


def main():
    print("="*70)
    print("CADASTRO DE NOVOS PARCELAMENTOS - JANEIRO 2026")
    print("="*70)
    print()

    installments = [
        {
            'description': 'LOJAS RENNER - Roupas',
            'total_amount': 361.90,  # 180.95 × 2
            'installment_amount': 180.95,
            'total_installments': 2,
            'current_installment': 1,  # Primeira parcela apareceu em jan
            'start_date': '2026-01-21',
            'category': 'compras',
            'status': 'active'
        },
        {
            'description': 'AMAZON MARKET - Compras',
            'total_amount': 2799.52,  # 1399.76 × 2
            'installment_amount': 1399.76,
            'total_installments': 2,
            'current_installment': 2,  # Última parcela apareceu em jan
            'start_date': '2025-12-31',  # Estimado (parcela 1 em dez)
            'category': 'compras',
            'status': 'ending'  # Última parcela
        },
        {
            'description': 'MARIA LUIZA B - Serviço Pessoal',
            'total_amount': 410.00,  # 102.50 × 4
            'installment_amount': 102.50,
            'total_installments': 4,
            'current_installment': 4,  # Última parcela apareceu em jan
            'start_date': '2025-09-26',  # Estimado
            'category': 'compras',
            'status': 'ending'  # Última parcela
        },
        {
            'description': 'ALFATEC COMER - Eletrodomésticos',
            'total_amount': 8689.96,  # 413.76 × 21
            'installment_amount': 413.76,
            'total_installments': 21,
            'current_installment': 17,  # Parcela 17 apareceu em jan
            'start_date': '2024-09-29',  # Estimado (16 meses antes de jan/2026)
            'category': 'compras',
            'status': 'active'  # Ainda 4 parcelas restantes
        }
    ]

    added = 0
    for inst in installments:
        print(f"📝 Cadastrando: {inst['description']}")
        print(f"   • Total: R$ {inst['total_amount']:.2f}")
        print(f"   • Parcela {inst['current_installment']}/{inst['total_installments']}: R$ {inst['installment_amount']:.2f}")
        print(f"   • Categoria: {inst['category']}")
        print(f"   • Status: {inst['status']}")

        success = add_installment(
            description=inst['description'],
            total_amount=inst['total_amount'],
            installment_amount=inst['installment_amount'],
            total_installments=inst['total_installments'],
            current_installment=inst['current_installment'],
            start_date=inst['start_date'],
            category_name=inst['category'],
            status=inst['status']
        )

        if success:
            print("   ✅ Cadastrado com sucesso!")
            added += 1
        else:
            print("   ❌ Erro ao cadastrar")

        print()

    print("="*70)
    print(f"✨ Total cadastrado: {added}/{len(installments)} parcelamentos")
    print("="*70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Remove duplicate transactions from finance.db
Uses hash-based detection: MD5(date|description|amount)
Keeps first occurrence, deletes subsequent duplicates
"""

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'finance.db'

def calculate_hash(date: str, description: str, amount: float) -> str:
    """Calculate MD5 hash for transaction."""
    key = f"{date}|{description}|{amount:.2f}"
    return hashlib.md5(key.encode()).hexdigest()

def update_missing_hashes(conn):
    """Update hash column for transactions that don't have one."""
    cursor = conn.cursor()

    # Get transactions without hash
    cursor.execute("""
        SELECT id, date, description, amount
        FROM transactions
        WHERE hash IS NULL OR hash = ''
    """)

    transactions = cursor.fetchall()

    if not transactions:
        return 0

    # Update each transaction with calculated hash
    for txn_id, date, description, amount in transactions:
        txn_hash = calculate_hash(date, description, amount)
        cursor.execute("UPDATE transactions SET hash = ? WHERE id = ?", (txn_hash, txn_id))

    conn.commit()
    return len(transactions)

def find_duplicates(conn):
    """Find all duplicate transactions in database."""
    cursor = conn.cursor()

    # Get all transactions
    cursor.execute("""
        SELECT id, date, description, amount, hash
        FROM transactions
        ORDER BY date, id
    """)

    transactions = cursor.fetchall()

    # Track seen hashes and duplicates
    seen_hashes = {}
    duplicates = []

    for txn_id, date, description, amount, stored_hash in transactions:
        # Calculate hash (in case it's missing in DB)
        calc_hash = calculate_hash(date, description, amount)

        # Use stored hash if available, otherwise calculated
        txn_hash = stored_hash or calc_hash

        if txn_hash in seen_hashes:
            # This is a duplicate
            original_id = seen_hashes[txn_hash]
            duplicates.append({
                'id': txn_id,
                'original_id': original_id,
                'date': date,
                'description': description,
                'amount': amount,
                'hash': txn_hash
            })
        else:
            # First occurrence
            seen_hashes[txn_hash] = txn_id

    return duplicates

def remove_duplicates(conn, duplicates):
    """Remove duplicate transactions from database."""
    cursor = conn.cursor()

    duplicate_ids = [d['id'] for d in duplicates]

    if not duplicate_ids:
        return 0

    # Delete duplicates
    placeholders = ','.join('?' * len(duplicate_ids))
    cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", duplicate_ids)

    conn.commit()
    return len(duplicate_ids)

def main():
    """Main execution."""
    print("=" * 60)
    print("IDENTIFICAÇÃO E REMOÇÃO DE DUPLICATAS")
    print("=" * 60)
    print()

    conn = sqlite3.connect(DB_PATH)

    # Update missing hashes first
    print("🔧 Atualizando hashes faltantes...")
    updated = update_missing_hashes(conn)
    if updated > 0:
        print(f"   ✅ {updated} transações tiveram hash calculado")
    print()

    # Find duplicates
    print("🔍 Procurando duplicatas...")
    duplicates = find_duplicates(conn)

    if not duplicates:
        print("✅ Nenhuma duplicata encontrada!")
        conn.close()
        return

    print(f"\n🔴 Encontradas {len(duplicates)} transações duplicadas:\n")

    # Group by description for summary
    by_description = {}
    total_duplicated_amount = 0

    for dup in duplicates:
        desc = dup['description']
        if desc not in by_description:
            by_description[desc] = {
                'count': 0,
                'amount': dup['amount'],
                'dates': []
            }
        by_description[desc]['count'] += 1
        by_description[desc]['dates'].append(dup['date'])
        total_duplicated_amount += dup['amount']

    # Print summary
    for desc, info in sorted(by_description.items(), key=lambda x: x[1]['amount'], reverse=True):
        dates_str = ', '.join(sorted(set(info['dates'])))
        print(f"  • {desc}")
        print(f"    Valor: R$ {info['amount']:,.2f}")
        print(f"    Duplicatas: {info['count']}x")
        print(f"    Datas: {dates_str}")
        print()

    print(f"💰 Valor total duplicado: R$ {total_duplicated_amount:,.2f}")
    print(f"📊 Total de duplicatas a remover: {len(duplicates)}")
    print()

    # Remove duplicates
    print("🗑️  Removendo duplicatas...")
    removed_count = remove_duplicates(conn, duplicates)

    print(f"✅ {removed_count} transações duplicadas removidas com sucesso!")
    print()

    # Verify removal
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE strftime('%Y-%m', date) = '2026-01'")
    jan_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE strftime('%Y-%m', date) = '2026-01'")
    jan_total = cursor.fetchone()[0] or 0

    print("=" * 60)
    print("RESULTADO FINAL - JANEIRO 2026")
    print("=" * 60)
    print(f"Transações: {jan_count}")
    print(f"Total: R$ {jan_total:,.2f}")
    print()

    conn.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Schema Migration Script
Adiciona colunas is_excluded e installment_id, e recalcula todos os hashes
com a nova função normalizada.
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'data' / 'finance.db'

def generate_hash_new(date_str: str, description: str, amount: float) -> str:
    """Nova função de hash robusta com normalização."""
    # Normalizar descrição: remover espaços extras, lowercase
    normalized_desc = ' '.join(description.strip().split()).lower()
    # Formatar valor com 2 casas decimais
    amount_str = f"{abs(amount):.2f}"
    # Usar separador null byte (não aparece em texto)
    content = f"{date_str}\x00{normalized_desc}\x00{amount_str}"
    return hashlib.md5(content.encode()).hexdigest()

def backup_database():
    """Criar backup do banco antes da migration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = DB_PATH.parent / f'finance_backup_{timestamp}.db'

    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path

def add_column_if_not_exists(cursor, table: str, column: str, type_def: str):
    """Adiciona coluna se não existir."""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
        print(f"  ✅ Coluna {table}.{column} adicionada")
        return True
    else:
        print(f"  ⏭️  Coluna {table}.{column} já existe")
        return False

def migrate_schema():
    """Executa migration completa do schema."""
    print("=" * 60)
    print("SCHEMA MIGRATION - Agent Finance")
    print("=" * 60)
    print()

    # Backup primeiro
    backup_path = backup_database()
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Etapa 1: Adicionar is_excluded à tabela categories
        print("[1/5] Adicionando coluna is_excluded...")
        added = add_column_if_not_exists(cursor, 'categories', 'is_excluded', 'BOOLEAN DEFAULT 0')

        if added:
            # Marcar obra e esportes como excluded
            cursor.execute("""
                UPDATE categories
                SET is_excluded = 1
                WHERE name IN ('obra', 'esportes')
            """)
            print(f"  ✅ Marcadas categorias 'obra' e 'esportes' como excluded")

        conn.commit()
        print()

        # Etapa 2: Adicionar installment_id à tabela transactions
        print("[2/5] Adicionando coluna installment_id...")
        add_column_if_not_exists(cursor, 'transactions', 'installment_id', 'INTEGER')
        conn.commit()

        # Criar índice
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_installment_id'
        """)
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_installment_id ON transactions(installment_id)")
            print("  ✅ Índice idx_installment_id criado")
        else:
            print("  ⏭️  Índice idx_installment_id já existe")

        conn.commit()
        print()

        # Etapa 3: Recalcular TODOS os hashes
        print("[3/5] Recalculando hashes de todas as transações...")
        cursor.execute("SELECT id, date, description, amount FROM transactions")
        transactions = cursor.fetchall()

        updated = 0
        for txn_id, date, desc, amt in transactions:
            new_hash = generate_hash_new(date, desc, amt)
            cursor.execute("UPDATE transactions SET hash = ? WHERE id = ?", (new_hash, txn_id))
            updated += 1

        conn.commit()
        print(f"  ✅ {updated} hashes recalculados")
        print()

        # Etapa 4: Associar transações existentes aos installments (best effort)
        print("[4/5] Associando transações a parcelamentos...")

        # Buscar todos os installments ativos
        cursor.execute("""
            SELECT id, description, installment_amount, total_installments
            FROM installments
            WHERE status = 'active'
        """)
        installments = cursor.fetchall()

        associated = 0
        for inst_id, inst_desc, inst_amt, inst_total in installments:
            # Buscar transações que parecem ser deste installment
            # Critérios: descrição similar + valor próximo + sem installment_id ainda
            cursor.execute("""
                SELECT id, description, amount
                FROM transactions
                WHERE installment_id IS NULL
                AND (
                    description LIKE ? OR
                    description LIKE ?
                )
            """, (f"%{inst_desc}%", f"%{inst_desc.split()[0]}%"))

            matches = cursor.fetchall()

            for txn_id, txn_desc, txn_amt in matches:
                # Verificar se valor bate (±2% tolerância)
                if abs(txn_amt - inst_amt) / inst_amt < 0.02:
                    cursor.execute("""
                        UPDATE transactions
                        SET installment_id = ?
                        WHERE id = ?
                    """, (inst_id, txn_id))
                    associated += 1

        conn.commit()
        print(f"  ✅ {associated} transações associadas a parcelamentos")
        print()

        # Etapa 5: Verificar resultado final
        print("[5/5] Verificando migration...")

        # Verificar categorias excluded
        cursor.execute("SELECT COUNT(*) FROM categories WHERE is_excluded = 1")
        excluded_count = cursor.fetchone()[0]
        print(f"  Categorias excluded: {excluded_count}")

        # Verificar transações com installment_id
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE installment_id IS NOT NULL")
        with_installment = cursor.fetchone()[0]
        print(f"  Transações com installment_id: {with_installment}")

        # Verificar hashes não-nulos
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE hash IS NOT NULL AND hash != ''")
        with_hash = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_txns = cursor.fetchone()[0]
        print(f"  Transações com hash: {with_hash}/{total_txns}")

        print()
        print("=" * 60)
        print("MIGRATION COMPLETA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. Verificar se há duplicatas: python scripts/remove_duplicates_jan2026.py")
        print("2. Regenerar relatórios: python scripts/sync_obsidian.py syncall 2026 1")
        print()

    except Exception as e:
        print(f"\n❌ ERRO na migration: {e}")
        print(f"Restaure o backup: {backup_path}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_schema()

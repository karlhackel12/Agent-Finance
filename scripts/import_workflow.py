#!/usr/bin/env python3
"""
Workflow Unificado de Importação e Sincronização

Integra todos os passos do processo de importação:
1. Importar statement BB (opcional)
2. Gerar parcelamentos automáticos
3. Remover duplicatas
4. Regenerar relatórios

Uso:
    python import_workflow.py 2026 1              # Só regenerar
    python import_workflow.py 2026 1 fatura.txt   # Importar + regenerar
"""

import sys
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Importar módulos do projeto
try:
    from scripts.finance_db import (
        generate_installment_transactions,
        generate_hash,
        get_connection
    )
    from scripts.sync_obsidian import sync_to_obsidian, sync_pj
except ImportError:
    from finance_db import (
        generate_installment_transactions,
        generate_hash,
        get_connection
    )
    from sync_obsidian import sync_to_obsidian, sync_pj

DB_PATH = Path(__file__).parent.parent / 'data' / 'finance.db'


def find_duplicates(year: int, month: int) -> List[Dict]:
    """Encontra duplicatas em um mês específico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    month_str = f"{year}-{month:02d}"

    # Buscar todas transações do mês
    cursor.execute("""
        SELECT id, date, description, amount, hash
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
        ORDER BY date, id
    """, (month_str,))

    transactions = cursor.fetchall()
    conn.close()

    # Detectar duplicatas por hash
    seen_hashes = {}
    duplicates = []

    for txn_id, date, description, amount, stored_hash in transactions:
        # Usar hash armazenado
        if stored_hash in seen_hashes:
            duplicates.append({
                'id': txn_id,
                'original_id': seen_hashes[stored_hash],
                'date': date,
                'description': description,
                'amount': amount,
                'hash': stored_hash
            })
        else:
            seen_hashes[stored_hash] = txn_id

    return duplicates


def remove_duplicates(duplicates: List[Dict]) -> int:
    """Remove transações duplicadas do banco."""
    if not duplicates:
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    duplicate_ids = [d['id'] for d in duplicates]
    placeholders = ','.join('?' * len(duplicate_ids))
    cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", duplicate_ids)

    conn.commit()
    conn.close()

    return len(duplicate_ids)


def import_bb_statement(statement_file: str, year: int, month: int) -> Dict:
    """
    Importa statement do Banco do Brasil.

    Retorna estatísticas da importação.
    """
    # TODO: Implementar parser completo do statement BB
    # Por enquanto, retorna placeholder
    print(f"  ⏭️  Importação de statement ainda não implementada")
    print(f"  Use scripts/import_bb_cartao_jan2026.py para importar manualmente")

    return {
        'imported': 0,
        'skipped': 0,
        'errors': []
    }


def import_and_sync_month(
    year: int,
    month: int,
    statement_file: Optional[str] = None
) -> Dict:
    """
    Workflow completo de importação e sincronização.

    1. Importa CC statement (se fornecido)
    2. Gera parcelamentos faltantes
    3. Remove duplicatas
    4. Regenera relatórios

    Retorna estatísticas de cada etapa.
    """
    stats = {
        'imported': 0,
        'installments_created': 0,
        'duplicates_removed': 0,
        'errors': []
    }

    print("=" * 60)
    print("WORKFLOW DE IMPORTAÇÃO E SINCRONIZAÇÃO")
    print("=" * 60)
    print(f"Mês: {month:02d}/{year}")
    print()

    try:
        # Etapa 1: Importar statement (se fornecido)
        if statement_file:
            print(f"[1/4] Importando statement: {statement_file}")
            result = import_bb_statement(statement_file, year, month)
            stats['imported'] = result['imported']
            stats['errors'].extend(result.get('errors', []))
            print()
        else:
            print("[1/4] Sem statement para importar (pulando)")
            print()

        # Etapa 2: Gerar parcelamentos
        print(f"[2/4] Gerando transações de parcelamentos...")
        result = generate_installment_transactions(year, month)
        stats['installments_created'] = result.get('created', 0)
        skipped = result.get('skipped', 0)
        print(f"  ✅ Criados: {stats['installments_created']}")
        print(f"  ⏭️  Já existentes: {skipped}")
        print()

        # Etapa 3: Remover duplicatas
        print(f"[3/4] Verificando e removendo duplicatas...")
        duplicates = find_duplicates(year, month)

        if duplicates:
            # Agrupar por descrição para resumo
            by_description = {}
            total_dup_amount = 0

            for dup in duplicates:
                desc = dup['description']
                if desc not in by_description:
                    by_description[desc] = {
                        'count': 0,
                        'amount': dup['amount']
                    }
                by_description[desc]['count'] += 1
                total_dup_amount += dup['amount']

            print(f"  🔴 Encontradas {len(duplicates)} duplicatas:")
            for desc, info in sorted(by_description.items(), key=lambda x: x[1]['amount'], reverse=True)[:5]:
                print(f"     • {desc}: R$ {info['amount']:,.2f} ({info['count']}x)")

            if len(by_description) > 5:
                print(f"     ... e mais {len(by_description) - 5} itens")

            print(f"  💰 Valor total duplicado: R$ {total_dup_amount:,.2f}")
            print()
            print("  🗑️  Removendo duplicatas...")

            removed = remove_duplicates(duplicates)
            stats['duplicates_removed'] = removed
            print(f"  ✅ {removed} duplicatas removidas")
        else:
            print("  ✅ Nenhuma duplicata encontrada")
        print()

        # Etapa 4: Regenerar relatórios
        print(f"[4/4] Regenerando relatórios...")

        # Sync Obsidian PF
        sync_to_obsidian(year, month)
        print("  ✅ Obsidian PF atualizado")

        # Sync Obsidian PJ
        sync_pj(year)
        print("  ✅ Obsidian PJ atualizado")

        print()

        # Resumo final
        print("=" * 60)
        print("IMPORTAÇÃO COMPLETA!")
        print("=" * 60)

        if statement_file:
            print(f"Transações importadas: {stats['imported']}")
        print(f"Parcelamentos criados: {stats['installments_created']}")
        print(f"Duplicatas removidas: {stats['duplicates_removed']}")

        if stats['errors']:
            print(f"\n⚠️  {len(stats['errors'])} erros:")
            for err in stats['errors']:
                print(f"  - {err}")

        print()
        print("✅ Workflow concluído com sucesso!")
        print()

        return stats

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        stats['errors'].append(str(e))
        raise


def main():
    """Main execution."""
    if len(sys.argv) < 3:
        print("Uso: python import_workflow.py <ano> <mes> [arquivo_statement]")
        print()
        print("Exemplos:")
        print("  python import_workflow.py 2026 1              # Só regenerar")
        print("  python import_workflow.py 2026 1 fatura.txt   # Importar + regenerar")
        sys.exit(1)

    year = int(sys.argv[1])
    month = int(sys.argv[2])
    statement_file = sys.argv[3] if len(sys.argv) > 3 else None

    import_and_sync_month(year, month, statement_file)


if __name__ == "__main__":
    main()

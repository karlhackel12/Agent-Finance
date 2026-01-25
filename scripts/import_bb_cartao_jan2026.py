#!/usr/bin/env python3
"""
Script de Importação - Fatura Cartão BB Janeiro 2026

Importa transações das faturas do cartão de crédito BB com:
- Categorização automática + regras manuais validadas
- Detecção de duplicatas via hash MD5
- Filtro de transações de dezembro
- Filtro de parcelamentos já auto-gerados
- Suporte a IOF agregado

Decisões do Usuário (Janeiro 2026):
- Thiago Adauto → esportes (aula de tênis)
- AI Tools (FLOWITH, MANUS, etc) → assinaturas
- CASA CHIESSE, Macopil, THAURUS, AREDES → obra
- OZIEL BATISTA → obra
- AIRBNB → lazer
- OLA RETIRO → transporte
- FAST MASSAGEM → saude
- DEPILAR → lazer
- IORCLASS → assinaturas
- PROMOLIVROS → compras
- JUSBRASIL, ESTADAO → educacao
- MARIA LUIZA B, ALFATEC → compras
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Adicionar parent directory ao path
sys.path.insert(0, str(Path(__file__).parent))

from finance_db import add_transaction, get_connection
from bb_parser import categorize_transaction, parse_installment

# Regras manuais específicas desta importação (validadas pelo usuário)
# Ordem: Matches mais específicos primeiro
MANUAL_CATEGORIZATION = {
    # Pessoas e serviços específicos
    "thiago adauto": "esportes",  # Aula de Tênis
    "fast massagem": "saude",
    "oziel batista": "obra",
    "chok eletric": "obra",

    # Ferramentas e serviços
    "clash royale": "lazer",  # Game mobile (override Google assinaturas)
    "amazon kindle": "educacao",  # Override Amazon compras
    "z-api": "assinaturas",  # API service
    "zoom.com": "assinaturas",  # Video conferencing
    "contabilizei": "taxas",  # Serviço contábil
    "picpay*unimed": "saude",  # Plano de saúde via PicPay
    "unimed": "saude",  # Plano de saúde (fallback)

    # Estabelecimentos
    "my pet": "casa",  # Pet store
    "depilar": "lazer",
    "airbnb": "lazer",
    "ola retiro": "transporte",
    "promolivros": "compras",
    "estadao": "educacao",
    "jusbrasil": "educacao",
}

# Parcelamentos que JÁ EXISTEM no sistema (não importar como transação avulsa)
KNOWN_INSTALLMENTS = {
    "MOVEIS PLANEJADOS",
    "PICPAY MOVEIS",  # R$ 5.238
    "PICPAY OBRA",    # R$ 986
    "DROGARIAS PAC",
    "AMAZONMKTPLC",
    "SHOPEE *MEUPU",
    "SHOPEE *FIDCO",
    "MLP*MAGALU",
    "VINDI BROIL",
    "FIRE VERBO",
    "AREDES",
    "CASA CHIESSE",
    "MACOPIL",
    "RAIA311",
    "LOVABLE",
    "OPENAI",
    "EDZCOLLAB",
    "OTIQUE",
    "TAVUS",
    "FLOWITH.IO PARC",  # Parcelamento, não compra à vista
}


def parse_fatura_line(line: str) -> Optional[Tuple[str, str, float]]:
    """
    Parseia uma linha da fatura BB.

    Retorna: (data, descrição, valor) ou None se não for uma transação válida
    """
    # Ignorar linhas vazias ou cabeçalhos
    if not line.strip() or "Data" in line or "Transações" in line or "País" in line:
        return None

    # Padrão: DD/MM    DESCRICAO    ...    R$    VALOR
    # Regex para capturar: data (DD/MM), descrição (tudo no meio), valor (último R$ XX,XX ou X.XXX,XX)
    match = re.match(r'^(\d{2}/\d{2})\s+(.+?)\s+(?:BR|CA|CO|GB|NL|SG|DE|TX|NY)?\s*(?:R\$)?\s+([-]?\d{1,3}(?:[\.]\d{3})*[\,]\d{2})\s*$', line.strip())

    if not match:
        return None

    date_str = match.group(1)
    description = match.group(2).strip()
    amount_str = match.group(3)

    # Converter data para formato YYYY-MM-DD
    try:
        day, month = date_str.split('/')
        # Ano 2026 para Janeiro, 2025 para Dezembro
        year = "2025" if month == "12" else "2026"
        date = f"{year}-{month}-{day}"
    except:
        return None

    # Converter valor
    try:
        amount = float(amount_str.replace('.', '').replace(',', '.'))
        # Valor absoluto (ignora sinal negativo)
        amount = abs(amount)
    except:
        return None

    return date, description, amount


def should_ignore_transaction(date: str, description: str, amount: float) -> Tuple[bool, str]:
    """
    Verifica se a transação deve ser ignorada.

    Retorna: (ignorar: bool, motivo: str)
    """
    # Ignorar transações de dezembro (28-31/12)
    if date.startswith("2025-12"):
        return True, "transação de dezembro"

    # Ignorar pagamentos de fatura
    if "PGTO" in description.upper() or "PAGAMENTO" in description.upper():
        return True, "pagamento de fatura"

    # Ignorar PIX de retirada (auto-transferências)
    if "PIX - KARL ALVES HACKEL" in description.upper():
        return True, "PIX de retirada"

    # Ignorar devoluções (valores negativos já convertidos para positivo, usar flag no nome)
    if "DEVOLUCAO" in description.upper():
        return True, "devolução de encargo"

    # Ignorar saldo anterior
    if "SALDO FATURA ANTERIOR" in description.upper():
        return True, "saldo anterior"

    # Ignorar parcelamentos já cadastrados no sistema
    desc_upper = description.upper()
    for known in KNOWN_INSTALLMENTS:
        if known in desc_upper:
            return True, f"parcelamento já cadastrado: {known}"

    return False, ""


def categorize_with_manual_rules(description: str) -> str:
    """
    Categoriza transação usando regras manuais + auto keywords.
    """
    desc_lower = description.lower()

    # Aplicar regras manuais primeiro
    for keyword, category in MANUAL_CATEGORIZATION.items():
        if keyword in desc_lower:
            return category

    # Fallback para categorização automática
    return categorize_transaction(description)


def aggregate_iof(transactions: List[Dict]) -> List[Dict]:
    """
    Agrupa IOF com transação principal quando possível.

    IOF geralmente aparece logo após a compra internacional.
    """
    result = []
    i = 0

    while i < len(transactions):
        tx = transactions[i]

        # Se for IOF, verificar se há uma transação anterior no mesmo dia
        if "IOF" in tx['description'].upper():
            # Buscar transação anterior (mesma data, não IOF)
            if result and result[-1]['date'] == tx['date'] and "IOF" not in result[-1]['description'].upper():
                # Agregar IOF à transação anterior (apenas registrar, não somar valor)
                result[-1]['tags'] = result[-1].get('tags', []) + [f"IOF: R$ {tx['amount']:.2f}"]
            else:
                # IOF isolado (manter como taxas)
                result.append(tx)
        else:
            result.append(tx)

        i += 1

    return result


def import_fatura(fatura_path: str, dry_run: bool = False) -> Dict:
    """
    Importa transações da fatura para o banco.

    Args:
        fatura_path: Caminho do arquivo de fatura
        dry_run: Se True, não insere no banco (apenas simula)

    Returns:
        Estatísticas da importação
    """
    stats = {
        "total_lines": 0,
        "parsed": 0,
        "ignored": {"dez": 0, "pagamentos": 0, "parcelamentos": 0, "outros": 0},
        "imported": 0,
        "duplicates": 0,
        "errors": 0,
        "by_category": {},
        "total_amount": 0.0
    }

    transactions = []

    # Ler e parsear fatura
    with open(fatura_path, 'r', encoding='utf-8') as f:
        for line in f:
            stats["total_lines"] += 1

            parsed = parse_fatura_line(line)
            if not parsed:
                continue

            date, description, amount = parsed
            stats["parsed"] += 1

            # Verificar se deve ignorar
            should_ignore, reason = should_ignore_transaction(date, description, amount)
            if should_ignore:
                if "dezembro" in reason:
                    stats["ignored"]["dez"] += 1
                elif "pagamento" in reason:
                    stats["ignored"]["pagamentos"] += 1
                elif "parcelamento" in reason:
                    stats["ignored"]["parcelamentos"] += 1
                else:
                    stats["ignored"]["outros"] += 1
                continue

            # Categorizar
            category = categorize_with_manual_rules(description)

            # Extrair info de parcelamento
            inst_current, inst_total = parse_installment(description)

            transactions.append({
                "date": date,
                "description": description,
                "amount": amount,
                "category": category,
                "installment_current": inst_current,
                "installment_total": inst_total,
                "tags": []
            })

    # Agregar IOF
    transactions = aggregate_iof(transactions)

    # Importar para banco
    for tx in transactions:
        if dry_run:
            print(f"[DRY RUN] {tx['date']} | {tx['description'][:40]} | R$ {tx['amount']:.2f} | {tx['category']}")
            stats["imported"] += 1
            stats["total_amount"] += tx["amount"]
            stats["by_category"][tx["category"]] = stats["by_category"].get(tx["category"], 0) + tx["amount"]
        else:
            try:
                result = add_transaction(
                    date_str=tx["date"],
                    description=tx["description"],
                    amount=tx["amount"],
                    category=tx["category"],
                    account="BB Credito",
                    type_="expense",
                    installment_current=tx["installment_current"],
                    installment_total=tx["installment_total"],
                    tags=tx["tags"] if tx["tags"] else None,
                    source="bb_fatura_jan2026"
                )

                if result["status"] == "inserted":
                    stats["imported"] += 1
                    stats["total_amount"] += tx["amount"]
                    stats["by_category"][tx["category"]] = stats["by_category"].get(tx["category"], 0) + tx["amount"]
                elif result["status"] == "duplicate":
                    stats["duplicates"] += 1

            except Exception as e:
                print(f"ERRO ao importar: {tx['description']} - {e}")
                stats["errors"] += 1

    return stats


def print_report(stats: Dict):
    """Imprime relatório de importação."""
    print("\n" + "="*70)
    print("RELATÓRIO DE IMPORTAÇÃO - FATURA CARTÃO BB JANEIRO 2026")
    print("="*70 + "\n")

    print(f"📄 Linhas processadas: {stats['total_lines']}")
    print(f"✅ Transações parseadas: {stats['parsed']}")
    print()

    print("🚫 IGNORADAS:")
    print(f"   • Dezembro 2025: {stats['ignored']['dez']}")
    print(f"   • Pagamentos fatura: {stats['ignored']['pagamentos']}")
    print(f"   • Parcelamentos já cadastrados: {stats['ignored']['parcelamentos']}")
    print(f"   • Outros (devoluções, PIX): {stats['ignored']['outros']}")
    print(f"   TOTAL IGNORADO: {sum(stats['ignored'].values())}")
    print()

    print("💾 IMPORTAÇÃO:")
    print(f"   • Novas transações: {stats['imported']}")
    print(f"   • Duplicatas (já no banco): {stats['duplicates']}")
    print(f"   • Erros: {stats['errors']}")
    print(f"   • Valor total importado: R$ {stats['total_amount']:,.2f}")
    print()

    if stats['by_category']:
        print("📊 POR CATEGORIA:")
        for category, total in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            count = sum(1 for c in stats.get('transactions', []) if c == category)
            print(f"   • {category.title():20s}: R$ {total:>10,.2f}")

    print("\n" + "="*70)


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description='Importa fatura cartão BB Janeiro 2026')
    parser.add_argument('--dry-run', action='store_true', help='Simula importação sem inserir no banco')
    parser.add_argument('--fatura', default='fatura_jan2026.txt', help='Caminho do arquivo de fatura')

    args = parser.parse_args()

    fatura_path = Path(__file__).parent / args.fatura

    if not fatura_path.exists():
        print(f"❌ Arquivo não encontrado: {fatura_path}")
        return 1

    print(f"📂 Importando fatura: {fatura_path}")
    print(f"🔧 Modo: {'DRY RUN (simulação)' if args.dry_run else 'IMPORTAÇÃO REAL'}")
    print()

    stats = import_fatura(str(fatura_path), dry_run=args.dry_run)
    print_report(stats)

    if args.dry_run:
        print("\n⚠️  DRY RUN - Nenhuma transação foi inserida no banco.")
        print("Execute sem --dry-run para importar de fato.")
    else:
        print("\n✅ Importação concluída com sucesso!")

    return 0


if __name__ == "__main__":
    sys.exit(main())

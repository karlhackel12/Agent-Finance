---
name: bb-extractor
description: |
  Extrai transacoes da fatura do cartao de credito do Banco do Brasil via Chrome automation.
  Use quando: (1) Usuario pedir para sincronizar fatura, (2) Atualizar gastos do cartao,
  (3) Importar transacoes do BB, (4) Verificar fatura atual.
  Triggers: "sincronizar fatura bb", "extrair transacoes bb", "atualizar cartao bb",
  "importar fatura", "pegar gastos do cartao", "sync bb credit card".
---

# BB Extractor v1.0

Skill para extracao automatizada de transacoes do Banco do Brasil via Chrome.

## Requisitos

- Chrome browser aberto
- Claude in Chrome extension instalada
- Acesso a conta BB (credenciais do usuario)

## Workflow de Extracao

### Passo 1: Preparar Browser

```
1. Verificar se Chrome esta conectado (tabs_context_mcp)
2. Criar nova aba se necessario (tabs_create_mcp)
3. Navegar para bb.com.br
```

### Passo 2: Login (Usuario)

**IMPORTANTE**: O Claude NUNCA deve inserir credenciais bancarias.

```
1. Navegar ate a pagina de login
2. PAUSAR e solicitar que usuario faca login manualmente
3. Aguardar confirmacao do usuario
```

### Passo 3: Navegar ate Fatura

```
1. Clicar em "Cartoes" no menu
2. Selecionar cartao de credito
3. Clicar em "Fatura"
4. Selecionar "Fatura Atual" ou mes especifico
```

### Passo 4: Extrair Transacoes

```
1. Ler pagina com read_page ou get_page_text
2. Identificar tabela de transacoes
3. Extrair: Data, Descricao, Valor, Parcela (se houver)
4. Parsear dados para formato padrao
```

### Passo 5: Processar e Salvar

```python
from scripts.finance_db import add_transaction
from scripts.bb_parser import parse_bb_transactions

# Parsear transacoes extraidas
transactions = parse_bb_transactions(raw_data)

# Salvar no banco
for tx in transactions:
    result = add_transaction(
        date_str=tx['date'],
        description=tx['description'],
        amount=tx['amount'],
        category=tx['category'],
        source='bb_fatura'
    )
    print(f"{result['status']}: {tx['description']}")
```

## Seguranca

### Regras Absolutas

1. **NUNCA** inserir credenciais bancarias
2. **NUNCA** armazenar senhas ou tokens
3. **SEMPRE** solicitar login manual ao usuario
4. **SEMPRE** confirmar antes de qualquer acao
5. Nao fazer cache de dados sensiveis

### Fluxo Seguro

```
Usuario: "sincronizar minha fatura do BB"

Claude:
1. Abrir bb.com.br
2. PAUSAR: "Por favor, faca login na sua conta. Me avise quando estiver logado."
3. Usuario confirma login
4. Claude navega ate fatura
5. Claude extrai transacoes (apenas leitura)
6. Claude processa e salva no banco local
7. Claude gera relatorio
```

## Comandos

| Comando | Acao |
|---------|------|
| "extrair fatura bb" | Workflow completo |
| "verificar fatura atual" | Apenas visualizar |
| "importar mes X" | Importar mes especifico |

## Categorias Automaticas

O parser identifica categorias por palavras-chave:

| Padrao | Categoria |
|--------|-----------|
| IFOOD, RAPPI, RESTAURANTE, MERCADO | alimentacao |
| UBER, 99, SHELL, POSTO | transporte |
| FARMACIA, DROGARIA, CLINICA | saude |
| NETFLIX, SPOTIFY, AMAZON PRIME | assinaturas |
| AMAZON, MAGALU, MERCADO LIVRE | compras |
| CINEMA, STEAM, INGRESSO | lazer |
| UDEMY, COURSERA, KINDLE | educacao |
| LEROY, TELHA, COBASI | casa |
| IOF, TAXA, ANUIDADE | taxas |

## Deteccao de Parcelamentos

Padroes reconhecidos:
- `PARC 3/10` → parcela 3 de 10
- `3 DE 10` → parcela 3 de 10
- `(3/10)` → parcela 3 de 10

## Integracao

### Com Finance DB

```python
from scripts.finance_db import add_transaction, get_monthly_summary

# Apos extracao
summary = get_monthly_summary(2026, 1)
print(f"Total importado: R$ {summary['total_spent']:,.2f}")
```

### Com Obsidian Sync

```python
from scripts.sync_obsidian import sync_to_obsidian

# Apos importacao
sync_to_obsidian(2026, 1)
```

### Com Alertas

```python
from scripts.budget_monitor import check_alerts
from scripts.notifications import send_budget_alerts

# Verificar alertas apos importacao
send_budget_alerts(2026, 1)
```

## Exemplo de Uso

```
Usuario: "sincronizar minha fatura do BB de janeiro"

Claude:
1. [Abre Chrome e navega para bb.com.br]
2. "Por favor, faca login na sua conta do Banco do Brasil.
    Me avise quando estiver logado para eu continuar."

Usuario: "ja loguei"

Claude:
3. [Navega: Cartoes > Fatura > Janeiro 2026]
4. [Extrai transacoes da pagina]
5. "Encontrei 45 transacoes totalizando R$ 12.450,00.

    Resumo por categoria:
    - Alimentacao: R$ 3.200 (15 transacoes)
    - Compras: R$ 4.500 (8 transacoes)
    - ...

    Posso importar essas transacoes para o banco?"

Usuario: "sim"

Claude:
6. [Importa transacoes]
7. "Importacao concluida!
    - 45 transacoes importadas
    - 3 duplicatas ignoradas
    - Dashboard atualizado

    Alertas:
    - Compras em 90% do budget"
```

## Tratamento de Erros

| Erro | Acao |
|------|------|
| Sessao expirada | Solicitar novo login |
| Fatura nao encontrada | Verificar mes/ano |
| Elemento nao encontrado | Tentar seletores alternativos |
| Rate limit | Aguardar e tentar novamente |

## Changelog

| Versao | Data | Alteracoes |
|--------|------|------------|
| 1.0 | 27/12/2025 | Versao inicial |

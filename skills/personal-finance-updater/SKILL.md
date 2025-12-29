---
name: personal-finance-updater
description: |
  Automatiza a atualizacao do planejamento financeiro pessoal extraindo transacoes do Banco do Brasil.
  Use quando: (1) Usuario pedir para atualizar gastos/despesas do cartao, (2) Sincronizar fatura BB com planilha,
  (3) Adicionar novas transacoes ao forecast, (4) Atualizar parcelamentos e categorias, (5) Comparar real vs projetado.
  Triggers: "atualizar meus gastos", "sincronizar fatura", "pegar transacoes do BB", "atualizar planejamento financeiro",
  "extrair fatura do cartao", "update my expenses", "sync credit card", "atualizar dashboard financeiro",
  "comparar real vs projetado", "sincronizar dashboard".
---

# Personal Finance Updater v2.0

Skill para extrair transacoes do Banco do Brasil e atualizar o planejamento financeiro pessoal.
Atualiza tanto a planilha Excel quanto o dashboard Obsidian.

## Contexto do Usuario

- **Perfil**: Senior PM trabalhando via nearshoring para empresas USA
- **Renda**: USD 12k/mes (~R$ 55k liquido)
- **Banco Principal**: Banco do Brasil (cartao de credito)
- **Metodologia**: Budget 50/30/20 adaptado
- **Vault Obsidian**: Agent Finance

### Compromissos Fixos 2026

| Item | Valor | Ate |
|------|-------|-----|
| Financiamento Imovel | R$ 7.500 | 2045 |
| Moveis Planejados | R$ 9.400 | Out/2026 |
| Carro (assinatura) | R$ 3.200 | Continuo |
| Contas Casa | R$ 3.000 | Continuo |
| Plano de Saude | R$ 1.300 | Continuo |
| Software Trabalho | R$ 661 | Continuo |
| Streaming | R$ 350 | Continuo |

## Workflow Principal: Atualizacao de Gastos

### Trigger
Usuario solicita: "atualizar meus gastos", "sincronizar dashboard", "comparar real vs projetado"

### Passo 1: Extrair Transacoes do BB

1. Acessar `https://www.bb.com.br`
2. Solicitar credenciais ao usuario - **NUNCA armazenar**
3. Navegar: Cartoes > Fatura > Fatura Atual
4. Extrair todas as transacoes:
   - Data
   - Estabelecimento/Descricao
   - Valor
   - Parcela (se aplicavel)

### Passo 2: Categorizar Transacoes

Aplicar regras de `references/categorias.md`:

| Categoria | Exemplos |
|-----------|----------|
| Alimentacao | iFood, Rappi, restaurantes, supermercados |
| Transporte | Uber, 99, combustivel, estacionamento |
| Saude | farmacias, consultas, exames |
| Assinaturas | Netflix, Spotify, software, streaming |
| Compras | Amazon, Mercado Livre, lojas |
| Lazer | cinema, jogos, hobbies |
| Educacao | cursos, livros |
| Casa | manutencao, decoracao |
| Taxas | IOF, tarifas, anuidade |

### Passo 3: Atualizar Planilha Excel

Arquivo: `projections/Planejamento_2026_Reestruturado.xlsx`

1. Abrir sheet "Janeiro Real vs Plan" (ou mes corrente)
2. Atualizar coluna "Real" com valores extraidos
3. Recalcular variacoes automaticamente
4. Atualizar status (OK/Atencao/Critico)

### Passo 4: Atualizar Dashboard Obsidian

#### 4.1 Arquivo: `tracking/Dashboard-Mensal.md`

Atualizar:
- KPIs principais (Gastos Totais, Taxa Poupanca, Saldo)
- Tabela de gastos por categoria
- Alertas ativos

#### 4.2 Arquivo: `tracking/2026/{Mes}.md`

Atualizar:
- Lista de transacoes por categoria
- Totais por categoria
- Status de cada categoria (% do budget)

### Passo 5: Gerar Relatorio

Retornar ao usuario:

```markdown
## Sincronizacao Concluida

**Periodo**: Janeiro 2026
**Transacoes encontradas**: X
**Novas transacoes**: Y

### Resumo
| Categoria | Real | Budget | Status |
|-----------|------|--------|--------|
| ... | ... | ... | ... |

### Alertas
- [Lista de categorias acima do budget]

### Proximos Passos
- [Recomendacoes baseadas nos dados]
```

## Estrutura de Dados

### Transacao

```json
{
  "data": "2025-01-15",
  "estabelecimento": "IFOOD *RESTAURANTE",
  "valor": 45.90,
  "parcela_atual": null,
  "parcelas_total": null,
  "categoria": "Alimentacao",
  "tipo": "avista",
  "mes_fatura": "Janeiro/2026"
}
```

### Parcelamento

```json
{
  "data_compra": "2024-11-20",
  "estabelecimento": "AMAZON BR",
  "valor_total": 1200.00,
  "valor_parcela": 120.00,
  "parcela_atual": 2,
  "parcelas_total": 10,
  "categoria": "Compras Diversas",
  "primeira_fatura": "Dezembro/2024",
  "ultima_fatura": "Setembro/2025"
}
```

## Categorias e Budgets

| Categoria | Budget Mensal | % Renda |
|-----------|---------------|---------|
| Alimentacao | R$ 3.500 | 6% |
| Transporte | R$ 1.500 | 3% |
| Saude | R$ 1.500 | 3% |
| Assinaturas/Software | R$ 2.011 | 4% |
| Compras Diversas | R$ 5.000 | 9% |
| Lazer | R$ 2.000 | 4% |
| Educacao | R$ 500 | 1% |
| Casa | R$ 2.000 | 4% |
| Taxas/Servicos | R$ 500 | 1% |
| **Total Variaveis** | **R$ 18.511** | **34%** |

## Regras de Negocio

### Status por Categoria

| % do Budget | Status | Cor |
|-------------|--------|-----|
| <= 90% | OK | Verde |
| 91-110% | Atencao | Amarelo |
| > 110% | Critico | Vermelho |

### Identificacao de Parcelamentos

Padroes:
- "X/Y" ou "X DE Y"
- "PARC X/Y"
- "PARCELA X"

### Transacoes Recorrentes

- Mesmo valor + mesmo estabelecimento + mesmo dia
- Marcar como "recorrente"
- Projetar para meses futuros

## Banco de Dados Local (SQLite)

### Localizacao
- **Database**: `data/finance.db`
- **Modulo Python**: `scripts/finance_db.py`

### Tabelas

| Tabela | Descricao |
|--------|-----------|
| categories | Categorias com budgets |
| accounts | Contas (BB Credito, etc) |
| transactions | Transacoes individuais |
| installments | Parcelamentos ativos |
| monthly_budgets | Budgets mensais |

### Funcoes Principais

```python
from scripts.finance_db import (
    add_transaction,      # Adicionar transacao
    get_transactions,     # Buscar transacoes
    get_monthly_summary,  # Resumo mensal
    get_categories,       # Listar categorias
    get_active_installments,  # Parcelamentos
    generate_monthly_report   # Relatorio MD
)
```

### Uso via CLI

```bash
# Ver categorias
python scripts/finance_db.py categories

# Resumo do mes
python scripts/finance_db.py summary 2026 1

# Transacoes do mes
python scripts/finance_db.py transactions 2026 1

# Gerar relatorio
python scripts/finance_db.py report 2026 1
```

## Arquivos Relacionados

### Banco de Dados

- `data/finance.db` - SQLite com transacoes
- `scripts/finance_db.py` - Modulo de acesso

### Planilhas Excel

- `projections/Planejamento_2026_Reestruturado.xlsx` - Plano ativo
- `projections/Planejamento_2026_Atualizado_Janeiro.xlsx` - Referencia original

### Dashboard Obsidian

- `tracking/Dashboard-Mensal.md` - Visao executiva
- `tracking/2026/*.md` - Detalhamento mensal

### Referencias

- `skills/personal-finance-updater/references/categorias.md` - Regras de categorizacao
- `skills/personal-finance-updater/references/parcelamentos-ativos.md` - Parcelamentos

## Seguranca

- **NUNCA** armazenar credenciais bancarias
- Solicitar login a cada sessao
- Confirmar com usuario antes de qualquer acao
- Nao fazer cache de dados sensiveis

## Comandos Rapidos

| Comando | Acao |
|---------|------|
| "atualizar gastos" | Workflow completo |
| "sincronizar janeiro" | Atualizar mes especifico |
| "comparar real vs planejado" | Gerar relatorio comparativo |
| "listar parcelamentos" | Mostrar parcelamentos ativos |
| "alertas do mes" | Mostrar categorias criticas |

## Modulos Avancados (Fase 2)

### Sincronizacao Obsidian

```bash
# Sincronizar dashboard e detalhamento mensal
python scripts/sync_obsidian.py sync 2026 1
```

### Monitor de Budget

```bash
# Verificar alertas
python scripts/budget_monitor.py check 2026 1

# Gerar relatorio de alertas
python scripts/budget_monitor.py report 2026 1
```

### Analisador de Despesas

```bash
# Analise completa
python scripts/expense_analyzer.py analyze 2026 1

# Projecao de fechamento
python scripts/expense_analyzer.py projection 2026 1

# Sugestoes de economia
python scripts/expense_analyzer.py savings 2026 1

# Salvar analise no Obsidian
python scripts/expense_analyzer.py save 2026 1
```

### Sistema de Notificacoes

```bash
# Status dos canais
python scripts/notifications.py status

# Enviar alertas de budget
python scripts/notifications.py alerts 2026 1
```

**Canais disponiveis:**
- Console (sempre ativo)
- Arquivo de log (`logs/notifications.log`)
- Obsidian (`tracking/Alertas-Ativos.md`)
- Telegram (configurar `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`)
- Pushover (configurar `PUSHOVER_USER_KEY` e `PUSHOVER_API_TOKEN`)

## Arquivos Fase 2

| Arquivo | Descricao |
|---------|-----------|
| `scripts/sync_obsidian.py` | Sincroniza SQLite → Obsidian |
| `scripts/budget_monitor.py` | Sistema de alertas de budget |
| `scripts/expense_analyzer.py` | Analise de gastos e tendencias |
| `scripts/notifications.py` | Notificacoes multi-canal |
| `tracking/Alertas-Ativos.md` | Alertas no Obsidian |
| `tracking/2026/Analise-*.md` | Analises mensais |

## Modulos IA (Fase 3)

### AI Insights Engine

```bash
# Previsao de gastos
python scripts/ai_insights.py predict 2026 1

# Detectar padroes
python scripts/ai_insights.py patterns 2026 1

# Simular cenarios what-if
python scripts/ai_insights.py scenarios 2026 1

# Acompanhar metas
python scripts/ai_insights.py goals

# Projecao de patrimonio (Monte Carlo)
python scripts/ai_insights.py wealth

# Recomendacoes personalizadas
python scripts/ai_insights.py recommend 2026 1

# Relatorio completo de insights
python scripts/ai_insights.py report 2026 1
```

### Capacidades IA

| Feature | Descricao |
|---------|-----------|
| Previsao | Modelo preditivo por categoria |
| Padroes | Detecta recorrencias e anomalias |
| What-If | Simula cenarios de corte |
| Metas | Acompanha 4 metas de longo prazo |
| Monte Carlo | Projeta patrimonio com 1000 simulacoes |
| Recomendacoes | Engine personalizado de sugestoes |

### Arquivos Fase 3

| Arquivo | Descricao |
|---------|-----------|
| `scripts/ai_insights.py` | Engine de IA completo |
| `skills/ai-insights/SKILL.md` | Documentacao da skill |

## Changelog

| Versao | Data | Alteracoes |
|--------|------|------------|
| 4.0 | 27/12/2025 | Fase 3: IA, Previsoes, Monte Carlo, Recomendacoes |
| 3.0 | 27/12/2025 | Fase 2: Alertas, Analise, Notificacoes |
| 2.0 | 27/12/2025 | Adicao de Dashboard Obsidian, workflow integrado |
| 1.0 | 26/12/2025 | Versao inicial |

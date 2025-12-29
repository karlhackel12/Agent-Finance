---
name: expense-analyzer
description: |
  Analisa gastos, detecta anomalias e sugere otimizacoes no orcamento.
  Use quando: (1) Usuario pedir analise de gastos, (2) Comparar meses,
  (3) Identificar onde economizar, (4) Projetar fechamento do mes,
  (5) Detectar padroes de consumo.
  Triggers: "analisar meus gastos", "onde posso economizar", "como esta meu mes",
  "projecao de gastos", "comparar com mes anterior", "padroes de consumo",
  "anomalias nos gastos", "tendencias financeiras".
---

# Expense Analyzer v1.0

Skill para analise inteligente de gastos e recomendacoes de otimizacao.

## Contexto do Usuario

- **Perfil**: Senior PM, renda R$ 55k/mes
- **Metodologia**: 50/30/20 adaptado
- **Meta Poupanca**: 28%
- **Categorias**: 9 categorias de gastos

## Comandos Disponiveis

| Comando | Descricao | Exemplo |
|---------|-----------|---------|
| `analyze` | Analise completa do mes | `python expense_analyzer.py analyze 2026 1` |
| `trends` | Tendencias por categoria | `python expense_analyzer.py trends 2026 1` |
| `savings` | Sugestoes de economia | `python expense_analyzer.py savings 2026 1` |
| `projection` | Projecao de fechamento | `python expense_analyzer.py projection 2026 1` |
| `anomalies` | Deteccao de anomalias | `python expense_analyzer.py anomalies 2026 1` |

## Workflow: Analise Completa

### Trigger
Usuario solicita: "analisar meus gastos", "como esta meu mes"

### Passo 1: Coletar Dados

```python
from scripts.expense_analyzer import ExpenseAnalyzer

analyzer = ExpenseAnalyzer(2026, 1)
report = analyzer.full_analysis()
```

### Passo 2: Analisar Padroes

O sistema automaticamente:
- Calcula media diaria de gastos
- Identifica dias de pico
- Detecta categorias problematicas
- Compara com budget

### Passo 3: Gerar Insights

```markdown
## Analise de Janeiro 2026

### Visao Geral
- Gastos totais: R$ X.XXX
- Media diaria: R$ XXX
- Taxa de poupanca: XX%

### Por Categoria
| Categoria | Gasto | Budget | Tendencia |
|-----------|-------|--------|-----------|
| ... | ... | ... | ↑/↓/→ |

### Insights
1. [Insight sobre categoria mais impactada]
2. [Insight sobre tendencia]
3. [Insight sobre anomalias]

### Recomendacoes
1. [Acao especifica para economizar]
2. [Acao para equilibrar budget]
```

## Analises Disponiveis

### 1. Analise de Tendencias

Compara gastos atuais com:
- Mes anterior
- Media dos ultimos 3 meses
- Mesmo periodo do ano anterior

### 2. Deteccao de Anomalias

Identifica:
- Transacoes atipicas (>2 desvios padrao)
- Picos de gastos em dias especificos
- Categorias com variacao anormal

### 3. Sugestoes de Economia

Baseado em:
- Categorias acima do budget
- Transacoes recorrentes evitaveis
- Padroes de consumo otimizaveis

### 4. Projecao de Fechamento

Estima:
- Gasto total ate fim do mes
- Taxa de poupanca projetada
- Categorias que vao estourar

## Metricas Calculadas

| Metrica | Formula | Descricao |
|---------|---------|-----------|
| Burn Rate | gastos / dias | Velocidade de gasto |
| Runway | budget_restante / burn_rate | Dias ate estourar |
| Savings Rate | (receita - gastos) / receita | Taxa de poupanca |
| Budget Usage | gasto / budget | % do budget usado |

## Integracao

### Com Budget Monitor

```python
from scripts.budget_monitor import check_alerts
from scripts.expense_analyzer import ExpenseAnalyzer

# Combinar analise com alertas
alerts = check_alerts(2026, 1)
analysis = ExpenseAnalyzer(2026, 1).full_analysis()
```

### Com Obsidian Sync

```python
from scripts.sync_obsidian import sync_to_obsidian
from scripts.expense_analyzer import ExpenseAnalyzer

# Gerar analise e sincronizar
analyzer = ExpenseAnalyzer(2026, 1)
analyzer.save_to_obsidian()
sync_to_obsidian(2026, 1)
```

## Exemplo de Output

```
=== Analise Janeiro 2026 ===

RESUMO
  Total gasto: R$ 17.401,60
  Media diaria: R$ 580,05
  Dias restantes: 4
  Projecao mes: R$ 19.722 (107% budget)

CATEGORIAS CRITICAS
  🛒 Compras: 275% budget (CRITICO)
  🍔 Alimentacao: 92% budget (ATENCAO)

TOP 5 MAIORES GASTOS
  1. APPLE STORE: R$ 8.500
  2. AMAZON BR: R$ 2.500
  3. MERCADO LIVRE: R$ 1.800
  4. SUPERMERCADO CARREFOUR: R$ 1.200
  5. MAGALU: R$ 950

RECOMENDACOES
  1. Pausar compras diversas ate proximo mes
  2. Limitar alimentacao a R$ 269 restantes
  3. Evitar novas assinaturas
```

## Seguranca

- Dados processados localmente
- Sem envio para servicos externos
- Analises baseadas apenas em dados do SQLite

## Changelog

| Versao | Data | Alteracoes |
|--------|------|------------|
| 1.0 | 27/12/2025 | Versao inicial |

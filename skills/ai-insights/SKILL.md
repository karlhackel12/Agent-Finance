---
name: ai-insights
description: |
  Analise preditiva, deteccao de padroes e recomendacoes financeiras personalizadas.
  Use quando: (1) Usuario pedir previsoes de gastos, (2) Simular cenarios what-if,
  (3) Acompanhar metas de longo prazo, (4) Projetar patrimonio futuro,
  (5) Receber recomendacoes personalizadas de economia.
  Triggers: "prever meus gastos", "simular cenario", "como estao minhas metas",
  "projecao de patrimonio", "recomendacoes financeiras", "analise preditiva",
  "o que acontece se eu cortar", "vou atingir minha meta", "monte carlo".
---

# AI Insights v1.0

Skill de inteligencia artificial para analise preditiva e recomendacoes financeiras.

## Capacidades

### 1. Previsao de Gastos

Modelo preditivo baseado em historico que:
- Analisa tendencias por categoria
- Calcula confianca da previsao
- Identifica direcao (subindo/descendo/estavel)

```bash
python scripts/ai_insights.py predict 2026 1
```

### 2. Deteccao de Padroes

Identifica automaticamente:
- **Gastos recorrentes**: Assinaturas, pagamentos fixos
- **Padroes temporais**: Dias da semana com mais gastos
- **Concentracao**: Categorias dominando o orcamento
- **Anomalias**: Compras atipicas

```bash
python scripts/ai_insights.py patterns 2026 1
```

### 3. Simulador What-If

Permite testar cenarios como:
- "E se eu cortar 30% em compras?"
- "E se eu reduzir alimentacao em 20%?"
- "Quanto preciso cortar para atingir 30% de poupanca?"

```bash
python scripts/ai_insights.py scenarios 2026 1
```

**Cenarios pre-definidos:**
- Corte Agressivo (-20% alimentacao, -50% lazer, -30% compras)
- Corte Moderado (-10% alimentacao, -20% lazer, -15% compras)
- Foco em Categorias Criticas (-30% nas criticas)
- Meta 30% Poupanca (corte proporcional)

### 4. Acompanhamento de Metas

Metas configuradas:
- Reserva de Emergencia (24 meses)
- Patrimonio 2025 (R$ 365k)
- Patrimonio 2030 (R$ 4M)
- Independencia Financeira 2035 (R$ 7.7M)

```bash
python scripts/ai_insights.py goals
```

### 5. Projecao de Patrimonio (Monte Carlo)

Simula 1000 cenarios para projetar patrimonio futuro considerando:
- Retorno esperado: 11% a.a.
- Volatilidade: 15% a.a.
- Inflacao: 4.5% a.a.
- Taxa de poupanca: 28%

```bash
python scripts/ai_insights.py wealth
```

**Output:**
- Percentis 10, 25, 50, 75, 90
- Probabilidade de atingir meta

### 6. Recomendacoes Personalizadas

Engine que gera recomendacoes baseadas em:
- Analise de budget (categorias criticas)
- Padroes detectados (gastos recorrentes)
- Metas financeiras (progresso)
- Otimizacoes gerais (poupanca, parcelamentos)

```bash
python scripts/ai_insights.py recommend 2026 1
```

## Relatorio Completo

Gera relatorio Markdown com todos os insights:

```bash
python scripts/ai_insights.py report 2026 1
```

## Uso via Python

```python
from scripts.ai_insights import (
    SpendingPredictor,
    PatternDetector,
    ScenarioSimulator,
    GoalTracker,
    RecommendationEngine,
    generate_insights_report
)

# Previsoes
predictor = SpendingPredictor()
predictions = predictor.predict_all()

# Padroes
detector = PatternDetector(2026, 1)
patterns = detector.detect_all()

# Cenarios
simulator = ScenarioSimulator(2026, 1)
scenario = simulator.simulate({"compras": -30, "lazer": -20})

# Metas
tracker = GoalTracker()
projection = tracker.project_wealth(10, 1000)

# Recomendacoes
engine = RecommendationEngine(2026, 1)
recommendations = engine.generate_recommendations()

# Relatorio completo
report = generate_insights_report(2026, 1)
```

## Configuracao do Usuario

Parametros em `USER_PROFILE`:

| Parametro | Valor | Descricao |
|-----------|-------|-----------|
| income | 55000 | Renda mensal liquida |
| savings_target | 0.28 | Meta de poupanca (28%) |
| emergency_fund_months | 24 | Meses de reserva |
| retirement_year | 2035 | Ano alvo IF |
| retirement_target | 7700000 | Patrimonio alvo |
| current_assets | 180000 | Patrimonio atual |
| expected_return | 0.11 | Retorno esperado (11%) |
| inflation | 0.045 | Inflacao (4.5%) |

## Exemplos de Uso

### Prever gastos do proximo mes

```
User: "Quanto vou gastar no proximo mes?"

Agent:
=== Previsoes para Proximo Mes ===

  Alimentacao: R$ 3.500 (75% confianca) ↑
  Compras: R$ 4.200 (60% confianca) ↓
  ...

  TOTAL: R$ 18.500 | Poupanca: 66.4%
```

### Simular corte de gastos

```
User: "O que acontece se eu cortar 50% em lazer?"

Agent:
=== Cenario: Corte em Lazer ===

  Poupanca atual: R$ 15.400 (28%)
  Poupanca projetada: R$ 16.400 (29.8%)

  Impacto: +R$ 1.000/mes de economia
```

### Verificar probabilidade de atingir meta

```
User: "Vou conseguir atingir R$ 7.7M em 2035?"

Agent:
=== Projecao Monte Carlo (10 anos) ===

  Mediana: R$ 4.2M
  Probabilidade de sucesso: 15%

  Para aumentar chances:
  1. Aumentar taxa de poupanca para 35%
  2. Buscar retornos de 13% a.a.
  3. Estender prazo em 3 anos
```

## Integracao com Outras Skills

```python
# Combinar com alertas
from scripts.budget_monitor import check_alerts
from scripts.ai_insights import RecommendationEngine

alerts = check_alerts(2026, 1)
recommendations = RecommendationEngine(2026, 1).generate_recommendations()
```

## Limitacoes

- Previsoes baseadas em historico disponivel
- Monte Carlo assume distribuicao normal de retornos
- Nao considera eventos extraordinarios (bonus, heranças)
- Metas sao estimativas, nao garantias

## Changelog

| Versao | Data | Alteracoes |
|--------|------|------------|
| 1.0 | 27/12/2025 | Versao inicial com todas as features |

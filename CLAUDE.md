# Claude Instructions - Agent Finance

## Project Context

You are assisting a **Senior Product Manager** working in **nearshoring** (PJ contractor for US companies based in Brazil) with personal financial management and a 10-year wealth building plan (2025-2035).

## Financial Profile

### Income
- **Gross USD**: $12,000/month
- **Base Exchange Rate**: R$ 6.00
- **Gross BRL**: R$ 72,000/month
- **Net BRL** (after Simples Nacional): R$ 55,000-60,000/month
- **Tax Regime**: Simples Nacional (~R$ 720k annual revenue, Anexo III)

### Fixed Monthly Commitments
| Item | Value |
|------|-------|
| Home Loan | R$ 7,500 |
| Car Subscription (Movida) | R$ 3,200 |
| Health Insurance | R$ 1,300 |
| Work Subscriptions | R$ 661 |
| Streaming | R$ 350 |

## Expense Categories

When categorizing transactions, use these 9 standard categories:

1. **Alimentacao** - Groceries, restaurants, delivery, coffee (Target: R$ 5,000)
2. **Transporte** - Fuel, tolls, parking, rides (Target: R$ 1,500)
3. **Saude** - Pharmacy, appointments, gym, wellness (Target: R$ 1,500)
4. **Assinaturas/Software** - Streaming, apps, SaaS tools (Target: R$ 1,000)
5. **Compras Diversas** - Shopping, home items, gifts (Target: R$ 3,000)
6. **Lazer** - Entertainment, events, travel (Target: R$ 2,500)
7. **Educacao** - Courses, books, certifications (Target: R$ 500)
8. **Casa** - Maintenance, repairs, utilities (Target: R$ 3,000)
9. **Taxas/Servicos** - Bank fees, services, government (Target: R$ 500)

**Important**: Fixed commitments (home loan, car subscription, health insurance) are tracked separately from variable expenses.

## Budget Framework

Adapted 50/30/20 based on net income of R$ 55,000:

| Category | % | Target |
|----------|---|--------|
| Necessities | 50% | R$ 27,500 |
| Wants | 30% | R$ 16,500 |
| Savings | 20% | R$ 11,000 |

**Target Savings Rate**: 35% (aggressive wealth building)

## Key Financial Goals

### 2025 Goals
- Build Tier 1 emergency reserve: R$ 240,000 (6 months)
- Contract all essential insurance (DIT, Life, Prestamista)
- Open international accounts (Wise Business, IBKR)
- Configure 20% salary receipt in USD
- Net worth target: R$ 365,000

### 2026 Goals
- Complete Tier 2 reserve: R$ 480,000 total
- Net worth target: R$ 800,000
- Launch MVP side project
- Diversify to 2nd client

### Long-term (2035)
- Net worth: R$ 7.7 million
- Passive income: R$ 21,700/month
- 36 months of reserves

## Investment Allocation (Target)

| Asset Class | % |
|-------------|---|
| Fixed Income BR (Tesouro IPCA+, CDBs, LCI/LCA) | 30% |
| Equities BR (ETFs, stocks) | 25% |
| FIIs (Real Estate Funds) | 20% |
| USD Hedge (offshore, US ETFs) | 25% |

## Metodologia de Datas

**REGRA FUNDAMENTAL**: Sempre usar a **DATA DA TRANSAÇÃO** (quando a compra foi feita), não a data de pagamento da fatura.

### Exemplo Prático
- Compra feita em 20/12/2025 → Planejamento de **Dezembro 2025**
- Mesmo que a fatura do cartão seja paga em Janeiro 2026
- Isso permite análise precisa de quando o gasto ocorreu

### Aplicação no Sistema
- Campo `date` no banco = data da transação
- Relatórios mensais agrupam por data da transação
- Extração do BB "Meus Gastos" já fornece a data correta

---

## Task Guidelines

### Transaction Processing
When extracting or categorizing transactions:
1. Use the 9 standard categories above
2. Flag any transaction > R$ 1,000 for review
3. Separate fixed vs variable expenses
4. Convert USD transactions at daily rate
5. Output in consistent format (JSON or Excel-compatible)
6. **Always use transaction date, not payment date**

### Financial Analysis
When analyzing spending or projections:
1. Compare against category targets
2. Calculate actual savings rate
3. Track deviation from 50/30/20 framework
4. Consider FX impact on USD income

### Automation Tasks
For bank statement extraction (Banco do Brasil):
1. Never store banking credentials
2. Auto-end banking sessions after extraction
3. Output as structured JSON
4. Verify totals match statement

## Currency Handling

- Default exchange rate: R$ 6.00
- Always specify currency (USD or BRL)
- For projections, use conservative FX assumptions:
  - 2025: R$ 6.00
  - 2030: R$ 6.50
  - 2035: R$ 6.70

## Security Protocols

1. **Never** store or request banking passwords
2. **Never** execute financial transactions automatically
3. **Always** verify calculations against official sources
4. Flag any suspicious transaction patterns
5. Use secure environment for financial data

## Response Guidelines

When discussing finances:
- Be precise with numbers (always specify currency)
- Provide actionable recommendations
- Reference specific targets from this document
- Consider tax implications (Simples Nacional)
- Account for Brazil-specific financial instruments (Tesouro, FIIs, LCI/LCA)

### Brazilian Financial Terms
- **Tesouro Selic/IPCA+**: Government bonds
- **CDB**: Bank certificates of deposit
- **LCI/LCA**: Tax-exempt real estate/agribusiness letters
- **FIIs**: Real estate investment funds (REITs equivalent)
- **PGBL**: Private pension with tax deduction
- **DIT**: Income protection insurance
- **Simples Nacional**: Simplified tax regime for small businesses

## Review Cadence

Support the user with:
- **Weekly**: Expense tracking updates
- **Monthly**: Savings rate calculation, budget deviation analysis
- **Quarterly**: Goal progress review, rebalancing recommendations
- **Annually**: Full strategy review, tax planning

## Important Dates

- **June 2026**: Mudanca para casa nova (interior pronto)
- **October 2026**: Furniture installments end (R$ 9,400/month)
- **November 2026**: Deck Cumaru completion (exterior finalizado)
- **2026**: Home construction costs (R$ 80,940 obra + R$ 126,000 moveis = R$ 206,940 total)
- **2045**: Home loan completion

## 2026 Planning Spreadsheets

### Original Plan (Reference)
File: `projections/Planejamento_2026_Atualizado_Janeiro.xlsx`

| Sheet | Purpose |
|-------|---------|
| Janeiro Real vs Plan | Monthly tracking: actual vs budget |
| Forecast 2026 | Full year projection with all costs |
| Custos Obra 2026 | Detailed construction breakdown |
| Análise Impacto | Impact analysis on savings goals |
| Fluxo Mensal | Monthly cash flow projection |

### Restructured Plan (Active)
File: `projections/Planejamento_2026_Reestruturado.xlsx`

| Sheet | Purpose |
|-------|---------|
| Resumo Comparativo | Original vs restructured metrics |
| Cronograma Reestruturado | New construction timeline |
| Fluxo Caixa Novo | Updated monthly cash flow |
| Mudanças Realizadas | Change log with justifications |

### 2026 Key Metrics - RESTRUCTURED

**Improvement Summary**:
| Metric | Original | Restructured | Change |
|--------|----------|--------------|--------|
| Deficit months | 4 | 0 | -100% |
| Lowest balance | -R$ 33,485 | +R$ 525 | +102% |
| Year-end savings | R$ 63,368 | R$ 98,368 | +55% |
| Loan needed | R$ 60,000 | R$ 0 | Eliminated |

**Restructured Construction Timeline (v3.0)**:

**ETAPAS INTERNAS (Prontas ate Junho 2026)**:
| Etapa | Item | Cost | Periodo | Status |
|-------|------|------|---------|--------|
| 1 | Elétrica 2 Quartos | R$ 3,590 | Jan | ⏳ Planejado |
| 2 | Piso 80m² | R$ 6,000 | Jan-Fev | ⏳ Planejado |
| 3 | Acabamentos Internos | R$ 13,000 | Fev-Mai | ⏳ Planejado |
| - | **Subtotal Interno** | **R$ 22,590** | | |

**ETAPAS EXTERNAS (Ao longo do ano)**:
| Etapa | Item | Cost | Periodo | Status |
|-------|------|------|---------|--------|
| 4 | Pintura Externa 200m² | R$ 24,500 | Mar-Ago | ⏳ Planejado |
| 5 | Acabamento Externo | R$ 28,000 | Jul-Out | ⏳ Planejado |
| 6 | Deck Cumaru 18m² | R$ 5,850 | Nov | ⏳ Planejado |
| - | **Subtotal Externo** | **R$ 58,350** | | |

**MOVEIS E ELETROS**:
| Item | Cost | Periodo | Status |
|------|------|---------|--------|
| Móveis Planejados (10x) | R$ 95,000 | Dez/25-Set/26 | ✅ 1/10 Pago (R$ 9.500) |
| Mesa + 6 Cadeiras (10x) | R$ 16,000 | Jan-Out | 🟡 Planejado |
| Eletro (6x) | R$ 15,000 | Set-Fev27 | ⏳ Set/26 |

**TOTAL PROJETO**: R$ 206,940 (Obra: R$ 80,940 + Móveis/Eletros: R$ 126,000)

**New Monthly Cash Flow Pattern**:
- Jan: +R$ 525 (essentials only)
- Fev: +R$ 8,615 (month of rest)
- Mar-Mai: Building buffer (+R$ 6-7k/month)
- Jun: -R$ 2,905 (Pintura M.O. using buffer)
- Jul-Out: Recovery (+R$ 7-9k/month)
- Nov-Dez: Strong finish (+R$ 17-22k/month)
- Year-end accumulated: R$ 98,368

**Note**: Eletrodomésticos installments 5/6 and 6/6 continue into Jan-Feb 2027 (R$ 5,000)

## Monte Carlo Projections (2035)

For reference when discussing probabilities:
- 75% chance of > R$ 6.0 million
- 50% chance of > R$ 7.5 million
- 25% chance of > R$ 9.0 million

## Skills Disponiveis

### personal-finance-updater

Skill para atualizacao automatica de gastos.

**Triggers**: "atualizar meus gastos", "sincronizar dashboard", "comparar real vs projetado"

**Workflow**:
1. Extrair transacoes do BB
2. Categorizar automaticamente
3. Atualizar planilha Excel
4. Atualizar Dashboard Obsidian
5. Gerar relatorio com alertas

**Arquivos**:
- `skills/personal-finance-updater/SKILL.md` - Definicao da skill
- `skills/personal-finance-updater/references/categorias.md` - Regras de categorizacao
- `skills/personal-finance-updater/references/parcelamentos-ativos.md` - Parcelamentos

## Dashboard Obsidian

### Tracking Mensal

- `tracking/Dashboard-Mensal.md` - Visao executiva com KPIs
- `tracking/2026/{Mes}.md` - Detalhamento por mes

### Campos Atualizados

| Campo | Descricao |
|-------|-----------|
| Gastos Totais | Soma de todas as despesas |
| Taxa Poupanca | (Receita - Despesas) / Receita |
| Saldo Mensal | Receita - Despesas |
| Status por Categoria | OK/Atencao/Critico |

## Documentacao de Obra

### Arquivos

- `obra/Plano-Obra-2026.md` - Plano completo para mestre de obras (v3.0)
- `obra/Checklist-Etapas.md` - Acompanhamento de execucao (6 etapas)

### Etapas 2026 (Cronograma v3.0 - Mudanca Junho)

**ETAPAS INTERNAS (Prontas ate Junho 2026)**:
| Etapa | Descricao | Periodo | Custo | Status |
|-------|-----------|---------|-------|--------|
| 1 | Eletrica 2 Quartos | Janeiro | R$ 3.590 | ⏳ Planejado |
| 2 | Piso 80m² | Jan-Fev | R$ 6.000 | ⏳ Planejado |
| 3 | Acabamentos Internos | Fev-Mai | R$ 13.000 | ⏳ Planejado |
| - | **Subtotal Interno** | | **R$ 22.590** | |

**ETAPAS EXTERNAS (Ao longo do ano)**:
| Etapa | Descricao | Periodo | Custo | Status |
|-------|-----------|---------|-------|--------|
| 4 | Pintura Externa 200m² | Mar-Ago | R$ 24.500 | ⏳ Planejado |
| 5 | Acabamento Externo | Jul-Out | R$ 28.000 | ⏳ Planejado |
| 6 | Deck Cumaru 18m² | Novembro | R$ 5.850 | ⏳ Planejado |
| - | **Subtotal Externo** | | **R$ 58.350** | |

**MOVEIS E ELETRODOMESTICOS**:
| Item | Periodo | Custo | Status |
|------|---------|-------|--------|
| Móveis Planejados | Dez/25-Set/26 | R$ 95.000 | ✅ 1/10 Pago |
| Mesa + 6 Cadeiras | Jan-Out | R$ 16.000 | 🟡 Planejado |
| Eletrodomésticos | Set/26-Fev/27 | R$ 15.000 | ⏳ Set/26 |
| **Subtotal Móveis** | | **R$ 126.000** | |

**Total Investimento 2026**: R$ 206.940

---

*Always prioritize accuracy and conservative estimates in financial matters.*

# Agent Finance

Personal financial management system for a Senior PM working in nearshoring (PJ contractor for US companies), with a comprehensive 10-year wealth building plan (2025-2035).

## Overview

This project contains financial planning documents, tracking systems, and automation tools for managing:

- **Income**: $12,000 USD/month (~R$ 55,000-72,000 BRL net after taxes)
- **Tax Regime**: Simples Nacional (Brazil)
- **Planning Horizon**: 10 years (2025-2035)
- **Target Net Worth**: R$ 7.7 million by 2035

## Key Financial Framework

### Budget Methodology (Adapted 50/30/20)

| Category | Target % | Monthly Target |
|----------|----------|----------------|
| Necessities | 50% | R$ 27,500 |
| Wants/Lifestyle | 30% | R$ 16,500 |
| Savings/Investments | 20% | R$ 11,000 |

**Current Performance**: 28% savings rate (above target)

### 9 Expense Categories

1. **Alimentacao** - Food, groceries, restaurants
2. **Transporte** - Fuel, tolls, parking, rides
3. **Saude** - Health expenses (excluding insurance)
4. **Assinaturas/Software** - Subscriptions, SaaS tools
5. **Compras Diversas** - Shopping, personal items
6. **Lazer** - Entertainment, travel, hobbies
7. **Educacao** - Courses, books, certifications
8. **Casa** - Home maintenance (excluding loan)
9. **Taxas/Servicos** - Fees, professional services

### Fixed Commitments

| Item | Monthly | Duration |
|------|---------|----------|
| Home Loan | R$ 7,500 | 20 years |
| Car Subscription | R$ 3,200 | Ongoing |
| Health Insurance | R$ 1,300 | Ongoing |
| Work Software | R$ 661 | Ongoing |

## Investment Strategy

### Phase 1: Foundation (2025-2026)
- Build 24-month emergency reserve (R$ 960,000)
- Tesouro Selic, CDBs, LCI/LCA

### Phase 2: Diversification (2027-2030)
- Fixed Income BR: 30%
- Equities BR: 25%
- FIIs: 20%
- USD Hedge: 25%

### Phase 3: Income Generation (2031-2035)
- Target passive income: R$ 21,700/month

## Risk Management

### Insurance Coverage
- DIT (Income Protection): 12 months coverage
- Life + Disability: R$ 5 million
- Prestamista: Outstanding loan balance
- Health: Premium national coverage

**Total Insurance Cost**: R$ 2,400/month (3.33% of income)

## Key Milestones

| Year | Net Worth Target | Reserve Months |
|------|------------------|----------------|
| 2025 | R$ 365,000 | 12 |
| 2027 | R$ 1.5 million | 24 |
| 2030 | R$ 4 million | 30 |
| 2035 | R$ 7.7 million | 36 |

## Automation

### Transaction Extraction
- Source: Banco do Brasil credit card statements
- Method: Chrome automation
- Format: JSON to Excel categorization
- Frequency: Monthly

### Tools
- Expense Tracking: Mobills/Organizze
- Portfolio: Real Valor
- International: Wise
- Dashboard: Google Sheets

## Review Cadence

- **Weekly**: Update expense tracking
- **Monthly**: Calculate savings rate, check budget deviations
- **Quarterly**: Review goals, rebalance if needed
- **Annually**: Full strategy review, tax planning, insurance updates

## Project Structure

```
Agent Finance/
├── README.md                    # This file
├── CLAUDE.md                    # AI assistant instructions
├── obra/                        # Construction documentation
│   ├── Plano-Obra-2026.md      # Detailed plan for contractor
│   └── Checklist-Etapas.md     # Progress tracking
├── tracking/                    # Monthly expense tracking
│   ├── Dashboard-Mensal.md     # Executive KPI view
│   └── 2026/                   # Monthly details
│       ├── Janeiro.md
│       └── ...
├── projections/                 # Financial projections
│   ├── Planejamento_2026_Reestruturado.xlsx  # Active plan
│   └── Planejamento_2026_Atualizado_Janeiro.xlsx
├── skills/                      # Automation skills
│   └── personal-finance-updater/
│       ├── SKILL.md
│       └── references/
├── reference/                   # Financial reference documents
└── automation/                  # Scripts and tools
```

## Currency Assumptions

| Year | USD/BRL Rate |
|------|--------------|
| 2025 | R$ 6.00 |
| 2030 | R$ 6.50 |
| 2035 | R$ 6.70 |

---

*This project is for personal financial planning purposes only and does not constitute investment advice.*

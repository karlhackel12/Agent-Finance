---
tipo: dashboard
ano: 2026
mes: 1
atualizado: 2026-01-17 10:56
---

# Dashboard Financeiro 2026

> Sincronizado automaticamente em: `= this.atualizado`

## Mes Atual: Janeiro 2026

### KPIs Principais

```dataview
TABLE WITHOUT ID
  metrica as "Metrica",
  valor as "Valor",
  meta as "Meta",
  status as "Status"
FROM "tracking/data"
WHERE tipo = "kpi" AND ano = 2026 AND mes = 1
```

| Metrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Gastos Variaveis | R$ 38,563 | R$ 37,800 | Acima |
| Taxa Poupanca | 30% | 28% | OK |
| Categorias Criticas | 5 | 0 | Critico |

### Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
| 🏗️ Obra | R$ 18,833 | R$ 16,500 | 114% | Critico |
| 🏥 Saude | R$ 4,860 | R$ 4,000 | 122% | Critico |
| 💻 Assinaturas | R$ 4,292 | R$ 3,500 | 123% | Critico |
| 🚗 Transporte | R$ 3,370 | R$ 4,000 | 84% | OK |
| 🛒 Compras | R$ 2,273 | R$ 2,500 | 91% | Atencao |
| 🍔 Alimentacao | R$ 1,965 | R$ 3,500 | 56% | OK |
| 🎮 Lazer | R$ 1,799 | R$ 1,500 | 120% | Critico |
| 📝 Taxas | R$ 679 | R$ 100 | 679% | Critico |
| 🏠 Casa | R$ 393 | R$ 500 | 79% | OK |
| 📚 Educacao | R$ 99 | R$ 200 | 50% | OK |
| 🎾 Esportes | R$ 0 | R$ 1,500 | 0% | OK |

### Distribuicao 50/30/20

| Categoria | Ideal | Atual | Status |
|-----------|-------|-------|--------|
| Necessidades (50%) | R$ 27.500 | *calcular* | - |
| Desejos (30%) | R$ 16.500 | *calcular* | - |
| Poupanca (20%) | R$ 11.000 | R$ 16,437 | OK |

---

## Alertas Ativos

- **CRITICO**: 🏗️ Obra excedeu R$ 2,333 (114% do budget)
- **CRITICO**: 🏥 Saude excedeu R$ 860 (122% do budget)
- **CRITICO**: 💻 Assinaturas excedeu R$ 792 (123% do budget)
- **CRITICO**: 🎮 Lazer excedeu R$ 299 (120% do budget)
- **CRITICO**: 📝 Taxas excedeu R$ 579 (679% do budget)
- **Atencao**: 🛒 Compras em 91% do budget

---

## Parcelamentos Ativos

| Descricao | Parcela | Valor | Termina |
|-----------|---------|-------|---------|
| DROGARIAS PACHECO | 3/3 | R$ 1,847 | 2026-01-01 |
| DROGARIA MODERNA | 2/2 | R$ 238 | 2026-01-01 |
| AREDES | 8/8 | R$ 670 | 2026-01-01 |
| LOVABLE | 4/4 | R$ 153 | 2026-01-01 |
| CASA CHIESSE 2X | 2/2 | R$ 549 | 2026-01-01 |
| FIRE VERBO | 2/2 | R$ 220 | 2026-01-01 |
| OTIQUE | 9/10 | R$ 85 | 2026-02-01 |
| RAIA311 | 1/2 | R$ 930 | 2026-02-01 |
| PICPAY OBRA | 1/2 | R$ 986 | 2026-02-01 |
| PICPAY MOVEIS | 1/2 | R$ 5,238 | 2026-02-01 |

*... e mais 14 parcelamentos*

---

## Links Rapidos

- [[2026/Janeiro|Detalhamento Janeiro]]
- [[../obra/Plano-Obra-2026|Plano de Obra]]
- [[../obra/Checklist-Etapas|Checklist Obra]]

---

## Proximas Acoes

1. [ ] Revisar gastos de Obra
2. [ ] Revisar gastos de Saude
3. [ ] Revisar gastos de Assinaturas
4. [ ] Revisar gastos de Lazer
5. [ ] Revisar gastos de Taxas
6. [ ] Sincronizar fatura BB
7. [ ] Atualizar parcelamentos


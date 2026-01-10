---
tipo: dashboard
ano: 2026
mes: 1
atualizado: 2026-01-10 12:41
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
| Gastos Variaveis | R$ 26,758 | R$ 37,800 | OK |
| Taxa Poupanca | 51% | 28% | OK |
| Categorias Criticas | 1 | 0 | Critico |

### Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
| 🏗️ Obra | R$ 11,010 | R$ 16,500 | 67% | OK |
| 💻 Assinaturas | R$ 3,544 | R$ 3,500 | 101% | Atencao |
| 🏥 Saude | R$ 3,382 | R$ 4,000 | 85% | OK |
| 🚗 Transporte | R$ 3,370 | R$ 4,000 | 84% | OK |
| 🛒 Compras | R$ 2,576 | R$ 2,500 | 103% | Atencao |
| 🍔 Alimentacao | R$ 1,310 | R$ 3,500 | 37% | OK |
| 🎮 Lazer | R$ 1,026 | R$ 1,500 | 68% | OK |
| 🏠 Casa | R$ 393 | R$ 500 | 79% | OK |
| 📝 Taxas | R$ 146 | R$ 100 | 146% | Critico |
| 📚 Educacao | R$ 0 | R$ 200 | 0% | OK |
| 🎾 Esportes | R$ 0 | R$ 1,500 | 0% | OK |

### Distribuicao 50/30/20

| Categoria | Ideal | Atual | Status |
|-----------|-------|-------|--------|
| Necessidades (50%) | R$ 27.500 | *calcular* | - |
| Desejos (30%) | R$ 16.500 | *calcular* | - |
| Poupanca (20%) | R$ 11.000 | R$ 28,242 | OK |

---

## Alertas Ativos

- **CRITICO**: 📝 Taxas excedeu R$ 46 (146% do budget)
- **Atencao**: 💻 Assinaturas em 101% do budget
- **Atencao**: 🛒 Compras em 103% do budget

---

## Parcelamentos Ativos

| Descricao | Parcela | Valor | Termina |
|-----------|---------|-------|---------|
| FIRE VERBO | 1/2 | R$ 220 | 2026-02-01 |
| CASA CHIESSE 2X | 1/2 | R$ 549 | 2026-02-01 |
| DROGARIA MODERNA | 1/2 | R$ 238 | 2026-02-01 |
| AREDES | 7/8 | R$ 670 | 2026-02-01 |
| DROGARIAS PACHECO | 2/3 | R$ 1,847 | 2026-02-01 |
| LOVABLE | 3/4 | R$ 153 | 2026-02-01 |
| MARIA LUIZA | 3/4 | R$ 102 | 2026-02-01 |
| OTIQUE | 8/10 | R$ 85 | 2026-03-01 |
| FLOWITH.IO | 1/5 | R$ 61 | 2026-05-01 |
| TAVUS | 1/5 | R$ 72 | 2026-05-01 |

*... e mais 12 parcelamentos*

---

## Links Rapidos

- [[2026/Janeiro|Detalhamento Janeiro]]
- [[../obra/Plano-Obra-2026|Plano de Obra]]
- [[../obra/Checklist-Etapas|Checklist Obra]]

---

## Proximas Acoes

1. [ ] Revisar gastos de Taxas
2. [ ] Sincronizar fatura BB
3. [ ] Atualizar parcelamentos

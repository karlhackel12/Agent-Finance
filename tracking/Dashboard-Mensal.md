---
tipo: dashboard
ano: 2025
mes: 12
atualizado: 2025-12-30 21:49
---

# Dashboard Financeiro 2025

> Sincronizado automaticamente em: `= this.atualizado`

## Mes Atual: Dezembro 2025

### KPIs Principais

```dataview
TABLE WITHOUT ID
  metrica as "Metrica",
  valor as "Valor",
  meta as "Meta",
  status as "Status"
FROM "tracking/data"
WHERE tipo = "kpi" AND ano = 2025 AND mes = 12
```

| Metrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Gastos Variaveis | R$ 31,101 | R$ 22,500 | Acima |
| Taxa Poupanca | 44% | 28% | OK |
| Categorias Criticas | 4 | 0 | Critico |

### Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
| 🏠 Casa | R$ 9,500 | R$ 2,000 | 475% | Critico |
| 🛒 Compras | R$ 7,882 | R$ 3,500 | 225% | Critico |
| 🍔 Alimentacao | R$ 5,049 | R$ 4,000 | 126% | Critico |
| 🚗 Transporte | R$ 3,493 | R$ 4,200 | 83% | OK |
| 💻 Assinaturas | R$ 2,551 | R$ 1,300 | 196% | Critico |
| 🏥 Saude | R$ 1,967 | R$ 3,800 | 52% | OK |
| 🎮 Lazer | R$ 619 | R$ 1,500 | 41% | OK |
| 📚 Educacao | R$ 40 | R$ 400 | 10% | OK |
| 📝 Taxas | R$ 0 | R$ 300 | 0% | OK |
| 🎾 Esportes | R$ 0 | R$ 1,500 | 0% | OK |

### Distribuicao 50/30/20

| Categoria | Ideal | Atual | Status |
|-----------|-------|-------|--------|
| Necessidades (50%) | R$ 27.500 | *calcular* | - |
| Desejos (30%) | R$ 16.500 | *calcular* | - |
| Poupanca (20%) | R$ 11.000 | R$ 23,899 | OK |

---

## Alertas Ativos

- **CRITICO**: 🏠 Casa excedeu R$ 7,500 (475% do budget)
- **CRITICO**: 🛒 Compras excedeu R$ 4,382 (225% do budget)
- **CRITICO**: 🍔 Alimentacao excedeu R$ 1,049 (126% do budget)
- **CRITICO**: 💻 Assinaturas excedeu R$ 1,251 (196% do budget)

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

*... e mais 13 parcelamentos*

---

## Links Rapidos

- [[2026/Dezembro|Detalhamento Dezembro]]
- [[../obra/Plano-Obra-2026|Plano de Obra]]
- [[../obra/Checklist-Etapas|Checklist Obra]]

---

## Proximas Acoes

1. [ ] Revisar gastos de Casa
2. [ ] Revisar gastos de Compras
3. [ ] Revisar gastos de Alimentacao
4. [ ] Revisar gastos de Assinaturas
5. [ ] Sincronizar fatura BB
6. [ ] Atualizar parcelamentos

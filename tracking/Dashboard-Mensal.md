---
tipo: dashboard
ano: 2026
mes: 1
atualizado: 2026-01-25 10:30
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
| Gastos Variaveis | R$ 87,576 | R$ 37,800 | Acima |
| Taxa Poupanca | -59% | 28% | Atencao |
| Categorias Criticas | 10 | 0 | Critico |

### Gastos por Categoria

| Categoria | Gasto | Budget | % | Status |
|-----------|-------|--------|---|--------|
| 🏗️ Obra | R$ 38,320 | R$ 16,500 | 232% | Critico |
| 🛒 Compras | R$ 11,710 | R$ 2,500 | 468% | Critico |
| 🏥 Saude | R$ 9,484 | R$ 4,000 | 237% | Critico |
| 💻 Assinaturas | R$ 8,253 | R$ 3,500 | 236% | Critico |
| 🚗 Transporte | R$ 7,055 | R$ 4,000 | 176% | Critico |
| 🍔 Alimentacao | R$ 4,907 | R$ 3,500 | 140% | Critico |
| 🎮 Lazer | R$ 3,423 | R$ 1,500 | 228% | Critico |
| 📝 Taxas | R$ 2,195 | R$ 100 | 2195% | Critico |
| 🎾 Esportes | R$ 1,180 | R$ 1,500 | 79% | OK |
| 🏠 Casa | R$ 786 | R$ 500 | 157% | Critico |
| 📚 Educacao | R$ 263 | R$ 200 | 131% | Critico |

### Distribuicao 50/30/20

| Categoria | Ideal | Atual | Status |
|-----------|-------|-------|--------|
| Necessidades (50%) | R$ 27.500 | *calcular* | - |
| Desejos (30%) | R$ 16.500 | *calcular* | - |
| Poupanca (20%) | R$ 11.000 | R$ -32,576 | Atencao |

---

## Alertas Ativos

- **CRITICO**: 🏗️ Obra excedeu R$ 21,820 (232% do budget)
- **CRITICO**: 🛒 Compras excedeu R$ 9,210 (468% do budget)
- **CRITICO**: 🏥 Saude excedeu R$ 5,484 (237% do budget)
- **CRITICO**: 💻 Assinaturas excedeu R$ 4,753 (236% do budget)
- **CRITICO**: 🚗 Transporte excedeu R$ 3,055 (176% do budget)
- **CRITICO**: 🍔 Alimentacao excedeu R$ 1,407 (140% do budget)
- **CRITICO**: 🎮 Lazer excedeu R$ 1,923 (228% do budget)
- **CRITICO**: 📝 Taxas excedeu R$ 2,095 (2195% do budget)
- **CRITICO**: 🏠 Casa excedeu R$ 286 (157% do budget)
- **CRITICO**: 📚 Educacao excedeu R$ 63 (131% do budget)

---

## Parcelamentos Ativos

| Descricao | Parcela | Valor | Termina |
|-----------|---------|-------|---------|
| ALFATEC COMER - Eletrodom | 17/21 | R$ 414 | 2025-01-29 |
| DROGARIAS PACHECO | 3/3 | R$ 1,847 | 2026-01-01 |
| DROGARIA MODERNA | 2/2 | R$ 238 | 2026-01-01 |
| AREDES | 8/8 | R$ 670 | 2026-01-01 |
| LOVABLE | 4/4 | R$ 153 | 2026-01-01 |
| CASA CHIESSE 2X | 2/2 | R$ 549 | 2026-01-01 |
| FIRE VERBO | 2/2 | R$ 220 | 2026-01-01 |
| OTIQUE | 9/10 | R$ 85 | 2026-02-01 |
| RAIA311 | 1/2 | R$ 930 | 2026-02-01 |
| PICPAY OBRA | 1/2 | R$ 986 | 2026-02-01 |

*... e mais 16 parcelamentos*

---

## Links Rapidos

- [[2026/Janeiro|Detalhamento Janeiro]]
- [[../obra/Plano-Obra-2026|Plano de Obra]]
- [[../obra/Checklist-Etapas|Checklist Obra]]

---

## Proximas Acoes

1. [ ] Revisar gastos de Obra
2. [ ] Revisar gastos de Compras
3. [ ] Revisar gastos de Saude
4. [ ] Revisar gastos de Assinaturas
5. [ ] Revisar gastos de Transporte
6. [ ] Revisar gastos de Alimentacao
7. [ ] Revisar gastos de Lazer
8. [ ] Revisar gastos de Taxas
9. [ ] Revisar gastos de Casa
10. [ ] Revisar gastos de Educacao
11. [ ] Sincronizar fatura BB
12. [ ] Atualizar parcelamentos

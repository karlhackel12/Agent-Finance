#!/usr/bin/env python3
"""
Fluxo Anual - Annual cash flow projection page
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

# Add scripts to path
SCRIPTS_PATH = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from finance_db import get_monthly_summary, get_active_installments, get_categories

st.set_page_config(page_title="Fluxo Anual", page_icon="📈", layout="wide")

st.title("📈 Fluxo de Caixa Anual 2026")

# Categorias excluídas do cálculo de variáveis (obra é separada)
EXCLUDED_CATEGORIES = ['obra', 'esportes']

# Constants
RECEITA = 55000
FINANCIAMENTO = 7500    # Empréstimo imobiliário (58 meses até Out/2030)

# Calcular VARIAVEIS_PROJ dinamicamente do banco (budget mensal excl. obra/esportes)
categories = get_categories()
VARIAVEIS_PROJ = sum(
    c.get('budget_monthly', 0) for c in categories
    if c.get('name') not in EXCLUDED_CATEGORIES
)

# Obra projections per month (móveis/construção, NÃO é o empréstimo)
OBRA_PROJ = {
    1: 9590, 2: 6250, 3: 7333, 4: 7333, 5: 7333, 6: 19083,
    7: 7084, 8: 7084, 9: 7000, 10: 7000, 11: 5850, 12: 0
}

# Get installments
installments = get_active_installments()

# Calculate monthly installment totals
def get_monthly_installments():
    monthly = {m: 0 for m in range(1, 13)}
    for inst in installments:
        start = inst['start_date']
        end = inst['end_date']
        amount = inst['installment_amount']

        start_year, start_month = int(start[:4]), int(start[5:7])
        end_year, end_month = int(end[:4]), int(end[5:7])

        for month in range(1, 13):
            month_start = (2026, month)
            inst_start = (start_year, start_month)
            inst_end = (end_year, end_month)

            if inst_start <= month_start <= inst_end:
                monthly[month] += amount

    return monthly

monthly_inst = get_monthly_installments()

# Build data
months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

data = []
for m in range(1, 13):
    # Get real data
    summary = get_monthly_summary(2026, m)

    # Separar variáveis de obra
    cats = summary.get('categories', [])
    var_real = sum(c.get('total', 0) for c in cats if c.get('category') not in EXCLUDED_CATEGORIES)
    obra_real = sum(c.get('total', 0) for c in cats if c.get('category') == 'obra')

    parc_real = 0  # Parcelamentos já estão em var_real/obra_real
    financ_real = FINANCIAMENTO if m == 1 else 0  # Assume pago

    saida_proj = VARIAVEIS_PROJ + monthly_inst[m] + OBRA_PROJ[m] + FINANCIAMENTO
    saida_real = var_real + obra_real + financ_real
    poup_proj = RECEITA - saida_proj
    poup_real = RECEITA - saida_real if (var_real > 0 or obra_real > 0) else 0

    data.append({
        'Mês': months[m-1],
        'Receita': RECEITA,
        'Financiam (P)': FINANCIAMENTO,
        'Variáveis (P)': VARIAVEIS_PROJ,
        'Variáveis (R)': var_real,
        'Parcelam (P)': monthly_inst[m],
        'Parcelam (R)': parc_real,
        'Obra (P)': OBRA_PROJ[m],
        'Obra (R)': obra_real,
        'Saída (P)': saida_proj,
        'Saída (R)': saida_real,
        'Poupança (P)': poup_proj,
        'Poupança (R)': poup_real
    })

df = pd.DataFrame(data)

# Summary metrics
st.markdown("### Resumo Anual")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Anual", f"R$ {RECEITA * 12:,.0f}")
with col2:
    total_saida = df['Saída (P)'].sum()
    st.metric("Saída Projetada", f"R$ {total_saida:,.0f}")
with col3:
    poupanca_anual = df['Poupança (P)'].sum()
    st.metric("Poupança Projetada", f"R$ {poupanca_anual:,.0f}")
with col4:
    taxa_poup = (poupanca_anual / (RECEITA * 12)) * 100
    st.metric("Taxa de Poupança", f"{taxa_poup:.0f}%")

st.markdown("---")

# Chart: Monthly breakdown
st.markdown("### Composição Mensal de Gastos")

fig = go.Figure()
fig.add_trace(go.Bar(name='Financiamento', x=df['Mês'], y=df['Financiam (P)'], marker_color='#9b59b6'))
fig.add_trace(go.Bar(name='Variáveis', x=df['Mês'], y=df['Variáveis (P)'], marker_color='#3498db'))
fig.add_trace(go.Bar(name='Obra', x=df['Mês'], y=df['Obra (P)'], marker_color='#f39c12'))
fig.update_layout(barmode='stack', height=400)
st.plotly_chart(fig, use_container_width=True)

# Chart: Poupança projection
st.markdown("### Projeção de Poupança")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df['Mês'],
    y=df['Poupança (P)'],
    mode='lines+markers',
    name='Projetado',
    line=dict(color='#2ecc71', width=3)
))
fig2.add_trace(go.Scatter(
    x=df['Mês'],
    y=df['Poupança (R)'],
    mode='lines+markers',
    name='Real',
    line=dict(color='#3498db', width=3, dash='dot')
))
fig2.add_hline(y=df['Poupança (P)'].mean(), line_dash="dash",
               annotation_text=f"Média: R$ {df['Poupança (P)'].mean():,.0f}")
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Table
st.markdown("### Dados Mensais Detalhados")

# Format and display
display_cols = ['Mês', 'Receita', 'Financiam (P)', 'Variáveis (P)', 'Variáveis (R)',
                'Obra (P)', 'Obra (R)', 'Poupança (P)', 'Poupança (R)']

st.dataframe(
    df[display_cols].style.format({
        'Receita': 'R$ {:,.0f}',
        'Financiam (P)': 'R$ {:,.0f}',
        'Variáveis (P)': 'R$ {:,.0f}',
        'Variáveis (R)': 'R$ {:,.0f}',
        'Obra (P)': 'R$ {:,.0f}',
        'Obra (R)': 'R$ {:,.0f}',
        'Poupança (P)': 'R$ {:,.0f}',
        'Poupança (R)': 'R$ {:,.0f}'
    }),
    use_container_width=True,
    hide_index=True
)

# Totals
st.markdown("### Totais Anuais")
totals = df[['Receita', 'Financiam (P)', 'Variáveis (P)', 'Obra (P)', 'Poupança (P)']].sum()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Receita", f"R$ {totals['Receita']:,.0f}")
with col2:
    st.metric("Financiam", f"R$ {totals['Financiam (P)']:,.0f}")
with col3:
    st.metric("Variáveis", f"R$ {totals['Variáveis (P)']:,.0f}")
with col4:
    st.metric("Obra", f"R$ {totals['Obra (P)']:,.0f}")
with col5:
    st.metric("Poupança", f"R$ {totals['Poupança (P)']:,.0f}")

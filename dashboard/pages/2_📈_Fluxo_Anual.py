#!/usr/bin/env python3
"""
Fluxo Anual - Annual cash flow projection page

SIMPLIFICADO: Parcelamentos já estão incluídos nas transações por categoria.
Não precisam ser contados separadamente.
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

# Add scripts to path
SCRIPTS_PATH = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from finance_db import get_monthly_summary, get_categories

st.set_page_config(page_title="Fluxo Anual", page_icon="📈", layout="wide")

st.title("📈 Fluxo de Caixa Anual 2026")

# Categorias excluídas do cálculo de variáveis (obra é separada)
EXCLUDED_CATEGORIES = ['obra', 'esportes']

# Constants
RECEITA = 55000
FINANCIAMENTO = 7500    # Empréstimo imobiliário (58 meses até Out/2030)

# Calcular budgets dinamicamente do banco
categories = get_categories()

# Budget de variáveis (excl. obra/esportes) - R$ 19,800
VARIAVEIS_BUDGET = sum(
    c.get('budget_monthly', 0) for c in categories
    if c.get('name') not in EXCLUDED_CATEGORIES
)

# Budget de obra - R$ 16,500/mês médio
OBRA_BUDGET = sum(
    c.get('budget_monthly', 0) for c in categories
    if c.get('name') == 'obra'
)

# Build data
months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

data = []
for m in range(1, 13):
    # Get real data from transactions (parcelamentos já incluídos nas categorias)
    summary = get_monthly_summary(2026, m)

    # Separar variáveis de obra
    cats = summary.get('categories', [])
    var_real = sum(c.get('total', 0) for c in cats if c.get('category') not in EXCLUDED_CATEGORIES)
    obra_real = sum(c.get('total', 0) for c in cats if c.get('category') == 'obra')

    # Projetado: Budget mensal (teto de gastos)
    # Real: Soma das transações por categoria (já inclui parcelamentos)
    saida_proj = VARIAVEIS_BUDGET + OBRA_BUDGET + FINANCIAMENTO
    saida_real = var_real + obra_real + FINANCIAMENTO
    poup_proj = RECEITA - saida_proj
    poup_real = RECEITA - saida_real if (var_real > 0 or obra_real > 0) else 0

    data.append({
        'Mês': months[m-1],
        'Receita': RECEITA,
        'Financiam (P)': FINANCIAMENTO,
        'Variáveis (P)': VARIAVEIS_BUDGET,
        'Variáveis (R)': var_real,
        'Obra (P)': OBRA_BUDGET,
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
st.caption("💡 Parcelamentos já incluídos nas categorias (Variáveis e Obra)")

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

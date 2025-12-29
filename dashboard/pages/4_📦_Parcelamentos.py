#!/usr/bin/env python3
"""
Parcelamentos - Installments tracking page
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add scripts to path
SCRIPTS_PATH = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from finance_db import get_active_installments

st.set_page_config(page_title="Parcelamentos", page_icon="📦", layout="wide")

st.title("📦 Controle de Parcelamentos")

# Load data
installments = get_active_installments()

if not installments:
    st.warning("Nenhum parcelamento ativo encontrado")
    st.stop()

# Create dataframe
df = pd.DataFrame([{
    'Descrição': inst.get('description', 'N/A'),
    'Categoria': inst.get('category_name', 'N/A').title() if inst.get('category_name') else 'N/A',
    'Valor Mensal': inst.get('installment_amount', 0),
    'Parcela Atual': inst.get('current_installment', 0),
    'Total Parcelas': inst.get('total_installments', 0),
    'Início': inst.get('start_date', 'N/A'),
    'Término': inst.get('end_date', 'N/A'),
    'Progresso': inst.get('current_installment', 0) / inst.get('total_installments', 1)
} for inst in installments])

# Summary metrics
st.markdown("### Resumo")

col1, col2, col3, col4 = st.columns(4)

total_mensal = df['Valor Mensal'].sum()
total_items = len(df)
avg_parcelas = df['Total Parcelas'].mean()

with col1:
    st.metric("Total Mensal", f"R$ {total_mensal:,.0f}")
with col2:
    st.metric("Parcelamentos Ativos", f"{total_items}")
with col3:
    st.metric("Média de Parcelas", f"{avg_parcelas:.0f}")
with col4:
    # Calculate remaining value
    remaining = sum(
        inst['installment_amount'] * (inst['total_installments'] - inst['current_installment'])
        for inst in installments
    )
    st.metric("Valor Restante", f"R$ {remaining:,.0f}")

st.markdown("---")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Distribuição por Valor")

    # Top 10 by value
    df_sorted = df.nlargest(10, 'Valor Mensal')

    fig = px.bar(
        df_sorted,
        x='Descrição',
        y='Valor Mensal',
        color='Categoria',
        title="Top 10 Parcelamentos por Valor"
    )
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### Por Categoria")

    # Group by category
    df_cat = df.groupby('Categoria')['Valor Mensal'].sum().reset_index()

    fig2 = px.pie(
        df_cat,
        values='Valor Mensal',
        names='Categoria',
        hole=0.4,
        title="Distribuição por Categoria"
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Timeline
st.markdown("### Cronograma de Quitação")

# Sort by end date
df_timeline = df.sort_values('Término')

fig3 = go.Figure()

for i, row in df_timeline.iterrows():
    fig3.add_trace(go.Bar(
        y=[row['Descrição'][:30]],
        x=[row['Progresso'] * 100],
        orientation='h',
        name=row['Descrição'][:20],
        text=f"{row['Parcela Atual']}/{row['Total Parcelas']}",
        textposition='inside',
        showlegend=False,
        marker_color='#3498db' if row['Progresso'] < 0.5 else '#2ecc71' if row['Progresso'] < 0.8 else '#e74c3c'
    ))

fig3.update_layout(
    height=max(300, len(df) * 30),
    xaxis_title="Progresso (%)",
    xaxis_range=[0, 100],
    showlegend=False
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Detailed table
st.markdown("### Lista Completa")

# Add filter
filter_cat = st.multiselect(
    "Filtrar por categoria:",
    options=df['Categoria'].unique(),
    default=df['Categoria'].unique()
)

df_filtered = df[df['Categoria'].isin(filter_cat)]

st.dataframe(
    df_filtered.style.format({
        'Valor Mensal': 'R$ {:,.0f}',
        'Progresso': '{:.0%}'
    }).background_gradient(subset=['Progresso'], cmap='RdYlGn'),
    use_container_width=True,
    hide_index=True,
    height=400
)

# Monthly projection
st.markdown("---")
st.markdown("### Projeção Mensal")

# Calculate monthly totals for next 12 months
monthly_proj = []
months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

for m in range(1, 13):
    total = 0
    for inst in installments:
        start_year, start_month = int(inst['start_date'][:4]), int(inst['start_date'][5:7])
        end_year, end_month = int(inst['end_date'][:4]), int(inst['end_date'][5:7])

        month_start = (2026, m)
        inst_start = (start_year, start_month)
        inst_end = (end_year, end_month)

        if inst_start <= month_start <= inst_end:
            total += inst['installment_amount']

    monthly_proj.append({'Mês': months[m-1], 'Total': total})

df_proj = pd.DataFrame(monthly_proj)

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_proj['Mês'],
    y=df_proj['Total'],
    mode='lines+markers+text',
    text=[f"R$ {v:,.0f}" for v in df_proj['Total']],
    textposition='top center',
    line=dict(color='#e74c3c', width=3)
))
fig4.update_layout(height=350, title="Projeção de Parcelamentos por Mês")
st.plotly_chart(fig4, use_container_width=True)

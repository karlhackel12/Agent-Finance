#!/usr/bin/env python3
"""
Categorias - Detailed category analysis page
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Add scripts to path
SCRIPTS_PATH = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from finance_db import get_monthly_summary, get_categories

st.set_page_config(page_title="Categorias", page_icon="📊", layout="wide")

st.title("📊 Análise por Categoria")

# Month selector
col1, col2 = st.columns([1, 4])
with col1:
    month = st.selectbox("Mês", range(1, 13), index=0,
                         format_func=lambda x: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                                                "Jul", "Ago", "Set", "Out", "Nov", "Dez"][x-1])
    year = 2026

# Load data
summary = get_monthly_summary(year, month)
categories = summary.get('categories', [])

if not categories:
    st.warning("Sem dados para este mês")
    st.stop()

# Create dataframe
df = pd.DataFrame([{
    'Categoria': c['category'].title(),
    'Ícone': c.get('icon', '📁'),
    'Budget': c['budget'],
    'Gasto': c['total'],
    'Disponível': c['budget'] - c['total'],
    'Utilização': c['percent'] / 100
} for c in categories])

# Summary metrics
st.markdown("### Resumo")
col1, col2, col3, col4 = st.columns(4)

total_budget = df['Budget'].sum()
total_gasto = df['Gasto'].sum()

with col1:
    st.metric("Budget Total", f"R$ {total_budget:,.0f}")
with col2:
    st.metric("Gasto Total", f"R$ {total_gasto:,.0f}")
with col3:
    st.metric("Disponível", f"R$ {total_budget - total_gasto:,.0f}")
with col4:
    util = (total_gasto / total_budget * 100) if total_budget > 0 else 0
    st.metric("Utilização", f"{util:.0f}%")

st.markdown("---")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Budget vs Gasto Real")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Budget',
        x=df['Categoria'],
        y=df['Budget'],
        marker_color='#3498db'
    ))
    fig.add_trace(go.Bar(
        name='Gasto',
        x=df['Categoria'],
        y=df['Gasto'],
        marker_color='#e74c3c'
    ))
    fig.update_layout(barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### Distribuição de Gastos")

    # Only show categories with spending
    df_pie = df[df['Gasto'] > 0]

    if len(df_pie) > 0:
        fig2 = px.pie(
            df_pie,
            values='Gasto',
            names='Categoria',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem gastos registrados")

st.markdown("---")

# Detailed table
st.markdown("### Detalhamento")

# Add status column
def get_status(row):
    util = row['Utilização']
    if util > 1:
        return "🔴 Excedido"
    elif util > 0.8:
        return "🟠 Atenção"
    elif util > 0.5:
        return "🟡 Normal"
    else:
        return "🟢 Folga"

df['Status'] = df.apply(get_status, axis=1)

# Display with formatting
st.dataframe(
    df[['Categoria', 'Budget', 'Gasto', 'Disponível', 'Utilização', 'Status']].style.format({
        'Budget': 'R$ {:,.0f}',
        'Gasto': 'R$ {:,.0f}',
        'Disponível': 'R$ {:,.0f}',
        'Utilização': '{:.0%}'
    }),
    use_container_width=True,
    hide_index=True,
    height=400
)

# Progress bars for each category
st.markdown("### Progresso por Categoria")

for _, row in df.iterrows():
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.text(f"{row['Categoria']}")
    with col2:
        progress = min(row['Utilização'], 1.0)
        st.progress(progress)
    with col3:
        st.text(f"{row['Utilização']*100:.0f}%")

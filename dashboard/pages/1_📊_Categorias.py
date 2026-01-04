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

# Categorias excluídas do cálculo de budget (obra/esportes são separadas)
EXCLUDED_CATEGORIES = ['obra', 'esportes']

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

# Create dataframe with all categories
df = pd.DataFrame([{
    'Categoria': c['category'].title(),
    'CatName': c['category'],  # Keep original name for filtering
    'Ícone': c.get('icon', '📁'),
    'Budget': c['budget'],
    'Gasto': c['total'],
    'Disponível': c['budget'] - c['total'],
    'Utilização': c['percent'] / 100
} for c in categories])

# Separar variáveis de obra/esportes
df_variaveis = df[~df['CatName'].isin(EXCLUDED_CATEGORIES)]
df_obra = df[df['CatName'] == 'obra']
df_esportes = df[df['CatName'] == 'esportes']

# Summary metrics - APENAS VARIÁVEIS
st.markdown("### Resumo - Variáveis")
st.caption("💡 Excluindo Obra e Esportes (rastreados separadamente)")
col1, col2, col3, col4 = st.columns(4)

total_budget = df_variaveis['Budget'].sum()
total_gasto = df_variaveis['Gasto'].sum()

with col1:
    st.metric("Budget Variáveis", f"R$ {total_budget:,.0f}")
with col2:
    st.metric("Gasto Variáveis", f"R$ {total_gasto:,.0f}")
with col3:
    st.metric("Disponível", f"R$ {total_budget - total_gasto:,.0f}")
with col4:
    util = (total_gasto / total_budget * 100) if total_budget > 0 else 0
    st.metric("Utilização", f"{util:.0f}%")

# Metrics for Obra/Esportes (separate)
col_obra, col_esportes = st.columns(2)
with col_obra:
    obra_budget = df_obra['Budget'].sum() if len(df_obra) > 0 else 0
    obra_gasto = df_obra['Gasto'].sum() if len(df_obra) > 0 else 0
    st.metric("🏗️ Obra", f"R$ {obra_gasto:,.0f}", delta=f"Budget: R$ {obra_budget:,.0f}")
with col_esportes:
    esp_budget = df_esportes['Budget'].sum() if len(df_esportes) > 0 else 0
    esp_gasto = df_esportes['Gasto'].sum() if len(df_esportes) > 0 else 0
    st.metric("🎾 Esportes", f"R$ {esp_gasto:,.0f}", delta=f"Budget: R$ {esp_budget:,.0f}")

st.markdown("---")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Budget vs Gasto Real (Variáveis)")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Budget',
        x=df_variaveis['Categoria'],
        y=df_variaveis['Budget'],
        marker_color='#3498db'
    ))
    fig.add_trace(go.Bar(
        name='Gasto',
        x=df_variaveis['Categoria'],
        y=df_variaveis['Gasto'],
        marker_color='#e74c3c'
    ))
    fig.update_layout(barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### Distribuição de Gastos (Todos)")

    # Show all categories with spending
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

# Detailed table - Variáveis
st.markdown("### Detalhamento - Variáveis")

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

df_variaveis = df_variaveis.copy()
df_variaveis['Status'] = df_variaveis.apply(get_status, axis=1)

# Display with formatting
st.dataframe(
    df_variaveis[['Categoria', 'Budget', 'Gasto', 'Disponível', 'Utilização', 'Status']].style.format({
        'Budget': 'R$ {:,.0f}',
        'Gasto': 'R$ {:,.0f}',
        'Disponível': 'R$ {:,.0f}',
        'Utilização': '{:.0%}'
    }),
    use_container_width=True,
    hide_index=True,
    height=350
)

# Obra/Esportes table (if they have data)
df_excluded = df[df['CatName'].isin(EXCLUDED_CATEGORIES)]
if len(df_excluded) > 0 and df_excluded['Gasto'].sum() > 0:
    st.markdown("### Detalhamento - Obra/Esportes")
    st.caption("💡 Rastreados separadamente do budget mensal")
    df_excluded = df_excluded.copy()
    df_excluded['Status'] = df_excluded.apply(get_status, axis=1)
    st.dataframe(
        df_excluded[['Categoria', 'Budget', 'Gasto', 'Disponível', 'Utilização', 'Status']].style.format({
            'Budget': 'R$ {:,.0f}',
            'Gasto': 'R$ {:,.0f}',
            'Disponível': 'R$ {:,.0f}',
            'Utilização': '{:.0%}'
        }),
        use_container_width=True,
        hide_index=True
    )

# Progress bars for variáveis only
st.markdown("### Progresso por Categoria (Variáveis)")

for _, row in df_variaveis.iterrows():
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.text(f"{row['Categoria']}")
    with col2:
        progress = min(row['Utilização'], 1.0)
        st.progress(progress)
    with col3:
        st.text(f"{row['Utilização']*100:.0f}%")

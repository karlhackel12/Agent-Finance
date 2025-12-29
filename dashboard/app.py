#!/usr/bin/env python3
"""
Agent Finance - Streamlit Dashboard
Interactive financial dashboard with real-time data from SQLite
"""

import streamlit as st
import sys
from pathlib import Path

# Add scripts to path for imports
SCRIPTS_PATH = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from finance_db import get_monthly_summary, get_categories, get_active_installments

# Page config
st.set_page_config(
    page_title="Agent Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Metric cards styling */
    [data-testid="stMetric"] {
        background-color: #1e3a5f;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    [data-testid="stMetric"] label {
        color: #a8c8e8 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #7bed9f !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
        fill: #7bed9f !important;
    }
    /* Negative delta */
    [data-testid="stMetric"] [data-testid="stMetricDelta"][style*="color: red"] {
        color: #ff6b6b !important;
    }
    .positive { color: #00c853; }
    .negative { color: #ff5252; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💰 Agent Finance")
st.sidebar.markdown("---")

# Month/Year selector
current_year = 2026
current_month = 1
month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

selected_month = st.sidebar.selectbox(
    "Mês",
    range(1, 13),
    index=current_month - 1,
    format_func=lambda x: month_names[x-1]
)

selected_year = st.sidebar.selectbox(
    "Ano",
    [2025, 2026, 2027],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.info(f"📅 Visualizando: {month_names[selected_month-1]} {selected_year}")

# Main content
st.title(f"📊 Dashboard - {month_names[selected_month-1]} {selected_year}")

# Load data
summary = get_monthly_summary(selected_year, selected_month)
categories = get_categories()
installments = get_active_installments()

# Calculate totals
total_budget = sum(c.get('budget_monthly', 0) for c in categories)
total_spent = summary.get('total_spent', 0)
total_installments = sum(i.get('installment_amount', 0) for i in installments)

# Constants
RECEITA = 55000
OBRA_PROJETADO = 9590 if selected_month == 1 else 0

# KPIs Row
st.markdown("### 📈 Resumo do Mês")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💵 Receita",
        value=f"R$ {RECEITA:,.0f}",
        delta="Fixa"
    )

with col2:
    delta_var = ((total_spent / total_budget) - 1) * 100 if total_budget > 0 else 0
    st.metric(
        label="🛒 Gastos Variáveis",
        value=f"R$ {total_spent:,.0f}",
        delta=f"{delta_var:+.0f}% vs budget",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="📦 Parcelamentos",
        value=f"R$ {total_installments:,.0f}",
        delta=f"{len(installments)} ativos"
    )

with col4:
    saida_total = total_spent + total_installments + OBRA_PROJETADO
    poupanca = RECEITA - saida_total
    poupanca_pct = (poupanca / RECEITA) * 100
    st.metric(
        label="💰 Poupança",
        value=f"R$ {poupanca:,.0f}",
        delta=f"{poupanca_pct:.0f}% da receita"
    )

st.markdown("---")

# Two columns layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📊 Gastos por Categoria")

    # Category data
    import plotly.express as px
    import plotly.graph_objects as go

    cat_data = []
    for cat in summary.get('categories', []):
        cat_data.append({
            'Categoria': cat['category'].title(),
            'Budget': cat['budget'],
            'Gasto': cat['total'],
            'Disponível': cat['budget'] - cat['total'],
            '%': cat['percent']
        })

    if cat_data:
        import pandas as pd
        df = pd.DataFrame(cat_data)

        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Budget',
            x=df['Categoria'],
            y=df['Budget'],
            marker_color='lightblue'
        ))
        fig.add_trace(go.Bar(
            name='Gasto Real',
            x=df['Categoria'],
            y=df['Gasto'],
            marker_color='coral'
        ))

        fig.update_layout(
            barmode='group',
            height=400,
            margin=dict(t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.dataframe(
            df.style.format({
                'Budget': 'R$ {:,.0f}',
                'Gasto': 'R$ {:,.0f}',
                'Disponível': 'R$ {:,.0f}',
                '%': '{:.0f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Sem dados de gastos para este mês")

with col_right:
    st.markdown("### 📦 Parcelamentos Ativos")

    # Top installments
    sorted_inst = sorted(installments, key=lambda x: x.get('installment_amount', 0), reverse=True)

    for inst in sorted_inst[:8]:
        desc = inst.get('description', 'N/A')[:25]
        amount = inst.get('installment_amount', 0)
        current = inst.get('current_installment', 0)
        total = inst.get('total_installments', 0)

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.text(f"{desc}")
            st.progress(current / total if total > 0 else 0)
        with col_b:
            st.text(f"R$ {amount:,.0f}")
            st.caption(f"{current}/{total}")

    if len(installments) > 8:
        st.caption(f"... e mais {len(installments) - 8} parcelamentos")

st.markdown("---")

# Footer
st.markdown("### 📋 Fluxo de Caixa")

# Simple cash flow visualization
flow_data = {
    'Tipo': ['Receita', 'Gastos Variáveis', 'Parcelamentos', 'Obra', 'Poupança'],
    'Projetado': [RECEITA, total_budget, total_installments, OBRA_PROJETADO,
                  RECEITA - total_budget - total_installments - OBRA_PROJETADO],
    'Real': [RECEITA, total_spent, 9500, 0, poupanca]  # Hardcoded real for now
}

import pandas as pd
df_flow = pd.DataFrame(flow_data)

fig2 = go.Figure()
fig2.add_trace(go.Bar(name='Projetado', x=df_flow['Tipo'], y=df_flow['Projetado'], marker_color='lightblue'))
fig2.add_trace(go.Bar(name='Real', x=df_flow['Tipo'], y=df_flow['Real'], marker_color='coral'))
fig2.update_layout(barmode='group', height=300, margin=dict(t=20, b=20))

st.plotly_chart(fig2, use_container_width=True)

# Info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Ações")
if st.sidebar.button("🔄 Atualizar Dados"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Agent Finance v1.0")
st.sidebar.caption("Powered by Streamlit + SQLite")

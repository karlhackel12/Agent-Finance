#!/usr/bin/env python3
"""
Previsões ML - Machine Learning predictions and budget optimization
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

# Add scripts to path
SCRIPTS_PATH = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

st.set_page_config(page_title="Previsões ML", page_icon="🤖", layout="wide")

st.title("🤖 Previsões e Otimização com Machine Learning")

# Try to load ML modules
try:
    from ml.spending_predictor import SpendingPredictor
    from ml.budget_optimizer import BudgetOptimizer

    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    st.error(f"Módulos ML não disponíveis: {e}")
    st.info("Execute: `pip install numpy scikit-learn`")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Previsões", "💡 Otimização", "📈 Cenários"])

with tab1:
    st.markdown("### Previsões para o Próximo Mês")

    predictor = SpendingPredictor(lookback_months=6)
    report = predictor.generate_report()

    predictions = report['predictions']
    trends = report['trends']

    # Filter out meta keys
    pred_items = [(k, v) for k, v in predictions.items() if not k.startswith('_')]

    if pred_items:
        # Create dataframe
        df_pred = pd.DataFrame([{
            'Categoria': cat.title(),
            'Previsão': pred.get('predicted', 0),
            'Confiança': pred.get('confidence', 0),
            'Mínimo': pred.get('lower_bound', 0),
            'Máximo': pred.get('upper_bound', 0),
            'Tendência': trends.get(cat, {}).get('trend', 'N/A')
        } for cat, pred in pred_items])

        # Metrics
        total_pred = df_pred['Previsão'].sum()
        avg_conf = df_pred['Confiança'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Previsto", f"R$ {total_pred:,.0f}")
        with col2:
            st.metric("Confiança Média", f"{avg_conf*100:.0f}%")
        with col3:
            increasing = sum(1 for _, t in trends.items() if t.get('trend') == 'increasing')
            st.metric("Categorias em Alta", f"{increasing}")

        st.markdown("---")

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_pred['Categoria'],
            y=df_pred['Previsão'],
            name='Previsão',
            marker_color='#3498db',
            error_y=dict(
                type='data',
                symmetric=False,
                array=df_pred['Máximo'] - df_pred['Previsão'],
                arrayminus=df_pred['Previsão'] - df_pred['Mínimo']
            )
        ))
        fig.update_layout(height=400, title="Previsões por Categoria (com intervalo de confiança)")
        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.dataframe(
            df_pred.style.format({
                'Previsão': 'R$ {:,.0f}',
                'Confiança': '{:.0%}',
                'Mínimo': 'R$ {:,.0f}',
                'Máximo': 'R$ {:,.0f}'
            }).background_gradient(subset=['Confiança'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Dados insuficientes para previsões. É necessário histórico de pelo menos 3 meses.")

    # Anomalies
    st.markdown("---")
    st.markdown("### ⚠️ Anomalias Detectadas")

    anomalies = report.get('anomalies', [])
    if anomalies:
        for a in anomalies[:5]:
            with st.expander(f"🔴 {a['description'][:40]} - R$ {a['amount']:,.0f}"):
                st.write(f"**Data:** {a['date']}")
                st.write(f"**Categoria:** {a['category'].title()}")
                st.write(f"**Motivo:** {a['reason']}")
                st.write(f"**Faixa esperada:** {a['expected_range']}")
    else:
        st.success("✅ Nenhuma anomalia detectada nos últimos 30 dias")

with tab2:
    st.markdown("### Otimização de Budget")

    optimizer = BudgetOptimizer(analysis_months=6)
    opt_report = optimizer.generate_recommendations_report()

    utilization = opt_report['utilization']
    recommendations = opt_report['recommendations']
    summary = opt_report['summary']

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Economia Potencial/Mês", f"R$ {abs(summary['net_change']):,.0f}")
    with col2:
        st.metric("Economia Anual", f"R$ {abs(summary['net_change'] * 12):,.0f}")
    with col3:
        st.metric("Recomendações", f"{len(recommendations)}")

    st.markdown("---")

    # Utilization chart
    st.markdown("### Utilização por Categoria")

    util_data = pd.DataFrame([{
        'Categoria': cat.title(),
        'Budget': stats['budget'],
        'Média Gasto': stats['avg_spending'],
        'Utilização': stats['utilization_pct'] / 100,
        'Status': stats['status']
    } for cat, stats in utilization.items()])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=util_data['Categoria'], y=util_data['Budget'], name='Budget', marker_color='lightblue'))
    fig.add_trace(go.Bar(x=util_data['Categoria'], y=util_data['Média Gasto'], name='Média', marker_color='coral'))
    fig.update_layout(barmode='group', height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    st.markdown("### 💡 Recomendações")

    if recommendations:
        for rec in recommendations:
            icon = "📈" if rec['change'] > 0 else "📉"
            priority_color = {"high": "🔴", "medium": "🟠", "low": "🟢"}[rec['priority']]

            with st.expander(f"{priority_color} {icon} {rec['category'].title()}: R$ {rec['current_budget']:,.0f} → R$ {rec['suggested_budget']:,.0f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mudança:** R$ {rec['change']:+,.0f} ({rec['change_pct']:+.0f}%)")
                    st.write(f"**Prioridade:** {rec['priority'].upper()}")
                with col2:
                    st.write(f"**Motivo:** {rec['reason']}")
                    st.write(f"**Confiança:** {rec['confidence']*100:.0f}%")
    else:
        st.info("Sem recomendações no momento. O budget parece estar bem equilibrado!")

with tab3:
    st.markdown("### Simulação de Cenários")

    scenarios = opt_report['scenarios']

    scenario_names = {
        'conservative': '🟢 Conservador (-5%)',
        'moderate': '🟡 Moderado (-15%)',
        'aggressive': '🔴 Agressivo (-30%)'
    }

    # Comparison chart
    fig = go.Figure()

    for name, scenario in scenarios.items():
        fig.add_trace(go.Bar(
            name=scenario_names[name],
            x=['Budget Atual', 'Budget Novo', 'Economia Mensal', 'Economia Anual'],
            y=[scenario['current_total'], scenario['new_total'],
               scenario['monthly_savings'], scenario['annual_savings'] / 12],
            text=[f"R$ {v:,.0f}" for v in [scenario['current_total'], scenario['new_total'],
                                           scenario['monthly_savings'], scenario['annual_savings'] / 12]],
            textposition='auto'
        ))

    fig.update_layout(barmode='group', height=400, title="Comparação de Cenários")
    st.plotly_chart(fig, use_container_width=True)

    # Scenario details
    st.markdown("---")

    for name, scenario in scenarios.items():
        with st.expander(f"{scenario_names[name]}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Budget Atual", f"R$ {scenario['current_total']:,.0f}")
            with col2:
                st.metric("Budget Novo", f"R$ {scenario['new_total']:,.0f}")
            with col3:
                st.metric("Economia Anual", f"R$ {scenario['annual_savings']:,.0f}")

            st.markdown("**Budgets por categoria:**")
            budgets_df = pd.DataFrame([
                {'Categoria': cat.title(), 'Novo Budget': val}
                for cat, val in scenario['budgets'].items()
            ])
            st.dataframe(
                budgets_df.style.format({'Novo Budget': 'R$ {:,.0f}'}),
                use_container_width=True,
                hide_index=True
            )

# Footer
st.markdown("---")
st.caption("🤖 Previsões baseadas em Machine Learning usando dados históricos")
st.caption("⚠️ Para melhores resultados, é necessário histórico de pelo menos 6 meses de transações")

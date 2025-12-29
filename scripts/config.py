#!/usr/bin/env python3
"""
Configurações centralizadas do Agent Finance
Valores de referência para orçamento e receita
"""

# Receita mensal líquida (após impostos PJ)
RECEITA_MENSAL = 55000

# Budgets por categoria (gastos variáveis)
BUDGETS = {
    'alimentacao': 4000,
    'compras': 3500,
    'casa': 2000,
    'transporte': 4200,  # Movida 3200 + Combustível 1000
    'saude': 3800,       # Plano 1300 + Tratamento 2500 (até Out/2026)
    'assinaturas': 1300,
    'lazer': 1500,
    'educacao': 400,
    'taxas': 300,
    'esportes': 1500,    # Tênis (PIX Thiago Mariotti)
}

# Total do budget de gastos variáveis
TOTAL_BUDGET_VARIAVEIS = sum(BUDGETS.values())  # 22.500

# Ícones por categoria
ICONS = {
    'alimentacao': '🍽️',
    'compras': '🛒',
    'casa': '🏠',
    'transporte': '🚗',
    'saude': '💊',
    'assinaturas': '📱',
    'lazer': '🎮',
    'educacao': '📚',
    'taxas': '🏦',
    'esportes': '🎾',
}

# Categorias essenciais (mais difícil cortar)
ESSENTIAL_CATEGORIES = {'alimentacao', 'saude', 'transporte', 'casa'}

# Gastos fixos não categorizados (débito automático)
FIXOS = {
    'financiamento_casa': 7500,
    # Movida já está em transporte
}

# Meta de poupança
META_POUPANCA_PCT = 0.27  # 27% da receita

# Após Out/2026 (término tratamento emagrecimento)
BUDGETS_POS_TRATAMENTO = BUDGETS.copy()
BUDGETS_POS_TRATAMENTO['saude'] = 1300  # Apenas plano de saúde

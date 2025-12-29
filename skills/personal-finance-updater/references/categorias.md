# Regras de Categorização - Transações Cartão de Crédito

## Padrões de Identificação por Categoria

### 🍔 Alimentação
**Keywords**: IFOOD, RAPPI, UBER EATS, RESTAURANTE, LANCHONETE, PADARIA, SUPERMERCADO, MERCADO, 
CARREFOUR, EXTRA, PÃO DE AÇUCAR, ASSAI, ATACADAO, SWIFT, MARFRIG, SEARA, FRIGORÍFICO

**Padrões Regex**:
```
/IFOOD\s*\*/i
/RAPPI\s*\*/i
/UBER\s*EATS/i
/REST(AURANTE)?/i
/PAD(ARIA)?/i
/SUPERM(ERCADO)?/i
/MERCAD(O|INH)/i
```

### 🚗 Transporte
**Keywords**: UBER, 99, CABIFY, INDRIVER, SHELL, IPIRANGA, BR DISTRIBUIDORA, PETROBRÁS, 
ESTACIONAMENTO, PARKING, ZONA AZUL, SEM PARAR, VELOE, CONECTCAR

**Padrões Regex**:
```
/UBER\s*(?!EATS)/i
/99\s*(APP|TAX)/i
/SHELL/i
/IPIRANGA/i
/ESTACIONAMENTO/i
/PARKING/i
```

### 💊 Saúde
**Keywords**: DROGARIA, FARMÁCIA, DROGA RAIA, DROGASIL, PAGUE MENOS, ULTRAFARMA, 
HOSPITAL, CLÍNICA, LABORATÓRIO, UNIMED, BRADESCO SAUDE, AMIL, CONSULTA

**Padrões Regex**:
```
/DROG(ARIA|ASIL)/i
/FARM(ÁCIA|ACIA)/i
/RAIA/i
/PAGUE\s*MENOS/i
/HOSPITAL/i
/CLÍNIC/i
/LABORAT/i
```

### 💻 Assinaturas/Software
**Keywords**: NETFLIX, SPOTIFY, AMAZON PRIME, DISNEY, HBO, APPLE, ICLOUD, GOOGLE ONE,
ADOBE, MICROSOFT, GITHUB, NOTION, SLACK, ZOOM, OPENAI, ANTHROPIC, FIGMA, MIRO

**Padrões Regex**:
```
/NETFLIX/i
/SPOTIFY/i
/AMAZON\s*PRIME/i
/DISNEY\s*\+/i
/HBO\s*MAX/i
/APPLE\.COM/i
/ICLOUD/i
/GOOGLE\s*(ONE|STORAGE)/i
/ADOBE/i
/MICROSOFT\s*365/i
/GITHUB/i
/NOTION/i
/OPENAI/i
/ANTHROPIC/i
/FIGMA/i
```

### 🛒 Compras Diversas
**Keywords**: AMAZON, MERCADO LIVRE, ALIEXPRESS, SHOPEE, MAGALU, MAGAZINE LUIZA,
CASAS BAHIA, AMERICANAS, SUBMARINO, SHEIN, NIKE, ADIDAS, ZARA, RENNER, C&A

**Padrões Regex**:
```
/AMAZON\s*(?!PRIME)/i
/MERCADO\s*LIVRE/i
/ML\s*\*/i
/ALIEXPRESS/i
/SHOPEE/i
/MAGALU/i
/MAGAZINE/i
/AMERICANAS/i
/SHEIN/i
```

### 🎮 Lazer
**Keywords**: CINEMA, CINEMARK, UCI, PLAYSTATION, XBOX, STEAM, NINTENDO, SPOTIFY,
INGRESSO, TICKET, SHOW, TEATRO, PARQUE, CLUBE

**Padrões Regex**:
```
/CINEM(A|ARK)/i
/UCI/i
/PLAYSTATION/i
/XBOX/i
/STEAM/i
/NINTENDO/i
/INGRESSO/i
/TEATRO/i
```

### 📚 Educação
**Keywords**: UDEMY, COURSERA, ALURA, ROCKETSEAT, DESCOMPLICA, HOTMART, 
LIVRARIA, SARAIVA, AMAZON KINDLE, AUDIBLE, CURSO

**Padrões Regex**:
```
/UDEMY/i
/COURSERA/i
/ALURA/i
/ROCKETSEAT/i
/HOTMART/i
/LIVRARIA/i
/KINDLE/i
/CURSO/i
```

### 🏠 Casa
**Keywords**: LEROY MERLIN, TELHANORTE, C&C, TOK STOK, ETNA, WESTWING,
MOBLY, MADEIRAMADEIRA, LIMPEZA, MANUTENCAO

**Padrões Regex**:
```
/LEROY\s*MERLIN/i
/TELHANORTE/i
/TOK\s*STOK/i
/ETNA/i
/MOBLY/i
/MADEIRA/i
```

### 💳 Taxas/Serviços
**Keywords**: IOF, ANUIDADE, TAXA, JUROS, ENCARGOS, MULTA, SEGURO CARTÃO,
PARCELAMENTO FATURA

**Padrões Regex**:
```
/IOF/i
/ANUIDADE/i
/TAXA\s*(SERV)?/i
/JUROS/i
/ENCARGOS/i
/MULTA/i
/SEGURO\s*CARTÃO/i
```

## Regras de Prioridade

1. **Assinaturas primeiro**: Se contém keyword de assinatura, categorizar como Assinatura
2. **Alimentação vs Compras**: iFood/Rappi sempre Alimentação, mesmo que pareça compra
3. **Uber específico**: "UBER EATS" = Alimentação, "UBER" sozinho = Transporte
4. **Amazon específico**: "AMAZON PRIME" = Assinatura, outros Amazon = Compras

## Identificação de Parcelamentos

**Padrões de Parcela**:
```
/(\d{1,2})\s*[\/DE]\s*(\d{1,2})/i  → Captura X/Y ou X DE Y
/PARC\s*(\d{1,2})\s*[\/]\s*(\d{1,2})/i
/PARCELA\s*(\d+)/i
```

**Exemplo de Extração**:
```
"AMAZON BR 3/10" → parcela_atual: 3, parcelas_total: 10
"MAGALU PARC 5/12" → parcela_atual: 5, parcelas_total: 12
```

## Categorização por Valor

| Faixa de Valor | Probabilidade de Categoria |
|----------------|---------------------------|
| < R$ 50 | Alimentação (60%), Transporte (25%), Outros (15%) |
| R$ 50-200 | Compras (40%), Alimentação (30%), Outros (30%) |
| R$ 200-500 | Compras (50%), Saúde (20%), Casa (20%), Outros (10%) |
| > R$ 500 | Compras (40%), Casa (30%), Saúde (20%), Outros (10%) |

## Tratamento de Casos Especiais

### Compras Internacionais
- Identificar por: USD, EUR, GBP no valor ou nome estrangeiro
- Adicionar tag: "internacional"
- Aplicar IOF: 4,38% se não incluído na descrição

### Estornos/Créditos
- Identificar por: "ESTORNO", "CREDITO", "DEVOLUCAO", valor negativo
- Categorizar igual ao original mas com sinal invertido
- Tag: "estorno"

### Transações Recorrentes
- Mesmo valor + mesmo estabelecimento + mesmo dia do mês
- Tag: "recorrente"
- Projetar automaticamente para meses futuros

# Template de Atualização - Dashboard Financeiro

## Estrutura de Dados para Sincronização

### Transação Nova (adicionar ao array)
```javascript
const novaTransacao = {
  id: `TXN_${Date.now()}`,
  data: "2025-01-15",
  estabelecimento: "ESTABELECIMENTO",
  valor: 0.00,
  categoria: "Categoria",
  tipo: "avista", // ou "parcelamento"
  parcela: null, // ou { atual: 1, total: 10 }
  mesFatura: "Janeiro/2025",
  sincronizadoEm: new Date().toISOString(),
  origem: "BB_CARTAO"
};
```

### Atualização de Parcelamento Existente
```javascript
const atualizarParcela = (parcelamentoId) => {
  // Incrementar parcela atual
  parcelamento.parcela.atual += 1;
  
  // Verificar se terminou
  if (parcelamento.parcela.atual > parcelamento.parcela.total) {
    parcelamento.status = "concluido";
    parcelamento.dataTermino = new Date().toISOString();
  }
  
  return parcelamento;
};
```

### Estrutura do Resumo Mensal
```javascript
const resumoMensal = {
  mes: "Janeiro",
  ano: 2026,
  receita: {
    salario: 55000,
    outros: 0,
    total: 55000
  },
  despesas: {
    fixos: {
      financiamento: 7500,
      moveis: 9400,
      carro: 3200,
      casa: 3000,
      subtotal: 23100
    },
    assinaturas: {
      planoSaude: 1300.17,
      softwareWork: 661.43,
      streaming: 350,
      subtotal: 2311.60
    },
    variaveis: {
      alimentacao: 0,
      transporte: 0,
      saude: 0,
      compras: 0,
      lazer: 0,
      educacao: 0,
      casa: 0,
      outros: 0,
      subtotal: 0
    },
    parcelamentos: {
      cartao: 0,
      lista: []
    },
    total: 0
  },
  saldo: 0,
  taxaPoupanca: 0,
  analise5030_20: {
    necessidades: { ideal: 27500, real: 0, percentual: 0 },
    desejos: { ideal: 16500, real: 0, percentual: 0 },
    poupanca: { ideal: 11000, real: 0, percentual: 0 }
  }
};
```

## Mapeamento de Campos BB → Dashboard

| Campo BB | Campo Dashboard | Transformação |
|----------|-----------------|---------------|
| Data Compra | data | YYYY-MM-DD |
| Descrição | estabelecimento | Uppercase, trim |
| Valor R$ | valor | parseFloat, 2 decimais |
| Parcela | parcela.atual / parcela.total | Parse X/Y |
| - | categoria | Aplicar regras categorias.md |
| - | mesFatura | Extrair do contexto |

## Validações Obrigatórias

### Antes de Adicionar
```javascript
const validarTransacao = (txn) => {
  // 1. Verificar duplicata
  const duplicata = transacoesExistentes.find(t => 
    t.data === txn.data && 
    t.estabelecimento === txn.estabelecimento && 
    t.valor === txn.valor
  );
  if (duplicata) throw new Error("Transação duplicada");
  
  // 2. Validar data (não futura)
  if (new Date(txn.data) > new Date()) {
    throw new Error("Data futura não permitida");
  }
  
  // 3. Validar valor (positivo para compras)
  if (txn.tipo !== "estorno" && txn.valor < 0) {
    throw new Error("Valor inválido");
  }
  
  return true;
};
```

### Após Adicionar
```javascript
const recalcularTotais = (mes, ano) => {
  // Somar por categoria
  // Atualizar percentuais 50/30/20
  // Recalcular saldo
  // Atualizar forecast meses futuros
};
```

## Relatório de Sincronização

```markdown
# Sincronização BB → Dashboard
**Data**: ${new Date().toLocaleDateString()}
**Período**: ${mesFatura}

## Resumo
- Transações encontradas: X
- Transações novas: Y
- Parcelamentos atualizados: Z
- Duplicatas ignoradas: W

## Transações Adicionadas
| Data | Estabelecimento | Valor | Categoria |
|------|-----------------|-------|-----------|
${transacoesNovas.map(t => `| ${t.data} | ${t.estabelecimento} | R$ ${t.valor} | ${t.categoria} |`).join('\n')}

## Parcelamentos Atualizados
| Estabelecimento | Parcela Anterior | Parcela Atual |
|-----------------|------------------|---------------|
${parcelamentosAtualizados.map(p => `| ${p.estabelecimento} | ${p.anterior} | ${p.atual} |`).join('\n')}

## Alertas
${alertas.map(a => `- ⚠️ ${a}`).join('\n')}

## Totais Atualizados
- Total gastos ${mesFatura}: R$ ${totalMes}
- Novo saldo mensal: R$ ${saldoMes}
- Taxa de poupança: ${taxaPoupanca}%
```

## Comandos de Sincronização

### Sincronização Completa
```
1. Acessar BB Internet Banking
2. Navegar: Cartões → Fatura → Fatura Atual
3. Extrair todas as transações
4. Comparar com base existente
5. Adicionar novas
6. Atualizar parcelamentos
7. Recalcular totais
8. Gerar relatório
```

### Sincronização Rápida (apenas novos)
```
1. Identificar última transação sincronizada
2. Extrair apenas transações posteriores
3. Adicionar e categorizar
4. Recalcular
```

### Sincronização de Fatura Anterior
```
1. Navegar: Cartões → Fatura → Faturas Anteriores
2. Selecionar mês desejado
3. Executar sincronização completa
```

# Casos de Teste — DebtFree AI

## TC-01 Fluxo feliz: endividado leve (Persona Carlos)
**Entrada:** renda R$ 4.000, cartão + loja  
**Esperado:**
- Situação: "Controlado" (verde)
- Prioridade: cartão antes da loja
- Análise menciona risco dos juros do cartão

---

## TC-02 Priorização de aluguel atrasado (Persona Ana)
**Entrada:** renda R$ 2.800, aluguel + luz + empréstimo + cartão  
**Esperado:**
- Situação: "Atenção" (amarelo)
- Aluguel aparece no topo da prioridade
- Plano de ação menciona risco de despejo

---

## TC-03 Superendividamento crítico + pensão (Persona João)
**Entrada:** renda R$ 1.800, 5 dívidas incluindo pensão  
**Esperado:**
- Situação: "Superendividado" (vermelho)
- Pensão aparece como #1 prioridade
- Análise menciona Lei 14.181/2021
- Análise menciona repactuação judicial

---

## TC-04 Dívida prescrita (Persona Maria)
**Entrada:** dívida com dueDate de 2018  
**Esperado:**
- isPrescribed: true
- UI exibe badge "pode estar prescrita"
- Análise menciona que dívida não pode mais ser cobrada judicialmente

---

## TC-05 Geração de carta de negociação
**Entrada:** qualquer dívida + renda + nome  
**Esperado:**
- Carta gerada em < 5 segundos
- Menciona o credor correto
- Propõe desconto (40-50% à vista) OU parcelamento
- Tom respeitoso

---

## TC-06 Edge case: renda zerada
**Entrada:** monthlyIncome = 0  
**Esperado:** Erro 400 com mensagem clara

---

## TC-07 Edge case: sem dívidas
**Entrada:** debts = []  
**Esperado:** Erro 400 com mensagem clara

---

## TC-08 Edge case: dívida maior que o patrimônio
**Entrada:** renda R$ 1.200, dívida total R$ 200.000  
**Esperado:** Situação "Superendividado", análise recomenda consultar PROCON ou advogado

---

## Roteiro da Demo (José)

**Cena 1 (30s):** Mostrar o problema — tela inicial, mencionar 70M inadimplentes  
**Cena 2 (60s):** Cadastrar a Persona João ao vivo — 5 dívidas, renda de 1 salário mínimo  
**Cena 3 (60s):** Mostrar o dashboard — situação crítica em vermelho, ranking de prioridades  
**Cena 4 (30s):** Gerar carta de negociação para o financiamento do carro  
**Cena 5 (20s):** Fechar com impacto — "isso resolve um problema de 70 milhões de pessoas"

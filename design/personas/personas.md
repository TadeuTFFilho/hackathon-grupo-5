# Personas para Demo e Testes

## Persona 1 — "Carlos, o endividado leve" 🟡
- **Renda:** R$ 4.000/mês
- **Dívidas:**
  - Cartão Nubank: R$ 3.200 (mínimo R$ 200/mês)
  - Loja C&A: R$ 800 (3x de R$ 270)
- **Total mensal em dívidas:** R$ 470 → 11,7% da renda
- **Situação:** Controlado — mas os juros do cartão vão piorar

---

## Persona 2 — "Ana, a que precisa de atenção" 🟠
- **Renda:** R$ 2.800/mês
- **Dívidas:**
  - Aluguel atrasado: R$ 4.200 (3 meses)
  - Luz/água: R$ 650
  - Empréstimo CEF: R$ 12.000 (parcela R$ 480/mês)
  - Cartão Bradesco: R$ 5.600 (mínimo R$ 300/mês)
- **Total mensal em dívidas:** R$ 1.430 → 51% da renda
- **Situação:** Atenção — risco de despejo

---

## Persona 3 — "João, o superendividado crítico" 🔴
- **Renda:** R$ 1.800/mês (salário mínimo)
- **Dívidas:**
  - Financiamento carro (garantia): R$ 18.000 (parcela R$ 650/mês)
  - Pensão alimentícia atrasada: R$ 6.000 (3 meses × R$ 800)
  - Empréstimo pessoal: R$ 9.500
  - Cartão de crédito (3 cartões): R$ 14.200
  - Luz/água: R$ 420
- **Total mensal em dívidas:** R$ 2.670 → 148% da renda
- **Situação:** Superendividado — candidato à repactuação judicial

---

## Persona 4 — "Maria, a dívida prescrita" 🟡 (edge case)
- **Renda:** R$ 3.200/mês
- **Dívidas:**
  - Dívida loja Magazine Luiza de **2018** (dueDate `2018-05-01`): R$ 2.300 (pode estar prescrita)
  - Cartão Inter: R$ 6.400 (parcela R$ 350/mês)
- **Total mensal em dívidas:** R$ 350 → 10,9% da renda
- **Situação:** Controlado — mas com dívida possivelmente prescrita
- **Objetivo:** testar flag de prescrição (dívida > 5 anos)

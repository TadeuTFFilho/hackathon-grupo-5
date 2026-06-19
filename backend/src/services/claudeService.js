const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

/**
 * Analisa a situação de superendividamento e gera recomendações
 */
async function analyzeDebts({ monthlyIncome, debts, prioritized, situation }) {
  const prompt = `Você é um assistente especializado na Lei do Superendividamento (Lei 14.181/2021) do Brasil.

Analise a situação financeira abaixo e responda em JSON com a estrutura exata indicada.

SITUAÇÃO DO USUÁRIO:
- Renda mensal: R$ ${monthlyIncome}
- Nível: ${situation.label}
- Dívidas (já ordenadas por prioridade):
${prioritized.map((d, i) => `  ${i + 1}. ${d.creditor} — R$ ${d.totalAmount} (${d.type})`).join('\n')}

Responda SOMENTE com JSON válido neste formato:
{
  "summary": "Resumo da situação em 2 frases, linguagem simples",
  "legalRights": "Explique em 3 frases os direitos pela Lei 14.181/2021 aplicáveis a este caso",
  "actionPlan": [
    { "step": 1, "action": "O que fazer primeiro", "reason": "Por quê" },
    { "step": 2, "action": "O que fazer segundo", "reason": "Por quê" },
    { "step": 3, "action": "O que fazer terceiro", "reason": "Por quê" }
  ],
  "negotiationTip": "Dica específica de negociação para a dívida mais urgente"
}`;

  const response = await client.messages.create({
    model: 'claude-opus-4-8',
    max_tokens: 1024,
    messages: [{ role: 'user', content: prompt }],
  });

  const text = response.content[0].text;
  return JSON.parse(text);
}

/**
 * Gera carta de negociação personalizada para uma dívida
 */
async function generateNegotiationLetter({ debt, monthlyIncome, userName }) {
  const prompt = `Escreva uma carta de negociação de dívida em nome de ${userName || 'o devedor'}.

Dívida: ${debt.creditor}
Valor: R$ ${debt.totalAmount}
Tipo: ${debt.type}
Renda mensal do devedor: R$ ${monthlyIncome}

Regras:
- Tom respeitoso e firme
- Mencionar a Lei 14.181/2021 se aplicável
- Propor pagamento de 40-50% do valor à vista OU parcelamento com juros máximos de 12% a.a.
- Máximo 3 parágrafos
- Linguagem simples, sem juridiquês excessivo`;

  const response = await client.messages.create({
    model: 'claude-opus-4-8',
    max_tokens: 512,
    messages: [{ role: 'user', content: prompt }],
  });

  return response.content[0].text;
}

module.exports = { analyzeDebts, generateNegotiationLetter };

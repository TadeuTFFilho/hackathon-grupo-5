const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

/**
 * System prompt compartilhado: define a persona, o tom e os limites da IA.
 * Público-alvo: pessoas endividadas e vulneráveis. Tom empático, mas firme e prático.
 */
const SYSTEM_PROMPT = `Você é o DebtFree AI, um assistente brasileiro especializado na Lei do Superendividamento (Lei 14.181/2021).

Seu público são pessoas endividadas, muitas vezes ansiosas e sem conhecimento jurídico. Por isso:
- Use linguagem simples e acolhedora, sem juridiquês. Trate a pessoa com respeito e sem julgamento.
- Seja prático e concreto: diga o que fazer, não só teoria.
- Nunca prometa resultados garantidos nem invente valores, prazos ou direitos.
- Você oferece orientação educativa, NÃO consultoria jurídica formal. Quando o caso for grave (ex.: risco de despejo, prisão por pensão, repactuação judicial), recomende procurar a Defensoria Pública, PROCON ou um advogado.`;

/**
 * Analisa a situação de superendividamento e gera recomendações
 */
async function analyzeDebts({ monthlyIncome, debts, prioritized, situation }) {
  const debtLines = prioritized
    .map((d, i) => {
      const parcela = d.monthlyPayment ? `, parcela R$ ${d.monthlyPayment}/mês` : '';
      const prescrita = d.isPrescribed ? ' — ⚠️ PODE ESTAR PRESCRITA (vencida há mais de 5 anos)' : '';
      return `  ${i + 1}. ${d.creditor} — R$ ${d.totalAmount} (${d.type})${parcela}${prescrita}`;
    })
    .join('\n');

  const hasPrescribed = prioritized.some((d) => d.isPrescribed);

  const prompt = `Analise a situação financeira abaixo e responda em JSON com a estrutura exata indicada.

SITUAÇÃO DO USUÁRIO:
- Renda mensal: R$ ${monthlyIncome}
- Nível: ${situation.label}
- Dívidas (já ordenadas por prioridade de pagamento):
${debtLines}

INSTRUÇÕES:
- A ordem das dívidas já reflete a urgência (pensão > aluguel > serviços essenciais > financiamento com garantia > empréstimo > cartão > loja). Respeite-a no plano de ação.
${hasPrescribed ? '- Há dívida possivelmente PRESCRITA: explique que dívidas vencidas há mais de 5 anos não podem mais ser cobradas judicialmente, e oriente a pessoa a não fazer acordo nem reconhecer a dívida sem antes verificar a prescrição.' : ''}
${situation.level === 'critical' ? '- O caso é crítico (superendividamento): mencione o direito à repactuação judicial e à proteção do mínimo existencial pela Lei 14.181/2021, e recomende procurar a Defensoria Pública ou PROCON.' : ''}

Responda SOMENTE com JSON válido (sem texto antes ou depois, sem markdown) neste formato:
{
  "summary": "Resumo da situação em 2 frases, linguagem simples e acolhedora",
  "legalRights": "Explique em até 3 frases os direitos pela Lei 14.181/2021 aplicáveis a este caso",
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
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: prompt }],
  });

  return parseJsonResponse(response.content[0].text);
}

/**
 * Extrai JSON da resposta do modelo de forma resiliente
 * (remove cercas markdown ou texto antes/depois, caso existam).
 */
function parseJsonResponse(text) {
  try {
    return JSON.parse(text);
  } catch {
    const match = text.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]);
    throw new Error('Resposta da IA não contém JSON válido');
  }
}

/**
 * Gera carta de negociação personalizada para uma dívida
 */
async function generateNegotiationLetter({ debt, monthlyIncome, userName }) {
  const prescrita = debt.isPrescribed
    ? '\n- A dívida pode estar PRESCRITA (vencida há mais de 5 anos): mencione, com firmeza e cordialidade, que a cobrança judicial pode não ser mais cabível e que o acordo é uma tentativa de resolução amigável.'
    : '';

  const prompt = `Escreva uma carta de negociação de dívida em nome de ${userName || 'o devedor'}.

Dívida: ${debt.creditor}
Valor: R$ ${debt.totalAmount}
Tipo: ${debt.type}
Renda mensal do devedor: R$ ${monthlyIncome}

Regras:
- Tom respeitoso e firme, em primeira pessoa
- Mencionar a Lei 14.181/2021 e o direito ao mínimo existencial, se aplicável
- Propor pagamento de 40-50% do valor à vista OU parcelamento com juros máximos de 12% a.a.
- Máximo 3 parágrafos
- Linguagem simples, sem juridiquês excessivo${prescrita}
- Terminar com um espaço para data, nome e assinatura

Escreva apenas o texto da carta, sem comentários antes ou depois.`;

  const response = await client.messages.create({
    model: 'claude-opus-4-8',
    max_tokens: 512,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: prompt }],
  });

  return response.content[0].text;
}

module.exports = { analyzeDebts, generateNegotiationLetter };

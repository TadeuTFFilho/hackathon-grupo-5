/**
 * Regras de negócio: priorização de dívidas
 * Baseado na Lei 14.181/2021 e boas práticas de educação financeira
 */

const DEBT_TYPES = {
  RENT: 'aluguel',
  UTILITIES: 'servicos_essenciais', // luz, água, gás
  SECURED_LOAN: 'financiamento_garantia', // carro, imóvel
  ALIMONY: 'pensao_alimenticia',
  BANK_LOAN: 'emprestimo_bancario',
  CREDIT_CARD: 'cartao_credito',
  STORE: 'loja_comercio',
  OTHER: 'outros',
};

const PRIORITY_ORDER = [
  DEBT_TYPES.ALIMONY,       // Risco de prisão
  DEBT_TYPES.RENT,          // Risco de despejo
  DEBT_TYPES.UTILITIES,     // Risco de corte
  DEBT_TYPES.SECURED_LOAN,  // Risco de perder o bem
  DEBT_TYPES.BANK_LOAN,     // Negativação
  DEBT_TYPES.CREDIT_CARD,   // Juros altos
  DEBT_TYPES.STORE,         // Mais flexível para negociação
  DEBT_TYPES.OTHER,
];

const MINIMUM_EXISTENTIAL_PERCENTAGE = 0.30; // 30% da renda

/**
 * Classifica a situação financeira do usuário
 */
function classifyFinancialSituation(monthlyIncome, debts) {
  const totalMonthlyDebt = debts.reduce((sum, d) => sum + (d.monthlyPayment || 0), 0);
  const debtRatio = totalMonthlyDebt / monthlyIncome;

  if (debtRatio <= 0.30) return { level: 'safe', label: 'Controlado', color: 'green' };
  if (debtRatio <= 0.50) return { level: 'warning', label: 'Atenção', color: 'yellow' };
  return { level: 'critical', label: 'Superendividado', color: 'red' };
}

/**
 * Ordena dívidas por prioridade de pagamento
 */
function prioritizeDebts(debts) {
  return [...debts].sort((a, b) => {
    const priorityA = PRIORITY_ORDER.indexOf(a.type);
    const priorityB = PRIORITY_ORDER.indexOf(b.type);
    const pa = priorityA === -1 ? 99 : priorityA;
    const pb = priorityB === -1 ? 99 : priorityB;
    return pa - pb;
  });
}

/**
 * Verifica se dívida pode estar prescrita (regra geral: 5 anos)
 */
function checkPrescription(debtDate) {
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5);
  return new Date(debtDate) < fiveYearsAgo;
}

module.exports = {
  DEBT_TYPES,
  PRIORITY_ORDER,
  MINIMUM_EXISTENTIAL_PERCENTAGE,
  classifyFinancialSituation,
  prioritizeDebts,
  checkPrescription,
};

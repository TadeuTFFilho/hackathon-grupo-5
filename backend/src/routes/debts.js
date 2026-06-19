const express = require('express');
const router = express.Router();
const { classifyFinancialSituation, prioritizeDebts, checkPrescription } = require('../rules/debtPriority');
const { analyzeDebts, generateNegotiationLetter } = require('../services/claudeService');

/**
 * POST /api/debts/analyze
 * Recebe renda + lista de dívidas, retorna análise completa
 *
 * Body: {
 *   monthlyIncome: number,
 *   debts: [{ creditor, type, totalAmount, monthlyPayment, dueDate }]
 * }
 */
router.post('/analyze', async (req, res) => {
  try {
    const { monthlyIncome, debts } = req.body;

    if (!monthlyIncome || !debts?.length) {
      return res.status(400).json({ error: 'monthlyIncome e debts são obrigatórios' });
    }

    // Verificar prescrição
    const debtsWithMeta = debts.map(d => ({
      ...d,
      isPrescribed: d.dueDate ? checkPrescription(d.dueDate) : false,
    }));

    // Classificar situação
    const situation = classifyFinancialSituation(monthlyIncome, debtsWithMeta);

    // Priorizar dívidas
    const prioritized = prioritizeDebts(debtsWithMeta);

    // Análise com IA
    const analysis = await analyzeDebts({ monthlyIncome, debts: debtsWithMeta, prioritized, situation });

    res.json({
      situation,
      prioritized,
      analysis,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao analisar dívidas', details: err.message });
  }
});

/**
 * POST /api/debts/letter
 * Gera carta de negociação para uma dívida específica
 *
 * Body: { debt: {...}, monthlyIncome: number, userName?: string }
 */
router.post('/letter', async (req, res) => {
  try {
    const { debt, monthlyIncome, userName } = req.body;

    if (!debt || !monthlyIncome) {
      return res.status(400).json({ error: 'debt e monthlyIncome são obrigatórios' });
    }

    const letter = await generateNegotiationLetter({ debt, monthlyIncome, userName });
    res.json({ letter });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao gerar carta', details: err.message });
  }
});

module.exports = router;

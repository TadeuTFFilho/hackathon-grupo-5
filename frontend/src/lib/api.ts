import axios from 'axios';
import { Debt, AnalyzeResponse } from '@/types/debt';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001',
});

export async function analyzeDebts(monthlyIncome: number, debts: Debt[]): Promise<AnalyzeResponse> {
  const { data } = await api.post('/api/debts/analyze', { monthlyIncome, debts });
  return data;
}

export async function generateLetter(debt: Debt, monthlyIncome: number, userName?: string): Promise<string> {
  const { data } = await api.post('/api/debts/letter', { debt, monthlyIncome, userName });
  return data.letter;
}

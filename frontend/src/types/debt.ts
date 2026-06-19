export type DebtType =
  | 'aluguel'
  | 'servicos_essenciais'
  | 'financiamento_garantia'
  | 'pensao_alimenticia'
  | 'emprestimo_bancario'
  | 'cartao_credito'
  | 'loja_comercio'
  | 'outros';

export interface Debt {
  id: string;
  creditor: string;
  type: DebtType;
  totalAmount: number;
  monthlyPayment?: number;
  dueDate?: string;
  isPrescribed?: boolean;
}

export type SituationLevel = 'safe' | 'warning' | 'critical';

export interface FinancialSituation {
  level: SituationLevel;
  label: string;
  color: string;
}

export interface ActionStep {
  step: number;
  action: string;
  reason: string;
}

export interface Analysis {
  summary: string;
  legalRights: string;
  actionPlan: ActionStep[];
  negotiationTip: string;
}

export interface AnalyzeResponse {
  situation: FinancialSituation;
  prioritized: Debt[];
  analysis: Analysis;
}

"""
Integração com a API da OpenAI — substitui claude_service.py para o demo.
"""
import json
import os
from openai import OpenAI


def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_debts(monthly_income: float, prioritized: list, situation: dict) -> dict:
    """Analisa a situação de superendividamento e retorna recomendações."""
    debt_list = "\n".join(
        f"  {i+1}. {d['creditor']} — R$ {d['total_amount']} ({d.get('type_label', d['type'])})"
        for i, d in enumerate(prioritized)
    )

    prompt = f"""Você é um assistente especializado na Lei do Superendividamento (Lei 14.181/2021) do Brasil.

Analise a situação financeira abaixo e responda em JSON com a estrutura exata indicada.

SITUAÇÃO DO USUÁRIO:
- Renda mensal: R$ {monthly_income}
- Nível: {situation['label']}
- Dívidas (já ordenadas por prioridade):
{debt_list}

Responda SOMENTE com JSON válido neste formato:
{{
  "summary": "Resumo da situação em 2 frases, linguagem simples",
  "legal_rights": "Explique em 3 frases os direitos pela Lei 14.181/2021 aplicáveis a este caso",
  "action_plan": [
    {{ "step": 1, "action": "O que fazer primeiro", "reason": "Por quê" }},
    {{ "step": 2, "action": "O que fazer segundo", "reason": "Por quê" }},
    {{ "step": 3, "action": "O que fazer terceiro", "reason": "Por quê" }}
  ],
  "negotiation_tip": "Dica específica de negociação para a dívida mais urgente"
}}"""

    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def generate_letter(debt: dict, monthly_income: float, user_name: str = "") -> str:
    """Gera carta de negociação personalizada para uma dívida."""
    prompt = f"""Escreva uma carta de negociação de dívida em nome de {user_name or 'o devedor'}.

Dívida: {debt['creditor']}
Valor: R$ {debt['total_amount']}
Tipo: {debt.get('type_label', debt['type'])}
Renda mensal do devedor: R$ {monthly_income}

Regras:
- Tom respeitoso e firme
- Mencionar a Lei 14.181/2021 se aplicável
- Propor pagamento de 40-50% do valor à vista OU parcelamento com juros máximos de 12% a.a.
- Máximo 3 parágrafos
- Linguagem simples, sem juridiquês excessivo
- Não inclua saudação inicial nem assinatura final (será adicionado pelo sistema)"""

    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content

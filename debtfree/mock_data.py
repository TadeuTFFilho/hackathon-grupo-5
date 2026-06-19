"""
Dados mockados para desenvolvimento do frontend.
Baseado na Persona 3 — João, o superendividado crítico.
Substituir pela resposta real da API quando Luis integrar o backend.
"""

MOCK_SESSION = {
    "user_name": "João Silva",
    "monthly_income": 1800,
    "situation": {
        "level": "critical",
        "label": "Superendividado",
        "color": "red",
    },
    "prioritized": [
        {
            "id": 0,
            "creditor": "Pensão — filha Ana",
            "type": "pensao_alimenticia",
            "type_label": "Pensão Alimentícia",
            "total_amount": 6000,
            "monthly_payment": 800,
            "is_prescribed": False,
        },
        {
            "id": 1,
            "creditor": "Financiamento CEF",
            "type": "financiamento_garantia",
            "type_label": "Financiamento (imóvel)",
            "total_amount": 18000,
            "monthly_payment": 650,
            "is_prescribed": False,
        },
        {
            "id": 2,
            "creditor": "Nubank",
            "type": "cartao_credito",
            "type_label": "Cartão de Crédito",
            "total_amount": 4200,
            "monthly_payment": 300,
            "is_prescribed": False,
        },
        {
            "id": 3,
            "creditor": "Magazine Luiza",
            "type": "loja_comercio",
            "type_label": "Loja / Comércio",
            "total_amount": 2300,
            "monthly_payment": 0,
            "is_prescribed": True,
        },
        {
            "id": 4,
            "creditor": "Empréstimo Bradesco",
            "type": "emprestimo_bancario",
            "type_label": "Empréstimo Bancário",
            "total_amount": 9500,
            "monthly_payment": 480,
            "is_prescribed": False,
        },
    ],
    "analysis": {
        "summary": (
            "Suas dívidas comprometem 148% da sua renda mensal — "
            "você está em situação de superendividamento grave. "
            "A boa notícia é que a Lei 14.181/2021 garante seu direito à repactuação."
        ),
        "legal_rights": (
            "Pela Lei 14.181/2021 você tem direito a solicitar a repactuação de todas as suas dívidas em juízo. "
            "O juiz pode reduzir juros abusivos e estender o prazo de pagamento em até 5 anos. "
            "Nenhum credor pode te cobrar valores que comprometam seu mínimo existencial (equivalente a 1 salário mínimo)."
        ),
        "action_plan": [
            {
                "step": 1,
                "action": "Regularize a pensão alimentícia",
                "reason": "É a única dívida que pode resultar em prisão. Prioridade máxima.",
            },
            {
                "step": 2,
                "action": "Entre em contato com a CEF sobre o financiamento",
                "reason": "Risco de perder o imóvel. Bancos públicos costumam ter programas de renegociação.",
            },
            {
                "step": 3,
                "action": "Procure o PROCON ou Defensoria Pública",
                "reason": "Com sua renda, você tem direito à repactuação judicial gratuita pela Lei 14.181/2021.",
            },
        ],
        "negotiation_tip": (
            "Para o Nubank e o Bradesco, ofereça 40% do valor à vista — "
            "bancos digitais costumam aceitar descontos maiores para quitação imediata. "
            "A dívida da Magazine Luiza de 2018 pode estar prescrita: confirme a data e não pague sem checar."
        ),
    },
}

"""
Dados mockados para desenvolvimento do frontend.
ATENÇÃO: dados fictícios apenas para fins de desenvolvimento.
CPFs gerados aleatoriamente e inválidos — não representam pessoas reais.
"""

# ---------------------------------------------------------------------------
# Usuários mockados — login por CPF + senha
# ---------------------------------------------------------------------------

MOCK_USERS = {
    "123.456.789-00": {
        # Credenciais
        "cpf":      "123.456.789-00",
        "password": "senha123",

        # Dados pessoais
        "name":       "João Silva",
        "email":      "joao.silva@email.com",
        "phone":      "(11) 98765-4321",
        "birthdate":  "1985-03-15",

        # Endereço (usado na carta de negociação)
        "address": {
            "street":       "Rua das Flores, 142, Apto 3",
            "neighborhood": "Vila Madalena",
            "city":         "São Paulo",
            "state":        "SP",
            "zip":          "05435-000",
        },

        # Situação financeira
        "monthly_income": 1800,
        "debt_data": None,   # preenchido após análise
    },

    "987.654.321-00": {
        "cpf":      "987.654.321-00",
        "password": "senha123",

        "name":      "Ana Pereira",
        "email":     "ana.pereira@email.com",
        "phone":     "(21) 97654-3210",
        "birthdate": "1990-07-22",

        "address": {
            "street":       "Av. Brasil, 890, Casa",
            "neighborhood": "Méier",
            "city":         "Rio de Janeiro",
            "state":        "RJ",
            "zip":          "20785-002",
        },

        "monthly_income": 2800,
        "debt_data": None,
    },
}

# ---------------------------------------------------------------------------
# Situação financeira mockada por usuário
# ---------------------------------------------------------------------------

MOCK_DEBT_DATA = {
    # João — superendividado crítico (Persona 3)
    "123.456.789-00": {
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
    },

    # Ana — em atenção (Persona 2)
    "987.654.321-00": {
        "monthly_income": 2800,
        "situation": {
            "level": "warning",
            "label": "Atenção",
            "color": "yellow",
        },
        "prioritized": [
            {
                "id": 0,
                "creditor": "Imobiliária Lar Doce",
                "type": "aluguel",
                "type_label": "Aluguel",
                "total_amount": 4200,
                "monthly_payment": 1400,
                "is_prescribed": False,
            },
            {
                "id": 1,
                "creditor": "Enel / CEDAE",
                "type": "servicos_essenciais",
                "type_label": "Luz / Água",
                "total_amount": 650,
                "monthly_payment": 0,
                "is_prescribed": False,
            },
            {
                "id": 2,
                "creditor": "CEF — Empréstimo",
                "type": "emprestimo_bancario",
                "type_label": "Empréstimo Bancário",
                "total_amount": 12000,
                "monthly_payment": 480,
                "is_prescribed": False,
            },
            {
                "id": 3,
                "creditor": "Bradesco Visa",
                "type": "cartao_credito",
                "type_label": "Cartão de Crédito",
                "total_amount": 5600,
                "monthly_payment": 300,
                "is_prescribed": False,
            },
        ],
        "analysis": {
            "summary": (
                "Suas dívidas comprometem 51% da sua renda mensal — você está em zona de atenção. "
                "O aluguel atrasado é o risco mais imediato e precisa ser resolvido primeiro."
            ),
            "legal_rights": (
                "Com 51% da renda comprometida, você está próxima do limite de superendividamento. "
                "A Lei 14.181/2021 já pode ser aplicada preventivamente para renegociar condições. "
                "O PROCON pode intermediar a negociação do aluguel sem necessidade de ação judicial."
            ),
            "action_plan": [
                {
                    "step": 1,
                    "action": "Negocie o aluguel atrasado diretamente com o proprietário",
                    "reason": "Risco de despejo. Proprietários preferem negociar a entrar com ação judicial.",
                },
                {
                    "step": 2,
                    "action": "Quite a conta de luz/água",
                    "reason": "Valores pequenos com risco de corte imediato. Priorize antes das dívidas bancárias.",
                },
                {
                    "step": 3,
                    "action": "Renegocie o cartão Bradesco com desconto",
                    "reason": "Juros de cartão são os mais altos. Ofereça 50% à vista para quitação.",
                },
            ],
            "negotiation_tip": (
                "Para o aluguel, proponha pagar 1 mês agora e parcelar os outros 2 em 3x. "
                "Coloque tudo por escrito para evitar problemas futuros."
            ),
        },
    },
}


def get_user_by_cpf(cpf: str):
    """Retorna o usuário pelo CPF (com ou sem formatação)."""
    cpf_clean = cpf.replace(".", "").replace("-", "")
    for key, user in MOCK_USERS.items():
        if key.replace(".", "").replace("-", "") == cpf_clean:
            return user
    return None

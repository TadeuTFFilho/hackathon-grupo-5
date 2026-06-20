"""
Dados mockados para desenvolvimento do frontend.
ATENÇÃO: dados fictícios apenas para fins de desenvolvimento.
CPFs gerados aleatoriamente e inválidos — não representam pessoas reais.
"""

# ---------------------------------------------------------------------------
# Usuários mockados — login por CPF + senha
# ---------------------------------------------------------------------------

MOCK_USERS = {
    # Persona 3 — João, superendividado crítico
    "123.456.789-00": {
        "cpf":      "123.456.789-00",
        "password": "senha123",
        "name":       "João Silva",
        "email":      "joao.silva@email.com",
        "phone":      "(11) 98765-4321",
        "birthdate":  "1985-03-15",
        "address": {
            "street":       "Rua das Flores, 142, Apto 3",
            "neighborhood": "Vila Madalena",
            "city":         "São Paulo",
            "state":        "SP",
            "zip":          "05435-000",
        },
        "monthly_income": 1800,
        "debt_data": None,
    },

    # Persona 2 — Ana, atenção
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

    # Persona 1 — Carlos, controlado
    "000.000.001-00": {
        "cpf":      "000.000.001-00",
        "password": "senha123",
        "name":      "Carlos Mendes",
        "email":     "carlos.mendes@email.com",
        "phone":     "(31) 99123-4567",
        "birthdate": "1992-11-08",
        "address": {
            "street":       "Rua Paraíba, 550, Apto 12",
            "neighborhood": "Funcionários",
            "city":         "Belo Horizonte",
            "state":        "MG",
            "zip":          "30130-140",
        },
        "monthly_income": 4000,
        "debt_data": None,
    },

    # Persona 4 — Maria, dívida prescrita (edge case)
    "000.000.002-00": {
        "cpf":      "000.000.002-00",
        "password": "senha123",
        "name":      "Maria Oliveira",
        "email":     "maria.oliveira@email.com",
        "phone":     "(85) 98876-5432",
        "birthdate": "1988-04-14",
        "address": {
            "street":       "Rua das Acácias, 33",
            "neighborhood": "Aldeota",
            "city":         "Fortaleza",
            "state":        "CE",
            "zip":          "60150-160",
        },
        "monthly_income": 3200,
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
        "situation": {"level": "critical", "label": "Superendividado", "color": "red"},
        "prioritized": [
            {
                "id": 0,
                "creditor": "Pensão — filha Ana",
                "type": "pensao_alimenticia",
                "type_label": "Pensão Alimentícia",
                "total_amount": 6000,
                "monthly_payment": 800,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 1,
                "creditor": "Financiamento CEF",
                "type": "financiamento_garantia",
                "type_label": "Financiamento (imóvel)",
                "total_amount": 18000,
                "monthly_payment": 650,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 2,
                "creditor": "Nubank",
                "type": "cartao_credito",
                "type_label": "Cartão de Crédito",
                "total_amount": 4200,
                "monthly_payment": 300,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 3,
                "creditor": "Magazine Luiza",
                "type": "loja_comercio",
                "type_label": "Loja / Comércio",
                "total_amount": 2300,
                "monthly_payment": 0,
                "due_date": "2018-03-01",
                "is_prescribed": True,
            },
            {
                "id": 4,
                "creditor": "Empréstimo Bradesco",
                "type": "emprestimo_bancario",
                "type_label": "Empréstimo Bancário",
                "total_amount": 9500,
                "monthly_payment": 480,
                "due_date": None,
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
                {"step": 1, "action": "Regularize a pensão alimentícia", "reason": "É a única dívida que pode resultar em prisão. Prioridade máxima."},
                {"step": 2, "action": "Entre em contato com a CEF sobre o financiamento", "reason": "Risco de perder o imóvel. Bancos públicos costumam ter programas de renegociação."},
                {"step": 3, "action": "Procure o PROCON ou Defensoria Pública", "reason": "Com sua renda, você tem direito à repactuação judicial gratuita pela Lei 14.181/2021."},
            ],
            "negotiation_tip": (
                "Para o Nubank e o Bradesco, ofereça 40% do valor à vista — "
                "bancos digitais costumam aceitar descontos maiores para quitação imediata. "
                "A dívida da Magazine Luiza de 2018 pode estar prescrita: confirme a data e não pague sem checar."
            ),
        },
    },

    # Ana — superendividada (Persona 2) — 77,8% da renda comprometida
    "987.654.321-00": {
        "monthly_income": 2800,
        "situation": {"level": "critical", "label": "Superendividado", "color": "red"},
        "prioritized": [
            {
                "id": 0,
                "creditor": "Imobiliária Lar Doce",
                "type": "aluguel",
                "type_label": "Aluguel",
                "total_amount": 4200,
                "monthly_payment": 1400,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 1,
                "creditor": "Enel / CEDAE",
                "type": "servicos_essenciais",
                "type_label": "Luz / Água",
                "total_amount": 650,
                "monthly_payment": 0,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 2,
                "creditor": "CEF — Empréstimo",
                "type": "emprestimo_bancario",
                "type_label": "Empréstimo Bancário",
                "total_amount": 12000,
                "monthly_payment": 480,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 3,
                "creditor": "Bradesco Visa",
                "type": "cartao_credito",
                "type_label": "Cartão de Crédito",
                "total_amount": 5600,
                "monthly_payment": 300,
                "due_date": None,
                "is_prescribed": False,
            },
        ],
        "analysis": {
            "summary": (
                "Suas dívidas comprometem cerca de 78% da sua renda mensal — você está em situação de superendividamento. "
                "O aluguel atrasado é o risco mais imediato e precisa ser resolvido primeiro."
            ),
            "legal_rights": (
                "Com 78% da renda comprometida, você está em situação de superendividamento pela Lei 14.181/2021. "
                "Você pode solicitar a repactuação de todas as dívidas em juízo com redução de juros e prazo estendido. "
                "O PROCON pode intermediar a negociação do aluguel sem necessidade de ação judicial."
            ),
            "action_plan": [
                {"step": 1, "action": "Negocie o aluguel atrasado diretamente com o proprietário", "reason": "Risco de despejo. Proprietários preferem negociar a entrar com ação judicial."},
                {"step": 2, "action": "Quite a conta de luz/água", "reason": "Valores pequenos com risco de corte imediato. Priorize antes das dívidas bancárias."},
                {"step": 3, "action": "Renegocie o cartão Bradesco com desconto", "reason": "Juros de cartão são os mais altos. Ofereça 50% à vista para quitação."},
            ],
            "negotiation_tip": (
                "Para o aluguel, proponha pagar 1 mês agora e parcelar os outros 2 em 3x. "
                "Coloque tudo por escrito para evitar problemas futuros."
            ),
        },
    },

    # Carlos — controlado (Persona 1)
    "000.000.001-00": {
        "monthly_income": 4000,
        "situation": {"level": "safe", "label": "Controlado", "color": "green"},
        "prioritized": [
            {
                "id": 0,
                "creditor": "Nubank",
                "type": "cartao_credito",
                "type_label": "Cartão de Crédito",
                "total_amount": 3200,
                "monthly_payment": 200,
                "due_date": None,
                "is_prescribed": False,
            },
            {
                "id": 1,
                "creditor": "C&A",
                "type": "loja_comercio",
                "type_label": "Loja / Comércio",
                "total_amount": 800,
                "monthly_payment": 270,
                "due_date": None,
                "is_prescribed": False,
            },
        ],
        "analysis": {
            "summary": (
                "Suas dívidas comprometem apenas 11,7% da sua renda — você está no controle. "
                "Atenção ao rotativo do cartão Nubank: se não quitado, os juros dobram a dívida em menos de 1 ano."
            ),
            "legal_rights": (
                "Mesmo com as dívidas sob controle, você tem direito à informação clara sobre juros e encargos. "
                "Pela Lei 14.181/2021, qualquer cláusula abusiva de juros pode ser revisada. "
                "Se o cartão praticar juros acima da média do mercado, você pode exigir revisão junto ao banco ou PROCON."
            ),
            "action_plan": [
                {"step": 1, "action": "Quite o cartão Nubank o quanto antes", "reason": "O rotativo do cartão cobra em média 10%/mês — quitar agora evita que R$ 3.200 virem R$ 6.400 em 8 meses."},
                {"step": 2, "action": "Termine de pagar a C&A em dia", "reason": "Com apenas 3 parcelas de R$ 270, vale manter o pagamento e fechar logo."},
                {"step": 3, "action": "Monte uma reserva de emergência", "reason": "Com 88% da renda livre, você tem condição de guardar R$ 400–600/mês e evitar novas dívidas."},
            ],
            "negotiation_tip": (
                "Ligue para o Nubank e ofereça quitar 80% do saldo à vista — "
                "mesmo clientes sem atraso conseguem desconto ao solicitar quitação antecipada pelo app."
            ),
        },
    },

    # Maria — dívida prescrita (Persona 4)
    "000.000.002-00": {
        "monthly_income": 3200,
        "situation": {"level": "safe", "label": "Controlado", "color": "green"},
        "prioritized": [
            {
                "id": 0,
                "creditor": "Magazine Luiza",
                "type": "loja_comercio",
                "type_label": "Loja / Comércio",
                "total_amount": 2300,
                "monthly_payment": 0,
                "due_date": "2018-05-01",
                "is_prescribed": True,
            },
            {
                "id": 1,
                "creditor": "Banco Inter",
                "type": "cartao_credito",
                "type_label": "Cartão de Crédito",
                "total_amount": 6400,
                "monthly_payment": 350,
                "due_date": None,
                "is_prescribed": False,
            },
        ],
        "analysis": {
            "summary": (
                "Suas dívidas comprometem 10,9% da renda — você está no controle. "
                "Atenção: a dívida da Magazine Luiza pode estar prescrita. Não pague sem verificar antes."
            ),
            "legal_rights": (
                "A dívida da Magazine Luiza venceu em 2018 — já se passaram mais de 5 anos. "
                "Dívidas prescritas não podem mais ser cobradas judicialmente pela Lei 10.406/2002. "
                "Pagar ou reconhecer a dívida pode reiniciar o prazo prescricional. Consulte a Defensoria antes de qualquer acordo."
            ),
            "action_plan": [
                {"step": 1, "action": "Verifique a prescrição da dívida Magazine Luiza", "reason": "Antes de pagar, confirme com a Defensoria Pública ou PROCON se a dívida está realmente prescrita."},
                {"step": 2, "action": "Não reconheça a dívida prescrita por escrito ou verbalmente", "reason": "Qualquer reconhecimento pode reiniciar o prazo de 5 anos e tornar a dívida exigível novamente."},
                {"step": 3, "action": "Continue pagando o cartão Inter normalmente", "reason": "Com R$ 350/mês, você quita em cerca de 22 meses. Evite atrasos para não cair no rotativo."},
            ],
            "negotiation_tip": (
                "Se a Magazine Luiza insistir na cobrança após confirmada a prescrição, "
                "registre uma reclamação formal no PROCON — a cobrança de dívida prescrita é prática abusiva e pode gerar indenização."
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

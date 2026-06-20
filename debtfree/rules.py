"""
Regras de negócio: priorização de dívidas.
Baseado na Lei 14.181/2021 e boas práticas de educação financeira.
"""
from datetime import date, timedelta

PRIORITY_ORDER = [
    "pensao_alimenticia",
    "aluguel",
    "servicos_essenciais",
    "financiamento_garantia",
    "emprestimo_bancario",
    "cartao_credito",
    "loja_comercio",
    "outros",
]

DEBT_TYPE_LABELS = {
    "pensao_alimenticia":   "Pensão Alimentícia",
    "aluguel":              "Aluguel",
    "servicos_essenciais":  "Luz / Água / Gás",
    "financiamento_garantia": "Financiamento (carro/imóvel)",
    "emprestimo_bancario":  "Empréstimo Bancário",
    "cartao_credito":       "Cartão de Crédito",
    "loja_comercio":        "Loja / Comércio",
    "outros":               "Outros",
}


def classify_situation(monthly_income: float, debts: list[dict]) -> dict:
    """Classifica a situação financeira do usuário."""
    if not monthly_income:
        return {"level": "critical", "label": "Superendividado", "color": "red"}

    total_monthly = sum(d.get("monthly_payment", 0) or 0 for d in debts)
    ratio = total_monthly / monthly_income

    if ratio <= 0.30:
        return {"level": "safe",     "label": "Controlado",     "color": "green"}
    elif ratio <= 0.50:
        return {"level": "warning",  "label": "Atenção",        "color": "yellow"}
    else:
        return {"level": "critical", "label": "Superendividado", "color": "red"}


def prioritize(debts: list[dict]) -> list[dict]:
    """Ordena dívidas por urgência de pagamento."""
    def priority_key(debt):
        debt_type = debt.get("type", "outros")
        try:
            return PRIORITY_ORDER.index(debt_type)
        except ValueError:
            return 99

    return sorted(debts, key=priority_key)


def check_prescribed(due_date_str: str | None) -> bool:
    """Verifica se uma dívida pode estar prescrita (regra geral: 5 anos)."""
    if not due_date_str:
        return False
    try:
        due_date = date.fromisoformat(due_date_str)
        five_years_ago = date.today() - timedelta(days=5 * 365)
        return due_date < five_years_ago
    except ValueError:
        return False


URGENT_TYPES = {"pensao_alimenticia", "aluguel", "servicos_essenciais"}


def calculate_score(monthly_income: float, debts: list[dict]) -> dict:
    """Calcula score de saúde financeira (0-100)."""
    if not monthly_income:
        return {"score": 5, "label": "Emergência", "color": "red"}

    # Sem dívidas = score perfeito
    if not debts:
        return {"score": 100, "label": "Excelente", "color": "green"}

    total_monthly = sum(d.get("monthly_payment", 0) or 0 for d in debts)
    ratio = total_monthly / monthly_income * 100

    if ratio <= 10:
        base = 95
    elif ratio <= 20:
        base = 85
    elif ratio <= 30:
        base = 75
    elif ratio <= 40:
        base = 60
    elif ratio <= 50:
        base = 45
    elif ratio <= 75:
        base = 25
    else:
        base = 10

    # Descontos
    debt_penalty = min(len(debts) * 2, 12)
    urgent_penalty = sum(
        5 for d in debts
        if d.get("type") in URGENT_TYPES and (d.get("monthly_payment") or 0) > 0
    )

    score = max(5, min(100, base - debt_penalty - urgent_penalty))

    if score >= 80:
        label, color = "Excelente", "green"
    elif score >= 60:
        label, color = "Bom", "blue"
    elif score >= 40:
        label, color = "Atenção", "yellow"
    elif score >= 20:
        label, color = "Crítico", "orange"
    else:
        label, color = "Emergência", "red"

    return {"score": score, "label": label, "color": color}


def enrich(debts: list[dict]) -> list[dict]:
    """Adiciona metadados calculados em cada dívida."""
    return [
        {
            **d,
            "is_prescribed": check_prescribed(d.get("due_date")),
            "type_label": DEBT_TYPE_LABELS.get(d.get("type", "outros"), "Outros"),
        }
        for d in debts
    ]

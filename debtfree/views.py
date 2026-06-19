import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .rules import enrich, prioritize, classify_situation
from .claude_service import analyze_debts, generate_letter
from .mock_data import MOCK_USERS, MOCK_DEBT_DATA, get_user_by_cpf
from .auth import login_required
from .financial_service import (
    get_market_rates, financial_summary, amortization_tip, prescription_detail
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_view(request):
    if request.session.get("user"):
        return redirect("dashboard")

    if request.method == "POST":
        cpf      = request.POST.get("cpf", "").strip()
        password = request.POST.get("password", "").strip()

        user = get_user_by_cpf(cpf)
        if user and user["password"] == password:
            # Salva dados não-sensíveis na sessão (sem senha)
            request.session["user"] = {
                "cpf":       user["cpf"],
                "name":      user["name"],
                "email":     user["email"],
                "phone":     user["phone"],
                "birthdate": user["birthdate"],
                "address":   user["address"],
            }
            return redirect("dashboard")

        return render(request, "debtfree/login.html", {"error": "CPF ou senha incorretos."})

    return render(request, "debtfree/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


# ---------------------------------------------------------------------------
# Bia — fluxo de entrada
# ---------------------------------------------------------------------------

def home(request):
    return render(request, "debtfree/home.html")


@login_required
def onboarding(request):
    user = request.session["user"]
    return render(request, "debtfree/onboarding.html", {"user": user})


@login_required
@require_http_methods(["POST"])
def analyze(request):
    """
    Recebe o formulário, salva na sessão e redireciona ao dashboard.
    TODO (Luis): substituir mock por chamada real à IA.
    """
    try:
        monthly_income = float(request.POST.get("monthly_income", 0))

        creditors        = request.POST.getlist("creditor")
        types            = request.POST.getlist("type")
        total_amounts    = request.POST.getlist("total_amount")
        monthly_payments = request.POST.getlist("monthly_payment")
        due_dates        = request.POST.getlist("due_date")

        debts = [
            {
                "creditor":        creditors[i],
                "type":            types[i] if i < len(types) else "outros",
                "total_amount":    float(total_amounts[i]) if i < len(total_amounts) else 0,
                "monthly_payment": float(monthly_payments[i]) if monthly_payments[i] else 0,
                "due_date":        due_dates[i] if i < len(due_dates) else None,
            }
            for i, creditor in enumerate(creditors)
            if creditor
        ]

        if not monthly_income or not debts:
            return render(request, "debtfree/onboarding.html",
                          {"error": "Preencha a renda e ao menos uma dívida.", "user": request.session["user"]})

        enriched    = enrich(debts)
        situation   = classify_situation(monthly_income, enriched)
        prioritized = prioritize(enriched)
        for i, d in enumerate(prioritized):
            d["id"] = i

        request.session["debt_data"] = {
            "monthly_income": monthly_income,
            "situation":      situation,
            "prioritized":    prioritized,
            "analysis":       None,  # Luis preenche aqui
        }

        return redirect("dashboard")

    except Exception as e:
        return render(request, "debtfree/onboarding.html",
                      {"error": str(e), "user": request.session.get("user")})


# ---------------------------------------------------------------------------
# Tadeu — resultados e ação
# ---------------------------------------------------------------------------

def _get_debt_data(request):
    """
    Prioridade: dados da sessão → mock do usuário logado → mock padrão do João.
    Remove quando Luis integrar a IA.
    """
    if request.session.get("debt_data"):
        return request.session["debt_data"]

    user = request.session.get("user")
    if user:
        cpf = user.get("cpf")
        if cpf in MOCK_DEBT_DATA:
            return MOCK_DEBT_DATA[cpf]

    # Fallback: João (demo sem login)
    return MOCK_DEBT_DATA["123.456.789-00"]


@login_required
def dashboard(request):
    user        = request.session["user"]
    debt_data   = _get_debt_data(request)
    market      = get_market_rates()
    prioritized = debt_data["prioritized"]
    income      = debt_data["monthly_income"]

    # Enriquece cada dívida com dica de amortização e detalhe de prescrição
    for debt in prioritized:
        debt["amortization"] = amortization_tip(debt, market)
        debt["prescription"] = prescription_detail(debt.get("due_date"))

    summary = financial_summary(income, prioritized, market)

    # Distribuição para o gráfico donut (labels + valores)
    chart_labels = [d["creditor"] for d in prioritized]
    chart_values = [d["total_amount"] for d in prioritized]

    return render(request, "debtfree/dashboard.html", {
        **debt_data,
        "user":          user,
        "market":        market,
        "summary":       summary,
        "chart_labels":  json.dumps(chart_labels),
        "chart_values":  json.dumps(chart_values),
    })


@login_required
def legal(request):
    user      = request.session["user"]
    debt_data = _get_debt_data(request)
    prescribed = [d for d in debt_data["prioritized"] if d.get("is_prescribed")]
    return render(request, "debtfree/legal.html", {**debt_data, "user": user, "prescribed_debts": prescribed})


@login_required
def letter(request, debt_index):
    user      = request.session["user"]
    debt_data = _get_debt_data(request)

    try:
        debt = debt_data["prioritized"][debt_index]
    except IndexError:
        return redirect("dashboard")

    address = user.get("address", {})
    address_str = (
        f"{address.get('street', '')}, {address.get('neighborhood', '')} — "
        f"{address.get('city', '')}/{address.get('state', '')} — CEP {address.get('zip', '')}"
    )

    # TODO (Luis): substituir pelo texto gerado pela IA
    mock_letter = f"""{address.get('city', 'São Paulo')}, {_today_br()}

{debt['creditor']}
A/C Departamento de Cobranças

Assunto: Proposta de Renegociação de Dívida

Prezados Senhores,

Eu, {user['name']}, CPF {user['cpf']}, residente à {address_str}, venho por meio desta carta manifestar meu interesse em regularizar a dívida referente ao contrato com {debt['creditor']}, no valor de R$ {debt['total_amount']:.2f}.

Em razão das dificuldades financeiras que enfrento atualmente, com renda mensal de R$ {debt_data['monthly_income']:.2f}, e amparado(a) pela Lei 14.181/2021 (Lei do Superendividamento), solicito a análise da seguinte proposta: quitação com desconto de 50% sobre o valor total (R$ {debt['total_amount'] * 0.5:.2f}), ou alternativamente o parcelamento do saldo devedor em até 24 vezes com juros máximos de 12% ao ano.

Estou disponível para negociação pelo telefone {user['phone']} ou e-mail {user['email']}. Aguardo retorno para formalização do acordo.

Atenciosamente,
{user['name']}
CPF: {user['cpf']}
Telefone: {user['phone']}"""

    return render(request, "debtfree/letter.html", {
        "debt":           debt,
        "letter":         mock_letter,
        "user":           user,
        "monthly_income": debt_data["monthly_income"],
    })


def _today_br():
    from datetime import date
    months = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    d = date.today()
    return f"{d.day} de {months[d.month]} de {d.year}"

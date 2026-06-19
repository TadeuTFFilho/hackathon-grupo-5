import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .rules import enrich, prioritize, classify_situation
from .claude_service import analyze_debts, generate_letter
from .mock_data import MOCK_SESSION

# ---------------------------------------------------------------------------
# Bia — fluxo de entrada
# ---------------------------------------------------------------------------

def home(request):
    return render(request, "debtfree/home.html")


def onboarding(request):
    return render(request, "debtfree/onboarding.html")


@require_http_methods(["POST"])
def analyze(request):
    """
    Recebe o formulário de dívidas, salva na sessão e redireciona ao dashboard.
    TODO (Luis): substituir mock por chamada real à IA.
    """
    try:
        monthly_income = float(request.POST.get("monthly_income", 0))
        user_name = request.POST.get("user_name", "")

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
                          {"error": "Preencha a renda e ao menos uma dívida."})

        enriched   = enrich(debts)
        situation  = classify_situation(monthly_income, enriched)
        prioritized = prioritize(enriched)

        # Adiciona id para referência nas URLs
        for i, d in enumerate(prioritized):
            d["id"] = i

        # Salva na sessão para as próximas telas
        request.session["debt_data"] = {
            "user_name":      user_name,
            "monthly_income": monthly_income,
            "situation":      situation,
            "prioritized":    prioritized,
            "analysis":       None,   # preenchido após chamada à IA (Luis)
        }

        return redirect("dashboard")

    except Exception as e:
        return render(request, "debtfree/onboarding.html", {"error": str(e)})


# ---------------------------------------------------------------------------
# Tadeu — resultados e ação
# ---------------------------------------------------------------------------

def _get_session_data(request):
    """
    Retorna os dados da sessão ou o mock enquanto a integração não está pronta.
    Quando Luis integrar a IA, remover o fallback para MOCK_SESSION.
    """
    return request.session.get("debt_data") or MOCK_SESSION


def dashboard(request):
    """Ranking de prioridades + resumo + plano de ação."""
    data = _get_session_data(request)
    return render(request, "debtfree/dashboard.html", data)


def legal(request):
    """Explicação da situação jurídica e direitos pela Lei 14.181/2021."""
    data = _get_session_data(request)
    prescribed = [d for d in data["prioritized"] if d.get("is_prescribed")]
    return render(request, "debtfree/legal.html", {**data, "prescribed_debts": prescribed})


def letter(request, debt_index):
    """Exibe a carta de negociação para a dívida selecionada."""
    data = _get_session_data(request)

    try:
        debt = data["prioritized"][debt_index]
    except IndexError:
        return redirect("dashboard")

    # TODO (Luis): substituir pelo texto gerado pela IA
    mock_letter = f"""Prezados Senhores,

Eu, {data['user_name'] or 'o(a) devedor(a)'}, portador(a) de documentos a apresentar, venho por meio desta carta manifestar meu interesse em regularizar a dívida referente ao contrato com {debt['creditor']}, no valor original de R$ {debt['total_amount']}.

Em razão das dificuldades financeiras que enfrento atualmente, com renda mensal de R$ {data['monthly_income']}, e amparado(a) pela Lei 14.181/2021 (Lei do Superendividamento), solicito a análise de proposta de quitação com desconto de 50% sobre o valor total (R$ {debt['total_amount'] * 0.5:.2f}), ou alternativamente o parcelamento do saldo devedor com juros máximos de 12% ao ano.

Estou disponível para negociação e aguardo retorno para formalização do acordo. Agradeço a atenção e coloco-me à disposição para quaisquer esclarecimentos.

Atenciosamente,
{data['user_name'] or 'Devedor(a)'}"""

    return render(request, "debtfree/letter.html", {
        "debt":          debt,
        "letter":        mock_letter,
        "user_name":     data["user_name"],
        "monthly_income": data["monthly_income"],
    })

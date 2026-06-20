import json
import os
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.conf import settings

from .rules import enrich, prioritize, classify_situation, calculate_score
from .claude_service import analyze_debts, generate_letter
from .mock_data import MOCK_USERS, MOCK_DEBT_DATA, get_user_by_cpf
from .auth import login_required
from .financial_service import (
    get_market_rates, financial_summary, amortization_tip, prescription_detail
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'debtfree', 'static', 'debtfree', 'sw.js')
    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')


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

        from django.contrib import messages
        n = len(debts)
        messages.success(
            request,
            f"{n} dívida{'s' if n > 1 else ''} adicionada{'s' if n > 1 else ''} com sucesso."
        )
        return redirect("dashboard")

    except Exception as e:
        return render(request, "debtfree/onboarding.html",
                      {"error": str(e), "user": request.session.get("user")})


# ---------------------------------------------------------------------------
# Renda
# ---------------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def renda(request):
    user = request.session["user"]
    debt_data = _get_debt_data(request)
    form_data = {"monthly_income": debt_data.get("monthly_income", "")}

    if request.method == "POST":
        try:
            monthly_income = float(request.POST.get("monthly_income", 0))
            if monthly_income <= 0:
                raise ValueError("Renda deve ser maior que zero.")

            income_source = request.POST.get("income_source", "")
            other_income = float(request.POST.get("other_income") or 0)

            # Atualiza na sessão
            if request.session.get("debt_data"):
                request.session["debt_data"]["monthly_income"] = monthly_income + other_income
                request.session.modified = True

            from django.contrib import messages
            messages.success(request, "Renda atualizada com sucesso!")
            return redirect("renda")

        except ValueError as e:
            from django.contrib import messages
            messages.error(request, str(e))
            form_data = {
                "monthly_income": request.POST.get("monthly_income", ""),
                "income_source":  request.POST.get("income_source", ""),
                "other_income":   request.POST.get("other_income", ""),
            }

    return render(request, "debtfree/renda.html", {"user": user, "form_data": form_data})


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

    # Score de saúde financeira
    score = calculate_score(income, prioritized)

    # Progresso de dívidas (Feature 6)
    total_debts = len(prioritized)
    paid_debts = sum(1 for d in prioritized if d.get("debt_status") == "paga")
    in_negotiation = sum(1 for d in prioritized if d.get("debt_status") == "em_negociacao")
    progress_pct = int(paid_debts / total_debts * 100) if total_debts else 0

    # Distribuição para o gráfico donut (labels + valores)
    chart_labels = [d["creditor"] for d in prioritized]
    chart_values = [d["total_amount"] for d in prioritized]

    # JSON completo das dívidas para o simulador (Feature 2)
    prioritized_json = json.dumps(prioritized)

    return render(request, "debtfree/dashboard.html", {
        **debt_data,
        "user":             user,
        "market":           market,
        "summary":          summary,
        "score":            score,
        "total_debts":      total_debts,
        "paid_debts":       paid_debts,
        "in_negotiation":   in_negotiation,
        "progress_pct":     progress_pct,
        "chart_labels":     json.dumps(chart_labels),
        "chart_values":     json.dumps(chart_values),
        "prioritized_json": prioritized_json,
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


@login_required
def perfil(request):
    user = request.session["user"]
    debt_data = _get_debt_data(request)
    return render(request, "debtfree/perfil.html", {
        "user": user,
        "monthly_income": debt_data.get("monthly_income"),
    })


@login_required
def procon(request):
    from .procon_data import PROCON_BY_STATE
    user = request.session["user"]
    state = user.get("address", {}).get("state", "SP")
    info = PROCON_BY_STATE.get(state, PROCON_BY_STATE.get("DEFAULT"))
    return render(request, "debtfree/procon.html", {
        "user":      user,
        "state":     state,
        "procon":    info.get("procon"),
        "defensoria": info.get("defensoria"),
    })


@login_required
def letter_pdf(request, debt_index):
    """Gera PDF da carta de negociação com xhtml2pdf."""
    from xhtml2pdf import pisa
    import io
    user = request.session["user"]
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

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{ font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.6; margin: 2cm; color: #1a1a1a; }}
    .header {{ border-bottom: 2px solid #028090; padding-bottom: 12px; margin-bottom: 24px; }}
    .header h1 {{ font-size: 14pt; color: #028090; margin: 0; }}
    .header p {{ font-size: 10pt; color: #666; margin: 4px 0 0; }}
    .letter {{ white-space: pre-line; }}
    .footer {{ margin-top: 40px; border-top: 1px solid #ccc; padding-top: 12px; font-size: 9pt; color: #888; }}
</style>
</head>
<body>
<div class="header">
    <h1>Carta de Negociação — Conta Limpa</h1>
    <p>Gerada com base na Lei 14.181/2021 · Caráter informativo, não constitui aconselhamento jurídico</p>
</div>
<div class="letter">{mock_letter}</div>
<div class="footer">Gerado pelo Conta Limpa · Para situações complexas, consulte a Defensoria Pública ou o PROCON.</div>
</body>
</html>"""

    buffer = io.BytesIO()
    pisa.CreatePDF(html_content, dest=buffer)
    buffer.seek(0)

    filename = f"carta-negociacao-{debt['creditor'].lower().replace(' ', '-')}.pdf"
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_http_methods(["POST"])
def mark_debt(request, debt_index):
    """Marca status de uma dívida na sessão."""
    new_status = request.POST.get("status", "")  # "", "em_negociacao", "paga"

    if not request.session.get("debt_data"):
        debt_data = _get_debt_data(request)
        request.session["debt_data"] = {
            "monthly_income": debt_data["monthly_income"],
            "situation":      debt_data["situation"],
            "prioritized":    list(debt_data["prioritized"]),
            "analysis":       debt_data.get("analysis"),
        }

    try:
        request.session["debt_data"]["prioritized"][debt_index]["debt_status"] = new_status
        request.session.modified = True
    except (IndexError, KeyError):
        pass

    return redirect("dashboard")


def _today_br():
    from datetime import date
    months = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    d = date.today()
    return f"{d.day} de {months[d.month]} de {d.year}"

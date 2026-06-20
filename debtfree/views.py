import json
import os
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings

from .rules import enrich, prioritize, classify_situation, calculate_score
from .openai_service import analyze_debts, generate_letter
from .mock_data import MOCK_USERS, MOCK_DEBT_DATA, get_user_by_cpf
from .auth import login_required
from .auth_utils import hash_password, check_password as check_pw
from .financial_service import (
    get_market_rates, financial_summary, amortization_tip, prescription_detail
)

BRAZIL_STATES = [
    ("AC","Acre"),("AL","Alagoas"),("AP","Amapá"),("AM","Amazonas"),
    ("BA","Bahia"),("CE","Ceará"),("DF","Distrito Federal"),("ES","Espírito Santo"),
    ("GO","Goiás"),("MA","Maranhão"),("MT","Mato Grosso"),("MS","Mato Grosso do Sul"),
    ("MG","Minas Gerais"),("PA","Pará"),("PB","Paraíba"),("PR","Paraná"),
    ("PE","Pernambuco"),("PI","Piauí"),("RJ","Rio de Janeiro"),("RN","Rio Grande do Norte"),
    ("RS","Rio Grande do Sul"),("RO","Rondônia"),("RR","Roraima"),("SC","Santa Catarina"),
    ("SP","São Paulo"),("SE","Sergipe"),("TO","Tocantins"),
]

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

        # 1. Verifica mock users
        mock_user = get_user_by_cpf(cpf)
        if mock_user and mock_user["password"] == password:
            request.session["user"] = {
                "cpf":        mock_user["cpf"],
                "name":       mock_user["name"],
                "email":      mock_user["email"],
                "phone":      mock_user["phone"],
                "birthdate":  mock_user["birthdate"],
                "address":    mock_user["address"],
                "is_db_user": False,
            }
            return redirect("dashboard")

        # 2. Verifica usuários do banco
        try:
            from .models import UserProfile
            db_user = UserProfile.objects.get(cpf=cpf)
            if check_pw(password, db_user.password_hash):
                request.session["user"] = db_user.to_session_dict()
                return redirect("dashboard")
        except Exception:
            pass

        return render(request, "debtfree/login.html", {"error": "CPF ou senha incorretos."})

    return render(request, "debtfree/login.html")


def register(request):
    if request.session.get("user"):
        return redirect("dashboard")

    error = None
    form  = {}

    if request.method == "POST":
        form     = request.POST
        cpf      = request.POST.get("cpf", "").strip()
        name     = request.POST.get("name", "").strip()
        password = request.POST.get("password", "").strip()
        confirm  = request.POST.get("password2", "").strip()
        income   = request.POST.get("monthly_income", "").strip()
        state    = request.POST.get("state", "SP")
        city     = request.POST.get("city", "").strip()
        email    = request.POST.get("email", "").strip()
        phone    = request.POST.get("phone", "").strip()

        if not cpf or not name or not password:
            error = "CPF, nome e senha são obrigatórios."
        elif len(password) < 6:
            error = "A senha deve ter no mínimo 6 caracteres."
        elif password != confirm:
            error = "As senhas não coincidem."
        elif not income or float(income) <= 0:
            error = "Informe sua renda mensal."
        elif not state or not city:
            error = "Informe seu estado e cidade."
        elif get_user_by_cpf(cpf):
            error = "Este CPF já está cadastrado."
        else:
            try:
                from .models import UserProfile
                if UserProfile.objects.filter(cpf=cpf).exists():
                    error = "Este CPF já está cadastrado."
                else:
                    db_user = UserProfile.objects.create(
                        cpf           = cpf,
                        name          = name,
                        email         = email,
                        phone         = phone,
                        monthly_income= float(income),
                        state         = state,
                        city          = city,
                        password_hash = hash_password(password),
                    )
                    request.session["user"] = db_user.to_session_dict()
                    return redirect("dashboard")
            except Exception as e:
                error = f"Erro ao criar conta: {e}"

    return render(request, "debtfree/register.html", {
        "form":   form,
        "error":  error,
        "states": BRAZIL_STATES,
    })


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

        # Análise de IA — tenta chamar OpenAI, fallback silencioso
        try:
            analysis = analyze_debts(monthly_income, prioritized, situation)
        except Exception:
            analysis = None

        request.session["debt_data"] = {
            "monthly_income": monthly_income,
            "situation":      situation,
            "prioritized":    prioritized,
            "analysis":       analysis,
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
    Prioridade:
    1. session["debt_data"] (mock em edição / session-based)
    2. DB (usuário real)
    3. MOCK_DEBT_DATA por CPF
    4. Fallback João
    """
    if request.session.get("debt_data"):
        return request.session["debt_data"]

    user = request.session.get("user")
    if user:
        if user.get("is_db_user"):
            return _get_db_debt_data(user)
        cpf = user.get("cpf")
        if cpf in MOCK_DEBT_DATA:
            return MOCK_DEBT_DATA[cpf]

    return MOCK_DEBT_DATA["123.456.789-00"]


def _get_db_debt_data(user_session):
    """Monta debt_data a partir do banco para usuários reais."""
    try:
        from .models import UserProfile
        db_user    = UserProfile.objects.get(pk=user_session["db_pk"])
        debts_qs   = db_user.debts.all()
        debts      = [d.to_dict(i) for i, d in enumerate(debts_qs)]
        enriched   = enrich(debts)
        prioritized = prioritize(enriched)
        for i, d in enumerate(prioritized):
            d["id"] = i
        income = db_user.monthly_income
        return {
            "monthly_income": income,
            "situation":      classify_situation(income, prioritized),
            "prioritized":    prioritized,
            "analysis":       None,
        }
    except Exception:
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
def debts_list(request):
    """Página dedicada de listagem e gestão de dívidas (aba 'Dívidas')."""
    user      = request.session["user"]
    debt_data = _get_debt_data(request)
    market    = get_market_rates()
    prioritized = debt_data["prioritized"]
    income      = debt_data["monthly_income"]
    summary     = financial_summary(income, prioritized, market)
    return render(request, "debtfree/debts_list.html", {
        **debt_data,
        "user":    user,
        "summary": summary,
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

    # Gera corpo da carta via IA
    try:
        ai_body = generate_letter(
            debt          = debt,
            monthly_income= debt_data["monthly_income"],
            user_name     = user["name"],
        )
    except Exception:
        ai_body = (
            f"Eu, {user['name']}, CPF {user['cpf']}, venho por meio desta carta manifestar "
            f"meu interesse em regularizar a dívida com {debt['creditor']}, no valor de "
            f"R$ {debt['total_amount']:.2f}, e solicito proposta de renegociação nos termos "
            f"da Lei 14.181/2021."
        )

    letter_text = f"""{address.get('city', 'São Paulo')}, {_today_br()}

{debt['creditor']}
A/C Departamento de Cobranças

Assunto: Proposta de Renegociação de Dívida

{ai_body}

Atenciosamente,
{user['name']}
CPF: {user['cpf']}
Telefone: {user['phone']}"""

    return render(request, "debtfree/letter.html", {
        "debt":           debt,
        "letter":         letter_text,
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
@require_http_methods(["GET", "POST"])
def perfil_edit(request):
    user  = request.session["user"]
    is_db = user.get("is_db_user", False)
    error = None
    form  = {}

    if request.method == "POST":
        form         = request.POST
        name         = request.POST.get("name", "").strip()
        email        = request.POST.get("email", "").strip()
        phone        = request.POST.get("phone", "").strip()
        state        = request.POST.get("state", "").strip()
        city         = request.POST.get("city", "").strip()
        neighborhood = request.POST.get("neighborhood", "").strip()
        street       = request.POST.get("street", "").strip()
        zip_code     = request.POST.get("zip_code", "").strip()

        if not state or not city:
            error = "Estado e cidade são obrigatórios."
        else:
            if is_db:
                try:
                    from .models import UserProfile
                    db_user = UserProfile.objects.get(pk=user["db_pk"])
                    if name:         db_user.name         = name
                    if email:        db_user.email        = email
                    if phone:        db_user.phone        = phone
                    db_user.state        = state
                    db_user.city         = city
                    db_user.neighborhood = neighborhood
                    db_user.street       = street
                    db_user.zip_code     = zip_code
                    db_user.save()
                    request.session["user"] = db_user.to_session_dict()
                    request.session.modified = True
                except Exception as e:
                    error = f"Erro ao salvar: {e}"
            else:
                # Mock user — atualiza só a sessão
                if name:  request.session["user"]["name"]  = name
                if email: request.session["user"]["email"] = email
                if phone: request.session["user"]["phone"] = phone
                request.session["user"]["address"] = {
                    "state":        state,
                    "city":         city,
                    "neighborhood": neighborhood,
                    "street":       street,
                    "zip":          zip_code,
                }
                request.session.modified = True

            if not error:
                messages.success(request, "Dados atualizados com sucesso.")
                return redirect("perfil")

    return render(request, "debtfree/perfil_edit.html", {
        "user":   request.session["user"],
        "form":   form,
        "states": BRAZIL_STATES,
        "error":  error,
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
    """Página de impressão da carta — o browser gera o PDF nativamente."""
    user = request.session["user"]
    debt_data = _get_debt_data(request)
    try:
        debt = debt_data["prioritized"][debt_index]
    except IndexError:
        return redirect("dashboard")

    address = user.get("address", {})

    # Gera corpo via IA
    try:
        ai_body = generate_letter(
            debt           = debt,
            monthly_income = debt_data["monthly_income"],
            user_name      = user["name"],
        )
    except Exception:
        ai_body = (
            f"Eu, {user['name']}, CPF {user['cpf']}, venho por meio desta carta manifestar "
            f"meu interesse em regularizar a dívida com {debt['creditor']}, no valor de "
            f"R$ {debt['total_amount']:.2f}, e solicito proposta de renegociação nos termos "
            f"da Lei 14.181/2021."
        )

    letter_text = f"""{address.get('city', 'São Paulo')}, {_today_br()}

{debt['creditor']}
A/C Departamento de Cobranças

Assunto: Proposta de Renegociação de Dívida

{ai_body}

Atenciosamente,
{user['name']}
CPF: {user['cpf']}
Telefone: {user['phone']}"""

    # Retorna HTML otimizado para impressão — browser faz "Salvar como PDF"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Carta — {debt['creditor']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.7;
    color: #111;
    padding: 2.5cm 3cm;
    max-width: 21cm;
    margin: 0 auto;
  }}
  .header {{
    border-bottom: 2px solid #028090;
    padding-bottom: 12px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .header-brand {{ font-size: 11pt; color: #028090; font-weight: bold; }}
  .header-sub {{ font-size: 9pt; color: #888; margin-top: 3px; }}
  .letter {{ white-space: pre-line; margin-bottom: 40px; }}
  .footer {{
    border-top: 1px solid #ccc;
    padding-top: 10px;
    font-size: 8pt;
    color: #aaa;
  }}
  .no-print {{
    position: fixed;
    top: 16px; right: 16px;
    background: #028090;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    font-family: system-ui, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,.2);
  }}
  @media print {{
    .no-print {{ display: none; }}
    body {{ padding: 0; }}
  }}
</style>
</head>
<body>
<button class="no-print" onclick="window.print()">⬇ Baixar / Imprimir PDF</button>
<div class="header">
  <div>
    <div class="header-brand">QuitAI — Carta de Negociação</div>
    <div class="header-sub">Gerada com base na Lei 14.181/2021 · Caráter informativo</div>
  </div>
</div>
<div class="letter">{letter_text}</div>
<div class="footer">Gerado pelo QuitAI · Para situações complexas, consulte a Defensoria Pública ou o PROCON.</div>
<script>
  // Abre diálogo de impressão automaticamente após carregar
  window.addEventListener('load', function() {{
    setTimeout(function() {{ window.print(); }}, 600);
  }});
</script>
</body>
</html>"""

    return HttpResponse(html, content_type="text/html; charset=utf-8")


@login_required
@require_http_methods(["POST"])
def mark_debt(request, debt_index):
    """Marca status de uma dívida (sessão ou DB)."""
    new_status = request.POST.get("status", "")  # "", "em_negociacao", "paga"
    user  = request.session["user"]
    is_db = user.get("is_db_user", False)

    if is_db:
        try:
            from .models import UserProfile
            db_user  = UserProfile.objects.get(pk=user["db_pk"])
            debt_obj = list(db_user.debts.all())[debt_index]
            debt_obj.debt_status = new_status
            debt_obj.save()
            request.session.pop("debt_data", None)
            request.session.modified = True
        except (IndexError, Exception):
            pass
    else:
        _init_session_debts(request)
        try:
            request.session["debt_data"]["prioritized"][debt_index]["debt_status"] = new_status
            request.session.modified = True
        except (IndexError, KeyError):
            pass

    return redirect("dashboard")


def _init_session_debts(request):
    """Garante que session["debt_data"] existe (copia do mock se necessário)."""
    if not request.session.get("debt_data"):
        debt_data = _get_debt_data(request)
        request.session["debt_data"] = {
            "monthly_income": debt_data["monthly_income"],
            "situation":      debt_data["situation"],
            "prioritized":    [dict(d) for d in debt_data["prioritized"]],
            "analysis":       debt_data.get("analysis"),
        }
    return request.session["debt_data"]


def _recalc_session(request):
    """Recalcula situation e reordena prioridades após edição.
    Faz reassign explícito do top-level key para garantir que
    signed_cookies serialize a sessão atualizada."""
    from .rules import classify_situation, enrich
    data   = request.session.get("debt_data", {})
    income = data.get("monthly_income", 0)
    debts  = list(data.get("prioritized", []))
    enriched = enrich(debts)
    for i, d in enumerate(enriched):
        d["id"] = i
    # Reassign completo — evita problema de mutação aninhada com signed_cookies
    request.session["debt_data"] = {
        "monthly_income": income,
        "situation":      classify_situation(income, enriched),
        "prioritized":    enriched,
        "analysis":       data.get("analysis"),
    }
    request.session.modified = True


DEBT_TYPES = [
    ("pensao_alimenticia",    "Pensão Alimentícia"),
    ("aluguel",               "Aluguel"),
    ("servicos_essenciais",   "Luz / Água / Gás"),
    ("financiamento_garantia","Financiamento (carro/imóvel)"),
    ("emprestimo_bancario",   "Empréstimo Bancário"),
    ("cartao_credito",        "Cartão de Crédito"),
    ("loja_comercio",         "Loja / Comércio"),
    ("outros",                "Outros"),
]


@login_required
@require_http_methods(["GET", "POST"])
def debt_add(request):
    user    = request.session["user"]
    is_db   = user.get("is_db_user", False)
    error   = None
    form    = {}

    if request.method == "POST":
        try:
            creditor        = request.POST.get("creditor", "").strip()
            debt_type       = request.POST.get("type", "outros")
            total_amount    = float(request.POST.get("total_amount", 0) or 0)
            monthly_payment = float(request.POST.get("monthly_payment", 0) or 0)
            due_date        = request.POST.get("due_date", "").strip() or None

            if not creditor or total_amount <= 0:
                raise ValueError("Preencha o credor e o valor total.")

            if is_db:
                from .models import UserProfile, Debt
                db_user = UserProfile.objects.get(pk=user["db_pk"])
                Debt.objects.create(
                    user            = db_user,
                    creditor        = creditor,
                    type            = debt_type,
                    total_amount    = total_amount,
                    monthly_payment = monthly_payment,
                    due_date        = due_date,
                )
                # Limpa cache de sessão para forçar releitura do DB
                request.session.pop("debt_data", None)
                request.session.modified = True
            else:
                _init_session_debts(request)
                new_debt = {
                    "id":              len(request.session["debt_data"]["prioritized"]),
                    "creditor":        creditor,
                    "type":            debt_type,
                    "type_label":      dict(DEBT_TYPES).get(debt_type, "Outros"),
                    "total_amount":    total_amount,
                    "monthly_payment": monthly_payment,
                    "due_date":        due_date,
                    "is_prescribed":   False,
                    "debt_status":     "",
                }
                request.session["debt_data"]["prioritized"].append(new_debt)
                _recalc_session(request)
            messages.success(request, f"Dívida com {creditor} adicionada com sucesso.")
            return redirect("dashboard")
        except ValueError as e:
            error = str(e)
            form  = request.POST

    return render(request, "debtfree/debt_form.html", {
        "user":       user,
        "form":       form,
        "debt_types": DEBT_TYPES,
        "action":     "add",
        "error":      error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def debt_edit(request, debt_index):
    user  = request.session["user"]
    is_db = user.get("is_db_user", False)
    error = None

    # Busca dívida (DB ou sessão)
    if is_db:
        try:
            from .models import Debt
            db_user = __import__("debtfree.models", fromlist=["UserProfile"]).UserProfile.objects.get(pk=user["db_pk"])
            debt_obj = list(db_user.debts.all())[debt_index]
            debt = debt_obj.to_dict(debt_index)
        except (IndexError, Exception):
            return redirect("dashboard")
    else:
        _init_session_debts(request)
        try:
            debt = request.session["debt_data"]["prioritized"][debt_index]
        except IndexError:
            return redirect("dashboard")

    if request.method == "POST":
        try:
            creditor        = request.POST.get("creditor", "").strip()
            debt_type       = request.POST.get("type", "outros")
            total_amount    = float(request.POST.get("total_amount", 0) or 0)
            monthly_payment = float(request.POST.get("monthly_payment", 0) or 0)
            due_date        = request.POST.get("due_date", "").strip() or None

            if not creditor or total_amount <= 0:
                raise ValueError("Preencha o credor e o valor total.")

            if is_db:
                from .models import Debt as DebtModel
                from .models import UserProfile
                db_user = UserProfile.objects.get(pk=user["db_pk"])
                debt_obj = list(db_user.debts.all())[debt_index]
                debt_obj.creditor        = creditor
                debt_obj.type            = debt_type
                debt_obj.total_amount    = total_amount
                debt_obj.monthly_payment = monthly_payment
                debt_obj.due_date        = due_date
                debt_obj.save()
                request.session.pop("debt_data", None)
                request.session.modified = True
            else:
                debt.update({
                    "creditor":        creditor,
                    "type":            debt_type,
                    "type_label":      dict(DEBT_TYPES).get(debt_type, "Outros"),
                    "total_amount":    total_amount,
                    "monthly_payment": monthly_payment,
                    "due_date":        due_date,
                })
                _recalc_session(request)
            messages.success(request, f"Dívida com {creditor} atualizada com sucesso.")
            return redirect("dashboard")
        except ValueError as e:
            error = str(e)
            debt  = request.POST

    return render(request, "debtfree/debt_form.html", {
        "user":       user,
        "form":       debt,
        "debt_types": DEBT_TYPES,
        "action":     "edit",
        "debt_index": debt_index,
        "error":      error,
    })


@login_required
@require_http_methods(["POST"])
def debt_delete(request, debt_index):
    user  = request.session["user"]
    is_db = user.get("is_db_user", False)

    if is_db:
        try:
            from .models import UserProfile
            db_user  = UserProfile.objects.get(pk=user["db_pk"])
            debt_obj = list(db_user.debts.all())[debt_index]
            debt_obj.delete()
            request.session.pop("debt_data", None)
            request.session.modified = True
        except (IndexError, Exception):
            pass
    else:
        _init_session_debts(request)
        try:
            request.session["debt_data"]["prioritized"].pop(debt_index)
            _recalc_session(request)
        except IndexError:
            pass
    messages.success(request, "Dívida removida da lista.")
    return redirect("dashboard")


def _today_br():
    from datetime import date
    months = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    d = date.today()
    return f"{d.day} de {months[d.month]} de {d.year}"

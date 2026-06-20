"""
Integração com a API do Banco Central do Brasil (BCB) e cálculos financeiros.
Todas as chamadas têm fallback para valores hardcoded caso a API esteja fora do ar.
"""
import urllib.request
import json
import time
from datetime import date, timedelta

# Cache simples em memória — evita 9s de latência no load do dashboard
_RATES_CACHE = {"data": None, "ts": 0}
_CACHE_TTL   = 900  # 15 minutos

# Séries do BCB (SGS)
BCB_SERIES = {
    "selic_meta":           432,    # SELIC meta % ao ano
    "juros_cartao":         20714,  # Juros cartão de crédito total % ao mês
    "juros_emprestimo":     20754,  # Juros empréstimo pessoal % ao mês
    "juros_cheque_especial": 7,     # Juros cheque especial % ao mês
}

# Fallback caso a API esteja indisponível
# Valores de referência BCB — jun/2025
FALLBACK_RATES = {
    "selic_meta":            14.75,   # SELIC meta % a.a.
    "juros_cartao":          15.10,   # Cartão rotativo total % a.m. (BCB 20714)
    "juros_emprestimo":       6.24,   # Empréstimo pessoal % a.m. (BCB 20754)
    "juros_cheque_especial":  7.93,   # Cheque especial % a.m.
}

# Taxas de juros típicas por tipo de dívida (ao mês)
# Usadas quando o usuário não informou a taxa da dívida
DEFAULT_RATES_BY_TYPE = {
    "cartao_credito":        10.0,   # rotativo médio (conservador)
    "emprestimo_bancario":    3.5,
    "financiamento_garantia": 1.2,
    "loja_comercio":          6.0,
    "cheque_especial":        7.9,
    "pensao_alimenticia":     0.0,   # não tem juro, tem multa
    "aluguel":                0.0,
    "servicos_essenciais":    0.0,
    "outros":                 3.0,
}


def _fetch_bcb(series_id: int, fallback: float) -> tuple[float, bool]:
    """Busca o valor mais recente de uma série do BCB. Retorna (valor, is_live)."""
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados/ultimos/1?formato=json"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
            return float(data[0]["valor"]), True
    except Exception:
        return fallback, False


def get_market_rates() -> dict:
    """
    Retorna taxas de mercado atualizadas do BCB.
    Cache de 15 minutos em memória para evitar latência na demo.
    Inclui flag `rates_live` para indicar se vieram do BCB ou do fallback.
    """
    global _RATES_CACHE
    now = time.time()
    if _RATES_CACHE["data"] and (now - _RATES_CACHE["ts"]) < _CACHE_TTL:
        return _RATES_CACHE["data"]

    selic_anual,  selic_live  = _fetch_bcb(BCB_SERIES["selic_meta"],       FALLBACK_RATES["selic_meta"])
    juros_cartao, cartao_live = _fetch_bcb(BCB_SERIES["juros_cartao"],     FALLBACK_RATES["juros_cartao"])
    juros_empr,   empr_live   = _fetch_bcb(BCB_SERIES["juros_emprestimo"], FALLBACK_RATES["juros_emprestimo"])

    selic_mensal = round(((1 + selic_anual / 100) ** (1 / 12) - 1) * 100, 4)
    rates_live   = selic_live and cartao_live and empr_live

    result = {
        "selic_anual":             selic_anual,
        "selic_mensal":            selic_mensal,
        "juros_cartao_mensal":     juros_cartao,
        "juros_emprestimo_mensal": juros_empr,
        "rates_live":              rates_live,
    }
    _RATES_CACHE = {"data": result, "ts": now}
    return result


# ---------------------------------------------------------------------------
# Cálculos de amortização
# ---------------------------------------------------------------------------

def months_to_pay(total: float, monthly_payment: float, monthly_rate_pct: float) -> int | None:
    """
    Calcula quantos meses para quitar uma dívida com pagamento fixo.
    Retorna None se o pagamento não cobre nem os juros.
    """
    if monthly_rate_pct <= 0:
        if monthly_payment <= 0:
            return None
        return max(1, round(total / monthly_payment))

    r = monthly_rate_pct / 100
    if monthly_payment <= total * r:
        return None  # pagamento não cobre juros

    import math
    n = math.log(monthly_payment / (monthly_payment - total * r)) / math.log(1 + r)
    return max(1, round(n))


def total_paid(total: float, monthly_payment: float, monthly_rate_pct: float) -> float:
    """Total pago até quitar a dívida (incluindo juros)."""
    n = months_to_pay(total, monthly_payment, monthly_rate_pct)
    if n is None:
        return float("inf")
    return round(monthly_payment * n, 2)


def savings_if_paid_now(total: float, monthly_payment: float, monthly_rate_pct: float) -> float:
    """Quanto o usuário economiza em juros se quitar agora vs. pagar normalmente."""
    paid = total_paid(total, monthly_payment, monthly_rate_pct)
    if paid == float("inf"):
        return 0.0
    return round(paid - total, 2)


def amortization_tip(debt: dict, market_rates: dict) -> dict:
    """
    Gera dica de amortização personalizada para uma dívida,
    comparando com a SELIC.
    """
    debt_type      = debt.get("type", "outros")
    total          = debt.get("total_amount", 0)
    monthly_pmt    = debt.get("monthly_payment") or 0
    rate_mensal    = DEFAULT_RATES_BY_TYPE.get(debt_type, 3.0)
    selic_mensal   = market_rates["selic_mensal"]
    selic_anual    = market_rates["selic_anual"]

    # Sem juro relevante (aluguel, pensão, serviços)
    if rate_mensal == 0:
        return {
            "has_tip": False,
            "rate_mensal": 0,
            "selic_mensal": selic_mensal,
        }

    juros_vs_selic_ratio = round(rate_mensal / selic_mensal, 1)

    # Cálculo com pagamento atual
    n_atual    = months_to_pay(total, monthly_pmt, rate_mensal) if monthly_pmt > 0 else None
    total_pago = total_paid(total, monthly_pmt, rate_mensal) if monthly_pmt > 0 else None
    economia   = savings_if_paid_now(total, monthly_pmt, rate_mensal) if monthly_pmt > 0 else None

    # Cálculo com +20% no pagamento
    extra_pmt   = round(monthly_pmt * 1.20, 2) if monthly_pmt > 0 else None
    n_extra     = months_to_pay(total, extra_pmt, rate_mensal) if extra_pmt else None
    meses_ganhos = (n_atual - n_extra) if (n_atual and n_extra) else None

    return {
        "has_tip":           True,
        "rate_mensal":       rate_mensal,
        "selic_anual":       selic_anual,
        "selic_mensal":      selic_mensal,
        "juros_vs_selic":    juros_vs_selic_ratio,
        "meses_para_quitar": n_atual,
        "total_pago":        total_pago,
        "economia_juros":    economia,
        "extra_pmt":         extra_pmt,
        "meses_ganhos":      meses_ganhos,
    }


# ---------------------------------------------------------------------------
# Prescrição com data exata
# ---------------------------------------------------------------------------

def prescription_detail(due_date_str: str | None) -> dict:
    """
    Retorna detalhe de prescrição: se já prescreveu, data exata e dias restantes.
    """
    if not due_date_str:
        return {"has_date": False}

    try:
        due = date.fromisoformat(due_date_str)
        prescription_date = due + timedelta(days=5 * 365)
        today = date.today()
        days_left = (prescription_date - today).days

        return {
            "has_date":          True,
            "prescription_date": prescription_date.strftime("%d/%m/%Y"),
            "is_prescribed":     days_left <= 0,
            "days_left":         max(0, days_left),
            "urgent":            0 < days_left <= 90,
        }
    except ValueError:
        return {"has_date": False}


# ---------------------------------------------------------------------------
# Painel resumo financeiro
# ---------------------------------------------------------------------------

def financial_summary(monthly_income: float, debts: list[dict], market_rates: dict) -> dict:
    """Agrega os principais indicadores financeiros do usuário."""
    total_debt     = sum(d.get("total_amount", 0) for d in debts)
    total_monthly  = sum(d.get("monthly_payment", 0) or 0 for d in debts)
    income_ratio   = round((total_monthly / monthly_income * 100), 1) if monthly_income else 0

    # Quanto paga de juros por mês (estimativa)
    monthly_interest = sum(
        d.get("total_amount", 0) * DEFAULT_RATES_BY_TYPE.get(d.get("type", "outros"), 3.0) / 100
        for d in debts
        if DEFAULT_RATES_BY_TYPE.get(d.get("type", "outros"), 0) > 0
    )

    # Quanto a SELIC renderia no mesmo valor (benchmark)
    selic_monthly_yield = round(total_debt * market_rates["selic_mensal"] / 100, 2)
    interest_vs_selic   = round(monthly_interest / selic_monthly_yield, 1) if selic_monthly_yield > 0 else 0

    return {
        "total_debt":          round(total_debt, 2),
        "total_monthly":       round(total_monthly, 2),
        "income_ratio":        income_ratio,
        "monthly_interest":    round(monthly_interest, 2),
        "selic_monthly_yield": selic_monthly_yield,
        "interest_vs_selic":   interest_vs_selic,
        "free_income":         round(monthly_income - total_monthly, 2),
    }

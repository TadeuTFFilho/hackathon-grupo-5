defmodule Debtfree.DebtRules do
  @moduledoc """
  Regras de negócio para priorização de dívidas.
  Baseado na Lei 14.181/2021 e boas práticas de educação financeira.
  """

  @priority_order ~w(
    pensao_alimenticia
    aluguel
    servicos_essenciais
    financiamento_garantia
    emprestimo_bancario
    cartao_credito
    loja_comercio
    outros
  )

  @minimum_existential_ratio 0.30

  @doc "Classifica a situação financeira baseada na % da renda comprometida"
  def classify_situation(monthly_income, debts) when monthly_income > 0 do
    total_monthly = debts |> Enum.map(&(&1["monthlyPayment"] || 0)) |> Enum.sum()
    ratio = total_monthly / monthly_income

    cond do
      ratio <= 0.30 -> %{level: "safe",     label: "Controlado",     color: "green"}
      ratio <= 0.50 -> %{level: "warning",  label: "Atenção",        color: "yellow"}
      true          -> %{level: "critical", label: "Superendividado", color: "red"}
    end
  end

  def classify_situation(_, _), do: %{level: "critical", label: "Superendividado", color: "red"}

  @doc "Ordena dívidas por urgência de pagamento"
  def prioritize(debts) do
    Enum.sort_by(debts, fn debt ->
      type = debt["type"] || "outros"
      Enum.find_index(@priority_order, &(&1 == type)) || 99
    end)
  end

  @doc "Verifica se uma dívida pode estar prescrita (regra geral: 5 anos)"
  def prescribed?(nil), do: false
  def prescribed?(due_date) do
    case Date.from_iso8601(due_date) do
      {:ok, date} ->
        five_years_ago = Date.add(Date.utc_today(), -5 * 365)
        Date.before?(date, five_years_ago)
      _ -> false
    end
  end

  @doc "Enriquece cada dívida com metadados calculados"
  def enrich(debts) do
    Enum.map(debts, fn debt ->
      Map.put(debt, "isPrescribed", prescribed?(debt["dueDate"]))
    end)
  end
end

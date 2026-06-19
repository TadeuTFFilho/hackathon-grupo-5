defmodule DebtfreeWeb.DebtController do
  use Phoenix.Controller, formats: [:json]

  alias Debtfree.{DebtRules, ClaudeService}

  @doc """
  POST /api/debts/analyze
  Body: { monthlyIncome, debts: [{ creditor, type, totalAmount, monthlyPayment, dueDate }] }
  """
  def analyze(conn, %{"monthlyIncome" => income, "debts" => debts}) when is_list(debts) and length(debts) > 0 do
    enriched   = DebtRules.enrich(debts)
    situation  = DebtRules.classify_situation(income, enriched)
    prioritized = DebtRules.prioritize(enriched)

    case ClaudeService.analyze_debts(%{
           monthly_income: income,
           debts: enriched,
           prioritized: prioritized,
           situation: situation
         }) do
      {:ok, analysis} ->
        json(conn, %{situation: situation, prioritized: prioritized, analysis: analysis})

      {:error, reason} ->
        conn |> put_status(502) |> json(%{error: "Erro na análise IA", details: reason})
    end
  end

  def analyze(conn, _params) do
    conn |> put_status(400) |> json(%{error: "monthlyIncome e debts são obrigatórios"})
  end

  @doc """
  POST /api/debts/letter
  Body: { debt, monthlyIncome, userName? }
  """
  def letter(conn, %{"debt" => debt, "monthlyIncome" => income} = params) do
    case ClaudeService.generate_letter(%{
           debt: debt,
           monthly_income: income,
           user_name: params["userName"]
         }) do
      {:ok, letter} ->
        json(conn, %{letter: letter})

      {:error, reason} ->
        conn |> put_status(502) |> json(%{error: "Erro ao gerar carta", details: reason})
    end
  end

  def letter(conn, _params) do
    conn |> put_status(400) |> json(%{error: "debt e monthlyIncome são obrigatórios"})
  end
end

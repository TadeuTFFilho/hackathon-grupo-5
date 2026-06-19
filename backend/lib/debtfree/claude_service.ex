defmodule Debtfree.ClaudeService do
  @moduledoc """
  Integração com a API do Claude (Anthropic) via Req (HTTP client).
  """

  @anthropic_url "https://api.anthropic.com/v1/messages"
  @anthropic_version "2023-06-01"

  defp api_key, do: Application.get_env(:debtfree, :claude)[:api_key]
  defp model,   do: Application.get_env(:debtfree, :claude)[:model] || "claude-opus-4-8"

  defp request(prompt, max_tokens \\ 1024) do
    Req.post(@anthropic_url,
      headers: [
        {"x-api-key", api_key()},
        {"anthropic-version", @anthropic_version},
        {"content-type", "application/json"}
      ],
      json: %{
        model: model(),
        max_tokens: max_tokens,
        messages: [%{role: "user", content: prompt}]
      }
    )
  end

  @doc "Analisa a situação de superendividamento e retorna recomendações em JSON"
  def analyze_debts(%{monthly_income: income, debts: debts, prioritized: prioritized, situation: situation}) do
    debt_list =
      prioritized
      |> Enum.with_index(1)
      |> Enum.map(fn {d, i} -> "  #{i}. #{d["creditor"]} — R$ #{d["totalAmount"]} (#{d["type"]})" end)
      |> Enum.join("\n")

    prompt = """
    Você é um assistente especializado na Lei do Superendividamento (Lei 14.181/2021) do Brasil.

    Analise a situação financeira abaixo e responda em JSON com a estrutura exata indicada.

    SITUAÇÃO DO USUÁRIO:
    - Renda mensal: R$ #{income}
    - Nível: #{situation.label}
    - Dívidas (já ordenadas por prioridade):
    #{debt_list}

    Responda SOMENTE com JSON válido neste formato:
    {
      "summary": "Resumo da situação em 2 frases, linguagem simples",
      "legalRights": "Explique em 3 frases os direitos pela Lei 14.181/2021 aplicáveis a este caso",
      "actionPlan": [
        { "step": 1, "action": "O que fazer primeiro", "reason": "Por quê" },
        { "step": 2, "action": "O que fazer segundo", "reason": "Por quê" },
        { "step": 3, "action": "O que fazer terceiro", "reason": "Por quê" }
      ],
      "negotiationTip": "Dica específica de negociação para a dívida mais urgente"
    }
    """

    case request(prompt) do
      {:ok, %{status: 200, body: body}} ->
        text = get_in(body, ["content", Access.at(0), "text"])
        Jason.decode(text)

      {:ok, %{status: status, body: body}} ->
        {:error, "Claude API error #{status}: #{inspect(body)}"}

      {:error, reason} ->
        {:error, "HTTP error: #{inspect(reason)}"}
    end
  end

  @doc "Gera carta de negociação personalizada para uma dívida"
  def generate_letter(%{debt: debt, monthly_income: income, user_name: name}) do
    prompt = """
    Escreva uma carta de negociação de dívida em nome de #{name || "o devedor"}.

    Dívida: #{debt["creditor"]}
    Valor: R$ #{debt["totalAmount"]}
    Tipo: #{debt["type"]}
    Renda mensal do devedor: R$ #{income}

    Regras:
    - Tom respeitoso e firme
    - Mencionar a Lei 14.181/2021 se aplicável
    - Propor pagamento de 40-50% do valor à vista OU parcelamento com juros máximos de 12% a.a.
    - Máximo 3 parágrafos
    - Linguagem simples, sem juridiquês excessivo
    """

    case request(prompt, 512) do
      {:ok, %{status: 200, body: body}} ->
        text = get_in(body, ["content", Access.at(0), "text"])
        {:ok, text}

      {:ok, %{status: status, body: body}} ->
        {:error, "Claude API error #{status}: #{inspect(body)}"}

      {:error, reason} ->
        {:error, "HTTP error: #{inspect(reason)}"}
    end
  end
end

defmodule Debtfree.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {Phoenix.PubSub, name: Debtfree.PubSub},
      DebtfreeWeb.Endpoint
    ]

    opts = [strategy: :one_for_one, name: Debtfree.Supervisor]
    Supervisor.start_link(children, opts)
  end

  @impl true
  def config_change(changed, _new, removed) do
    DebtfreeWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end

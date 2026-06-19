defmodule DebtfreeWeb.Router do
  use Phoenix.Router, helpers: false

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", DebtfreeWeb do
    pipe_through :api

    get  "/health",          HealthController, :index
    post "/debts/analyze",   DebtController,   :analyze
    post "/debts/letter",    DebtController,   :letter
  end
end

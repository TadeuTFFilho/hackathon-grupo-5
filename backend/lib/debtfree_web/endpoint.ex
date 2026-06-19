defmodule DebtfreeWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :debtfree

  plug CorsPlug, origin: ["http://localhost:3000"]

  plug Plug.RequestId
  plug Plug.Telemetry, event_prefix: [:phoenix, :endpoint]

  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Plug.MethodOverride
  plug Plug.Head
  plug DebtfreeWeb.Router
end

import Config

config :debtfree, DebtfreeWeb.Endpoint,
  url: [host: "localhost"],
  render_errors: [
    formats: [json: DebtfreeWeb.ErrorJSON],
    layout: false
  ],
  pubsub_server: Debtfree.PubSub,
  live_view: [signing_salt: "debtfree_salt"]

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

config :phoenix, :json_library, Jason

import_config "#{config_env()}.exs"

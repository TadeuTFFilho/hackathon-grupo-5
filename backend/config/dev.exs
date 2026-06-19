import Config

config :debtfree, DebtfreeWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 3001],
  check_origin: false,
  code_reloader: true,
  debug_errors: true,
  secret_key_base: "dev_secret_key_base_replace_in_prod_please_change_this"

config :debtfree, :claude,
  api_key: System.get_env("ANTHROPIC_API_KEY"),
  model: "claude-opus-4-8",
  base_url: "https://api.anthropic.com/v1"

config :logger, :console, format: "[$level] $message\n"
config :phoenix, :stacktrace_depth, 20

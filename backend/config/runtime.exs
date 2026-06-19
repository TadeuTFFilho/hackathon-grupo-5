import Config

if config_env() == :prod do
  config :debtfree, :claude,
    api_key: System.fetch_env!("ANTHROPIC_API_KEY"),
    model: "claude-opus-4-8",
    base_url: "https://api.anthropic.com/v1"
end

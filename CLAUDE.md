# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**DebtFree AI** (nome de marca em desenvolvimento: **Passo**) — assistente de IA para superendividados brasileiros. Prioriza dívidas segundo a Lei 14.181/2021, gera cartas de negociação personalizadas e exibe taxas de juros reais do BCB. Projeto de hackathon do Grupo 5 (Orla Tech).

**Persona central:** Mariana, 38 anos, Guarulhos, ~R$2.800/mês, múltiplas dívidas, resolve tudo pelo celular.

---

## Stack

Single Django 5 app — sem frontend separado. Django Templates + Tailwind via CDN + Lucide icons via CDN. OpenAI `gpt-4o-mini` para análise de IA e geração de cartas. BCB SGS API para taxas em tempo real.

`frontend/` (Next.js) e `backend/` (Node.js/Elixir) são versões anteriores descartadas — **ignorar**.

## Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env   # preencher OPENAI_API_KEY (e opcionalmente ANTHROPIC_API_KEY)

# Migrations (necessário após clonar ou alterar models.py)
python manage.py migrate

# Rodar
python manage.py runserver   # http://localhost:8000

# Criar superusuário (só se precisar do admin Django)
python manage.py createsuperuser
```

`.env` necessário: `OPENAI_API_KEY`. `ANTHROPIC_API_KEY` e `DJANGO_SECRET_KEY` são opcionais em dev.

---

## Architecture

Toda a lógica ativa está em `debtfree/`. Arquitetura: Django views → session → templates.

### Session vs. Banco de dados

O app tem dois tipos de usuário:

- **Mock users** (`is_db_user: False`) — autenticam via `mock_data.MOCK_USERS`; dados de dívida vêm de `mock_data.MOCK_DEBT_DATA`. Nada é salvo no banco.
- **DB users** (`is_db_user: True`) — criados via `/register/`; armazenados em `UserProfile` + `Debt` (SQLite). Dívidas são carregadas do banco e salvas na sessão após modificação.

`SESSION_ENGINE = "signed_cookies"` — a sessão inteira vive no cookie assinado. Para forçar serialização após mutação de sub-dicts, sempre reatribuir a chave de nível raiz (ex: `request.session["debt_data"] = {...}`); `request.session.modified = True` não é suficiente para dicts aninhados.

### Fonte de dados — `_get_debt_data(request)`

Prioridade de carregamento de dívidas (em `views.py`):
1. `session["debt_data"]` (sempre preferido após qualquer edição)
2. Banco SQLite via `_get_db_debt_data()` (DB users sem sessão ainda)
3. `MOCK_DEBT_DATA[cpf]` (mock users)
4. Fallback João (`123.456.789-00`)

### Módulos principais

| Arquivo | Responsabilidade |
|---|---|
| `views.py` | Todas as views. Helpers `_parse_float()`, `_format_brl()`, `_safe_json()` definidos aqui. |
| `rules.py` | `enrich()`, `prioritize()`, `classify_situation()`, `calculate_score()`. Lógica pura, sem I/O. |
| `financial_service.py` | BCB API com cache 15min, `amortization_tip()`, `financial_summary()`, `prescription_detail()`. |
| `openai_service.py` | `analyze_debts()` e `generate_letter()` via `gpt-4o-mini`. Cliente criado lazy por chamada. |
| `models.py` | `UserProfile` + `Debt`. `to_session_dict()` / `to_dict()` convertem para o formato da sessão. |
| `mock_data.py` | 4 personas demo: João (crítico, `123.456.789-00`), Ana (atenção, `987.654.321-00`), Carlos (controlado, `000.000.001-00`), Maria (prescrita, `000.000.002-00`). Senha: `senha123`. |
| `auth.py` | Decorator `@login_required` → redireciona para `/login/`. |
| `auth_utils.py` | `hash_password()` / `check_password()` — bcrypt wrapper simples. |
| `procon_data.py` | Dict `PROCON_BY_STATE` indexado por UF. |
| `context_processors.py` | Injeta `current_user` em todos os templates. |
| `templatetags/debtfree_filters.py` | Filtro `|brl` — formata float para `R$ 1.240,90`. |

### Fluxo principal de dados

```
POST /analyze/
  → _parse_float() em todos os valores monetários
  → enrich(debts)          # adiciona type_label, is_prescribed
  → classify_situation()   # safe / warning / critical
  → prioritize(debts)      # ordena por PRIORITY_ORDER
  → analyze_debts() OpenAI # fallback silencioso se falhar
  → session["debt_data"] = {...}
  → redirect dashboard

GET /dashboard/
  → _get_debt_data()
  → financial_summary()
  → get_market_rates()     # BCB com cache 15min
  → amortization_tip() por dívida
  → calculate_score()
  → _safe_json() para chart_labels/values (XSS via nomes de credores)
```

### Rotas

```
/                                       home (landing)
/login/                                 login (CPF + senha)
/register/                              cadastro novo usuário
/logout/                                flush sessão
/onboarding/                            formulário lote de dívidas
/analyze/                               POST — processa formulário e salva na sessão
/renda/                                 GET/POST — atualizar renda mensal
/perfil/                                página de perfil
/perfil/editar/                         editar dados pessoais
/dashboard/                             painel principal (login obrigatório)
/debts/                                 lista de dívidas + add/edit individual
/dashboard/legal/                       direitos Lei 14.181/2021
/dashboard/procon/                      PROCON/Defensoria pelo estado do usuário
/dashboard/letter/<int>/                carta de negociação por índice
/dashboard/letter/<int>/pdf/            download PDF (browser print HTML)
/dashboard/mark/<int>/                  POST — altera debt_status
/dashboard/debt/add/                    add dívida individual
/dashboard/debt/<int>/edit/             editar dívida
/dashboard/debt/<int>/delete/           deletar dívida
```

---

## Business Rules

Implementadas em `rules.py`, documentadas em `docs/business-rules.md`:

- **Prioridade de pagamento:** `pensao_alimenticia > aluguel > servicos_essenciais > financiamento_garantia > emprestimo_bancario > cartao_credito > loja_comercio > outros`
- **Classificação:** ≤30% renda = `safe/Controlado`, 31–50% = `warning/Atenção`, >50% = `critical/Superendividado`
- **Score:** 100 se sem dívidas; base por ratio de comprometimento → descontos por número de dívidas (max -12) e por dívidas urgentes com pagamento (-5 cada); mínimo 5
- **Prescrição:** `due_date` + 5 anos; dívidas prescritas não podem ser cobradas judicialmente (exibido com badge)
- **Status de dívida:** `""` → `"em_negociacao"` → `"paga"` (ciclo via `mark_debt`)

## BCB API

`financial_service._fetch_bcb()` consome `api.bcb.gov.br/dados/serie/bcdata.sgs.{id}/dados/ultimos/1`. Timeout 3s com fallback hardcoded (valores jun/2025). Séries: 432 (SELIC meta a.a.), 20714 (cartão rotativo % a.m.), 20754 (empréstimo pessoal % a.m.). Cache módulo-level `_RATES_CACHE` TTL 15min; flag `rates_live` no retorno indica se vieram do BCB ou do fallback.

## Formatação monetária

- Sempre usar `_parse_float(value)` em `views.py` para qualquer input monetário do usuário — aceita tanto `5.000,00` (BR) quanto `5000.00` (EN).
- Sempre usar `_format_brl(value)` ou o filtro `|brl` para exibir valores — produz `R$ 1.240,90`.
- Placeholders nos inputs: `"R$ 0,00"` (sem span overlay separado).
- Nunca chamar `float()` diretamente em inputs do usuário.

## Templates

`base.html` define classes semânticas globais (`.card`, `.btn-primary`, `.input`, `.section-title`, `.debt-row--urgent`, etc.) num bloco `<style>` centralizado — alterar lá afeta todas as telas.

Lucide icons: `<i data-lucide="name"></i>` + `lucide.createIcons()` no final do body. Sempre usar Lucide; nunca emoji como ícone na UI.

CPF mask em JS disponível em `login.html` e `register.html` — formata `12345678900` → `123.456.789-00` no `input` e `paste`.

Empty state do dashboard (sem dívidas): seções de score, barra de progresso, comprometimento de renda, gráfico, simulador e ranking ficam ocultas — exibe apenas card CTA apontando para `/debts/`.

## Brand

- Cor primária: teal `#2C8377` (não azul de banco)
- Tipografia: Plus Jakarta Sans
- Tom: calma, direta, acolhedora, não-julgadora — nunca "regularize imediatamente"
- Sentence case em tudo; sem emoji na UI; Lucide para ícones
- Dinheiro: `R$ 1.240,90` (vírgula decimal, ponto milhar, numerais tabulares)
- Disclaimers obrigatórios: `design/copy/legal-disclaimer.md` (versão curta no rodapé, média abaixo da análise, prescrição quando `is_prescribed`)
- Microcopy oficial: `design/copy/ui-copy.md` — usar esses textos, não inventar alternativas

## Design System — Vocabulário

Status de dívida: `cadastrada · em_atraso · com_proposta · negociando · acordo_ativo · paga · arquivada`
Prioridade: `resolver · negociar · acompanhar · esperar`
Situação financeira: `safe · warning · critical` (em `rules.py`)

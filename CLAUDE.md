# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**DebtFree AI** — assistente de IA para superendividados brasileiros. Prioriza dívidas, explica direitos pela Lei 14.181/2021 e gera cartas de negociação personalizadas. Projeto de hackathon do Grupo 5 (Orla Tech).

## Stack

Single Django 5 app — sem frontend separado. Django Templates com Tailwind via CDN. Claude API (Anthropic) para análise e geração de cartas. BCB API pública para taxas de juros em tempo real.

## Commands

```bash
# Setup
pip3 install -r requirements.txt
cp .env.example .env        # adicionar ANTHROPIC_API_KEY

# Rodar
python3 manage.py runserver  # http://localhost:8000

# Não há banco de dados — sem necessidade de migrate
# Sessions usam signed_cookies (SESSION_ENGINE)
```

## Architecture

Toda a lógica está em `debtfree/`. Não há models Django — nenhum banco de dados é usado.

**Fluxo de dados:**
1. `login_view` autentica via `mock_data.MOCK_USERS` (CPF + senha) e salva o usuário na sessão
2. `analyze` recebe o formulário, passa por `rules.py` (enrich → classify → prioritize) e salva em `request.session["debt_data"]`
3. `dashboard` lê a sessão, enriquece cada dívida com `financial_service.amortization_tip()`, busca taxas BCB via `financial_service.get_market_rates()`, e passa tudo para o template

**`_get_debt_data(request)` — fonte de dados para o dashboard:**
Prioridade: `session["debt_data"]` → `MOCK_DEBT_DATA[cpf]` → fallback para João (CPF `123.456.789-00`). Remove esse fallback quando Luis integrar a IA no `analyze`.

**Módulos principais:**

- `debtfree/rules.py` — priorização de dívidas (PRIORITY_ORDER), classificação da situação financeira (safe/warning/critical), enriquecimento com `type_label` e `is_prescribed`
- `debtfree/financial_service.py` — BCB API (séries SGS), cálculos de amortização, `financial_summary`, `amortization_tip` por dívida, `prescription_detail` com data exata
- `debtfree/claude_service.py` — `analyze_debts()` e `generate_letter()` via Anthropic SDK. Cliente criado lazy via `get_client()` para não exigir API key no boot
- `debtfree/mock_data.py` — `MOCK_USERS` e `MOCK_DEBT_DATA` indexados por CPF. Perfis disponíveis: João (`123.456.789-00`, superendividado crítico) e Ana (`987.654.321-00`, atenção). Senha: `senha123`. Ver `design/personas/personas.md` para os 4 perfis de demo completos (Carlos e Maria ainda não estão no mock).
- `debtfree/auth.py` — decorator `@login_required` que redireciona para `/login/`
- `debtfree/context_processors.py` — injeta `current_user` em todos os templates

**Templates:** `base.html` define todas as classes semânticas (`.card`, `.debt-row--urgent`, `.btn-primary`, etc.) num bloco `<style>` centralizado — mudar lá afeta todas as telas.

**Rotas:**
```
/               home
/login/         login (CPF + senha)
/logout/        flush de sessão
/onboarding/    formulário de dívidas
/analyze/       POST — processa formulário e salva na sessão
/dashboard/     análise principal (login obrigatório)
/dashboard/legal/          direitos Lei 14.181/2021
/dashboard/letter/<int>/   carta de negociação por índice da dívida
```

## Business Rules

Definidas em `docs/business-rules.md` e implementadas em `rules.py`:

- **Prioridade de pagamento:** pensão > aluguel > serviços essenciais > financiamento com garantia > empréstimo bancário > cartão > loja
- **Situação financeira:** ≤30% da renda = controlado, 31–50% = atenção, >50% = superendividado
- **Prescrição:** dívidas com mais de 5 anos do vencimento não podem ser cobradas judicialmente
- **Lei 14.181/2021:** repactuação judicial em até 5 anos, proteção do mínimo existencial (1 salário mínimo)

## BCB API (Banco Central)

`financial_service._fetch_bcb()` consome `api.bcb.gov.br/dados/serie/bcdata.sgs.{id}/dados/ultimos/1`. Timeout de 3s com fallback hardcoded. Séries usadas: 432 (SELIC meta), 20714 (juros cartão), 20754 (juros empréstimo pessoal).

## TODOs ativos no código

- `views.analyze` — `analysis: None` precisa ser substituído por `claude_service.analyze_debts()` quando Luis integrar
- `views.letter` — carta mockada precisa ser substituída por `claude_service.generate_letter()`
- `financial_service.get_market_rates()` — sem cache; em produção, adicionar `django.core.cache`

## design/ — Copy e Personas

- `design/copy/ui-copy.md` — microcopy oficial de toda a UI. Tom: empático, simples e encorajador. Usar esses textos nos templates — não inventar copy alternativo.
- `design/copy/legal-disclaimer.md` — disclaimers legais obrigatórios em três versões: curta (rodapé), média (abaixo da análise) e prescrição (quando `is_prescribed` for verdadeiro). Exibir conforme o contexto.
- `design/personas/personas.md` — 4 personas para demo e testes: Carlos (🟡 controlado), Ana (🟠 atenção, risco despejo), João (🔴 superendividado crítico), Maria (🟡 dívida prescrita — edge case para testar flag de prescrição). Os perfis João e Ana têm equivalentes em `mock_data.py`; Carlos e Maria são apenas referência de demo.

## backend/src/services/claudeService.js

Implementação Node.js da integração com Claude — **ativa**, não residual. Contém:
- `analyzeDebts({ monthlyIncome, debts, prioritized, situation })` — retorna JSON com `summary`, `legalRights`, `actionPlan` (3 passos) e `negotiationTip`
- `generateNegotiationLetter({ debt, monthlyIncome, userName })` — retorna texto da carta de negociação
- Modelo: `claude-opus-4-8`. System prompt compartilhado define persona empática e limites (orientação educativa, não consultoria jurídica).
- `parseJsonResponse()` — extrai JSON resiliente (remove markdown fences se presentes).

A versão Python equivalente está em `debtfree/claude_service.py` (usa Anthropic SDK Python). Os prompts canônicos vivem no arquivo JS acima — ao ajustar tom ou estrutura de resposta, manter os dois em sincronia.

## Arquivos residuais (ignorar)

`frontend/` (Next.js) é versão anterior descartada da stack. A aplicação ativa é o projeto Django na raiz; `backend/` contém o serviço Node.js da integração Claude.

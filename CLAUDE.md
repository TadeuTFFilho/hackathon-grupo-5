# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**DebtFree AI** (nome de trabalho: **Passo**) — assistente de IA para superendividados brasileiros. Prioriza dívidas, explica direitos pela Lei 14.181/2021 e gera cartas de negociação personalizadas. Projeto de hackathon do Grupo 5 (Orla Tech).

> "Passo" é o nome de marca em desenvolvimento. O produto deve sentir como **uma pausa segura no meio da pressão** — nunca um banco, uma cobradora ou uma promessa milagrosa.

**Persona central:** Mariana, 38 anos, Guarulhos, ~R$2.800/mês, múltiplas dívidas, resolve tudo pelo celular, tem medo de aceitar uma proposta que não vai conseguir cumprir.

---

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
- `debtfree/mock_data.py` — `MOCK_USERS` e `MOCK_DEBT_DATA` indexados por CPF. 4 perfis: João (`123.456.789-00`, crítico), Ana (`987.654.321-00`, atenção), Carlos (`000.000.001-00`, controlado), Maria (`000.000.002-00`, prescrita). Senha: `senha123`
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
/dashboard/                          análise principal (login obrigatório)
/dashboard/legal/                    direitos Lei 14.181/2021
/dashboard/letter/<int>/             carta de negociação por índice da dívida
/dashboard/letter/<int>/pdf/         download PDF da carta (xhtml2pdf)
/dashboard/procon/                   PROCON e Defensoria do estado do usuário
/dashboard/mark/<int>/               POST — marca dívida como em_negociacao ou paga
```

## Features v2 (feat/dashboard-interativo)

### Feature 1 — Score de saúde financeira
`calculate_score(monthly_income, debts)` em `rules.py`. Retorna `{"score": int, "label": str, "color": str}`. Lógica: ratio de comprometimento de renda → base score → descontos por número de dívidas (max -12) e por dívidas urgentes com pagamento ativo (-5 cada). Score 0–100, labels: Excelente/Bom/Atenção/Crítico/Emergência. Exibido no dashboard como círculo SVG com cor semântica.

### Feature 2 — Simulador interativo
Seção no `dashboard.html` com slider + input numérico sincronizados. Dado um valor disponível, o JS percorre `DEBTS_DATA` (JSON das dívidas injetado no template via `prioritized_json` no contexto) e recomenda a primeira dívida não-paga, calculando `payment`, `remaining` e `interest_saved` (estimativa: 12%/ano sobre o valor quitado).

### Feature 3 — Localizador PROCON/Defensoria
`debtfree/procon_data.py` — dict `PROCON_BY_STATE` com dados de SP, RJ, MG, RS, BA, PR, PE, CE, GO, DF, AM, SC e entrada `DEFAULT`. View `procon(request)` lê o estado de `session["user"]["address"]["state"]`. Template `procon.html` com cards de contato (telefone clicável, endereço, site) e seção explicativa de 3 passos. Link adicionado em `legal.html` na seção "Onde buscar ajuda gratuita".

### Feature 4 — WhatsApp na carta
`letter.html`: botão "Enviar pelo WhatsApp" com `href` montado via JS (`encodeURIComponent` do texto da carta) apontando para `https://wa.me/?text=...`. O link é construído no `DOMContentLoaded` para garantir que o texto final do DOM seja usado.

### Feature 5 — PDF real da carta
View `letter_pdf(request, debt_index)` gera PDF com `xhtml2pdf` (`pip install xhtml2pdf`). Reutiliza a mesma lógica de montagem de texto da view `letter`. Retorna `HttpResponse` com `content_type='application/pdf'` e header `Content-Disposition: attachment`. O botão "Baixar PDF" em `letter.html` aponta para `/dashboard/letter/<id>/pdf/` (não mais `window.print()`).

### Feature 6 — Status de dívida + barra de progresso
View `mark_debt(request, debt_index)` — POST-only, atualiza `session["debt_data"]["prioritized"][i]["debt_status"]` com `""`, `"em_negociacao"` ou `"paga"`. Se não houver `debt_data` na sessão (usuário usando mock), inicializa a partir de `_get_debt_data()` antes de gravar. Dashboard calcula `paid_debts`, `in_negotiation`, `progress_pct` e exibe barra de progresso Tailwind. Cada dívida no ranking tem mini-formulário de status com transições de estado: `→ em_negociacao → paga → (desfazer)`.

---

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
- **Pendente visual:** paleta atual usa Tailwind blue-600; direção de marca é teal `#2C8377` — migrar quando houver tempo

## Auditoria de responsividade (feat/dashboard-interativo)

Checklist mobile concluído — todos os templates são mobile-first com viewport-fit=cover:

- ✅ `{% load debtfree_filters %}` adicionado em `dashboard.html`, `legal.html`, `letter.html`, `perfil.html` — filtro `|brl` agora funciona em todos os templates
- ✅ CPFs corrigidos em `login.html`: Carlos `000.000.001-00`, Maria `000.000.002-00`
- ✅ Labels dos `grid-cols-3` encurtados para caber em 320px: "Comprometida", "Cartão", "Empréstimo" (dashboard, seções de sumário e BCB)
- ✅ Tab bar: `grid-cols-3`, `pb-safe`, `env(safe-area-inset-bottom)` — sem problema
- ✅ Nav principal: `hidden` em mobile, só aparece em `md:flex`
- ✅ Viewport: `<meta name="viewport" content="... viewport-fit=cover">` em `base.html`
- ✅ `grid-cols-2 sm:grid-cols-3` já usado em cards de ação do dashboard (linha ~425)

## design/ — Copy e Personas

- `design/copy/ui-copy.md` — microcopy oficial de toda a UI. Tom: empático, simples e encorajador. Usar esses textos nos templates — não inventar copy alternativo.
- `design/copy/legal-disclaimer.md` — disclaimers legais obrigatórios em três versões: curta (rodapé), média (abaixo da análise) e prescrição (quando `is_prescribed` for verdadeiro). Exibir conforme o contexto.
- `design/personas/personas.md` — 4 personas para demo e testes: Carlos (🟢 controlado), Ana (🟡 atenção, risco despejo), João (🔴 superendividado crítico), Maria (🟢 dívida prescrita — edge case). Todos têm equivalente em `mock_data.py`.

## backend/src/services/claudeService.js

Implementação Node.js da integração com Claude — **ativa**, não residual. Contém:
- `analyzeDebts({ monthlyIncome, debts, prioritized, situation })` — retorna JSON com `summary`, `legalRights`, `actionPlan` (3 passos) e `negotiationTip`
- `generateNegotiationLetter({ debt, monthlyIncome, userName })` — retorna texto da carta de negociação
- Modelo: `claude-opus-4-8`. System prompt compartilhado define persona empática e limites (orientação educativa, não consultoria jurídica).
- `parseJsonResponse()` — extrai JSON resiliente (remove markdown fences se presentes).

A versão Python equivalente está em `debtfree/claude_service.py`. Os prompts canônicos vivem no arquivo JS — ao ajustar tom ou estrutura de resposta, manter os dois em sincronia.

---

## Brand & Design Foundations (Passo)

Regras de voz e visual que se aplicam a qualquer tela do produto, independente da stack.

### Voz e conteúdo

- Tom: **calma, direta, acolhedora, didática, transparente, não julgadora.** Reduz ansiedade; nunca envergonha.
- Tratar o usuário como **"você"**; falar *com* ele — usar **"vamos"**. Nunca imperativo de cobrança.
- **Sentence case** em tudo (títulos, botões, labels). MAIÚSCULAS apenas em eyebrow labels pequenos.
- **Sem emoji na UI/copy.** Ícones fazem o trabalho visual. *(Nota: versão atual ainda usa emoji — migrar para Lucide progressivamente.)*
- Dinheiro em BRL: `R$ 1.240,90` (vírgula decimal, ponto milhar), numerais tabulares.
- Erros **orientam** ("Você pode revisar antes de salvar"), nunca repreendem. Toda recomendação responde **"por que estou vendo isso?"**.
- Preferir palavras simples: "Valor total" (não *saldo consolidado*), "Dívida em atraso" (não *inadimplência ativa*), "Parcela que cabe no mês" (não *capacidade de pagamento*), "Gastos essenciais" (não *mínimo existencial*).
- **Evitar:** "Você está devendo" · "Sua situação é grave" · "Regularize imediatamente" · "Limpe seu nome agora" · "Oferta imperdível / Última chance".
- Disclaimer sempre disponível: *"Esta ferramenta oferece orientação informativa e não substitui apoio jurídico ou financeiro especializado."*

### Fundações visuais

- **Cor** — primária: teal calmo `#2C8377` (verde azulado; **não** azul de banco). Secundária: areia/pêssego quente. Neutros warm-gray. Escada semântica `safe → attention → caution → critical → info`; **vermelho é raro e nunca superfície dominante**. Significado nunca por cor sozinha — sempre par ícone + label.
- **Tipografia** — uma família: **Plus Jakarta Sans**. Mobile-first; corpo ≥14px, labels ≥12px. Valores monetários com `font-variant-numeric: tabular-nums`.
- **Espaçamento** — base 4px. Gutter mobile 20px, padding card 16px, gap de seção 28px, gap entre cards 12px. Touch targets ≥44px.
- **Raio/elevação** — arredondado suave (cards 14px, inputs 10px, sheets 24px, botões pill). Sombra warm-tinted suave ou borda hairline. Sem sombras duras estilo fintech.
- **Movimento** — calmo: 120–320ms, easing suave, fades/slides gentis, press scale 0.98. Sem bounce, sem decoração em loop. Respeitar `prefers-reduced-motion`.
- **Ícones** — **Lucide** (linha 2px arredondada), via CDN: `<i data-lucide="name"></i>` + `lucide.createIcons()`. Não desenhar SVG à mão; não usar emoji/unicode como ícone.
- Sem gradientes decorativos, sem padrões densos. Única superfície rica: bloco de total no dashboard em teal escuro.

### Vocabulário semântico

Manter esses termos consistentes em templates, variáveis Python e comentários:

- **Status da dívida:** `cadastrada · em_atraso · com_proposta · negociando · acordo_ativo · paga · arquivada`
- **Prioridade:** `resolver · negociar · acompanhar · esperar`
- **Situação financeira:** `safe · warning · critical` (implementado em `rules.py`)
- **Tom de feedback:** `safe · attention · caution · critical · info`

### Acessibilidade (inegociável)

Contraste AA em texto · touch targets ≥44px · significado nunca apenas por cor · focus ring visível · `prefers-reduced-motion` respeitado · linguagem simples · uma ação primária clara por tela · modo discreto mascara valores (`R$ ••••`) e nomes de credores.

---

## Arquivos residuais (ignorar)

`frontend/` (Next.js) é versão anterior descartada da stack. A aplicação ativa é o projeto Django na raiz; `backend/` contém o serviço Node.js da integração Claude.

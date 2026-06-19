# 💸 DebtFree AI — Hackathon Grupo 5

Assistente de IA para superendividados: prioriza dívidas, explica direitos pela Lei do Superendividamento e gera cartas de negociação em linguagem simples.

## Time

| Nome  | Papel                    |
|-------|--------------------------|
| Flora | Designer + Conteúdo IA   |
| Bia   | Dev Frontend (templates) |
| Tadeu | Dev Frontend (templates) |
| Luis  | Dev Backend + IA         |
| José  | QA + Demo                |

## Stack

**Uma base só:** Django 5 + Django Templates + Claude API

## Estrutura

```
hackathon-grupo-5/
├── manage.py
├── requirements.txt
├── .env.example
├── config/               → settings, urls, wsgi
└── debtfree/             → app principal
    ├── rules.py          → priorização de dívidas (Lei 14.181/2021)
    ├── claude_service.py → integração com Claude API
    ├── views.py          → home, onboarding, analyze, letter
    ├── urls.py
    └── templates/debtfree/
        ├── base.html
        ├── home.html
        ├── onboarding.html   → formulário de dívidas
        ├── dashboard.html    → análise + ranking + plano de ação
        ├── letter.html       → carta de negociação
        └── partials/
            └── debt_row.html
```

## Como rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis
cp .env.example .env
# editar .env e adicionar ANTHROPIC_API_KEY

# 3. Rodar
python manage.py runserver
```

Acesse: http://localhost:8000

## Fluxo do usuário

1. **Home** → CTA para começar
2. **Onboarding** → preenche renda + dívidas
3. **Dashboard** → situação (verde/amarelo/vermelho), ranking de prioridades, plano de ação, direitos legais
4. **Carta** → gera carta de negociação personalizada para qualquer dívida

## Problema que resolvemos

Brasil tem ~70 milhões de inadimplentes. A maioria não sabe por onde começar, quais dívidas priorizar ou quais direitos tem pela [Lei 14.181/2021](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm).

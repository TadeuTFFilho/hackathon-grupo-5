# 💸 DebtFree AI — Hackathon Grupo 5

Assistente de IA para superendividados: prioriza dívidas, explica direitos pela Lei do Superendividamento e gera cartas de negociação em linguagem simples.

## Time

| Nome  | Papel              |
|-------|--------------------|
| Flora | Designer + Conteúdo IA |
| Bia   | Dev Frontend       |
| Tadeu | Dev Frontend       |
| Luis  | Dev Backend + IA   |
| José  | QA + Demo          |

## Estrutura

```
hackathon-grupo-5/
├── frontend/       → Next.js (Bia + Tadeu)
├── backend/        → Node.js + Express + Claude API (Luis)
├── design/         → Personas, assets, copy (Flora)
├── qa/             → Casos de teste e roteiro de demo (José)
└── docs/           → Regras de negócio e decisões técnicas
```

## Como rodar

### Backend
```bash
cd backend
cp .env.example .env   # adicionar ANTHROPIC_API_KEY
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Problema que resolvemos

Brasil tem ~70 milhões de inadimplentes. A maioria não sabe por onde começar, quais dívidas priorizar ou quais direitos tem pela [Lei 14.181/2021](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm).

**DebtFree AI** recebe as dívidas do usuário, analisa a situação, prioriza o que pagar primeiro e gera uma carta de negociação personalizada — tudo com IA.

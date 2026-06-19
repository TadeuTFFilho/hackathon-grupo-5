# CLAUDE.md — Passo Design System

> This is the **Passo design system project** (it has `_ds_manifest.json` at root). You are *authoring* the system here, not consuming it. The compiler regenerates `_ds_bundle.js`, `_ds_manifest.json`, and `_adherence.oxlintrc.json` on every turn — **never write those files by hand.** After editing sources, run `check_design_system` and fix what it reports.

Full design guide & manifest: **`readme.md`**. Downloadable Agent-Skill front matter: **`SKILL.md`**. This file is the quick orientation that loads into every conversation.

---

## What Passo is

A calm, mobile-first product for Brazilians dealing with debt / *superendividamento*. It helps people organize debts, understand priorities, simulate negotiation offers, and learn their rights — to take **the next possible step** without compromising essentials. It must feel like **a safe pause in the middle of pressure** — never a bank, a debt collector, or a miracle promise.

> "Passo" is a **working name** (final naming is a later step per the brief). Built entirely from the written brand brief — there is no upstream codebase or Figma. Persona: **Mariana**, 38, Guarulhos, ~R$2.800/mo, multiple debts, solves things on her phone, fears accepting an offer she can't keep.

---

## Voice & content rules (as important as the visuals)

- Tone: **calma, direta, acolhedora, didática, transparente, não julgadora.** Lower anxiety; never shame.
- Address the user as **"você"**; speak *with* them — use **"vamos"**. Never cobrança imperative.
- **Sentence case** everywhere (titles, buttons, labels). UPPERCASE only on tiny eyebrow labels.
- **No emoji** in UI/copy. Icons do the visual work.
- Money is BRL: `R$ 1.240,90` (comma decimal, dot thousands), tabular numerals.
- Errors **guide** ("Você pode revisar antes de salvar"), never scold. Every recommendation answers **"por que estou vendo isso?"**. The AI's reading is always **correctable** before saving.
- Prefer plain words: "Valor total" (not *saldo consolidado*), "Dívida em atraso" (not *inadimplência ativa*), "Parcela que cabe no mês" (not *capacidade de pagamento*), "Gastos essenciais" (not *mínimo existencial*).
- Avoid: "Você está devendo" · "Sua situação é grave" · "Regularize imediatamente" · "Limpe seu nome agora" · "Oferta imperdível / Última chance".
- Always keep the disclaimer available: *"Esta ferramenta oferece orientação informativa e não substitui apoio jurídico ou financeiro especializado."*

---

## Visual foundations

- **Color** — primary calm teal `--color-primary` = `--teal-500` `#2C8377` (verde azulado; **not** bank-blue). Secondary warm sand/peach (`--sand-*`). Warm-gray neutrals (`--warm-*`) — page is `--warm-50`, cards white. Semantic ladder `safe→attention→caution→critical→info`; **red is rare and never a dominant surface**. **Meaning is never carried by color alone** — always pair with icon + label.
- **Type** — one family, **Plus Jakarta Sans** (loaded via Google Fonts in `tokens/fonts.css`; needs self-hosted `.woff2` for production). Mobile-first scale; body ≥14px, labels ≥12px. Money/numbers use `font-variant-numeric: tabular-nums`.
- **Space** — 4px base. Mobile gutter 20px, card padding 16px, section gap 28px, card gap 12px. Touch targets ≥44px.
- **Radius/elevation** — gently rounded (cards 14px, inputs 10px, sheets 24px, buttons/chips pill). Soft warm-tinted shadows or a hairline border. No hard fintech shadows.
- **Motion** — calm: 120–320ms, soft easing, gentle fades/slides, press scale 0.98. No bounce, no looping/pulsing decoration. Respect `prefers-reduced-motion`.
- **Icons** — **Lucide** (rounded 2px line), via CDN, rendered `<i data-lucide="name"></i>` + `lucide.createIcons()`. Never hand-draw SVG icons; no emoji/unicode glyphs.
- **No decorative gradients**, no busy patterns. The one rich surface is the dashboard total block in `--teal-700`.

---

## How the project is built

- **`styles.css`** (root) is the single entry point — only `@import`s. It reaches `tokens/colors.css · typography.css · spacing.css · radius.css · motion.css · fonts.css`. Tokens are base values + semantic aliases (`--color-primary`, `--text-body`, `--surface-card`, `--safe-bg`, …).
- **Components** live in `components/<group>/` as React (`Name.jsx` + sibling `Name.d.ts` + `Name.prompt.md`), one `@dsCard` HTML per directory. Groups: `core/` (Button, IconButton, Badge, Tag) · `forms/` (Input, MoneyInput, Textarea, Select, Checkbox, Radio, Switch, Stepper) · `feedback/` (Alert, Toast, EmptyState, Sheet) · `finance/` (MoneyValue, StatusPill, PriorityTag, CommitmentBar, DebtCard, SimulationVerdict) · `ai/` (ExtractionCard, WhyExplained, Disclaimer) · `navigation/` (TopBar, BottomNav) · `educational/` (Accordion).
- **Consume components** from the compiled bundle: `const { Button, DebtCard } = window.PassoDesignSystem_3d94f8`. Load `_ds_bundle.js` via `<script src>` — never `<script src>` a `.jsx` directly. Read each component's `.prompt.md` for usage.
- **`guidelines/*.card.html`** — foundation specimen cards (Colors, Type, Spacing, Brand) shown in the Design System tab.
- **`ui_kits/app/`** — the interactive reference app: `index.html` + `ScreensOnboarding.jsx` (welcome → goal → income → add-debt) + `ScreensApp.jsx` (dashboard hub, list, detail, simulation, result, plan, educational, profile) + `App.jsx` (shell/routing/phone frame) + `tweaks-panel.jsx` + `data.js`. Copy its patterns for new screens.
- **`assets/`** — `logo.svg`, `logomark.svg`, `logo-on-dark.svg` (the "próximo passo" ascending-path mark).

### UI-kit gotchas (learned)
- **Lucide icons inside React**: render each via the self-contained `LIcon` helper (`window.PassoUI.LIcon`) that owns its own `<i>` through `innerHTML` — do **not** drop `<i data-lucide>` straight into JSX and rely on a global `createIcons()`; React reconciliation fights the swapped-in `<svg>`.
- **Screen layout**: use the shared `Screen` wrapper (`window.PassoUI.Screen`) — scrollable content + **fixed bottom action footer** so the primary CTA stays pinned.
- The app's navigation has two modes exposed as a **Tweak** (`navMode`: `tabbar` 3-item Início/Dívidas/Perfil, or `fluid` no-tabbar). Settings live in the **Perfil** tab (incl. logout, discreet mode), not a top-bar gear.

---

## Semantic vocabulary (keep names consistent)

- **Debt status** (`StatusPill`): `cadastrada · em_atraso · com_proposta · negociando · acordo_ativo · paga · arquivada`
- **Priority** (`PriorityTag`): `resolver · negociar · acompanhar · esperar`
- **Simulation verdict** (`SimulationVerdict`): `safe · tight · not_advised`
- **Tones**: `safe · attention · caution · critical · info`

---

## Accessibility (non-negotiable)

AA text contrast · 44px+ touch targets · meaning never by color alone · visible focus ring · `prefers-reduced-motion` honored · plain language · one clear primary action per screen · discreet mode masks values (`R$ ••••`) and creditor names.

---

## Workflow when editing

1. Make changes in the source files (tokens / components / cards / ui kit).
2. Run **`check_design_system`** — it reports components, cards, tokens, and issues. Fix and re-run until clean.
3. For component cards & the UI kit, the runtime `_ds_bundle.js` recompiles at end of turn — component-driven previews can't be screenshotted mid-turn; verify token-only specimen cards directly.
4. Keep brand voice + visual foundations above. When unsure about scope, change only what's asked and suggest the rest.

*Namespace for `@dsCard` / bundle consumption: `window.PassoDesignSystem_3d94f8`.*

# Modo escuro — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A dark theme for the whole panel, toggled by a ☀/☾ button in the top bar, following the OS theme until the user chooses.

**Architecture:** `data-tema="escuro"` on `<html>` redefines the CSS custom properties of `estilo.css`; a tiny inline script in `index.html` applies the saved/OS theme before first paint; `tema.ts` owns the rule and storage; charts read the current theme for their neutral colors.

**Tech Stack:** React + Vite, plain CSS custom properties, ECharts (echarts-for-react), Vitest.

**Spec:** `docs/superpowers/specs/2026-11-18-modo-escuro-design.md`

## Global Constraints

- Light theme looks exactly as today: every new variable's light value equals the current hard-coded color.
- Pillar, sector, theme and traffic-light colors (`#1B8A4C`, `#D9730D`, `#0B3D91`, `#5B2C83`, `#4B5563`, `#E0A100`, `#C62828`, menu.ts entries) are not changed.
- Dark background is dark blue-grey, not pure black; body text contrast ≥ 4.5:1.
- Storage key `asg_tema`, values `claro` | `escuro`. Excel exports untouched.
- pt-BR copy: button `aria-label` "Usar tema escuro" / "Usar tema claro".

## Review Focus

1. Opening the site in dark mode must not flash light first — Task 25 inline script; checked in Task 26 Step 3 by loading `/` with `asg_tema=escuro`.
2. Text drawn by charts (axis labels, bar values, legends, donut labels) must stay readable on dark — Task 26 Step 1 test + Step 3 screenshots.
3. Status seals (OK/Verificar/Atingida/Abaixo), the index ruler and the upload preview's occurrence rows must keep their meaning in dark — Task 26 Step 3 screenshots of Qualidade and Envio.
4. A stored value other than `claro`/`escuro` (old or tampered) must fall back to the OS theme — Task 25 test `valor_invalido_segue_o_sistema`.
5. Switching theme on a page with charts must recolor the charts without reload — Task 26 Step 3.

---

### Task 25: Theme rule, early apply, toggle and dark palette

**Files:**
- Create: `frontend/src/tema.ts`, `frontend/src/tema.test.ts`
- Modify: `frontend/index.html`, `frontend/src/estilo.css`, `frontend/src/layout/Shell.tsx`

**Interfaces:**
- Produces: `type Tema = 'claro' | 'escuro'`; `temaInicial(salvo: string | null, sistemaEscuro: boolean): Tema`; `aplicarTema(t: Tema): void` (sets `document.documentElement.dataset.tema` and `localStorage.asg_tema`); `useTema(): [Tema, () => void]` (current theme + toggle, re-renders subscribers).

- [ ] **Step 1: Write the failing tests** in `tema.test.ts`

```ts
it('sem escolha salva, segue o sistema', () => {
  expect(temaInicial(null, true)).toBe('escuro')
  expect(temaInicial(null, false)).toBe('claro')
})
it('a escolha salva vence o sistema', () => {
  expect(temaInicial('claro', true)).toBe('claro')
  expect(temaInicial('escuro', false)).toBe('escuro')
})
it('valor_invalido_segue_o_sistema', () => {
  expect(temaInicial('azul', true)).toBe('escuro')
})
```

- [ ] **Step 2: Run** `npx vitest run` in `frontend/`. Expected: FAIL (module `./tema` missing).
- [ ] **Step 3: Implement.**
  - `tema.ts` as in Interfaces; `useTema` keeps module-level state with a listener set (or `useSyncExternalStore`).
  - `index.html` `<head>`: inline script doing the same rule as `temaInicial` (read `localStorage.asg_tema`, else `matchMedia('(prefers-color-scheme: dark)')`) and setting `data-tema`, wrapped in `try`.
  - `estilo.css`: turn each hard-coded light color outside `:root` into a variable defined in `:root` with today's value (e.g. `--superficie-suave: #eef1f2`, `--selo-verde-fundo: #dcefe3`, `--selo-verde-texto: #12673a`, `--selo-amarelo-fundo: #fbefc9`, `--selo-vermelho-fundo: #f8dcdc`, `--selo-vermelho-texto: #9c1f1f`, `--faixa-*`, `--topo-translucido`, `--sombra`, `--sobre-cor: #fff`); then a `[data-tema='escuro']` block with dark values for all variables, plus `color-scheme: dark` so native inputs/scrollbars follow.
  - `Shell.tsx`: button `.tema-alternar` before the user name; shows ☾ in light, ☀ in dark; `aria-label` per Global Constraints.
- [ ] **Step 4: Run** `npx vitest run` and `npm run build`. Expected: PASS (13+ tests), no TS errors.
- [ ] **Step 5: Commit** — `feat: dark theme toggle that follows the system until chosen`

---

### Task 26: Charts follow the theme, and a visual check

**Files:**
- Modify: `frontend/src/components/Grafico.tsx`
- Test: `frontend/src/graficoLayout.test.ts` (or a new `graficoCores.test.ts`)

**Interfaces:**
- Consumes: `useTema()` from Task 25.
- Produces: `coresNeutras(t: Tema): { texto: string; suave: string; linha: string; borda: string }` (exported from a non-component module so Vite fast refresh keeps working).

- [ ] **Step 1: Write the failing test**

```ts
it('coresNeutras muda texto e linhas no escuro e mantém o claro de hoje', () => {
  expect(coresNeutras('claro')).toEqual({ texto: '#1F2933', suave: '#5F6B76', linha: '#E3E7EA', borda: '#fff' })
  const e = coresNeutras('escuro')
  expect(e.texto).not.toBe('#1F2933'); expect(e.linha).not.toBe('#E3E7EA')
})
```

- [ ] **Step 2: Run** `npx vitest run`. Expected: FAIL.
- [ ] **Step 3: Implement** `coresNeutras` and use it in `opcoes(g, largura, cores)` for `textStyle`, axis labels, split lines, bar labels, legend, donut labels and the donut border; `Grafico` passes `coresNeutras(tema)` from `useTema()`. Series/pillar colors unchanged.
- [ ] **Step 4: Run** `npx vitest run`, `npm run build`. Expected: PASS, no TS errors.
- [ ] **Step 5: Check in the browser** (Opera test profile against local dev, as before) in both themes: Login, Visão Geral, Ambiental, Indicadores (search box), Qualidade, Envio with `planilha_demo_com_avisos.xlsx` (lists open), Usuários. Load `/` with `asg_tema=escuro` stored: first screenshot already dark. Click the toggle on Visão Geral: charts recolor without reload. Light screenshots must match today's look.
- [ ] **Step 6: Commit** — `feat: charts follow the light/dark theme`

## Final check

- `npx vitest run` and `npm run build` green; backend untouched.
- PR opened; GitHub Actions `backend` and `frontend` pass; user merges → Vercel publishes; quick look at https://investpi.vercel.app in dark.

# Tela "Investe Piauí" (indicadores ASG da instituição) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Uma tela inicial "Investe Piauí" com três blocos (Nossa gestão, Nossa operação, Nosso impacto). O bloco 2 vem de uma aba nova e opcional, `dInstitucional`, preenchida com dados fictícios na planilha modelo.

**Architecture:** O backend ganha a aba no esquema. Também ganha um módulo `app/calculos/institucional.py`, que avalia os indicadores da sede com a mesma regra de farol de dMetas, e uma página `app/paginas/investe_piaui.py`, que monta a `Pagina` com `secoes` (campo novo, opcional). O frontend desenha as seções no `PaginaPainel`. A rota `/` passa a ser a tela nova e a Visão Geral vai para `/carteira`.

**Tech Stack:** FastAPI + pandas + pydantic, pytest, openpyxl; React + TypeScript (Vite), oxlint.

**Spec:** `docs/superpowers/specs/2026-11-18-investe-piaui-institucional-design.md`

## Global Constraints

- `dInstitucional` é opcional (`obrigatoria=False`). Uma planilha sem ela continua sendo aceita e as 12 checagens não mudam.
- Colunas, nesta ordem: `ID Institucional`, `Pilar`, `Indicador`, `Unidade`, `Formato`, `Polaridade`, `Ano Referência`, `Valor Anterior`, `Valor Atual`, `Meta`, `Limite Atenção`, `Referência GRI`, `Fonte`.
- `Formato` aceita `%`, `n`, `dec` e `R$` (vira `pct`, `num`, `dec` e `brl`; qualquer outro valor vira `num`). `Polaridade` aceita `Maior melhor` ou `Menor melhor`.
- Farol = `metas._status` (Atingida→verde, Atenção→amarelo, Abaixo→vermelho). Sem meta, o card fica sem status.
- Nenhum número das outras telas muda: o Índice ASG Geral continua 68 na base modelo.
- Os filtros valem para os blocos 1 e 3. O bloco 2 ignora os filtros.
- Selo exato: `Dados de demonstração`. É exibido quando qualquer linha tem `Fonte` começando com "Demonstração".
- Textos e código em português, como no resto do projeto.

## Review Focus

1. Planilha sem a aba `dInstitucional` → a tela abre, o bloco 2 aparece vazio com o aviso "A planilha ainda não tem a aba dInstitucional." e os blocos 1 e 3 aparecem normalmente (teste na Task 2).
2. Filtro que não deixa nenhum projeto (`?municipio=Inexistente`) → status 200, o bloco 1 e o bloco 3 sem valor, e o bloco 2 igual ao da carteira inteira (teste na Task 3).
3. `Valor Anterior` vazio → o card aparece sem a comparação com o ano anterior, sem erro (teste na Task 1).
4. Link antigo `/` → abre a tela nova, e a Visão Geral responde em `/carteira` com os filtros levados junto (verificado na Task 4 pelo build e pelo print).
5. Exportar Excel da tela nova → os cards das seções aparecem na aba "Indicadores", com a coluna "Seção" (teste na Task 3).

---

### Task 1: Aba `dInstitucional` (esquema, dados fictícios, cálculo)

**Files:**
- Modify: `backend/app/planilha/esquema.py` (entrada `'dInstitucional'` depois de `'dIndicador'`)
- Modify: `backend/app/calculos/filtros.py` (`TABELAS_SEM_FILTRO` inclui `"dInstitucional"`)
- Modify: `backend/dados/base_modelo.xlsx` (aba nova, gerada por um script de uso único que não é commitado; abrir com openpyxl e acrescentar a aba, sem tocar nas outras)
- Create: `backend/app/calculos/institucional.py`
- Test: `backend/tests/test_institucional.py`

**Interfaces:**
- Produces: `avaliar_institucional(base: Base) -> list[ItemInstitucional]`; `ItemInstitucional(id: str, pilar: str, indicador: str, unidade: str | None, formato: FormatoValor, valor: float | None, anterior: float | None, ano: int | None, meta: float | None, status: Semaforo | None, demonstracao: bool)`. Devolve `[]` quando a aba não existe. A lista vem ordenada por `ID Institucional`.

Dados fictícios: 15 linhas, `INS01`…`INS15`, `Ano Referência` 2026, `Fonte` = `Demonstração (fictício)`. Os valores ficam a critério de quem implementa, mas as linhas fixadas pelos testes são:

| ID | Pilar | Indicador | Formato | Polaridade | Anterior | Atual | Meta | Limite |
|---|---|---|---|---|---|---|---|---|
| INS01 | Ambiental | Consumo de energia da sede | n | Menor melhor | 184 | 162 | 150 | 170 |
| INS07 | Social | Mulheres no quadro de servidores | % | Maior melhor | 0.44 | 0.48 | 0.5 | 0.45 |
| INS13 | Governança | Servidores treinados em ética e integridade | % | Maior melhor | 0.70 | 0.96 | 0.95 | 0.85 |

Cerca de 5 indicadores por pilar, com as unidades da spec (MWh, m³, tCO2e, resmas, %, h/servidor, nº).

- [ ] **Step 1: Write the failing tests** em `test_institucional.py`:
  - `test_modelo_tem_15_indicadores`: `len(avaliar_institucional(base_modelo())) == 15`; ids ordenados.
  - `test_farol_menor_melhor`: INS01 → `valor == 162`, `anterior == 184`, `status == "amarelo"`, `formato == "num"`, `demonstracao is True`.
  - `test_farol_maior_melhor`: INS07 → `"amarelo"`, `formato == "pct"`; INS13 → `"verde"`.
  - `test_sem_aba`: base sem `dInstitucional` → `[]`.
  - `test_anterior_vazio`: `Valor Anterior` de INS01 = None → `anterior is None`, sem exceção.
  - `test_sem_meta`: `Meta` de INS01 = None → `status is None`.
  - `test_planilha_sem_aba_e_aceita`: `validar_estrutura` de uma base sem `dInstitucional` não traz erros dessa aba.
  - `test_filtro_nao_altera`: `aplicar_filtros(base, Filtros(municipios=["Inexistente"]))["dInstitucional"]` tem 15 linhas.
- [ ] **Step 2: Run** `cd backend && .venv/Scripts/python -m pytest tests/test_institucional.py -q` → FAIL (import).
- [ ] **Step 3: Implement** o esquema, a aba na planilha modelo, `TABELAS_SEM_FILTRO` e `institucional.py`. Reusar `metas._status` e o mapa `SEMAFORO` de `paginas/comum.py`.
- [ ] **Step 4: Run** a suíte inteira do backend (com o Postgres do Docker no ar) → todos passam, incluindo o teste do download do modelo em `test_api.py` e os índices 68/75/67/62.
- [ ] **Step 5: Commit** `feat: aba opcional dInstitucional com indicadores fictícios da sede`.

### Task 2: Página "Investe Piauí" no backend (`secoes`)

**Files:**
- Modify: `backend/app/paginas/tipos.py`
- Create: `backend/app/paginas/investe_piaui.py`
- Modify: `backend/app/api/painel.py` (`PAGINAS["investe-piaui"] = investe_piaui.montar`)
- Test: `backend/tests/test_paginas_investe_piaui.py`

**Interfaces:**
- Consumes: `avaliar_institucional` (Task 1); `Contexto.card` (`paginas/comum.py`).
- Produces: `Card` ganha `anterior: float | None = None` e `rotulo_anterior: str | None = None` (ex.: `"2025"`). `Secao(id: str, titulo: str, descricao: str | None = None, selo: str | None = None, cards: list[Card] = [], subsecoes: list[Secao] = [])`. `Pagina` ganha `secoes: list[Secao] = []`. `GET /api/painel/investe-piaui` → `Pagina` com `titulo="Investe Piauí"`, `cards=[]` e `secoes` com ids `gestao`, `operacao` e `impacto`.

Conteúdo das seções:
- `gestao`: os cards `% Contratos Fiscalizados`, `% Recomendações Atendidas`, `% Execução Orçamentária`, `% Prestação de Contas Atualizada`, `% Colaboradores Treinados Integridade`, `Tempo Médio Resposta dias` e `Casos Fraude ou Corrupção`, pelo `ctx.card`.
- `operacao`: `selo="Dados de demonstração"` (quando algum item tiver `demonstracao`); uma subseção por pilar (Ambiental, Social, Governança, nessa ordem; um pilar sem itens não aparece). Cada card tem `id = ID Institucional`, título "Indicador (Unidade)", `anterior` e `rotulo_anterior = str(ano - 1)`. Sem a aba: `cards=[]`, `subsecoes=[]` e `descricao` = "A planilha ainda não tem a aba dInstitucional."
- `impacto`: `Investimento Previsto`, `Empresas Confirmadas`, `Empregos Diretos Gerados` e `Emissões Evitadas tCO2e`.

- [ ] **Step 1: Write the failing tests** (fixtures `cliente`, `com_versao` e `h_leitor`, como em `test_paginas_pilares.py`):
  - `test_tres_secoes`: ids `["gestao", "operacao", "impacto"]`; `operacao.selo == "Dados de demonstração"`; os títulos das subseções são `["Ambiental", "Social", "Governança"]`; 15 cards ao todo.
  - `test_card_institucional`: o card `INS01` tem `valor 162`, `anterior 184`, `rotulo_anterior "2025"` e `status "amarelo"`.
  - `test_gestao_usa_carteira`: o valor de `% Contratos Fiscalizados` em `gestao` é igual ao da página Governança.
  - `test_sem_aba_institucional`: com uma versão salva sem `dInstitucional`, status 200 e `operacao.descricao` igual ao aviso exato.
  - `test_outras_telas_sem_secoes`: `visao-geral` → `secoes == []`.
- [ ] **Step 2: Run** `pytest tests/test_paginas_investe_piaui.py -q` → FAIL (404).
- [ ] **Step 3: Implement** os tipos, a página e o registro em `PAGINAS`.
- [ ] **Step 4: Run** a suíte inteira → passa.
- [ ] **Step 5: Commit** `feat: página Investe Piauí com seções gestão, operação e impacto`.

### Task 3: Filtros e exportação da tela nova

**Files:**
- Modify: `backend/app/exportacao.py` (`_indicadores`)
- Test: `backend/tests/test_paginas_investe_piaui.py`, `backend/tests/test_exportacao.py`

**Interfaces:**
- Consumes: `Secao` (Task 2).
- Produces: a aba "Indicadores" do Excel ganha a 4ª coluna, `Seção`. Ela fica vazia para os cards soltos e recebe o título da seção (ou "Seção · Subseção") para os cards das seções.

- [ ] **Step 1: Write the failing tests:**
  - `test_filtro_vazio_investe_piaui`: `?municipio=Inexistente` → 200; em `gestao` e `impacto`, os valores de `Investimento Previsto` e `Empresas Confirmadas` são `0`, e os percentuais são `None`; os cards de `operacao` são iguais aos da carteira inteira.
  - `test_exportar_investe_piaui`: baixar `investe-piaui` → a aba "Indicadores" tem o cabeçalho `["Indicador", "Valor", "Status", "Seção"]` e uma linha com `Seção == "Nossa operação · Ambiental"`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** a coluna "Seção" em `_indicadores`.
- [ ] **Step 4: Run** a suíte inteira → passa (os testes de exportação que já existem continuam passando).
- [ ] **Step 5: Commit** `feat: exportação e filtros da tela Investe Piauí`.

### Task 4: Frontend — menu, rotas e seções

**Files:**
- Modify: `frontend/src/api.ts` (`Card.anterior`, `Card.rotulo_anterior`, `Secao`, `Pagina.secoes`)
- Modify: `frontend/src/menu.ts` (item `{ rota: '/', rotulo: 'Investe Piauí', cor: COR.geral, pronto: true, painel: true, endpoint: '/api/painel/investe-piaui' }` primeiro; Visão Geral passa para `rota: '/carteira'`)
- Modify: `frontend/src/components/PaginaPainel.tsx` (esconde `linha-kpi` quando não há índice nem cards; desenha `secoes`)
- Create: `frontend/src/components/SecaoPainel.tsx`
- Modify: `frontend/src/components/CardKpi.tsx` (linha "2025: 184 · ▼ 12%" quando `anterior != null`)
- Modify: CSS do projeto (o mesmo arquivo dos estilos de `.cards` e `.card-kpi`)

**Interfaces:**
- Consumes: o JSON da Task 2.

- [ ] **Step 1: Implement.** `SecaoPainel` desenha `h2` com o título, o selo como etiqueta ao lado, a descrição em `p`, a grade `.cards` com os cards e as subseções com `h3`. A variação é `(valor - anterior) / |anterior|` em %, com ▲/▼ e o texto do valor anterior formatado por `valor(anterior, formato)`. A cor da seta é neutra, porque melhor ou pior depende da polaridade e o farol já mostra isso. Precisa funcionar nos modos claro e escuro (usar as variáveis CSS que já existem).
- [ ] **Step 2: Run** `cd frontend && npm run build && npm run lint && npx vitest run` → build ok, lint sem avisos novos e testes passando.
- [ ] **Step 3: Verificar no navegador** (backend e `npm run dev` locais): login, `/` mostra os três blocos e o selo, `/carteira` mostra a Visão Geral, um filtro aplicado muda os blocos 1 e 3 e deixa o bloco 2 igual, e o modo escuro fica legível. Tirar prints.
- [ ] **Step 4: Commit** `feat: tela Investe Piauí no menu, com seções e comparação com o ano anterior`.

### Task 5: README, push e PR

- [ ] **Step 1:** README: uma linha sobre a tela Investe Piauí e a aba opcional `dInstitucional` (dados de demonstração).
- [ ] **Step 2:** Suíte do backend e build do frontend → passam.
- [ ] **Step 3:** Commit, `git push -u origin investe-piaui-institucional` e PR para `main` com os prints. Pegar o link de pré-visualização da Vercel no PR. **Não fazer merge.**

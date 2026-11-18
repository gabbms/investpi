# Simulador de pesos das metas — design (curto)

## Intenção

Deixar o pessoal da Investe entender e discutir o Índice ASG mexendo nos pesos das 24 metas e vendo na hora o efeito ("e se fraude pesasse 5?"), sem tocar nos números oficiais. Quando o grupo decidir novos pesos, o administrador grava pelo site, sem editar a planilha, com histórico e volta.

## Objetivos

- Tela nova **"Simulador de pesos"** no menu (grupo de cima, depois de "Qualidade dos dados"), para leitor e admin.
- Topo: Índice ASG Geral e os três pilares, **oficial × simulado** lado a lado (ex.: "68 → 65", com a cor de cada faixa).
- Tabela das 24 metas, agrupadas por pilar: indicador, atingimento (nota 0–1, com o status), peso oficial, **peso simulado** (campo editável). Linhas com peso alterado ficam destacadas.
- Resultado recalcula ao editar (sem botão "calcular"); botão **"Restaurar pesos oficiais"**.
- Respeita os filtros do topo, como as demais telas.
- Admin: botão **"Salvar como nova versão"** → cria uma versão igual à ativa, só com a coluna `Peso` de `dMetas` trocada; nome do arquivo na versão: `pesos ajustados (a partir da versão N)`. Aparece no Histórico e pode ser revertida por "Ativar".
- Faixa "Simulação — não altera os números oficiais" sempre visível na tela.

## Não-objetivos

- Simulação valer para outras telas (opção C descartada).
- Peso de pilares no Índice Geral e peso de projetos (ideias 3 e 4, ficam para conversa com a Investe).
- Exportar a simulação para Excel.
- Guardar simulações por usuário.

## Antiobjetivos

- Qualquer tela oficial mostrar número simulado.
- Leitor conseguir gravar pesos.
- Com os pesos da planilha, o simulador mostrar algo diferente de 68 / 75 / 67 / 62.

## Abordagens

| | Onde | Troca |
|---|---|---|
| **A — tela própria (escolhida)** | "Simulador de pesos" no menu | Painel oficial intacto; comparação explícita |
| B — dentro de Metas ASG | Coluna Peso editável | Uma tela com dois modos; print pode circular com número simulado |
| C — simulação no site todo | Faixa em todas as telas | Mais trabalho e mais confusão |

## Como (decidido)

- **Regras de peso:** inteiro de 0 a 5; 0 tira a meta do cálculo; cada pilar precisa de pelo menos uma meta com peso > 0 (senão o servidor recusa com mensagem). Cálculo igual ao de hoje (média ponderada × 100; geral = soma dos 3 pilares ÷ 3).
- **Backend:** `avaliar_metas` aceita um mapa opcional `pesos: dict[id_meta, int]` que substitui o `Peso` da planilha; `POST /api/painel/simular-pesos` (leitor/admin, filtros como query) recebe `{pesos}` e devolve oficial e simulado (geral, pilares) mais as metas com atingimento; `POST /api/versoes/pesos` (admin) recebe `{pesos}`, copia a base ativa sem filtros, troca `Peso` e grava com `salvar_versao`. Pesos de IDs inexistentes → 400.
- **Frontend:** página própria `Simulador.tsx` (não a genérica), estado local dos pesos, chamada ao servidor com atraso curto (~300 ms) após editar; botão de salvar só para admin, com confirmação ("Isso cria a versão N+1 e passa a valer para todos").
- **Testes:** backend — sem pesos alterados devolve 68,15 / 75,4 / 66,8 / 62,2; trocar o peso de "Casos de fraude ou corrupção" muda Governança e Geral para o valor calculado à mão; pilar todo com peso 0 → 400; leitor no salvar → 403; salvar cria versão N+1 ativa com o peso novo e as outras abas iguais. Frontend — vitest das regras de destaque/limites; conferência no Opera.
- Entrega por PR com GitHub Actions; merge pelo usuário publica na Vercel.

## Deixado para quem implementa

- Layout fino da tabela (campos numéricos ou botões −/+) desde que funcione no teclado.

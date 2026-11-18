# Modo escuro — design (curto)

## Intenção

Dar ao painel uma versão com fundo escuro, para quem prefere ou usa em pouca luz, sem perder a leitura das cores dos pilares e do semáforo.

## Objetivos

- Botão ☀/☾ no topo, ao lado do nome do usuário e de "Sair", em todas as telas com o menu.
- Primeira visita: segue o tema do sistema (`prefers-color-scheme`). Depois de um clique, a escolha fica guardada no navegador (`localStorage`, chave `asg_tema`) e vale também na tela de login.
- Sem "piscar" claro ao abrir em modo escuro: o tema é aplicado antes de a página desenhar.
- Gráficos, cartões, tabelas, filtros, selos, régua do índice, prévia de envio e telas de admin legíveis nos dois temas.

## Não-objetivos

- Exportações para Excel (continuam claras).
- Trocar as cores dos pilares, setores, temas ou do semáforo — só tons de apoio (fundos dos selos, texto sobre fundo escuro) ganham versão escura.

## Antiobjetivos

- Texto ou número ilegível em qualquer tela no modo escuro.
- Modo claro mudar de aparência.

## Abordagens

| | Como | Troca |
|---|---|---|
| **Variáveis CSS com um segundo conjunto (escolhida)** | `[data-tema="escuro"]` no `<html>` redefine as variáveis de `estilo.css`; as ~25 cores claras fixas no CSS viram variáveis | Uma folha de estilo só; o modo claro não muda |
| Folha CSS separada para o escuro | Duplicar as regras com cores | Duas fontes de verdade que divergem |
| Biblioteca de temas | Dependência nova | Desnecessária com variáveis já prontas |

Modo de ligar: opção A do usuário (segue o sistema, botão guarda a escolha).

## Como (decidido)

- `frontend/src/tema.ts`: `type Tema = 'claro' | 'escuro'`; `temaInicial(salvo: string | null, sistemaEscuro: boolean): Tema`; `aplicarTema(t)` grava `data-tema` no `<html>` e em `localStorage`.
- `index.html`: script curto no `<head>` que aplica o tema salvo/do sistema antes do React (evita o piscar).
- `estilo.css`: bloco `[data-tema="escuro"]` com os valores escuros; cores fixas claras (fundos de selo, faixa da régua, cabeçalho translúcido, sombras, `#fff`/`#eef1f2`…) passam a ser variáveis com valor claro igual ao atual.
- `Grafico.tsx`: cores de texto, grade e eixos vêm do tema atual; as cores das séries/pilares não mudam.
- Botão em `Shell.tsx` (`aria-label` "Usar tema escuro"/"Usar tema claro").
- Testes vitest para `temaInicial`; conferência visual no Opera nos dois temas (Visão Geral, Ambiental, Indicadores, Qualidade, Envio com a planilha de avisos, Usuários, Login).
- Entrega por PR com os testes do GitHub Actions; merge pelo usuário publica na Vercel.

## Deixado para quem implementa

- Os valores exatos da paleta escura (fundo cinza-azulado escuro, não preto puro), desde que o contraste de texto fique ≥ 4,5:1.

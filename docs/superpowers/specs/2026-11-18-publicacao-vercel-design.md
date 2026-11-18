# Publicação do painel na Vercel + Neon — design (curto)

## Intenção

Deixar o painel num link público e gratuito para o pessoal da Investe Piauí abrir quando quiser e entender como o sistema funciona, sem depender do notebook ligado. O acesso será esporádico (não é uso diário), mas o link é definitivo.

## Objetivos

- Um endereço `https://<nome>.vercel.app` com o painel completo: login, filtros, envio de planilha, versões, usuários, exportações.
- Primeiro acesso depois de dias parado em poucos segundos (não um minuto).
- Custo zero.
- Cada merge na `main` publica sozinho.

## Não-objetivos

- Domínio próprio, alta disponibilidade, dados reais sigilosos (os dados continuam simulados).
- Mudar o jeito de rodar localmente: Docker + dois terminais continuam funcionando igual.

## Antiobjetivos

- As senhas de demonstração do README (repositório público) funcionarem no site publicado.
- O banco local ou os testes passarem a depender da nuvem.

## Abordagens consideradas

| | Como | Troca |
|---|---|---|
| **A — Vercel + Neon (escolhida)** | Telas e API na Vercel (função Python), banco Postgres grátis na Neon | Abre rápido mesmo após dias parado; exige uma "porta de entrada" para a Vercel e configuração de rotas; risco de tempo-limite em planilhas muito grandes |
| B — Render grátis + Neon | Serviço Python comum | Quase sem mudança no código, mas dorme após ~15 min e o primeiro acesso leva ~1 min |
| GitHub Pages | Só páginas estáticas | Não roda a API nem o banco: perderia login, filtros e envio. Descartado |

O usuário escolheu A porque quem abre o link de vez em quando não deve esperar um minuto.

## Como (decidido)

- **Um projeto Vercel** ligado ao repositório `gabbms/investpi`, na raiz.
  - Build do frontend (`frontend/` → `frontend/dist`) servido como páginas estáticas.
  - API: arquivo `api/index.py` que expõe o `app` do FastAPI; `vercel.json` manda `/api/*` para ele e todo o resto para `index.html` (rotas do React).
  - Tempo máximo da função elevado ao limite do plano grátis, para o envio de planilha.
- **Banco Neon** grátis, criado pela integração da Vercel. A URL que a Neon entrega (`postgres://…`) é convertida para o driver do projeto (`postgresql+psycopg://…`) em `config.py`, sem afetar o `.env` local.
- **Carga inicial**: `python -m app.cli inicializar` rodado uma vez do notebook apontando para o banco da Neon (cria tabelas, usuários e a versão 1 a partir de `base_modelo.xlsx`).
- **Senhas novas**: admin e leitor com senhas geradas, e `JWT_SEGREDO` aleatório, guardados só nas variáveis de ambiente da Vercel e entregues ao usuário fora do repositório. Os e-mails podem continuar `admin@asg.local` / `leitor@asg.local`.
- **README**: nova seção "Site publicado" (link, como publicar, aviso de que as senhas do README valem só localmente).
- Mesma origem para telas e API: sem mudança de CORS.

## Quem faz o quê

- **Usuário** (precisa da conta dele): criar conta na Vercel com o GitHub, importar o repositório, adicionar a integração Neon. Claude guia passo a passo.
- **Claude**: o ajuste de código e configuração, testes, carga inicial, conferência do site publicado no navegador.

## Deixado para quem implementa

- Nome exato do projeto/endereço na Vercel.
- Ajuste fino do pool de conexões para funções serverless, se a conferência mostrar erro de conexão.

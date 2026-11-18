# Sistema ASG Web · Investe Piauí (Grupo 3)

Versão web do painel ASG do grupo. Um administrador envia a planilha da base pelo navegador; o sistema confere a estrutura, roda as 12 checagens de qualidade e grava os dados como uma nova versão. Quem tem login vê o painel com os mesmos números do Power BI v3: Visão Geral, Ambiental, Social, Governança, Metas ASG e uma tela para cada setor, com filtros por setor, vice-presidência, status do projeto e município.

É a peça "Sistema" do fluxo *Sistema → Base de dados → Painel BI* do desafio, entregue como MVP. A especificação está em [docs/superpowers/specs/2026-11-17-sistema-asg-web-design.md](docs/superpowers/specs/2026-11-17-sistema-asg-web-design.md).

## O que é preciso ter instalado

- Docker Desktop (para o banco PostgreSQL)
- Python 3.12
- Node.js 24

O PostgreSQL roda num contêiner próprio do projeto, na porta **5433**. Ele não usa nem altera um PostgreSQL que já esteja instalado na máquina.

## Como rodar pela primeira vez

Para baixar o projeto do GitHub:

```powershell
git clone https://github.com/gabbms/investpi.git
cd investpi
```

O `.env`, a `.venv` e o `node_modules` não ficam no GitHub; os passos abaixo criam os três.

Os comandos são para o PowerShell, a partir da pasta do projeto (`investpi`, ou `SistemaWeb` no notebook do grupo). Com o Docker Desktop aberto:

```powershell
# 1. Banco de dados
docker compose up -d db

# 2. Configuração (usuários de demonstração, senha do banco, segredo do login)
Copy-Item .env.example .env

# 3. API (Python)
cd backend
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m app.cli inicializar
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

O comando `inicializar` cria as tabelas, os dois usuários de demonstração e importa a planilha modelo como versão 1. Pode ser rodado de novo sem problema: só cria o que estiver faltando.

Em **outro terminal**, também a partir da pasta do projeto:

```powershell
# 4. Site (React)
cd frontend
npm install
npm run dev
```

Abra **http://localhost:5173** no navegador.

## Rodar no dia a dia (3 terminais)

Depois da primeira vez, basta abrir o **Docker Desktop**, esperar ele terminar de iniciar e usar três terminais do PowerShell, todos a partir da pasta do projeto.

**Terminal 1: banco de dados**

```powershell
docker compose up -d db
```

Esse terminal pode ser fechado depois; o banco continua rodando em segundo plano.

**Terminal 2: API**

```powershell
cd backend
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

Deixe aberto. Ele mostra `Uvicorn running on http://127.0.0.1:8000`.

**Terminal 3: site**

```powershell
cd frontend
npm run dev
```

Deixe aberto e acesse **http://localhost:5173**.

Para parar: `Ctrl+C` nos terminais 2 e 3. Para desligar o banco: `docker compose stop`.

## Site publicado

O painel também está no ar em **https://investpi.vercel.app** (Vercel + banco PostgreSQL gratuito da Neon). Cada merge na `main` publica o site de novo, sozinho.

- Os logins são os mesmos e-mails (`admin@asg.local` e `leitor@asg.local`), mas com **outras senhas**, que ficam só nas configurações da Vercel. Peça ao administrador.
- O site publicado tem o próprio banco: o que se envia lá não aparece no computador local, e vice-versa.

**Como publicar do zero**

1. Em vercel.com, entre com o GitHub, clique em **Add New → Project** e importe este repositório (pasta raiz). As configurações de build vêm do `vercel.json`.
2. No projeto, abra **Storage → Create Database → Neon** (plano gratuito) e conecte a todos os ambientes. Isso cria a variável `DATABASE_URL`.
3. Uma única vez, no computador, carregue o banco da Neon (antes de publicar de novo, para o site já abrir com dados). Defina no terminal, não no `.env`, o `DATABASE_URL` da Neon e as variáveis `ADMIN_EMAIL`, `ADMIN_SENHA`, `LEITOR_EMAIL` e `LEITOR_SENHA`; depois, na pasta `backend`: `.venv\Scripts\python -m app.cli inicializar`. O comando recusa as senhas de demonstração deste README num banco na nuvem.
4. Em **Settings → Environment Variables**, adicione `JWT_SEGREDO` (texto longo e aleatório), `JWT_HORAS=8` e as mesmas `ADMIN_*`/`LEITOR_*`, e publique de novo (**Redeploy**).

As publicações de teste da Vercel (uma por PR aberto) usam o mesmo banco do site oficial, por isso só leem os dados: enviar planilha, salvar pesos, ativar versão e mexer em usuários ficam bloqueados nelas.

## Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `failed to connect to the docker API` | O Docker Desktop ainda não terminou de abrir. Espere e rode de novo. |
| "Erro 404" na tela de login | O site não está alcançando a API. Confira se o terminal 2 está aberto; depois pare o terminal 3 com `Ctrl+C` e rode `npm run dev` de novo. |
| "E-mail ou senha incorretos" com os usuários de demonstração | Os usuários ainda não foram criados. Na pasta `backend`, rode `.venv\Scripts\python -m app.cli inicializar`. |
| "Não foi possível carregar esta tela" ou "Ainda não há dados carregados" | Confira se o banco (terminal 1) e a API (terminal 2) estão rodando. Sem nenhuma versão, rode o `inicializar` ou envie a planilha como administrador. |
| `Port 5173 is already in use` | Já existe um site rodando. Use a aba aberta ou feche o terminal antigo. |
| `Address already in use` na porta 8000 | Já existe uma API rodando. Feche o terminal antigo antes de abrir outro. |

## Usuários de demonstração

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@asg.local | Admin@2026 |
| Leitor | leitor@asg.local | Leitor@2026 |

Valem só no computador local (o site publicado usa outras senhas). As credenciais vêm do arquivo `.env` (copiado de `.env.example`). Para trocar, edite o `.env` antes de rodar `inicializar`.

- **Leitor**: vê todas as telas do painel e usa os filtros.
- **Administrador**: tudo do leitor, mais enviar planilha, ver o histórico de versões, voltar a uma versão anterior e cadastrar, desativar ou redefinir a senha de usuários.

Não existe cadastro aberto nem recuperação de senha por e-mail: quem cria e redefine senhas é o administrador, na tela **Usuários**.

## Como enviar uma planilha

1. Entre como administrador e abra **Enviar planilha** no menu.
2. Se precisar de um ponto de partida, clique em **Baixar planilha modelo**. É a mesma base usada pelo Power BI (`Base_ASG_Grupo3_PowerBI.xlsx`).
3. Clique em **Escolher arquivo .xlsx**. O sistema lê a planilha e mostra a prévia, sem gravar nada ainda:
   - **Erros** (em vermelho) impedem a gravação: aba obrigatória ausente, coluna ausente, texto em coluna numérica, data inválida, código repetido ou vazio, projeto ou empresa que não existe na tabela de referência, ou uma "Medida" em `dMetas` que o sistema não sabe calcular. Corrija a planilha e envie de novo.
   - **Checagens de qualidade C01 a C12** são avisos, as mesmas da página Qualidade dos Dados do Power BI. Elas aparecem com o número de registros afetados, mas não impedem a gravação.
4. Sem erros, clique em **Confirmar envio**. A planilha vira uma nova versão, que passa a ser a versão em uso. A gravação é feita numa única transação: ou a versão entra inteira, ou nada muda.

O sistema encontra as abas e as colunas pelo nome do cabeçalho (linha 1). Colunas e abas a mais são ignoradas. Linhas totalmente vazias no fim da aba são descartadas. "Sim"/"Não" são aceitos com qualquer combinação de maiúsculas e espaços. A aba `dIndicador` é opcional; sem ela, os cards ficam sem o texto de explicação do "?".

**Histórico de versões** lista todos os envios, inclusive os rejeitados, e permite **ativar** uma versão anterior.

## Testes

Com o banco no ar (`docker compose up -d db`):

```powershell
cd backend
.venv\Scripts\python -m pytest -q
```

```powershell
cd frontend
npx vitest run
```

Os testes do backend usam um banco separado (`asg_test`), criado automaticamente pelo contêiner. Eles conferem os valores do Power BI v3 para a base atual: investimento de R$ 42,83 bi, 48 projetos, Índice ASG 68 e as metas 6/6/12. Também conferem o filtro Mineração, a importação (planilhas com erro não mudam a versão em uso) e as permissões (o leitor recebe recusa ao enviar planilha, ativar versão ou criar usuário).

## Organização do código

```
SistemaWeb/
├── docker-compose.yml        banco PostgreSQL 17 (porta 5433)
├── .env.example              configuração e usuários de demonstração
├── backend/                  API em FastAPI (Python)
│   ├── app/planilha/         leitura da planilha, esquema das abas e validação
│   ├── app/calculos/         medidas DAX portadas, filtros, metas, Índice ASG, checagens
│   ├── app/paginas/          conteúdo de cada tela (cards, gráficos, tabelas)
│   ├── app/api/              rotas HTTP (login, envio, versões, painel, usuários)
│   ├── app/repositorio.py    gravação das versões no banco
│   ├── dados/base_modelo.xlsx  planilha modelo e carga inicial
│   └── tests/
└── frontend/                 site em React + ECharts
    └── src/                  telas, componentes e formatação pt-BR
```

Os cálculos seguem as medidas DAX do Power BI v3 (`PowerBI/Painel_ASG_v3/.../_Medidas.tmdl`). Cada medida em [backend/app/calculos/medidas.py](backend/app/calculos/medidas.py) tem o mesmo nome da medida DAX correspondente.

## Fora do MVP

Ficaram para depois: Panorama Piauí (dados públicos ANEEL/ANM), Relações Internacionais, Evolução mensal, Ficha do Projeto e Catálogo de Indicadores; restrição de visualização por vice-presidência; envio separado por área; publicação na internet (o MVP roda localmente); recuperação de senha por e-mail.

Os dados da base são simulados pelo grupo, exceto o fator de emissão do MCTI.

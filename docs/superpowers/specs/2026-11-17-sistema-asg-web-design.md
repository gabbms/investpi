# Sistema ASG Web · Investe Piauí (Grupo 3) — Design

Data: 17/11/2026 · Entrega do MVP: 18/11/2026 à tarde

## 1. Intenção

O grupo já tem um painel em Power BI (`PowerBI/Painel_ASG_Investe_PI_v3.pbix`) que acompanha 48 projetos de Energia Renovável, Hidrogênio Verde, Mineração e Sustentabilidade Ambiental, compara 24 indicadores com metas e calcula um Índice ASG ponderado pela materialidade. Hoje os dados entram por uma planilha Excel aberta no Power BI.

O sistema web é a peça **"Sistema"** do fluxo de produtos ASG do desafio (*Sistema de Governança de Dados: Sistema → Base de dados → Painel BI*) e atende à entrega **"Protótipo Funcional ou MVP"**. Ele faz o mesmo que o painel, mas num site: um administrador envia a planilha pelo navegador, o sistema valida e guarda os dados, e todas as pessoas com login veem o painel atualizado, com filtros, métricas e gráficos.

O grupo vai apresentar o MVP para a banca (ICEV × Investe Piauí) e todos terão acesso ao código.

## 2. Objetivos, não-objetivos e antiobjetivos

**Objetivos (MVP)**
- Login com dois perfis: **administrador** e **leitor**.
- Envio da planilha (só administrador), com validação antes de gravar e resultado das 12 checagens de qualidade.
- Cada envio vira uma **versão completa** dos dados; o painel mostra a versão ativa; o histórico guarda todas e permite voltar a uma anterior.
- Painel com as telas: Visão Geral, Ambiental, Social, Governança, Metas ASG, e uma tela por setor (Energia Renovável, Hidrogênio Verde, Mineração, Sustentabilidade Ambiental).
- Filtros por Setor, Vice-Presidência, Status do Projeto e Município, valendo em todas as telas do painel.
- Os números do site **iguais aos do Power BI v3** para a mesma planilha.
- Cadastro de usuários pelo administrador.

**Não-objetivos (fora do MVP, podem vir depois)**
- Panorama Piauí (dados públicos ANEEL/ANM), Relações Internacionais, Evolução mensal, Ficha do Projeto, Catálogo de Indicadores.
- Restrição de visualização por Vice-Presidência (todo leitor vê todos os setores).
- Envio separado por área (só o administrador envia, e sempre a planilha completa).
- Publicação na internet: o MVP roda localmente.
- Recuperação de senha por e-mail (o administrador redefine).

**Antiobjetivos (seria fracasso mesmo funcionando)**
- Números diferentes dos do Power BI para a mesma base.
- Um envio com erro estrutural apagar ou corromper a versão em uso.
- Um leitor conseguir enviar planilha, trocar a versão ativa ou cadastrar usuários.
- Senhas guardadas sem criptografia.

**Prioridade de construção** (se o tempo apertar, corta-se de baixo para cima):
1. Login, envio com validação e Visão Geral com números iguais aos do Power BI.
2. Ambiental, Social, Governança e Metas ASG.
3. Histórico de versões com reativação e cadastro de usuários.
4. As quatro telas de setor.

## 3. Restrições

- Prazo: funcionando até 18/11/2026 à tarde.
- A demonstração para a banca roda **neste notebook** (o mesmo da construção). Não é preciso preparar instalação em outra máquina.
- Construído pelo Claude nesta sessão, em sequência, seguindo a prioridade acima; o grupo acompanha e lê o código no VS Code.
- Roda em Windows 10 com: Node 24, Python 3.12, Docker 29. O PostgreSQL roda **em contêiner Docker** com credenciais do próprio projeto (não usar a instalação pessoal do PostgreSQL da máquina).
- Interface em português do Brasil, com números no formato brasileiro (R$ 43 bi, 54,2%).
- Dados atuais são simulados (exceto o fator de emissão do MCTI). Os usuários de demonstração e suas senhas ficam documentados no README e no arquivo de exemplo de configuração, nunca no código.

## 4. Abordagens consideradas

| Abordagem | Prós | Contras |
|---|---|---|
| **React + API FastAPI (Python) + PostgreSQL** (escolhida) | Interface livre e interativa; processamento de Excel maduro em Python (pandas); lógica separada da tela, com testes; banco robusto para vários usuários e para transações | Mais partes (frontend, backend, banco) e mais trabalho |
| Streamlit + SQLite | Mais rápido de construir, tudo em Python | Não foi feito para vários usuários e perfis; visual preso ao padrão; SQLite frágil com acessos simultâneos |
| Django + gráficos em JavaScript | Login e administração prontos | Interatividade dos gráficos exige JavaScript à parte; mais pesado de configurar |

**Escolha do grupo:** a primeira, por ser a mais robusta.

## 5. Arquitetura

```
Navegador (React + ECharts)
   │  HTTP/JSON, token de login no cabeçalho
   ▼
API (FastAPI, Python)
   ├─ autenticação e perfis
   ├─ importação: leitura do Excel (pandas/openpyxl) → validação → gravação da versão
   ├─ cálculos: medidas, metas, semáforo, Índice ASG, checagens
   └─ endpoints de dados por tela, com filtros
   ▼
PostgreSQL (Docker)
   ├─ usuários
   ├─ versões (quem enviou, quando, status, resultado das checagens)
   └─ tabelas de dados por versão (espelho das abas da planilha)
```

- `docker compose up` sobe o PostgreSQL. A API e o frontend rodam em modo de desenvolvimento com um comando cada (ou também via compose — decisão do construtor, desde que o README tenha um passo a passo de poucos comandos).
- Pasta do projeto: `Desktop\investepi\SistemaWeb`, com `backend/`, `frontend/`, `docs/` e `docker-compose.yml`. Versionado com Git.

## 6. A planilha de entrada

A planilha aceita é a **mesma da base do Power BI**: `PowerBI/Base_ASG_Grupo3_PowerBI.xlsx`. O sistema localiza cada aba pelo nome e cada coluna pelo nome do cabeçalho (linha 1); colunas extras são ignoradas; abas não listadas são ignoradas.

**Abas obrigatórias no MVP** (colunas exatamente como estão na base hoje):

| Aba | Linhas hoje | Chave |
|---|---|---|
| dEmpresa | 40 | Código Empresa |
| dSetor | 4 | Setor Investe |
| dProjeto | 48 | Código Projeto |
| fAmbiental, fSocial, fTransparencia | 48 cada | Código Projeto (1 por projeto) |
| fEnergia (13), fHidrogenio (12), fMineracao (12), fSustentabilidade (11) | — | Código Projeto (1 por projeto do setor) |
| fFinanceiro | 432 (9 meses × 48) | ID Execução |
| fContratos | 60 | ID Processo |
| fManutencao | 48 | ID Processo |
| fEquipe | 62 | ID Servidor |
| dMetas | 24 | ID Meta |
| dPremissas | 5 | ID Premissa |

**Aba opcional:** dIndicador (82), usada para os textos de explicação dos cards ("?"). Sem ela, os cards ficam sem explicação, mas tudo funciona.

Colunas "Sim/Não" chegam como texto "Sim" ou "Não". Datas chegam como data do Excel. Percentuais chegam como fração (0,95 = 95%).

**Modelo para baixar:** a própria base atual é servida como "planilha modelo" na tela de envio.

## 7. Importação e versões

1. O administrador escolhe o arquivo `.xlsx`.
2. A API lê e valida em duas camadas:
   - **Erros estruturais (bloqueiam):** aba obrigatória ausente, coluna obrigatória ausente, tipo inválido (texto em coluna numérica, data inválida), chave vazia ou repetida, código de projeto ou empresa que não existe na tabela de referência, e, em dMetas, uma "Medida" que não seja uma das 24 que o sistema sabe calcular (decisão do Claude: protege o índice). Alterar Meta, Limite Atenção, Peso ou remover metas é permitido; o índice usa as metas presentes.
   - **Checagens de qualidade C01 a C12 (avisos):** as mesmas regras da aba `dChecagens` e da página Qualidade dos Dados do Power BI. São mostradas com o número de registros afetados e não impedem a gravação.
3. A tela mostra uma **prévia**: linhas lidas por aba, erros e avisos.
4. Sem erros estruturais, o administrador confirma. A versão é gravada **numa única transação**: ou entra inteira, ou não entra nada.
5. A nova versão passa a ser a **ativa**. Apenas uma versão é ativa por vez.
6. **Histórico:** lista de versões (número, data e hora, quem enviou, nome do arquivo, linhas por aba, avisos, ativa ou não). O administrador pode **reativar** uma versão anterior.

Envios com erro estrutural não viram versão; o resultado da tentativa pode ficar registrado no histórico como "rejeitado" (decisão do construtor).

Na primeira execução, um comando de carga inicial importa a base atual como versão 1, para o painel já abrir com dados.

## 8. Perfis e login

| Perfil | Pode |
|---|---|
| Administrador | Tudo do leitor + enviar planilha, ver e reativar versões, cadastrar, desativar e redefinir senha de usuários |
| Leitor | Ver todas as telas do painel e aplicar filtros |

- Login por e-mail e senha; senha com hash forte (bcrypt ou argon2); sessão por token com expiração (ex.: 8 horas).
- Sem cadastro aberto: só o administrador cria usuários.
- O primeiro administrador é criado por comando ou variável de ambiente na inicialização.
- Usuários de demonstração (1 administrador, 1 leitor) criados pela carga inicial, com credenciais no README.

## 9. Cálculos

**Fonte da verdade:** as medidas DAX do Power BI v3, em `PowerBI/Painel_ASG_v3/Painel_ASG_Investe_PI_v3.SemanticModel/definition/tables/_Medidas.tmdl`, e a explicação em `PowerBI/Documentacao/Documentacao_Tecnica.pdf` (seção 5 e Anexo A). O backend reimplementa em Python as medidas usadas pelas telas do MVP, com a mesma lógica.

Regras principais:
- **Filtros:** aplicados primeiro em dProjeto (Setor, Município, Status) e em dSetor (Vice-Presidência); as tabelas f* entram só para os projetos filtrados. dEmpresa é filtrada pelas empresas dos projetos filtrados.
- **Financeiro mensal:** Orçamento Previsto = soma do orçamento **no último mês** disponível (não somar os 9 meses); Empenhado, Liquidado e Pago = soma de todos os meses (são valores do mês). % Prestação de Contas = proporção no último mês.
- **Semáforo de cada meta (dMetas):** Maior melhor: verde se valor ≥ meta; amarelo se ≥ limite; vermelho abaixo. Menor melhor: verde se ≤ meta; amarelo se ≤ limite; vermelho acima.
- **Atingimento (0 a 1):** maior melhor → min(valor ÷ meta, 1) (meta 0 → 1); menor melhor → 1 se ≤ meta, 0,5 se ≤ limite, 0 acima.
- **Índice do pilar** = Σ(peso × atingimento) ÷ Σ(peso das metas com valor) × 100. **Índice ASG Geral** = média dos três pilares.
- **Emissões evitadas:** já vêm calculadas na aba fAmbiental (o site não recalcula).

**Valores de aceitação** (base atual, sem filtros): Investimento Previsto R$ 42,83 bi · 48 projetos · 17 empresas confirmadas · 7.236 empregos diretos gerados · Emissões evitadas 3.477.889 tCO2e · Índice Ambiental 75 · Social 67 · Governança 62 · Índice ASG Geral 68 · Metas: 6 atingidas, 6 em atenção, 12 abaixo (25%) · Contratos fiscalizados 55,0% · Licença válida 54,2% · Execução orçamentária 24,8% · Taxa de frequência de acidentes 2,12 · 12 de 12 checagens OK. Com filtro Setor = Mineração: 12 projetos, R$ 5,33 bi.

## 10. Telas

Layout comum: barra lateral esquerda com o menu nas cores dos pilares (Ambiental #1B8A4C, Social #D9730D, Governança #0B3D91, Metas #5B2C83, Visão Geral #4B5563) e os quatro setores; barra de filtros no topo das telas do painel; nome do usuário e sair no canto. Cards com semáforo (verde #1B8A4C, amarelo #E0A100, vermelho #C62828) quando o indicador tem meta, e um "?" com a explicação vinda de dIndicador/dMetas.

| Tela | Conteúdo mínimo (espelha a página equivalente do Power BI v3) |
|---|---|
| Login | e-mail, senha |
| Visão Geral | Cards: Investimento Previsto, Qtd Projetos, Empresas Confirmadas, Empregos Diretos Gerados, Emissões Evitadas, Índice ASG Geral · Barras: investimento por setor · Barras: investimento por município (cor = setor) · Colunas: índice por pilar e setor · Rosca: projetos por status |
| Ambiental | Índice Ambiental · Cards: Emissões CO2, Emissões Evitadas, Remoção de Carbono, Créditos de Carbono, Área Preservada, % Licença Válida · Emissões geradas × evitadas por setor · Água e resíduos por setor · Licenciamento, AIA e tecnologia limpa por setor |
| Social | Índice Social · Cards: Empregos Diretos Gerados, % Gerados vs Previstos, % Emprego Local, % Mulheres, Beneficiários, Taxa de Frequência de Acidentes · Empregos previstos × gerados por setor · Beneficiários por município · Tabela por projeto |
| Governança | Índice Governança · Cards: % Execução Orçamentária, Índice Execução Financeira, % Contratos Fiscalizados, % Recomendações Atendidas, % Riscos Mitigados, Casos de Fraude · Orçamento / % empenhado / % liquidado / % pago · Transparência por projeto · Tabela de contratos |
| Metas ASG | Cards: % metas atingidas, atingidas, em atenção, abaixo · Três tabelas (uma por pilar): Indicador, Peso, Atual, Meta, Status colorido |
| Energia Renovável | Cards: investimento, capacidade MW, geração MWh, fator de capacidade, % renovável no consumo · Capacidade por fonte · Tabela de projetos |
| Hidrogênio Verde | Cards: investimento, capacidade de eletrólise, produção H2, intensidade energética, % renovável nos eletrolisadores · Produção por produto final · Destino da produção · Tabela |
| Mineração | Cards: investimento, produção ROM, faturamento, intensidade hídrica, % tecnologia limpa · Valor de venda por substância · Tabela de conformidade ambiental |
| Sustentabilidade Ambiental | Cards: investimento, área de intervenção, remoção de carbono, créditos de carbono · Área por tipo de iniciativa · Tabela de projetos |
| Enviar planilha (admin) | Escolher arquivo · baixar modelo · prévia com linhas por aba, erros e avisos · confirmar |
| Histórico de versões (admin) | Tabela de versões · reativar |
| Usuários (admin) | Lista, criar, desativar, redefinir senha, escolher perfil |

## 11. Testes e verificação

- **Testes automáticos dos cálculos:** importar a base atual e conferir todos os valores de aceitação da seção 9, inclusive com o filtro Mineração.
- **Testes da importação:** planilha válida grava versão; aba ausente, coluna ausente, chave repetida e código inexistente são rejeitados sem alterar a versão ativa.
- **Testes de permissão:** leitor recebe recusa ao enviar planilha, ativar versão ou criar usuário.
- **Verificação manual no navegador:** login dos dois perfis, envio com prévia, cada tela, filtros, reativação de versão.

## 12. Entregáveis

- Código em `SistemaWeb/` com Git.
- `README.md`: pré-requisitos, como subir (poucos comandos), usuários de demonstração, como enviar uma planilha.
- Arquivo de exemplo de configuração (`.env.example`).

## 13. Deixado para o construtor

Organização interna do código, bibliotecas auxiliares (ORM, migrações, cliente HTTP, gerenciador de estado), formato exato dos endpoints, modelagem das tabelas por versão (tabelas espelho com `versao_id` ou outra forma equivalente, desde que a gravação seja transacional), estilo visual fino dentro das cores definidas, e se a API e o frontend também rodam no Docker.

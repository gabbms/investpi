# Dicionário de Dados

Sistema ASG Web · Investe Piauí (Grupo 3). Versão em Excel: [Dicionario_de_Dados.xlsx](Dicionario_de_Dados.xlsx).

- A base é uma planilha Excel (`backend/dados/base_modelo.xlsx`): cada aba é uma tabela e a linha 1 tem os nomes das colunas.
- Prefixo **d** = dimensão (cadastros). Prefixo **f** = fato (números medidos). As tabelas f* ligam em `dProjeto[Código Projeto]`.
- No envio, o sistema confere abas e colunas obrigatórias, tipos, chaves sem repetição, códigos que existem na tabela de referência e valores permitidos.
- Os dados da planilha modelo são **simulados pelo Grupo 3** (premissa P05). A aba `dInstitucional` traz **dados de demonstração**.
- Abas de apoio do Power BI que o sistema web não lê: LEIA-ME, dTemaMaterial, fEvolucaoASG, dChecagens, fUsinasPI, fCFEM_PI, dFontesDados, dPerfisAcesso.

## Tabelas

| Tabela | Conteúdo | Obrigatória | Chave | Linhas | Origem | Responsável | Periodicidade |
|---|---|---|---|---|---|---|---|
| dEmpresa | Uma linha por empresa investidora ou parceira da Investe Piauí. | Sim | Código Empresa | 40 | CRM de atração de investimentos | Diretoria Comercial / Escritórios internacionais | Mensal |
| dSetor | Os 4 setores do tema do Grupo 3 e a Vice-Presidência responsável por cada um. | Sim | Setor Investe | 4 | Estrutura da Investe Piauí | Gerência ASG | Quando mudar |
| dProjeto | Tabela central: uma linha por projeto acompanhado. As tabelas f* ligam aqui pelo Código Projeto. | Sim | Código Projeto | 48 | Carteira de projetos | Vice-Presidências setoriais | Mensal |
| fAmbiental | Indicadores ambientais comuns aos 4 setores, um registro por projeto. | Sim | Código Projeto | 48 | Relatórios dos empreendedores e licenças (SEMARH) | Vice-Presidência do setor | Mensal |
| fSocial | Empregos, capacitação, comunidades e saúde e segurança do trabalho, por projeto. | Sim | Código Projeto | 48 | Relatórios dos empreendedores | Vice-Presidência do setor | Mensal |
| fTransparencia | Transparência e tempo de resposta, por projeto. | Sim | Código Projeto | 48 | Ouvidoria e portal de transparência | Ouvidoria / Compliance | Mensal |
| fEnergia | Indicadores específicos dos projetos de Energia Renovável. | Sim | Código Projeto | 13 | Relatórios dos empreendedores | Vice-Presidência do setor | Mensal |
| fHidrogenio | Indicadores específicos dos projetos de Hidrogênio Verde. | Sim | Código Projeto | 12 | Relatórios dos empreendedores | Vice-Presidência do setor | Mensal |
| fMineracao | Indicadores específicos dos projetos de Mineração. | Sim | Código Projeto | 12 | Relatórios dos empreendedores | Vice-Presidência do setor | Mensal |
| fSustentabilidade | Indicadores específicos dos projetos de Sustentabilidade Ambiental. | Sim | Código Projeto | 11 | Relatórios dos empreendedores | Vice-Presidência do setor | Mensal |
| fFinanceiro | Execução orçamentária e financeira MENSAL de cada projeto (valores do mês; a soma dá o acumulado). | Sim | ID Execução | 432 | Sistema financeiro / prestação de contas ao TCE-PI | Diretoria Executiva Financeira (DFIN) | Mensal |
| fContratos | Licitações e contratos, com auditorias, denúncias e riscos. | Sim | ID Processo | 60 | SEI! e controles da DCLC | Diretoria Central de Licitações, Compras e Contratos (DCLC) | Mensal |
| fManutencao | Processos de engenharia e manutenção dos projetos. | Sim | ID Processo | 48 | Controles de engenharia | Vice-Presidência do setor | Mensal |
| fEquipe | Servidores da Investe Piauí alocados por projeto e treinamentos de integridade (exibir só agregado: LGPD). | Sim | ID Servidor | 62 | Gestão de pessoas | Gerência de Pessoas / Compliance | Trimestral |
| dMetas | As 24 metas ASG do Grupo 3, com polaridade, limite de atenção e peso no Índice ASG. | Sim | ID Meta | 24 | Política ASG e matriz de materialidade | Gerência ASG / Comitê de Governança ASG | Anual |
| dPremissas | Fatores de emissão e premissas usadas nos cálculos. | Sim | ID Premissa | 5 | MCTI e literatura técnica | Gerência ASG | Anual |
| dIndicador | OPCIONAL. Catálogo dos 82 indicadores, com cálculo, tema material, ODS e referência GRI. | Não (opcional) | ID Indicador | 82 | Política ASG e matriz de materialidade | Gerência ASG | Anual |
| dInstitucional | OPCIONAL. Indicadores ASG da própria Investe Piauí (sede). Na planilha modelo: DADOS DE DEMONSTRAÇÃO. | Não (opcional) | ID Institucional | 15 | Áreas internas da Investe Piauí (RH, administração, compliance) | Gerência ASG | Anual |

## Colunas

### dEmpresa

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Empresa | Texto | Código único da empresa (chave). | Chave: obrigatória e sem repetição | EMP001 |
| Empresa | Texto | Nome da empresa. |  | Nordvind Energi A/S |
| País | Texto | País de origem da empresa. |  | Dinamarca |
| Continente | Texto | Continente do país de origem. |  | Europa |
| Setor Empresa | Texto | Ramo de atuação da empresa. |  | Energia Eólica |
| Setor Investe | Texto | Setor da Investe Piauí em que a empresa atua. |  | Energia Renovável |
| Tipo de Relação | Texto | Natureza da relação com a Investe Piauí (Investimento, Parceria, Cooperação). |  | Investimento |
| Status Relação | Texto | Situação da relação (Confirmado, Em negociação, Em análise, Contato inicial). |  | Confirmado |
| Instrumento Formal | Texto | Documento que formaliza a relação (contrato, memorando etc.). |  | Contrato de Investimento |
| Evento Relacionado | Texto | Evento em que o contato começou. |  | Global Wind Summit |
| Data Primeiro Contato | Data | Data do primeiro contato com a empresa. |  | 14/01/2026 |
| Responsável Contato | Texto | Pessoa da Investe Piauí responsável pelo contato. |  | Carlos Silva |

### dSetor

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Setor Investe | Texto | Nome do setor (chave). Um dos 4 setores do Grupo 3. | Chave: obrigatória e sem repetição | Energia Renovável |
| Vice-Presidência | Texto | Vice-Presidência da Investe Piauí responsável pelo setor (usada no filtro do painel). |  | VP de Energias Renováveis e Hidrogênio Verde |
| ODS Principais | Texto | Objetivos de Desenvolvimento Sustentável ligados ao setor. |  | ODS 7, 9, 13 |
| Tema Material Principal | Texto | Tema da matriz de materialidade mais ligado ao setor. |  | T6 - Eficiência energética e energia limpa |
| Ordem | Número inteiro | Ordem de exibição do setor nas telas e gráficos. |  | 1 |
| Cor | Texto | Cor do setor nos gráficos (código hexadecimal). |  | #1565C0 |

### dProjeto

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código único do projeto (chave). | Chave: obrigatória e sem repetição | PROJ001 |
| Código Empresa | Texto | Código da empresa responsável. Deve existir em dEmpresa. | Deve existir em dEmpresa[Código Empresa] | EMP001 |
| Nome Projeto | Texto | Nome do projeto. |  | Parque Eólico Ventos de Luís Correia |
| Setor Investe | Texto | Setor do projeto: Energia Renovável, Hidrogênio Verde, Mineração ou Sustentabilidade Ambiental. Deve existir em dSetor. | Deve existir em dSetor[Setor Investe] | Energia Renovável |
| Categoria | Texto | Subtipo do projeto dentro do setor (ex.: Eólica, Solar). |  | Eólica |
| Município | Texto | Município do Piauí onde fica o projeto (usado no filtro do painel). |  | Luís Correia |
| Local Mapa | Texto | Endereço para localização no mapa. |  | Luís Correia, Piauí, Brasil |
| Status Projeto | Texto | Situação do projeto (Planejado, Em análise, Em andamento, Concluído). |  | Em andamento |
| Etapa | Texto | Fase atual do projeto (ex.: Licenciamento, Construção, Operação). |  | Construção |
| Investimento Previsto | Número | Valor total de investimento previsto (R$). |  | 780000000 |
| Custo Manutenção Anual | Número | Custo anual estimado de manutenção (R$). |  | 15600000 |
| Investimento Realizado | Número | Valor já investido até a data de referência (R$). |  | 395000000 |
| Valor Meta | Número | Meta física do projeto (ex.: potência a instalar). |  | 150 |
| Valor Realizado | Número | Quanto da meta física já foi realizado. |  | 105 |
| Unidade Meta | Texto | Unidade da meta física (ex.: MW, t/ano). |  | MW |
| Data Referência | Data | Data a que os valores se referem. |  | 30/09/2026 |

### fAmbiental

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Energia Renovável Consumida (MWh) | Número | Energia de fonte renovável consumida pelo projeto. |  | 4200 |
| Emissões CO2 (tCO2e) | Número | Emissões de gases de efeito estufa do projeto, em toneladas de CO2 equivalente. |  | 3900 |
| Emissões Evitadas (tCO2e) | Número | Emissões evitadas em relação à alternativa fóssil (ver dPremissas P01 e P02). |  | 26046.5 |
| Método Emissões Evitadas | Texto | Como as emissões evitadas foram calculadas. |  | Geração anual × fator da rede (P01) |
| Tecnologia Limpa | Sim/Não | O projeto usa tecnologia limpa? |  | Sim |
| Consumo Água (m3) | Número | Água consumida pelo projeto. |  | 2400 |
| Água Reutilizada (m3) | Número | Água reutilizada pelo projeto. |  | 360 |
| Resíduos Gerados (t) | Número | Resíduos sólidos gerados. |  | 85 |
| Resíduos Reciclados (t) | Número | Parte dos resíduos que foi reciclada. |  | 40 |
| Resíduos Destinados Corretamente (t) | Número | Parte dos resíduos com destinação ambientalmente adequada. |  | 80 |
| Licenciamento Ambiental | Sim/Não | O projeto tem processo de licenciamento ambiental? |  | Sim |
| Licença Válida | Sim/Não | A licença ambiental está válida? |  | Sim |
| Plano Recuperação Ambiental | Sim/Não | Existe plano de recuperação de áreas degradadas? |  | Sim |
| Área Recuperada (ha) | Número | Área recuperada, em hectares. |  | 6 |
| Área Preservada (ha) | Número | Área preservada, em hectares. |  | 180 |
| Medidas Mitigação | Sim/Não | Há medidas de mitigação de impactos? |  | Sim |
| Avaliação Impacto Ambiental | Sim/Não | Foi feita avaliação de impacto ambiental? |  | Sim |
| Incidentes Ambientais | Número | Quantidade de incidentes ambientais no período. |  | 1 |

### fSocial

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Empregos Diretos Previstos | Número | Empregos diretos previstos pelo projeto. |  | 600 |
| Empregos Diretos Gerados | Número | Empregos diretos já gerados. |  | 520 |
| Empregos Indiretos Previstos | Número | Empregos indiretos previstos. |  | 1200 |
| Empregos Indiretos Gerados | Número | Empregos indiretos já gerados. |  | 840 |
| Empregos População Local | Número | Empregos diretos ocupados por moradores da região. |  | 310 |
| Empregos Mulheres | Número | Empregos diretos ocupados por mulheres. |  | 95 |
| Empregos PCD | Número | Empregos diretos ocupados por pessoas com deficiência. |  | 22 |
| Trabalhadores Capacitados | Número | Trabalhadores que receberam capacitação. |  | 410 |
| Horas Treinamento (h) | Número | Total de horas de treinamento oferecidas. |  | 9840 |
| Investimento Capacitação | Número | Valor investido em capacitação (R$). |  | 2100000 |
| Programas Sociais Apoiados | Número | Quantidade de programas sociais apoiados. |  | 6 |
| Beneficiários Programas Sociais | Número | Pessoas beneficiadas pelos programas sociais. |  | 2400 |
| Comunidades Beneficiadas | Número | Quantidade de comunidades beneficiadas. |  | 5 |
| Investimento Social | Número | Valor investido em ações sociais (R$). |  | 3200000 |
| Consulta Comunidades | Sim/Não | As comunidades afetadas foram consultadas? |  | Sim |
| Avaliação Impacto Social | Sim/Não | Foi feita avaliação de impacto social? |  | Sim |
| Horas Trabalhadas (h) | Número | Horas trabalhadas no período (base da taxa de frequência de acidentes). |  | 780000 |
| Acidentes Trabalho | Número | Quantidade de acidentes de trabalho. |  | 2 |
| Ações SST | Número | Ações de saúde e segurança do trabalho realizadas. |  | 14 |
| Fornecedores Locais Contratados | Número | Fornecedores do Piauí contratados. |  | 28 |
| Valor Fornecedores Locais | Número | Valor contratado com fornecedores locais (R$). |  | 18500000 |
| Distribuição Territorial | Texto | Como os benefícios se distribuem no território. |  | Equilibrada |
| Reclamações Sociais | Número | Reclamações recebidas das comunidades. |  | 2 |

### fTransparencia

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Tempo Médio Resposta (dias) | Número | Tempo médio de resposta às demandas, em dias. |  | 2.8 |
| Informações Públicas Atualizadas | Sim/Não | As informações públicas do projeto estão atualizadas? |  | Sim |
| Dados Públicos Disponíveis | Sim/Não | Os dados do projeto estão disponíveis ao público? |  | Sim |
| Índice Transparência | Número | Índice de transparência do projeto, de 0 a 1. |  | 0.78 |

### fEnergia

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Fonte | Texto | Fonte de energia do projeto (Eólica, Solar etc.). |  | Eólica |
| Consumo Médio Mensal (MWh) | Número | Consumo médio mensal de energia. |  | 520 |
| Capacidade Instalada (MW) | Número | Potência instalada. |  | 150 |
| Geração Anual (MWh) | Número | Energia gerada no ano. |  | 565000 |

### fHidrogenio

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ004 |
| Produto Final | Texto | Produto final da planta (hidrogênio, amônia etc.). |  | Hidrogênio verde (gasoso) |
| Destino Produção | Texto | Destino da produção (mercado local, exportação). |  | Indústria local e exportação |
| Capacidade Eletrolisador (MW) | Número | Potência dos eletrolisadores. |  | 60 |
| Produção H2 (t) | Número | Hidrogênio produzido, em toneladas. |  | 6446 |
| Consumo Energia Eletrolisador (MWh) | Número | Energia consumida pelos eletrolisadores. |  | 341640 |
| % Renovável Eletrolisador | Número | Parte da energia dos eletrolisadores que é renovável (0 a 1). |  | 0.95 |

### fMineracao

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ007 |
| Substância | Texto | Substância mineral explorada. |  | Lítio (espodumênio) |
| Classe Substância | Texto | Classe da substância (metálica, não metálica). |  | Metálica |
| Porte Empresa | Texto | Porte da mineradora. |  | Grande |
| Faturamento Previsto | Número | Faturamento previsto (R$). |  | 640000000 |
| Produção ROM (t) | Número | Minério bruto extraído (run of mine), em toneladas. |  | 900000 |
| Quantidade Contido | Número | Quantidade de substância contida no minério. |  | 18000 |
| Unidade Contido | Texto | Unidade da quantidade contida. |  | t |
| Valor Venda | Número | Valor de venda da produção (R$). |  | 540000000 |

### fSustentabilidade

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Chave: obrigatória e sem repetição; Deve existir em dProjeto[Código Projeto] | PROJ010 |
| Tipo Iniciativa | Texto | Tipo de iniciativa (economia circular, restauração etc.). |  | Economia circular |
| Área Intervenção (ha) | Número | Área de intervenção, em hectares. |  | 12 |
| Capacidade Processamento Anual | Número | Capacidade de processamento por ano. |  | 120000 |
| Unidade Capacidade | Texto | Unidade da capacidade de processamento. |  | t/ano |
| Remoção Carbono (tCO2e) | Número | Carbono removido da atmosfera. |  | 0 |
| Créditos Carbono (tCO2e) | Número | Créditos de carbono emitidos. |  | 0 |
| Certificação Ambiental | Sim/Não | O projeto tem certificação ambiental? |  | Sim |

### fFinanceiro

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Execução | Texto | Identificador do registro mensal (projeto + mês). | Chave: obrigatória e sem repetição | FIN001-01 |
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Data Referência | Data | Data a que os valores se referem. |  | 01/01/2026 |
| Ano | Número inteiro | Ano do registro. |  | 2026 |
| Mês | Texto | Mês do registro, por extenso. |  | Janeiro |
| Orçamento Previsto | Número | Orçamento total previsto para o projeto (R$). |  | 780000000 |
| Valor Empenhado | Número | Valor empenhado no mês (R$). |  | 31707000 |
| Valor Liquidado | Número | Valor liquidado no mês (R$). |  | 29126000 |
| Valor Pago | Número | Valor pago no mês (R$). |  | 28020000 |
| Prestação Contas Atualizada | Sim/Não | A prestação de contas do mês está em dia? |  | Sim |
| Documentação Completa | Sim/Não | A documentação está completa? |  | Sim |

### fContratos

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Processo | Texto | Identificador do processo de licitação ou contrato (chave). | Chave: obrigatória e sem repetição | LIC001 |
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Modalidade | Texto | Modalidade da licitação. |  | Concorrência |
| Objeto | Texto | Objeto do contrato. |  | Fornecimento e instalação de aerogeradores |
| Empresa Contratada | Texto | Empresa contratada. |  | Aeolus Montagens Ltda. |
| Valor Contratado | Número | Valor do contrato (R$). |  | 310000000 |
| Data Início | Data | Início da vigência. |  | 12/01/2026 |
| Data Fim | Data | Fim da vigência. |  | 31/03/2027 |
| Status Contrato | Texto | Situação do contrato. |  | Em execução |
| Contrato Fiscalizado | Sim/Não | O contrato é fiscalizado? |  | Sim |
| Documentação Completa | Sim/Não | A documentação está completa? |  | Sim |
| Irregularidades Identificadas | Número | Irregularidades encontradas. |  | 2 |
| Irregularidades Corrigidas | Número | Irregularidades já corrigidas. |  | 2 |
| Auditoria Realizada | Sim/Não | Houve auditoria? |  | Sim |
| Recomendações Emitidas | Número | Recomendações emitidas pela auditoria. |  | 3 |
| Recomendações Atendidas | Número | Recomendações já atendidas. |  | 2 |
| Denúncias Recebidas | Número | Denúncias recebidas sobre o contrato. |  | 0 |
| Denúncias Apuradas | Número | Denúncias já apuradas. |  | 0 |
| Fraude ou Corrupção | Sim/Não | Houve caso confirmado de fraude ou corrupção? |  | Não |
| Análise de Riscos | Sim/Não | Foi feita análise de riscos? |  | Sim |
| Riscos Críticos | Número | Riscos críticos identificados. |  | 3 |
| Riscos Críticos Mitigados | Número | Riscos críticos já mitigados. |  | 2 |

### fManutencao

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Processo | Texto | Identificador do processo de manutenção (chave). | Chave: obrigatória e sem repetição | MAN001 |
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Tipo Manutenção | Texto | Preventiva ou corretiva. |  | Preventiva |
| Status Manutenção | Texto | Situação do processo de manutenção. |  | Em andamento |
| Custo Previsto | Número | Custo previsto (R$). |  | 6000000 |
| Custo Realizado | Número | Custo realizado (R$). |  | 2800000 |
| Data Conclusão | Data | Data de conclusão (prevista ou real). |  | 15/12/2026 |

### fEquipe

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Servidor | Texto | Identificador do servidor (sem nome, por LGPD). | Chave: obrigatória e sem repetição | SERV001 |
| Código Projeto | Texto | Código do projeto. Deve existir em dProjeto. | Deve existir em dProjeto[Código Projeto] | PROJ001 |
| Cargo | Texto | Cargo do servidor. |  | Gerente de Projetos Eólicos |
| Área | Texto | Área de atuação. |  | Energia |
| Tipo Vínculo | Texto | Tipo de vínculo (CLT, comissionado etc.). |  | CLT |
| Data Admissão | Data | Data de admissão. |  | 11/03/2024 |
| Situação | Texto | Situação funcional (Ativo, Afastado etc.). |  | Ativo |
| Custo Salarial | Número | Custo salarial mensal (R$). |  | 14500 |
| Treinamento Ética | Sim/Não | Recebeu treinamento em ética? |  | Sim |
| Horas Treinamento Ética (h) | Número | Horas de treinamento em ética. |  | 24 |
| Colaboradores Treinados Integridade | Número | Colaboradores do projeto treinados em integridade. |  | 360 |
| Colaboradores Totais | Número | Total de colaboradores do projeto. |  | 420 |
| Treinamentos Integridade | Número | Quantidade de treinamentos de integridade realizados. |  | 4 |

### dMetas

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Meta | Texto | Identificador da meta (META01…META24). | Chave: obrigatória e sem repetição | META01 |
| Pilar | Texto | Pilar ASG da meta: Ambiental, Social ou Governança. | Só Ambiental, Social ou Governança | Ambiental |
| Indicador | Texto | Nome da meta como aparece nas telas. |  | Projetos com licença ambiental válida |
| Medida | Texto | Nome do cálculo que mede a meta (o sistema só aceita as 24 medidas que sabe calcular). | Uma das 24 medidas que o sistema calcula | % Licença Válida |
| Polaridade | Texto | "Maior melhor" ou "Menor melhor". | Só "Maior melhor" ou "Menor melhor" | Maior melhor |
| Meta | Número | Valor-alvo da meta. |  | 1 |
| Limite Atenção | Número | Valor a partir do qual a meta fica em atenção (amarelo) em vez de abaixo (vermelho). |  | 0.8 |
| Formato | Texto | Como o valor é exibido: % (percentual), n (número), dec (decimal), idx (índice). |  | % |
| Tema Material | Texto | Código do tema material (T1…T14) da matriz de materialidade. |  | T5 |
| Peso | Número inteiro | Peso da meta no Índice ASG do pilar (1 = monitoramento, 2 = prioritário, 3 = tema de nota máxima na materialidade). |  | 2 |
| Justificativa | Texto | Por que a meta foi definida assim. |  | Todo projeto em instalação ou operação precisa de licença válida (conformidade legal). |
| Origem da Meta | Texto | Quem propôs a meta. |  | Proposta do Grupo 3 |

### dPremissas

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Premissa | Texto | Identificador da premissa (P01…). | Chave: obrigatória e sem repetição | P01 |
| Premissa | Texto | Descrição da premissa. |  | Fator de emissão da rede elétrica (SIN) · média anual 2025 |
| Valor | Texto | Valor adotado. |  | 0.0461 |
| Unidade | Texto | Unidade do valor. |  | tCO2/MWh |
| Fonte / Justificativa | Texto | Fonte oficial ou justificativa do valor. |  | MCTI, fator médio anual de emissão do SIN para inventários corporativos, ano de 2025 (último ano completo), planilha Inventario_2026_janset.xlsx (gov.br/mcti, atualizada em 16/10/2026). Revisar todo ano. |
| Onde é usada | Texto | Cálculos que usam a premissa. |  | Energia Renovável: Geração Anual × fator. Mineração: Energia Renovável Consumida × fator. |

### dIndicador

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Indicador | Texto | Identificador do indicador (IND01…IND82). | Chave: obrigatória e sem repetição | IND01 |
| Indicador | Texto | Nome do indicador. |  | Investimento em energias renováveis |
| Pilar | Texto | Pilar ASG do indicador. |  | Ambiental |
| Descrição | Texto | O que o indicador mede. |  | Soma do investimento previsto dos projetos de energia renovável. |
| Cálculo | Texto | Como o indicador é calculado. |  | SOMA(Investimento Previsto) |
| Tabela de Origem | Texto | Tabela(s) de onde vêm os dados. |  | dProjeto |
| Medida DAX | Texto | Nome do cálculo correspondente (o mesmo nome no Power BI e no sistema web). |  | Investimento Energia Renovável |
| Tema Material | Texto | Tema material relacionado (T1…T14). |  | T6 |
| ODS | Texto | Objetivo de Desenvolvimento Sustentável relacionado. |  | ODS 7 |
| Referência GRI | Texto | Divulgação das Normas GRI atendida (usada no índice GRI exportado). |  | GRI 203-1 |
| Polaridade | Texto | "Maior melhor" ou "Menor melhor". |  | Maior melhor |
| Página do Painel | Texto | Tela onde o indicador aparece. |  | Energia Renovável |

### dInstitucional

| Coluna | Tipo | Descrição | Regra de validação | Exemplo |
|---|---|---|---|---|
| ID Institucional | Texto | Identificador do indicador da sede (INS01…). | Chave: obrigatória e sem repetição | INS01 |
| Pilar | Texto | Pilar ASG: Ambiental, Social ou Governança. | Só Ambiental, Social ou Governança | Ambiental |
| Indicador | Texto | Nome do indicador da sede. |  | Consumo de energia da sede |
| Unidade | Texto | Unidade do valor (MWh, m³, %, nº…). Aparece no título do card, exceto %. |  | MWh |
| Formato | Texto | Como o valor é exibido: "%", "n", "dec" ou "R$". | Só "%", "n", "dec" ou "R$" | n |
| Polaridade | Texto | "Maior melhor" ou "Menor melhor". | Só "Maior melhor" ou "Menor melhor" | Menor melhor |
| Ano Referência | Número inteiro | Ano a que o Valor Atual se refere. |  | 2026 |
| Valor Anterior | Número | Valor do ano anterior (para a comparação no card). |  | 184 |
| Valor Atual | Número | Valor no ano de referência. |  | 162 |
| Meta | Número | Valor-alvo do indicador. |  | 150 |
| Limite Atenção | Número | A partir deste valor o card fica em atenção (amarelo) em vez de abaixo (vermelho). |  | 170 |
| Referência GRI | Texto | Divulgação GRI relacionada. |  | GRI 302-1 |
| Fonte | Texto | Origem do dado. Começando com "Demonstração", a tela mostra o selo "Dados de demonstração". |  | Demonstração (fictício) |

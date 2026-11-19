# Dicionário de Indicadores e Fórmulas (Índice ASG / score ESG)

Sistema ASG Web · Investe Piauí (Grupo 3). Versão em Excel: [Dicionario_de_Indicadores_e_Formulas.xlsx](Dicionario_de_Indicadores_e_Formulas.xlsx).
Valores calculados sobre a planilha modelo (dados simulados pelo Grupo 3).

## Índice ASG (score ESG)

- **O que é:** O Índice ASG é o SCORE ESG do projeto: uma nota de 0 a 100 que resume quanto das 24 metas ASG (aba dMetas) foi atingido. Existe um índice por pilar (Ambiental, Social, Governança) e o Índice ASG Geral.
- **1. Atingimento de cada meta (0 a 1, ou 0% a 100%):** Polaridade "Maior melhor": atingimento = mínimo(valor ÷ meta; 1). Ex.: meta 100%, valor 55% → 0,55. Polaridade "Menor melhor": 1 se valor ≤ meta; 0,5 se valor ≤ limite de atenção; 0 nos outros casos. Meta sem valor calculado (ex.: filtro sem projetos) fica fora da conta.
- **2. Índice do pilar (0 a 100):** Índice do pilar = 100 × Σ(peso × atingimento) ÷ Σ(peso), somando as metas do pilar que têm valor. Pesos: 1 = monitoramento, 2 = prioritário, 3 = temas de nota máxima na matriz de materialidade (T1, T4, T14).
- **3. Índice ASG Geral (0 a 100):** Índice ASG Geral = (Índice Ambiental + Índice Social + Índice Governança) ÷ 3. Os três pilares pesam igual, independentemente de quantas metas cada um tem.
- **4. Faixas de cor do índice:** ≥ 75 verde · de 50 a 74 amarelo · < 50 vermelho.
- **5. Status (farol) de cada meta:** "Maior melhor": Atingida se valor ≥ meta; Atenção se valor ≥ limite; senão Abaixo. "Menor melhor": Atingida se valor ≤ meta; Atenção se valor ≤ limite; senão Abaixo. Atingida = verde, Atenção = amarelo, Abaixo = vermelho.
- **Valores na planilha modelo:** Índice ASG Geral 68,2 · Ambiental 75,4 · Social 66,8 · Governança 62,2 (na tela, arredondados: 68 · 75 · 67 · 62).
- **Filtros:** Todos os índices respeitam os filtros do painel (setor, vice-presidência, status, município, empresa): são recalculados só com os projetos filtrados.
- **Simulador de pesos:** A tela Simulador de pesos permite testar outros pesos e ver o efeito no índice sem alterar os números oficiais.
- **Onde está no código:** backend/app/calculos/metas.py (atingimento, status e índices) e backend/app/calculos/medidas.py (as medidas). Os nomes das medidas são os mesmos do Power BI (Medida DAX).

## Metas ASG (24) — entram no Índice ASG

| ID | Pilar | Meta | Medida | Polaridade | Valor-alvo | Limite | Formato | Peso | Valor atual | Status | Atingimento |
|---|---|---|---|---|---|---|---|---|---|---|---|
| META01 | Ambiental | Projetos com licença ambiental válida | % Licença Válida | Maior melhor | 100,0% | 80,0% | % | 2 | 54,2% | Abaixo | 54,2% |
| META02 | Ambiental | Projetos com avaliação de impacto ambiental | % Avaliação Impacto Ambiental | Maior melhor | 100,0% | 80,0% | % | 2 | 75,0% | Abaixo | 75,0% |
| META03 | Ambiental | Resíduos com destinação correta | % Resíduos Destinados Corretamente | Maior melhor | 95,0% | 85,0% | % | 2 | 97,5% | Atingida | 100,0% |
| META04 | Ambiental | Resíduos reciclados | % Resíduos Reciclados | Maior melhor | 50,0% | 30,0% | % | 2 | 66,0% | Atingida | 100,0% |
| META05 | Ambiental | Água reutilizada | % Água Reutilizada | Maior melhor | 50,0% | 30,0% | % | 3 | 59,2% | Atingida | 100,0% |
| META06 | Ambiental | Projetos com tecnologia limpa | % Projetos Tecnologia Limpa | Maior melhor | 90,0% | 70,0% | % | 2 | 95,8% | Atingida | 100,0% |
| META07 | Ambiental | Energia renovável nos eletrolisadores | % Renovável nos Eletrolisadores | Maior melhor | 95,0% | 90,0% | % | 2 | 94,8% | Atenção | 99,7% |
| META08 | Ambiental | Incidentes ambientais | Incidentes Ambientais | Menor melhor | 0 | 5 | n | 3 | 13 | Abaixo | 0,0% |
| META09 | Social | Empregos para a população local | % Empregos População Local | Maior melhor | 60,0% | 40,0% | % | 2 | 60,8% | Atingida | 100,0% |
| META10 | Social | Empregos para mulheres | % Empregos Mulheres | Maior melhor | 30,0% | 20,0% | % | 1 | 25,0% | Atenção | 83,2% |
| META11 | Social | Empregos para pessoas com deficiência | % Empregos PCD | Maior melhor | 5,0% | 2,0% | % | 1 | 3,7% | Atenção | 74,6% |
| META12 | Social | Projetos com consulta às comunidades | % Consulta Comunidades | Maior melhor | 100,0% | 80,0% | % | 2 | 62,5% | Abaixo | 62,5% |
| META13 | Social | Projetos com avaliação de impacto social | % Avaliação Impacto Social | Maior melhor | 100,0% | 80,0% | % | 2 | 52,1% | Abaixo | 52,1% |
| META14 | Social | Empregos gerados sobre os previstos | % Empregos Gerados vs Previstos | Maior melhor | 80,0% | 50,0% | % | 2 | 39,3% | Abaixo | 49,1% |
| META15 | Social | Taxa de frequência de acidentes | Taxa Frequência Acidentes | Menor melhor | 2,00 | 4,00 | dec | 1 | 2,12 | Atenção | 50,0% |
| META16 | Governança | Contratos fiscalizados | % Contratos Fiscalizados | Maior melhor | 100,0% | 80,0% | % | 3 | 55,0% | Abaixo | 55,0% |
| META17 | Governança | Recomendações de auditoria atendidas | % Recomendações Atendidas | Maior melhor | 90,0% | 70,0% | % | 3 | 79,2% | Atenção | 88,0% |
| META18 | Governança | Riscos críticos mitigados | % Riscos Críticos Mitigados | Maior melhor | 80,0% | 60,0% | % | 3 | 45,7% | Abaixo | 57,1% |
| META19 | Governança | Prestação de contas atualizada | % Prestação de Contas Atualizada | Maior melhor | 100,0% | 90,0% | % | 2 | 62,5% | Abaixo | 62,5% |
| META20 | Governança | Colaboradores treinados em integridade | % Colaboradores Treinados Integridade | Maior melhor | 90,0% | 75,0% | % | 3 | 84,3% | Atenção | 93,6% |
| META21 | Governança | Denúncias apuradas | % Denúncias Apuradas | Maior melhor | 100,0% | 80,0% | % | 3 | 46,7% | Abaixo | 46,7% |
| META22 | Governança | Índice de transparência | Índice Transparência Médio | Maior melhor | 0,80 | 0,60 | idx | 2 | 0,58 | Abaixo | 73,0% |
| META23 | Governança | Tempo médio de resposta (dias) | Tempo Médio Resposta dias | Menor melhor | 5,00 | 10,00 | dec | 2 | 4,71 | Atingida | 100,0% |
| META24 | Governança | Casos de fraude ou corrupção | Casos Fraude ou Corrupção | Menor melhor | 0 | 0 | n | 3 | 4 | Abaixo | 0,0% |

## Catálogo de indicadores (82)

| ID | Indicador | Pilar | Cálculo | Origem | Tema | ODS | GRI | Valor atual |
|---|---|---|---|---|---|---|---|---|
| IND01 | Investimento em energias renováveis | Ambiental | SOMA(Investimento Previsto) | dProjeto | T6 | ODS 7 | GRI 203-1 | R$ 9,0 bi |
| IND02 | Quantidade de projetos por fonte renovável | Ambiental | CONTAGEM de projetos por Fonte | dProjeto | T6 | ODS 7 | - | 48 |
| IND03 | Capacidade instalada renovável (MW) | Ambiental | SOMA(Capacidade Instalada) | fEnergia | T6 | ODS 7 | GRI-G4 EU1 | 1.905 |
| IND04 | Geração energética anual (MWh) | Ambiental | SOMA(Geração Energética Anual) | fEnergia | T6 | ODS 7 | GRI-G4 EU2 | 5.694.000 |
| IND05 | Fator de capacidade médio | Ambiental | Geração ÷ (Capacidade × 8.760) | fEnergia | T6 | ODS 7 | - | 0,34 |
| IND06 | Percentual de energia renovável no consumo total | Ambiental | Energia Renovável Consumida ÷ (Consumo Médio Mensal × 12) | fEnergia / fAmbiental | T6 | ODS 7 | GRI 302-1 | 75,3% |
| IND07 | Investimento em hidrogênio verde | Ambiental | SOMA(Investimento Previsto) | dProjeto | T6 | ODS 7, 9 | GRI 203-1 | R$ 27,5 bi |
| IND08 | Capacidade de eletrólise (MW) | Ambiental | SOMA(Capacidade do Eletrolisador) | fHidrogenio | T6 | ODS 7, 9 | - | 2.740 |
| IND09 | Produção anual de hidrogênio verde (t) | Ambiental | SOMA(Produção Anual de H2) | fHidrogenio | T6 | ODS 7, 9 | - | 275.909 |
| IND10 | Intensidade energética do hidrogênio (kWh/kg) | Ambiental | Consumo de Energia ÷ Produção | fHidrogenio | T6 | ODS 7 | GRI 302-3 | 54,3 |
| IND11 | Percentual de energia renovável nos eletrolisadores | Ambiental | Σ(Consumo × %Renovável) ÷ Σ(Consumo) | fHidrogenio | T6 | ODS 7 | GRI 302-1 | 94,8% |
| IND12 | Intensidade hídrica do hidrogênio (m³/t H2) | Ambiental | Consumo de Água ÷ Produção Anual de H2 | fHidrogenio / fAmbiental | T4 | ODS 6 | GRI 303-5 | 22 |
| IND13 | Produção de minério ROM (t) | Ambiental | SOMA(Quantidade Produção - Minério ROM) | fMineracao | T5 | ODS 8, 9 | GRI 14 (Mineração) | 13.400.000 |
| IND14 | Quantidade de contido por substância | Ambiental | SOMA(Quantidade Contido) por Substância | fMineracao | T5 | ODS 9 | GRI 14 (Mineração) | 764.700 |
| IND15 | Intensidade hídrica da mineração (m³/t ROM) | Ambiental | Consumo de Água ÷ Minério ROM | fMineracao / fAmbiental | T4 | ODS 6 | GRI 303-5 | 1,2 |
| IND16 | Percentual de projetos minerários com tecnologia limpa | Ambiental | CONT.SE(Tecnologia Limpa = Sim) ÷ nº de projetos | fAmbiental | T9 | ODS 9, 12 | - | 83,3% |
| IND17 | Área de intervenção em sustentabilidade (ha) | Ambiental | SOMA(Área de Intervenção) | fSustentabilidade | T4 | ODS 15 | GRI 304-3 | 42.062 |
| IND18 | Remoção de carbono anual (tCO2e) | Ambiental | SOMA(Remoção de Carbono Anual) | fSustentabilidade | T4 | ODS 13 | GRI 305-5 | 330.300 |
| IND19 | Créditos de carbono emitidos (tCO2e) | Ambiental | SOMA(Créditos de Carbono Emitidos) | fSustentabilidade | T3 | ODS 13 | GRI 305-5 | 182.200 |
| IND20 | Capacidade anual de reúso e reciclagem | Ambiental | SOMA(Capacidade de Processamento Anual) por Unidade | fSustentabilidade | T4 | ODS 12 | GRI 306-2 | 16.500.000 |
| IND21 | Emissões de CO2 por setor (tCO2e) | Ambiental | SOMA(Emissões de CO2) por Setor Investe | fAmbiental | T4 | ODS 13 | GRI 305-1 | 291.160 |
| IND22 | Emissões de GEE evitadas (tCO2e) | Ambiental | SOMA(Emissões de GEE Evitadas) | fAmbiental | T4 | ODS 13 | GRI 305-5 | 3.477.889 |
| IND23 | Intensidade de emissões por investimento | Ambiental | Emissões de CO2 ÷ (Investimento Previsto ÷ 1.000.000) | fAmbiental / dProjeto | T4 | ODS 13 | GRI 305-4 | 6,8 |
| IND24 | Percentual de projetos com tecnologia limpa | Ambiental | CONT.SE(Sim) ÷ nº de projetos | fAmbiental | T9 | ODS 9 | - | 95,8% |
| IND25 | Volume total de água consumida (m³) | Ambiental | SOMA(Consumo de Água) | fAmbiental | T4 | ODS 6 | GRI 303-5 | 34.829.800 |
| IND26 | Percentual de água reutilizada | Ambiental | Água Reutilizada ÷ Consumo de Água | fAmbiental | T4 | ODS 6, 12 | GRI 303-3 | 59,2% |
| IND27 | Quantidade de resíduos gerados (t) | Ambiental | SOMA(Resíduos Gerados) | fAmbiental | T4 | ODS 12 | GRI 306-3 | 377.117 |
| IND28 | Percentual de resíduos reciclados | Ambiental | Resíduos Reciclados ÷ Resíduos Gerados | fAmbiental | T4 | ODS 12 | GRI 306-4 | 66,0% |
| IND29 | Percentual de resíduos destinados corretamente | Ambiental | Destinados Corretamente ÷ Gerados | fAmbiental | T4 | ODS 12 | GRI 306-5 | 97,5% |
| IND30 | Número de projetos com licenciamento ambiental | Ambiental | CONT.SE(Licenciamento = Sim) | fAmbiental | T5 | ODS 16 | GRI 2-27 | 31 |
| IND31 | Percentual de projetos com licença ambiental válida | Ambiental | CONT.SE(Licença Válida = Sim) ÷ nº de projetos | fAmbiental | T5 | ODS 16 | GRI 2-27 | 54,2% |
| IND32 | Número de projetos com plano de recuperação ambiental | Ambiental | CONT.SE(Plano = Sim) | fAmbiental | T4 | ODS 15 | GRI 304-3 | 20 |
| IND33 | Área recuperada (ha) | Ambiental | SOMA(Área Recuperada) | fAmbiental | T4 | ODS 15 | GRI 304-3 | 21.787 |
| IND34 | Área preservada (ha) | Ambiental | SOMA(Área Preservada) | fAmbiental | T4 | ODS 15 | GRI 304-3 | 32.085 |
| IND35 | Percentual de projetos com avaliação de impacto ambiental | Ambiental | CONT.SE(Avaliação = Sim) ÷ nº de projetos | fAmbiental | T5 | ODS 15 | GRI 2-27 | 75,0% |
| IND36 | Quantidade de incidentes ambientais | Ambiental | SOMA(Incidentes Ambientais) | fAmbiental | T4 | ODS 12, 15 | GRI 2-27 | 13 |
| IND37 | Total de empregos diretos previstos | Social | SOMA(Empregos Diretos Previstos) | fSocial | T8 | ODS 8 | GRI 203-2 | 18.407 |
| IND38 | Total de empregos diretos gerados | Social | SOMA(Empregos Diretos Gerados) | fSocial | T8 | ODS 8 | GRI 203-2 | 7.236 |
| IND39 | Empregos gerados por setor | Social | SOMA(Empregos Diretos Gerados) por Setor Investe | fSocial | T8 | ODS 8 | GRI 203-2 | 7.236 |
| IND40 | Geração de empregos por investimento | Social | Empregos Previstos ÷ (Investimento Previsto ÷ 1.000.000) | fSocial / dProjeto | T8 | ODS 8 | GRI 203-2 | 0,43 |
| IND41 | Percentual de empregos para a população local | Social | Empregos População Local ÷ Empregos Diretos Gerados | fSocial | T7 | ODS 8 | GRI 203-2 | 60,8% |
| IND42 | Percentual de empregos para mulheres | Social | Empregos Mulheres ÷ Empregos Diretos Gerados | fSocial | T10 | ODS 5 | GRI 405-1 | 25,0% |
| IND43 | Percentual de empregos para pessoas com deficiência | Social | Empregos PCD ÷ Empregos Diretos Gerados | fSocial | T10 | ODS 10 | GRI 405-1 | 3,7% |
| IND44 | Total de empregos indiretos gerados | Social | SOMA(Empregos Indiretos Gerados) | fSocial | T8 | ODS 8 | GRI 203-2 | 11.358 |
| IND45 | Número de trabalhadores capacitados | Social | SOMA(Trabalhadores Capacitados) | fSocial | T8 | ODS 4, 8 | GRI 404-2 | 5.830 |
| IND46 | Horas de treinamento por trabalhador | Social | Horas de Treinamento ÷ Trabalhadores Capacitados | fSocial | T8 | ODS 4, 8 | GRI 404-1 | 24,71 |
| IND47 | Investimento em capacitação profissional | Social | SOMA(Investimento em Capacitação) | fSocial | T8 | ODS 4, 8 | GRI 404-2 | R$ 30,7 mi |
| IND48 | Número de programas sociais apoiados | Social | SOMA(Programas Sociais Apoiados) | fSocial | T7 | ODS 11 | GRI 413-1 | 121 |
| IND49 | Beneficiários dos programas sociais | Social | SOMA(Beneficiários Programas Sociais) | fSocial | T7 | ODS 11 | GRI 413-1 | 42.740 |
| IND50 | Número de comunidades beneficiadas | Social | SOMA(Comunidades Beneficiadas) | fSocial | T7 | ODS 11 | GRI 413-1 | 152 |
| IND51 | Investimento em desenvolvimento social | Social | SOMA(Investimento Desenvolvimento Social) | fSocial | T7 | ODS 11 | GRI 203-1 | R$ 52,7 mi |
| IND52 | Percentual de projetos com consulta às comunidades | Social | CONT.SE(Consulta = Sim) ÷ nº de projetos | fSocial | T7 | ODS 16 | GRI 413-1 | 62,5% |
| IND53 | Percentual de projetos com avaliação de impacto social | Social | CONT.SE(Avaliação = Sim) ÷ nº de projetos | fSocial | T7 | ODS 16 | GRI 413-1 | 52,1% |
| IND54 | Número de acidentes de trabalho | Social | SOMA(Acidentes de Trabalho) | fSocial | T11 | ODS 8 | GRI 403-9 | 23 |
| IND55 | Taxa de frequência de acidentes | Social | Acidentes × 1.000.000 ÷ Horas Trabalhadas | fSocial | T11 | ODS 8 | GRI 403-9 | 2,12 |
| IND56 | Número de ações de saúde e segurança | Social | SOMA(Ações de Saúde e Segurança) | fSocial | T11 | ODS 8 | GRI 403-5 | 275 |
| IND57 | Percentual de valor contratado com fornecedores locais | Social | Valor Fornecedores Locais ÷ Orçamento Previsto | fSocial / fFinanceiro | T7 | ODS 8 | GRI 204-1 | 1,0% |
| IND58 | Número de reclamações sociais | Social | SOMA(Reclamações Sociais) | fSocial | T7 | ODS 16 | GRI 2-25 | 42 |
| IND59 | Percentual de execução orçamentária | Governança | Empenhado ÷ Orçamento Previsto | fFinanceiro | T2 | ODS 16 | GRI 201-1 | 24,8% |
| IND60 | Saldo orçamentário dos projetos | Governança | SOMA(Saldo Orçamentário) | fFinanceiro | T2 | ODS 16 | GRI 201-1 | R$ 32,2 bi |
| IND61 | Índice de execução financeira | Governança | Valor Pago ÷ Valor Empenhado | fFinanceiro | T2 | ODS 16 | GRI 201-1 | 0,89 |
| IND62 | Percentual de projetos concluídos | Governança | CONT.SE(Status = Concluído) ÷ nº de projetos | dProjeto | T5 | ODS 9 | - | 10,4% |
| IND63 | Percentual de projetos com prestação de contas atualizada | Governança | CONT.SE(Prestação = Sim) ÷ nº de projetos | fFinanceiro | T2 | ODS 16 | GRI 2-27 | 62,5% |
| IND64 | Valor total contratado | Governança | SOMA(Valor Contratado) | fContratos | T2 | ODS 16 | GRI 2-6 | R$ 5,1 bi |
| IND65 | Percentual de contratos em execução | Governança | CONT.SE(Status = Em execução) ÷ nº de contratos | fContratos | T5 | ODS 16 | - | 50,0% |
| IND66 | Percentual de contratos com documentação completa | Governança | CONT.SE(Documentação = Sim) ÷ nº de contratos | fContratos | T1 | ODS 16 | GRI 2-27 | 73,3% |
| IND67 | Percentual de contratos fiscalizados | Governança | Contratos Fiscalizados ÷ nº de contratos | fContratos | T14 | ODS 16 | GRI 2-27 | 55,0% |
| IND68 | Percentual de irregularidades corrigidas | Governança | Irregularidades Corrigidas ÷ Identificadas | fContratos | T14 | ODS 16 | GRI 2-27 | 77,4% |
| IND69 | Número de auditorias realizadas | Governança | SOMA(Auditorias Realizadas) | fContratos | T14 | ODS 16 | GRI 2-5 | 36 |
| IND70 | Percentual de recomendações de auditoria atendidas | Governança | Atendidas ÷ Emitidas | fContratos | T14 | ODS 16 | GRI 2-27 | 79,2% |
| IND71 | Número de denúncias recebidas | Governança | SOMA(Denúncias Recebidas) | fContratos | T14 | ODS 16 | GRI 2-26 | 15 |
| IND72 | Percentual de denúncias apuradas | Governança | Apuradas ÷ Recebidas | fContratos | T14 | ODS 16 | GRI 2-26 | 46,7% |
| IND73 | Número de casos de fraude ou corrupção | Governança | SOMA(Casos de Fraude ou Corrupção) | fContratos | T14 | ODS 16 | GRI 205-3 | 4 |
| IND74 | Percentual de colaboradores treinados em ética e integridade | Governança | Treinados ÷ Colaboradores Totais | fEquipe | T14 | ODS 16 | GRI 205-2 | 84,3% |
| IND75 | Número de treinamentos de integridade realizados | Governança | SOMA(Treinamentos de Integridade) | fEquipe | T14 | ODS 16 | GRI 205-2 | 145 |
| IND76 | Percentual de projetos com análise de riscos | Governança | SOMA(Projetos com Análise de Riscos) ÷ nº de projetos | fContratos | T1 | ODS 16 | GRI 2-12 | 85,4% |
| IND77 | Percentual de riscos críticos mitigados | Governança | Riscos Mitigados ÷ Riscos Críticos | fContratos | T1 | ODS 16 | GRI 2-12 | 45,7% |
| IND78 | Tempo médio de resposta às demandas (dias) | Governança | MÉDIA(Tempo Médio de Resposta) | fTransparencia | T2 | ODS 16 | GRI 2-25 | 4,71 |
| IND79 | Percentual de projetos com informações públicas atualizadas | Governança | CONT.SE(Sim) ÷ nº de projetos | fTransparencia | T2 | ODS 16 | GRI 2-29 | 66,7% |
| IND80 | Percentual de projetos com dados públicos disponíveis | Governança | CONT.SE(Sim) ÷ nº de projetos | fTransparencia | T2 | ODS 16 | GRI 2-29 | 50,0% |
| IND81 | Índice de transparência dos projetos | Governança | MÉDIA(Índice de Transparência) | fTransparencia | T2 | ODS 16 | GRI 2-29 | 0,58 |
| IND82 | Custo de manutenção realizado vs. previsto | Governança | Custo Realizado ÷ Custo Previsto | fManutencao | T9 | ODS 9 | - | 26,6% |

## Indicadores da sede da Investe Piauí (15, dados de demonstração)

O farol segue a mesma regra das metas (item 5 acima). Não entram no Índice ASG.

| ID | Pilar | Indicador | Unidade | Polaridade | Anterior | Atual | Meta | Limite | Status | GRI |
|---|---|---|---|---|---|---|---|---|---|---|
| INS01 | Ambiental | Consumo de energia da sede | MWh | Menor melhor | 184 | 162 | 150 | 170 | Atenção | GRI 302-1 |
| INS02 | Ambiental | Energia renovável no consumo da sede | % | Maior melhor | 35,0% | 62,0% | 80,0% | 60,0% | Atenção | GRI 302-1 |
| INS03 | Ambiental | Consumo de água da sede | m³ | Menor melhor | 1.250 | 1.100 | 1.000 | 1.150 | Atenção | GRI 303-5 |
| INS04 | Ambiental | Emissões de GEE da sede | tCO2e | Menor melhor | 48 | 41 | 42 | 46 | Atingida | GRI 305-1 |
| INS05 | Ambiental | Papel consumido | resmas | Menor melhor | 820 | 540 | 550 | 650 | Atingida | GRI 306-3 |
| INS06 | Social | Servidores no quadro | nº | Maior melhor | 86 | 92 | — | — | — | GRI 2-7 |
| INS07 | Social | Mulheres no quadro de servidores | % | Maior melhor | 44,0% | 48,0% | 50,0% | 45,0% | Atenção | GRI 405-1 |
| INS08 | Social | Mulheres em cargos de liderança | % | Maior melhor | 30,0% | 36,0% | 40,0% | 35,0% | Atenção | GRI 405-1 |
| INS09 | Social | Servidores com deficiência | % | Maior melhor | 2,0% | 3,0% | 5,0% | 4,0% | Abaixo | GRI 405-1 |
| INS10 | Social | Horas de capacitação por servidor | h/servidor | Maior melhor | 18,00 | 26,00 | 30,00 | 24,00 | Atenção | GRI 404-1 |
| INS11 | Social | Acidentes de trabalho na sede | nº | Menor melhor | 1 | 0 | 0 | 1 | Atingida | GRI 403-9 |
| INS12 | Governança | Pedidos de acesso à informação respondidos no prazo | % | Maior melhor | 91,0% | 96,0% | 98,0% | 95,0% | Atenção | GRI 2-26 |
| INS13 | Governança | Servidores treinados em ética e integridade | % | Maior melhor | 70,0% | 96,0% | 95,0% | 85,0% | Atingida | GRI 205-2 |
| INS14 | Governança | Reuniões do conselho de administração | nº | Maior melhor | 10 | 12 | 12 | 10 | Atingida | GRI 2-12 |
| INS15 | Governança | Recomendações da auditoria interna atendidas | % | Maior melhor | 62,0% | 71,0% | 90,0% | 75,0% | Abaixo | GRI 2-25 |

## Premissas

| ID Premissa | Premissa | Valor | Unidade | Fonte / Justificativa | Onde é usada |
|---|---|---|---|---|---|
| P01 | Fator de emissão da rede elétrica (SIN) · média anual 2025 | 0.0461 | tCO2/MWh | MCTI, fator médio anual de emissão do SIN para inventários corporativos, ano de 2025 (último ano completo), planilha Inventario_2026_janset.xlsx (gov.br/mcti, atualizada em 16/10/2026). Revisar todo ano. | Energia Renovável: Geração Anual × fator. Mineração: Energia Renovável Consumida × fator. |
| P02 | Emissão evitada por tonelada de H2 verde | 10 | tCO2e/t H2 | Hidrogênio cinza (reforma a vapor de gás natural) emite ~9 a 12 kgCO2 por kg de H2. Adotado 10. | Hidrogênio Verde: Produção Anual de H2 × fator. |
| P03 | Horas trabalhadas por empregado (acumulado até set/2026) | 1500 | h/empregado | Premissa do Grupo 3 para estimar horas trabalhadas. | Horas Trabalhadas = Empregos Diretos Gerados × 1.500. |
| P04 | Data de referência dos dados | 30/09/2026 | data | Posição acumulada até setembro/2026. | Usada em fFinanceiro e dProjeto. |
| P05 | Origem dos dados | Simulados pelo Grupo 3 | texto | Dados fictícios para prototipação. Substituir pelos dados da Investe Piauí mantendo as mesmas colunas. | - |

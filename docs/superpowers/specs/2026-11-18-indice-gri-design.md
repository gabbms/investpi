# Índice de conteúdo GRI exportável

Especificação curta. Complementa `2026-11-17-sistema-asg-web-design.md` e o Catálogo de Indicadores (plano `2026-11-18-exportar-indicadores-qualidade.md`, Tarefa 15).

## Por quê

Relatórios de sustentabilidade que seguem as Normas GRI trazem um anexo, o **índice de conteúdo GRI**, que liga cada divulgação das normas ao dado que a atende. A planilha ASG já associa 73 dos 82 indicadores a uma referência GRI, e o sistema já calcula o valor atual de cada indicador. A funcionalidade gera esse anexo pronto, para **ir direto para o relatório**, sem ajustes à mão.

## Decisões do grupo

- O arquivo vai **direto para o relatório**: precisa sair apresentável, sem colunas internas.
- Os valores **respeitam os filtros** da barra superior. Um relatório só de Mineração sai com os números de Mineração.
- O sistema traz o **nome oficial em português** de cada divulgação e de cada norma. A **localização** (página ou seção do relatório) fica como coluna vazia, para o grupo preencher.
- Construção: uma **exportação própria**, com o botão "Exportar índice GRI" na página Indicadores, ao lado de "Exportar Excel".

## Decisões minhas

- **Uma linha por indicador, agrupada por referência.** A norma e a divulgação aparecem só na primeira linha do grupo, e as linhas seguintes deixam essas células vazias. 34 referências cobrem 73 indicadores; com uma linha por referência seria preciso juntar valores diferentes ("23 acidentes" e "taxa 2,12") numa célula.
- **Ordem:** pelo número da norma (GRI 2, 201, 203…, 413), depois pela divulgação (403-5 antes de 403-9), depois pelo ID do indicador.
- **Valores como texto, no formato do painel** (`texto_valor`: "R$ 9,0 bi", "54,2%", "2,12"), iguais ao catálogo e aos cards, porque o arquivo vai para o texto do relatório. Medida que o sistema não calcula aparece como "—".
- **Referências fora das Normas GRI atuais vão para o bloco "Referências a revisar"**, no fim da aba, com o motivo, em vez de serem encaixadas por suposição:
  - `GRI-G4 EU1` e `GRI-G4 EU2`: "Divulgação do modelo GRI-G4, anterior às Normas GRI";
  - `GRI 14 (Mineração)`: "Norma setorial sem divulgação específica";
  - divulgação de uma norma **já substituída** na data da exportação: "Norma substituída por <nova norma> em dd/mm/aaaa". Hoje isso vale para a `GRI 304-3` (a GRI 304: Biodiversidade 2016 foi substituída pela GRI 101: Biodiversity 2024 em 01/01/2026); a partir de 01/01/2027, também para a `GRI 302-1` e a `GRI 302-3` (GRI 302: Energia 2016 → GRI 103: Energy 2025). A tabela de normas guarda a data de substituição de cada norma quando a GRI a publica, e a exportação compara com a data do dia (horário do Piauí);
  - qualquer referência que não esteja na tabela de nomes (por exemplo, numa planilha nova): "Divulgação não reconhecida".
- Acesso: qualquer usuário logado, como as outras exportações.

## Objetivos

O arquivo `ASG_indice_gri_<AAAA-MM-DD>.xlsx` (data no horário do Piauí) tem duas abas:

1. **"Índice GRI"**:
   - título "Índice de conteúdo GRI — indicadores quantitativos" e, abaixo, a linha "Versão nº <n> · <arquivo> · filtros: <resumo ou 'carteira inteira'>";
   - colunas: Norma GRI · Divulgação · Indicador · Valor · Localização no relatório;
   - Norma no formato oficial com o ano da versão (ex.: "GRI 403: Saúde e Segurança do Trabalho 2018"); Divulgação com código e título (ex.: "403-9 Acidentes de trabalho"); Indicador com o ID e o nome (ex.: "IND54 Número de acidentes de trabalho");
   - depois, o bloco "Referências a revisar": Referência · Motivo · Indicador · Valor;
   - cabeçalho congelado, larguras ajustadas, sem colunas internas.
2. **"Contexto"**: o mesmo da exportação das telas (página, gerado em, versão, um filtro por linha).

```
Índice de conteúdo GRI — indicadores quantitativos
Versão nº 1 · base_modelo.xlsx · filtros: carteira inteira

Norma GRI                                    Divulgação                     Indicador                                Valor     Localização no relatório
GRI 403: Saúde e Segurança do Trabalho 2018  403-5 <título oficial>         IND56 Número de ações de saúde e segurança  275
                                             403-9 Acidentes de trabalho    IND54 Número de acidentes de trabalho       23
                                                                            IND55 Taxa de frequência de acidentes       2,12
...
Referências a revisar
Referência           Motivo                                              Indicador                         Valor
GRI-G4 EU1           Divulgação do modelo GRI-G4, anterior às Normas GRI  IND03 Capacidade instalada…   1.905
```

## Fora do escopo

- **As divulgações qualitativas** (políticas, governança, abordagem de gestão). O sistema mede indicadores; o restante do índice o grupo completa no relatório.
- **Os 9 indicadores sem referência GRI** ("-"): não entram.
- **Uma tela "Índice GRI" no painel.** Só a exportação.
- **Mudar a planilha**: nenhuma coluna nova em `dIndicador`.

## O que não pode acontecer

- **O arquivo afirmar conformidade com as Normas GRI.** O título diz "indicadores quantitativos", e nada no arquivo diz que o relatório está "de acordo com" as normas.
- **Um nome de norma ou divulgação inventado ou desatualizado.** Os nomes vêm da tradução oficial das Normas GRI para o português, publicada pela GRI (lista em globalreporting.org, "GRI Standards Portuguese Translations"); a tabela no código registra a fonte de cada nome, e o plano traz os 31 títulos conferidos nos PDFs oficiais.
- **Uma divulgação de norma já substituída entrar no índice como se valesse.**
- **Uma referência fora do padrão ser encaixada numa norma por suposição.** Ela vai para "Referências a revisar".

## Restrições

- As 31 referências da planilha nas Normas GRI: GRI 2-5, 2-6, 2-12, 2-25, 2-26, 2-27, 2-29 · 201-1 · 203-1, 203-2 · 204-1 · 205-2, 205-3 · 302-1, 302-3 · 303-3, 303-5 · 304-3 · 305-1, 305-4, 305-5 · 306-2, 306-3, 306-4, 306-5 · 403-5, 403-9 · 404-1, 404-2 · 405-1 · 413-1. Na base atual, em novembro de 2026: 30 delas entram no índice (65 indicadores) e a 304-3 vai para "Referências a revisar", junto com G4 EU1, EU2 e GRI 14 (8 indicadores no bloco).
- A GRI 306 usada é a **GRI 306: Resíduos 2020**, a versão em vigor (306-2 a 306-5 mudaram de sentido em relação à de 2016).
- Sem dependência nova. Sem mudança no Índice ASG, nas metas ou nos pesos: o Índice ASG Geral continua 68.
- Reaproveitar o que existe: o cálculo do valor atual do catálogo (`paginas/indicadores.py`), `texto_valor`, `data_local` e o Contexto de `exportacao.py`.

## Abordagens

- **A. Exportação própria** (rota e botão novos, tabela fixa de nomes no código, aba no formato de anexo). **Escolhida:** é o único caminho em que o arquivo sai pronto para o relatório.
- B. Uma aba a mais no Excel da página Indicadores. Mais barato, mas o arquivo vem com as abas genéricas e alguém precisa recortar o índice.
- C. Uma tela "Índice GRI" exportada pelo botão genérico. A exportação genérica tem o formato das telas, não o de um anexo.

## Fica para quem construir

- A rota da API e o nome da função que monta o índice, desde que o cálculo dos valores seja o mesmo do catálogo.
- Como normalizar a referência lida da planilha (espaços, "GRI-G4" × "GRI G4") antes de procurar na tabela.
- O estilo visual do título e dos grupos (negrito, bordas), desde que legível ao colar num documento.

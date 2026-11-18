# Detalhes das checagens de qualidade (C01–C12)

Especificação curta. Complementa `2026-11-17-sistema-asg-web-design.md` e a página Qualidade dos dados (plano `2026-11-18-exportar-indicadores-qualidade.md`, Tarefa 16).

## Por quê

As checagens C01–C12 dizem **quantos** problemas a planilha tem ("C07: Verificar 1"), mas não **onde** eles estão. Para corrigir, quem cuida dos dados precisa abrir o Excel e procurar à mão. A funcionalidade mostra cada registro com problema e os valores que quebram a regra.

## Para quem

Decisões minhas, já que o grupo não sabia dizer quem vai usar:

- **Quem mais usa é o admin que envia a planilha**, porque só ele corrige o arquivo. O momento mais útil é a tela **Enviar planilha**, na prévia, antes de confirmar: ele vê o problema, corrige o Excel e envia de novo.
- **Na Qualidade dos dados**, qualquer usuário logado vê os mesmos detalhes da versão ativa e pode avisar quem cuida dos dados.

## Objetivos

- Em cada checagem com problemas, listar os registros que falharam com:
  - a **aba**;
  - o **identificador** que a pessoa procura no Excel: Código Projeto em dProjeto, fSocial e fHidrogenio; ID Execução em fFinanceiro; ID Processo em fContratos;
  - a **linha da planilha**, quando conhecida (ver Restrições);
  - os **valores que quebram a regra**, no formato pt-BR do painel. Por checagem:

| Checagem | O que mostrar |
|---|---|
| C01 | Código Projeto e o Código Empresa que não existe em dEmpresa |
| C02 | o Código Projeto repetido e quantas vezes aparece (uma linha por ocorrência) |
| C03–C06 | o Código Projeto e o Nome Projeto que não têm linha na aba citada |
| C07 | Investimento Realizado e Investimento Previsto |
| C08 | Empregos Diretos Gerados e cada subgrupo que passou dele (Mulheres, População Local, PCD) |
| C09 | Data Referência, Valor Empenhado, Liquidado e Pago |
| C10 | quais campos obrigatórios estão vazios |
| C11 | o % Renovável Eletrolisador fora de 0% a 100% |
| C12 | Data Início e Data Fim |

- Mostrar até **50 registros por checagem** na tela, com "e mais N" quando passar disso.
- O Excel exportado da Qualidade ganha uma aba **"Problemas"** com **todos** os registros (sem o limite de 50): Checagem · Aba · Linha · Identificador · Detalhe.
- Checagem sem problema continua como hoje: "OK" em verde, sem lista.

## Fora do escopo

- **Histórico de versões.** As versões antigas guardaram só as contagens em `avisos`. Mostrar detalhes ali exigiria gravar mais dados, e o histórico serve para auditar envios, não para corrigir.
- **Corrigir os dados pelo sistema.** A correção continua sendo no Excel, com um novo envio.
- **Checagens novas** ou mudança nas regras C01–C12.

## O que não pode acontecer

- A contagem de problemas mudar. A lista e o número "Verificar: N" vêm da mesma regra e precisam bater.
- A prévia do envio ficar lenta a ponto de atrapalhar. Os detalhes saem das mesmas máscaras que já contam os problemas.
- Uma planilha com milhares de problemas travar a tela. Por isso o limite de 50.

## Restrições

- **Linha da planilha.** A leitura (`planilha/leitura.py`) descarta as linhas totalmente em branco (`dropna(how="all")`) e renumera (`reset_index`). Então "posição + 2" só bate com o Excel quando não há linhas vazias no meio. O número precisa ser guardado **antes** dessas duas etapas e acompanhar os dados da versão.
- **Versões já enviadas** não têm esse número. Para elas, a coluna Linha fica vazia e o identificador basta para achar o registro (Ctrl+F no Excel).
- O guarda-linha não pode aparecer como coluna da aba nas outras telas, nem ser visto como coluna inesperada pela validação da estrutura.
- Sem dependência nova. Sem mudança no Índice ASG, nas metas ou nos pesos: o Índice ASG Geral continua 68.

## Abordagens

- **A. Recalcular os detalhes a cada pedido**, a partir das mesmas máscaras que hoje só contam (`rodar_checagens`). Não muda o banco e funciona para qualquer versão. **Escolhida.**
- B. Gravar os detalhes em `versao.avisos` no envio. Exige gravar mais dados, fica desatualizado se a regra mudar e não serve para as versões que já existem.
- C. Um endpoint extra que calcula os detalhes de uma checagem ao clicar. Exige mais código e mais uma chamada, para economizar pouco: a base já fica em cache.

## Como fica

```
C07  Investimento realizado maior que o previsto      Verificar: 1
     ▾ dProjeto · linha 2 · PROJ001
       Investimento Realizado R$ 7,8 bi  >  Investimento Previsto R$ 780 mi
C12  Contratos com data de fim antes do início        Verificar: 2
     ▾ fContratos · linha 9 · PROC014 · Data Início 10/03/2026 > Data Fim 01/02/2026
     ▾ fContratos · linha 31 · PROC027 · ...
```

Na Qualidade e na prévia do envio, cada checagem com problemas abre e fecha a sua lista, que começa fechada.

## Fica para quem construir

- Como guardar o número da linha (coluna interna, índice preservado ou outro meio), desde que respeite as Restrições.
- O formato exato da resposta da API, desde que `problemas` continue igual ao tamanho da lista completa.
- O desenho do abre/fecha, seguindo o estilo atual das tabelas e selos.

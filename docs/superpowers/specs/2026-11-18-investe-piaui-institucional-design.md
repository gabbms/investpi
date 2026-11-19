# Tela "Investe Piauí" — indicadores ASG da própria instituição — design (curto)

## Intenção

A professora pediu que o painel mostre indicadores ASG da **própria Investe Piauí**, e não só da carteira de projetos que ela atrai. A tela tem de responder "quais são os nossos indicadores ASG?" logo depois do login. Os dados da operação da sede ainda não existem, então a apresentação usa dados fictícios. Mesmo assim, o formato tem de servir para os dados reais quando eles existirem.

## Objetivos

- Item novo **"Investe Piauí"** no topo do menu, acima de "Visão Geral". É a tela que abre depois do login; a Visão Geral passa para `/carteira`.
- Três blocos, cada um com título e uma frase explicando de onde vêm os números:
  1. **Nossa gestão:** indicadores de Governança que já existem (fContratos, fFinanceiro, fEquipe, fTransparencia), somados de toda a carteira e apresentados como gestão da instituição. Exemplos: % contratos fiscalizados, % recomendações atendidas, % execução orçamentária, % prestação de contas atualizada, % colaboradores treinados em integridade, tempo médio de resposta e casos de fraude. Cada card usa a cor do farol da meta, quando houver meta.
  2. **Nossa operação:** indicadores da sede, vindos da aba nova `dInstitucional`. Cada card mostra o valor atual, a variação em relação ao ano anterior e a cor do farol em relação à meta. Os cards ficam agrupados por pilar (Ambiental, Social, Governança).
  3. **Nosso impacto:** o que a instituição ajudou a atrair, com investimento previsto, empresas confirmadas, empregos diretos gerados e emissões evitadas.
- Selo **"Dados de demonstração"** no bloco 2 enquanto os dados forem fictícios.
- "Exportar Excel" funciona como nas outras telas, com uma seção por bloco.
- Os filtros do topo valem para os blocos 1 e 3. O bloco 2 não muda com os filtros e diz isso na tela.

## Não-objetivos

- Uma segunda planilha ou uma segunda tela de envio (opção descartada: dobraria o trabalho de versões e validação).
- Os indicadores de `dInstitucional` entrarem no Índice ASG Geral ou na tela Metas ASG.
- Incluir `dInstitucional` no índice GRI exportado (fica para depois).
- Gráfico de séries históricas (só ano atual × ano anterior).

## Antiobjetivos

- Uma planilha sem `dInstitucional` ser recusada no envio.
- Algum número da carteira (Visão Geral, pilares, índice) mudar.
- A tela esconder que o bloco 2 é fictício.

## Abordagens

| | De onde vem o bloco 2 | Troca |
|---|---|---|
| **A — aba opcional `dInstitucional` na planilha (escolhida)** | Planilha modelo, aba nova | Dados reais entram só preenchendo a planilha; mexe no formato aceito |
| B — números fixos no código | Código | Mais rápido, mas descartável |
| C — planilha separada | Arquivo e envio próprios | Separa responsáveis, mas duplica versões, validação e modelo |

## Como (decidido)

- **Aba `dInstitucional`**, opcional (`obrigatoria=False`). Uma linha por indicador. Colunas: `ID Institucional` (chave), `Pilar`, `Indicador`, `Unidade`, `Formato` (`%`, `n`, `dec`, `R$`, como em dMetas), `Polaridade` (`Maior melhor` / `Menor melhor`), `Ano Referência`, `Valor Anterior`, `Valor Atual`, `Meta`, `Limite Atenção`, `Referência GRI`, `Fonte`.
- **Farol:** verde quando o valor atinge a meta; amarelo quando fica entre a meta e o limite de atenção; vermelho no resto. Respeita a polaridade e segue a mesma regra das metas de dMetas.
- **Dados fictícios** com cerca de 15 indicadores: energia, água, emissões, papel e reciclagem da sede; servidores, % mulheres, % mulheres na liderança, % PCD, horas de capacitação por servidor e acidentes; % servidores treinados em ética, % pedidos de acesso à informação no prazo e reuniões do conselho. Fonte = "Demonstração (fictício)".
- **Página com seções:** `Pagina` ganha `secoes` (título, descrição, selo opcional e cards). O frontend desenha as seções na ordem. As outras telas não mudam.

## A cargo de quem implementa

- Os nomes, valores e metas dos indicadores fictícios, desde que sejam plausíveis para uma agência estadual de cerca de 90 servidores.
- O texto de cada bloco e do selo.
- A disposição dos cards dentro de cada seção.

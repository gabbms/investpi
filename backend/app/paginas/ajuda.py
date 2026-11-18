"""Textos de ajuda ("?") para medidas que não aparecem na aba dIndicador.

A aba dIndicador da planilha tem prioridade; estes textos explicam as medidas
DAX restantes que aparecem em cards.
"""

AJUDA_PADRAO: dict[str, str] = {
    "Investimento Previsto": "Soma do investimento previsto dos projetos no filtro. Cálculo: SOMA(dProjeto[Investimento Previsto]).",
    "Investimento Realizado": "Soma do investimento já realizado dos projetos no filtro.",
    "Empresas Confirmadas": "Empresas distintas com projetos no filtro cuja relação com a Investe Piauí está confirmada. "
    'Cálculo: CONTAGEM DISTINTA(Código Empresa) com Status Relação = "Confirmado".',
    "Orçamento Previsto": "Orçamento previsto dos projetos no último mês informado (não soma os meses). "
    "Cálculo: SOMA(fFinanceiro[Orçamento Previsto]) no último mês.",
    "% Liquidado do Orçamento": "Valor liquidado acumulado dividido pelo orçamento previsto do último mês.",
    "% Pago do Orçamento": "Valor pago acumulado dividido pelo orçamento previsto do último mês.",
    "Faturamento Mineração": "Soma do faturamento previsto dos projetos de mineração. Cálculo: SOMA(fMineracao[Faturamento Previsto]).",
    "Valor de Venda Mineração": "Soma do valor de venda previsto da produção mineral.",
    "Índice Ambiental": "Média ponderada pelo peso do atingimento das metas do pilar Ambiental (0 a 100). "
    "Atingimento: maior melhor = valor ÷ meta (até 1); menor melhor = 1 se dentro da meta, 0,5 se dentro do limite, 0 acima.",
    "Índice Social": "Média ponderada pelo peso do atingimento das metas do pilar Social (0 a 100).",
    "Índice Governança": "Média ponderada pelo peso do atingimento das metas do pilar Governança (0 a 100).",
    "Índice ASG Geral": "Média dos índices Ambiental, Social e Governança (0 a 100). "
    "Verde a partir de 75, amarelo a partir de 50, vermelho abaixo.",
    "% Metas Atingidas": "Metas atingidas divididas pelas metas que têm valor no filtro atual.",
    "Metas Atingidas": "Metas cujo valor atual cumpre a meta.",
    "Metas em Atenção": "Metas que não cumprem a meta, mas estão dentro do limite de atenção.",
    "Metas Abaixo": "Metas abaixo do limite de atenção.",
    "% Empregos Gerados vs Previstos": "Empregos diretos gerados divididos pelos previstos.",
}

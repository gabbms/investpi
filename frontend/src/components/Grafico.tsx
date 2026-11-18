import ReactECharts from 'echarts-for-react'
import type { Grafico as TGrafico } from '../api'
import { eixo, valor } from '../format'

const PALETA = ['#0B3D91', '#1B8A4C', '#D9730D', '#5B2C83', '#00A19A', '#E0A100', '#4B5563', '#8E3B46']
const TEXTO = '#1F2933'
const SUAVE = '#5F6B76'
const LINHA = '#E3E7EA'
const FONTE = "'Public Sans Variable', system-ui, sans-serif"

function opcoes(g: TGrafico) {
  const fmt = (v: unknown) => valor(typeof v === 'number' ? v : null, g.formato)
  const base = {
    color: PALETA,
    textStyle: { fontFamily: FONTE, color: TEXTO },
    tooltip: {
      trigger: g.tipo === 'rosca' ? 'item' : 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: fmt,
      textStyle: { fontFamily: FONTE },
    },
    legend:
      g.series.length > 1 || g.tipo === 'rosca'
        ? { bottom: 0, icon: 'roundRect', itemWidth: 12, itemHeight: 12, textStyle: { color: SUAVE } }
        : undefined,
  }

  if (g.tipo === 'rosca') {
    const s = g.series[0]
    return {
      ...base,
      series: [
        {
          type: 'pie',
          radius: ['38%', '58%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: true,
          itemStyle: { borderColor: '#fff', borderWidth: 2 },
          label: { formatter: (p: { value: number; percent: number }) => `${fmt(p.value)} (${Math.round(p.percent)}%)`, color: SUAVE },
          data: g.categorias.map((c, i) => ({
            name: c,
            value: s?.valores[i] ?? 0,
            itemStyle: g.cores_categorias?.[i] ? { color: g.cores_categorias[i] } : undefined,
          })),
        },
      ],
    }
  }

  const horizontal = g.tipo === 'barra_h' || g.tipo === 'barra_h_empilhada'
  const eixoCategoria = {
    type: 'category',
    data: g.categorias,
    inverse: horizontal,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: LINHA } },
    axisLabel: { color: SUAVE, width: horizontal ? 180 : 110, overflow: 'truncate', interval: 0 },
  }
  const eixoValor = {
    type: 'value',
    splitLine: { lineStyle: { color: LINHA } },
    axisLabel: { color: SUAVE, formatter: (v: number) => eixo(v, g.formato) },
  }
  const empilhado = g.tipo === 'barra_h_empilhada'
  const series = g.series.map((s) => ({
    name: s.nome,
    type: 'bar',
    stack: empilhado ? 'total' : undefined,
    barMaxWidth: 28,
    itemStyle: s.cor ? { color: s.cor } : undefined,
    label: {
      show: !empilhado && g.series.length === 1,
      position: horizontal ? 'right' : 'top',
      color: TEXTO,
      formatter: (p: { value: number }) => fmt(p.value),
    },
    data: s.valores.map((v, i) =>
      g.cores_categorias?.[i] && g.series.length === 1 ? { value: v, itemStyle: { color: g.cores_categorias[i] } } : v,
    ),
  }))
  return {
    ...base,
    grid: { left: 8, right: horizontal ? 64 : 16, top: 24, bottom: base.legend ? 40 : 8, containLabel: true },
    xAxis: horizontal ? eixoValor : eixoCategoria,
    yAxis: horizontal ? eixoCategoria : eixoValor,
    series,
  }
}

export function Grafico({ grafico }: { grafico: TGrafico }) {
  const linhas = grafico.categorias.length
  const altura =
    grafico.tipo === 'barra_h' || grafico.tipo === 'barra_h_empilhada' ? Math.max(260, linhas * 30 + 80) : 320
  const vazio = linhas === 0
  return (
    <figure className={`grafico largura-${grafico.largura ?? 'metade'}`}>
      <figcaption>{grafico.titulo}</figcaption>
      {vazio ? (
        <p className="vazio">Nenhum dado para os filtros escolhidos.</p>
      ) : (
        <ReactECharts option={opcoes(grafico)} style={{ height: altura }} notMerge lazyUpdate />
      )}
    </figure>
  )
}

import { useEffect, useRef, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import type { Grafico as TGrafico } from '../api'
import { eixo, valor } from '../format'
import { coresNeutras, larguraRotuloBarras, marcasEixo, rotulosColunas, type CoresNeutras, type Medidor } from '../graficoLayout'
import { useTema } from '../tema'

const PALETA = ['#0B3D91', '#1B8A4C', '#D9730D', '#5B2C83', '#00A19A', '#E0A100', '#4B5563', '#8E3B46']
const FONTE = "'Public Sans Variable', system-ui, sans-serif"

// Mede o texto com a fonte dos eixos (12 px), para saber se um nome cabe embaixo da coluna.
let contexto: CanvasRenderingContext2D | null = null
const medirTexto: Medidor = (texto) => {
  contexto ??= document.createElement('canvas').getContext('2d')
  if (!contexto) return texto.length * 7
  contexto.font = `12px ${FONTE}`
  return contexto.measureText(texto).width
}

function opcoes(g: TGrafico, largura: number, cores: CoresNeutras) {
  const { texto: TEXTO, suave: SUAVE, linha: LINHA } = cores
  const fmt = (v: unknown) => valor(typeof v === 'number' ? v : null, g.formato)
  const base = {
    color: PALETA,
    textStyle: { fontFamily: FONTE, color: TEXTO },
    tooltip: {
      trigger: g.tipo === 'rosca' ? 'item' : 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: fmt,
      backgroundColor: cores.borda,
      borderColor: LINHA,
      textStyle: { fontFamily: FONTE, color: TEXTO },
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
          radius: ['32%', '50%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: true,
          itemStyle: { borderColor: cores.borda, borderWidth: 2 },
          labelLine: { length: 8, length2: 8 },
          label: {
            formatter: (p: { value: number; percent: number }) => `${fmt(p.value)} (${Math.round(p.percent)}%)`,
            color: SUAVE,
            overflow: 'none',
          },
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
  const nomesBarras = larguraRotuloBarras(largura)
  const colunas = rotulosColunas(largura, g.categorias, medirTexto)
  const eixoCategoria = {
    type: 'category',
    data: g.categorias,
    inverse: horizontal,
    axisTick: { show: false },
    axisLine: { lineStyle: { color: LINHA } },
    axisLabel: horizontal
      ? { color: SUAVE, width: nomesBarras, overflow: 'break', interval: 0 }
      : {
          color: SUAVE,
          width: colunas.largura,
          rotate: colunas.rotacao,
          overflow: 'break',
          interval: 0,
        },
  }
  const eixoValor = {
    type: 'value',
    splitNumber: marcasEixo(horizontal ? largura - nomesBarras - 80 : 320),
    splitLine: { lineStyle: { color: LINHA } },
    axisLabel: { color: SUAVE, hideOverlap: true, formatter: (v: number) => eixo(v, g.formato) },
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
    grid: { left: !horizontal && colunas.rotacao ? 40 : 8, right: horizontal ? 64 : 16, top: 24, bottom: base.legend ? 40 : 8, containLabel: true },
    xAxis: horizontal ? eixoValor : eixoCategoria,
    yAxis: horizontal ? eixoCategoria : eixoValor,
    series,
  }
}

/** Largura do elemento na tela, atualizada quando a janela muda de tamanho. */
function useLargura<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [largura, setLargura] = useState(600)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const medir = () => setLargura(Math.round(el.clientWidth))
    medir()
    const obs = new ResizeObserver(medir)
    obs.observe(el)
    return () => obs.disconnect()
  }, [])
  return [ref, largura] as const
}

export function Grafico({ grafico }: { grafico: TGrafico }) {
  const [ref, largura] = useLargura<HTMLDivElement>()
  const [tema] = useTema()
  const linhas = grafico.categorias.length
  const altura =
    grafico.tipo === 'barra_h' || grafico.tipo === 'barra_h_empilhada' ? Math.max(260, linhas * 30 + 80) : 320
  const vazio = linhas === 0
  return (
    <figure className={`grafico largura-${grafico.largura ?? 'metade'}`}>
      <figcaption>{grafico.titulo}</figcaption>
      <div ref={ref}>
        {vazio ? (
          <p className="vazio">Nenhum dado para os filtros escolhidos.</p>
        ) : (
          <ReactECharts option={opcoes(grafico, largura, coresNeutras(tema))} style={{ height: altura }} notMerge lazyUpdate />
        )}
      </div>
    </figure>
  )
}

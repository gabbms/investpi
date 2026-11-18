// Itens do menu lateral. `pronto: false` aparece desabilitado até a tela existir.
export interface ItemMenu {
  rota: string
  rotulo: string
  cor: string
  pronto: boolean
  painel: boolean // telas do painel levam os filtros junto ao navegar
  endpoint?: string // rota da API que monta a tela
}

export const COR = {
  ambiental: '#1B8A4C',
  social: '#D9730D',
  governanca: '#0B3D91',
  metas: '#5B2C83',
  geral: '#4B5563',
}

export const PILARES: ItemMenu[] = [
  { rota: '/', rotulo: 'Visão Geral', cor: COR.geral, pronto: true, painel: true, endpoint: '/api/painel/visao-geral' },
  { rota: '/ambiental', rotulo: 'Ambiental', cor: COR.ambiental, pronto: true, painel: true, endpoint: '/api/painel/ambiental' },
  { rota: '/social', rotulo: 'Social', cor: COR.social, pronto: true, painel: true, endpoint: '/api/painel/social' },
  { rota: '/governanca', rotulo: 'Governança', cor: COR.governanca, pronto: true, painel: true, endpoint: '/api/painel/governanca' },
  { rota: '/metas', rotulo: 'Metas ASG', cor: COR.metas, pronto: true, painel: true, endpoint: '/api/painel/metas' },
]

export const SETORES: ItemMenu[] = [
  { rota: '/setor/energia-renovavel', rotulo: 'Energia Renovável', cor: '#1565C0', pronto: true, painel: true, endpoint: '/api/painel/setor/energia-renovavel' },
  { rota: '/setor/hidrogenio-verde', rotulo: 'Hidrogênio Verde', cor: '#00A19A', pronto: true, painel: true, endpoint: '/api/painel/setor/hidrogenio-verde' },
  { rota: '/setor/mineracao', rotulo: 'Mineração', cor: '#E0A100', pronto: true, painel: true, endpoint: '/api/painel/setor/mineracao' },
  { rota: '/setor/sustentabilidade', rotulo: 'Sustentabilidade Ambiental', cor: '#1B8A4C', pronto: true, painel: true, endpoint: '/api/painel/setor/sustentabilidade' },
]

export const ADMIN: ItemMenu[] = [
  { rota: '/admin/envio', rotulo: 'Enviar planilha', cor: COR.geral, pronto: true, painel: false },
  { rota: '/admin/versoes', rotulo: 'Histórico de versões', cor: COR.geral, pronto: true, painel: false },
  { rota: '/admin/usuarios', rotulo: 'Usuários', cor: COR.geral, pronto: true, painel: false },
]

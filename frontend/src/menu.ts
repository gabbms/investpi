// Itens do menu lateral. `pronto: false` aparece desabilitado até a tela existir.
export interface ItemMenu {
  rota: string
  rotulo: string
  cor: string
  pronto: boolean
  painel: boolean // telas do painel levam os filtros junto ao navegar
}

export const COR = {
  ambiental: '#1B8A4C',
  social: '#D9730D',
  governanca: '#0B3D91',
  metas: '#5B2C83',
  geral: '#4B5563',
}

export const PILARES: ItemMenu[] = [
  { rota: '/', rotulo: 'Visão Geral', cor: COR.geral, pronto: true, painel: true },
  { rota: '/ambiental', rotulo: 'Ambiental', cor: COR.ambiental, pronto: false, painel: true },
  { rota: '/social', rotulo: 'Social', cor: COR.social, pronto: false, painel: true },
  { rota: '/governanca', rotulo: 'Governança', cor: COR.governanca, pronto: false, painel: true },
  { rota: '/metas', rotulo: 'Metas ASG', cor: COR.metas, pronto: false, painel: true },
]

export const SETORES: ItemMenu[] = [
  { rota: '/setor/energia-renovavel', rotulo: 'Energia Renovável', cor: '#1565C0', pronto: false, painel: true },
  { rota: '/setor/hidrogenio-verde', rotulo: 'Hidrogênio Verde', cor: '#00A19A', pronto: false, painel: true },
  { rota: '/setor/mineracao', rotulo: 'Mineração', cor: '#E0A100', pronto: false, painel: true },
  { rota: '/setor/sustentabilidade', rotulo: 'Sustentabilidade Ambiental', cor: '#1B8A4C', pronto: false, painel: true },
]

export const ADMIN: ItemMenu[] = [
  { rota: '/admin/envio', rotulo: 'Enviar planilha', cor: COR.geral, pronto: true, painel: false },
  { rota: '/admin/versoes', rotulo: 'Histórico de versões', cor: COR.geral, pronto: false, painel: false },
  { rota: '/admin/usuarios', rotulo: 'Usuários', cor: COR.geral, pronto: false, painel: false },
]

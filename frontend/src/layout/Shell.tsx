import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { api, quandoSessaoExpirar, type Opcoes } from '../api'
import { useAuth } from '../auth'
import { MultiSelect } from '../components/MultiSelect'
import { useFiltros } from '../filtros'
import { ADMIN, PILARES, SETORES, type ItemMenu } from '../menu'

const PERFIL = { admin: 'Administrador', leitor: 'Leitor' } as const

function Item({ item, busca }: { item: ItemMenu; busca: string }) {
  if (!item.pronto) {
    return (
      <li>
        <span className="menu-item desabilitado" style={{ ['--cor-item' as string]: item.cor }} title="Em construção">
          {item.rotulo}
        </span>
      </li>
    )
  }
  return (
    <li>
      <NavLink
        to={{ pathname: item.rota, search: item.painel ? busca : '' }}
        end={item.rota === '/'}
        className={({ isActive }) => `menu-item ${isActive ? 'ativo' : ''}`}
        style={{ ['--cor-item' as string]: item.cor }}
      >
        {item.rotulo}
      </NavLink>
    </li>
  )
}

function BarraFiltros() {
  const { filtros, setFiltro, limpar, ativos } = useFiltros()
  const [opcoes, setOpcoes] = useState<Opcoes | null>(null)

  useEffect(() => {
    api.get<Opcoes>('/api/painel/opcoes').then(setOpcoes).catch(() => setOpcoes(null))
  }, [])

  if (!opcoes) return <div className="filtros" />
  return (
    <div className="filtros" role="search" aria-label="Filtros do painel">
      <MultiSelect rotulo="Setor" opcoes={opcoes.setores} selecionados={filtros.setor} aoMudar={(v) => setFiltro('setor', v)} />
      <MultiSelect rotulo="Vice-Presidência" opcoes={opcoes.vps} selecionados={filtros.vp} aoMudar={(v) => setFiltro('vp', v)} />
      <MultiSelect rotulo="Status do projeto" opcoes={opcoes.status} selecionados={filtros.status} aoMudar={(v) => setFiltro('status', v)} />
      <MultiSelect rotulo="Município" opcoes={opcoes.municipios} selecionados={filtros.municipio} aoMudar={(v) => setFiltro('municipio', v)} />
      {ativos > 0 && (
        <button type="button" className="link-botao" onClick={limpar}>
          Limpar filtros ({ativos})
        </button>
      )}
    </div>
  )
}

export function Shell() {
  const { usuario, sair } = useAuth()
  const local = useLocation()
  const navegar = useNavigate()
  const [menuAberto, setMenuAberto] = useState(false)

  useEffect(() => {
    quandoSessaoExpirar(() => {
      sair()
      navegar('/login', { replace: true })
    })
  }, [sair, navegar])

  useEffect(() => setMenuAberto(false), [local.pathname])

  const ehPainel = !local.pathname.startsWith('/admin')
  const busca = ehPainel ? local.search : ''

  return (
    <div className={`shell ${menuAberto ? 'menu-aberto' : ''}`}>
      <aside className="lateral">
        <div className="marca">
          <span className="marca-nome">Painel ASG</span>
          <span className="marca-org">Investe Piauí</span>
        </div>
        <nav aria-label="Telas do painel">
          <ul className="menu">
            {PILARES.map((i) => (
              <Item key={i.rota} item={i} busca={busca} />
            ))}
          </ul>
          <p className="menu-grupo">Setores</p>
          <ul className="menu">
            {SETORES.map((i) => (
              <Item key={i.rota} item={i} busca={busca} />
            ))}
          </ul>
          {usuario?.perfil === 'admin' && (
            <>
              <p className="menu-grupo">Administração</p>
              <ul className="menu">
                {ADMIN.map((i) => (
                  <Item key={i.rota} item={i} busca={busca} />
                ))}
              </ul>
            </>
          )}
        </nav>
      </aside>

      <div className="principal">
        <header className="topo">
          <button type="button" className="menu-alternar" onClick={() => setMenuAberto((a) => !a)} aria-expanded={menuAberto}>
            Menu
          </button>
          {ehPainel ? <BarraFiltros /> : <div className="filtros" />}
          <div className="usuario">
            <span className="usuario-nome">{usuario?.nome}</span>
            {usuario && usuario.nome !== PERFIL[usuario.perfil] && <span className="usuario-perfil">{PERFIL[usuario.perfil]}</span>}
            <button type="button" className="link-botao" onClick={sair}>
              Sair
            </button>
          </div>
        </header>
        <main className="conteudo">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

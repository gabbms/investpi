import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export function Login() {
  const { usuario, entrar } = useAuth()
  const navegar = useNavigate()
  const local = useLocation()
  const estado = (local.state ?? {}) as { de?: string }
  const [expirou] = useState(() => sessionStorage.getItem('asg_expirou') === '1')
  useEffect(() => sessionStorage.removeItem('asg_expirou'), [])
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (usuario) return <Navigate to={estado.de ?? '/'} replace />

  async function enviar(e: FormEvent) {
    e.preventDefault()
    setErro(null)
    setEnviando(true)
    try {
      await entrar(email, senha)
      navegar(estado.de ?? '/', { replace: true })
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Não foi possível entrar.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="login">
      <section className="login-painel">
        <div className="login-barras" aria-hidden="true">
          <span style={{ background: '#1B8A4C', height: '46%' }} />
          <span style={{ background: '#D9730D', height: '68%' }} />
          <span style={{ background: '#0B3D91', height: '100%' }} />
        </div>
        <h1>Painel ASG</h1>
        <p>Indicadores ambientais, sociais e de governança dos projetos acompanhados pela Investe Piauí.</p>
      </section>

      <form className="login-form" onSubmit={enviar}>
        <h2>Entrar</h2>
        {expirou && !erro && <p className="alerta">Sua sessão terminou. Entre novamente para continuar.</p>}
        <label>
          E-mail
          <input type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Senha
          <input type="password" autoComplete="current-password" required value={senha} onChange={(e) => setSenha(e.target.value)} />
        </label>
        {erro && (
          <p className="erro" role="alert">
            {erro}
          </p>
        )}
        <button type="submit" className="botao" disabled={enviando}>
          {enviando ? 'Entrando…' : 'Entrar'}
        </button>
        <p className="suave pequeno">Não tem acesso? Peça ao administrador do painel.</p>
      </form>
    </div>
  )
}

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { api, token, type Usuario } from './api'

interface Auth {
  usuario: Usuario | null
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  sair: () => void
}

const Contexto = createContext<Auth | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(() => token.ler() !== null)

  useEffect(() => {
    if (!token.ler()) return
    api
      .get<Usuario>('/api/auth/eu')
      .then(setUsuario)
      .catch(() => token.apagar())
      .finally(() => setCarregando(false))
  }, [])

  const entrar = useCallback(async (email: string, senha: string) => {
    const r = await api.post<{ token: string; usuario: Usuario }>('/api/auth/login', { email, senha })
    token.gravar(r.token)
    setUsuario(r.usuario)
  }, [])

  const sair = useCallback(() => {
    token.apagar()
    setUsuario(null)
  }, [])

  return <Contexto.Provider value={{ usuario, carregando, entrar, sair }}>{children}</Contexto.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): Auth {
  const c = useContext(Contexto)
  if (!c) throw new Error('useAuth fora do AuthProvider')
  return c
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useAuth()
  const local = useLocation()
  if (carregando) return <div className="carregando-tela">Carregando…</div>
  if (!usuario) return <Navigate to="/login" replace state={{ de: local.pathname + local.search }} />
  return <>{children}</>
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { usuario } = useAuth()
  if (usuario?.perfil !== 'admin') return <Navigate to="/" replace />
  return <>{children}</>
}

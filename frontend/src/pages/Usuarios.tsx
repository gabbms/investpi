import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { api, ErroApi, type UsuarioAdmin } from '../api'
import { useAuth } from '../auth'

const PERFIS = { admin: 'Administrador', leitor: 'Leitor' } as const

function mensagemDe(e: unknown): string {
  if (e instanceof ErroApi && Array.isArray(e.detalhe)) return 'Confira os campos: e-mail válido e senha com pelo menos 8 caracteres.'
  return e instanceof Error ? e.message : 'Não foi possível salvar.'
}

export function Usuarios() {
  const { usuario: eu } = useAuth()
  const [lista, setLista] = useState<UsuarioAdmin[]>([])
  const [erro, setErro] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [novo, setNovo] = useState({ nome: '', email: '', senha: '', perfil: 'leitor' as 'admin' | 'leitor' })
  const [senhaDe, setSenhaDe] = useState<number | null>(null)
  const [novaSenha, setNovaSenha] = useState('')

  const carregar = useCallback(() => {
    api.get<UsuarioAdmin[]>('/api/usuarios').then(setLista).catch((e) => setErro(e.message))
  }, [])
  useEffect(carregar, [carregar])

  async function salvar(acao: () => Promise<unknown>, ok: string) {
    setErro(null)
    setAviso(null)
    try {
      await acao()
      setAviso(ok)
      carregar()
      return true
    } catch (e) {
      setErro(mensagemDe(e))
      return false
    }
  }

  async function criar(e: FormEvent) {
    e.preventDefault()
    if (await salvar(() => api.post('/api/usuarios', novo), `Usuário ${novo.email} criado.`)) {
      setNovo({ nome: '', email: '', senha: '', perfil: 'leitor' })
    }
  }

  async function redefinir(u: UsuarioAdmin, e: FormEvent) {
    e.preventDefault()
    if (await salvar(() => api.patch(`/api/usuarios/${u.id}`, { senha: novaSenha }), `Senha de ${u.nome} redefinida.`)) {
      setSenhaDe(null)
      setNovaSenha('')
    }
  }

  return (
    <div className="pagina admin" style={{ ['--cor-pagina' as string]: '#4B5563' }}>
      <header className="pagina-cabecalho">
        <h1>Usuários</h1>
        <p>Administradores enviam planilhas, ativam versões e cadastram pessoas. Leitores veem todas as telas do painel.</p>
      </header>

      <section className="bloco">
        <h2>Cadastrar usuário</h2>
        <form className="formulario" onSubmit={criar}>
          <label>
            Nome
            <input type="text" required value={novo.nome} onChange={(e) => setNovo({ ...novo, nome: e.target.value })} />
          </label>
          <label>
            E-mail
            <input type="email" required value={novo.email} onChange={(e) => setNovo({ ...novo, email: e.target.value })} />
          </label>
          <label>
            Senha inicial
            <input type="password" required minLength={8} autoComplete="new-password" value={novo.senha}
              onChange={(e) => setNovo({ ...novo, senha: e.target.value })} />
          </label>
          <label>
            Perfil
            <select value={novo.perfil} onChange={(e) => setNovo({ ...novo, perfil: e.target.value as 'admin' | 'leitor' })}>
              <option value="leitor">Leitor</option>
              <option value="admin">Administrador</option>
            </select>
          </label>
          <button type="submit" className="botao">
            Cadastrar
          </button>
        </form>
      </section>

      {aviso && <p className="bloco sucesso">{aviso}</p>}
      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}

      <section className="tabela">
        <h3>Pessoas com acesso</h3>
        <div className="tabela-rolagem">
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Situação</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {lista.map((u) => {
                const souEu = u.id === eu?.id
                return (
                  <tr key={u.id}>
                    <td>
                      {u.nome}
                      {souEu && <span className="suave"> (você)</span>}
                    </td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        aria-label={`Perfil de ${u.nome}`}
                        value={u.perfil}
                        disabled={souEu}
                        onChange={(e) =>
                          salvar(() => api.patch(`/api/usuarios/${u.id}`, { perfil: e.target.value }),
                            `${u.nome} agora é ${PERFIS[e.target.value as 'admin' | 'leitor']}.`)
                        }
                      >
                        <option value="leitor">Leitor</option>
                        <option value="admin">Administrador</option>
                      </select>
                    </td>
                    <td>
                      <span className={`selo ${u.ativo ? 'selo-verde' : 'selo-neutro'}`}>{u.ativo ? 'Ativo' : 'Desativado'}</span>
                    </td>
                    <td>
                      <div className="acoes-linha">
                        {!souEu && (
                          <button type="button" className="link-botao"
                            onClick={() => salvar(() => api.patch(`/api/usuarios/${u.id}`, { ativo: !u.ativo }),
                              `${u.nome} ${u.ativo ? 'desativado' : 'reativado'}.`)}>
                            {u.ativo ? 'Desativar' : 'Reativar'}
                          </button>
                        )}
                        <button type="button" className="link-botao" onClick={() => { setSenhaDe(senhaDe === u.id ? null : u.id); setNovaSenha('') }}>
                          Redefinir senha
                        </button>
                      </div>
                      {senhaDe === u.id && (
                        <form className="senha-linha" onSubmit={(e) => redefinir(u, e)}>
                          <input type="password" required minLength={8} autoComplete="new-password" placeholder="Nova senha (8+ caracteres)"
                            aria-label={`Nova senha de ${u.nome}`} value={novaSenha} onChange={(e) => setNovaSenha(e.target.value)} />
                          <button type="submit" className="botao secundario">
                            Salvar senha
                          </button>
                        </form>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

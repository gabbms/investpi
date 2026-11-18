import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, RequireAdmin, RequireAuth } from './auth'
import { Shell } from './layout/Shell'
import { Envio } from './pages/Envio'
import { PaginaPainel } from './components/PaginaPainel'
import { PILARES, SETORES, TEMAS } from './menu'
import { Login } from './pages/Login'
import { Usuarios } from './pages/Usuarios'
import { Versoes } from './pages/Versoes'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <RequireAuth>
                <Shell />
              </RequireAuth>
            }
          >
            {[...PILARES, ...TEMAS, ...SETORES]
              .filter((i) => i.pronto && i.endpoint)
              .map((i) => (
                <Route
                  key={i.rota}
                  path={i.rota}
                  element={<PaginaPainel key={i.endpoint} endpoint={i.endpoint!} cor={i.cor} exportacaoExtra={i.exportacaoExtra} />}
                />
              ))}
            <Route
              path="admin/envio"
              element={
                <RequireAdmin>
                  <Envio />
                </RequireAdmin>
              }
            />
            <Route
              path="admin/versoes"
              element={
                <RequireAdmin>
                  <Versoes />
                </RequireAdmin>
              }
            />
            <Route
              path="admin/usuarios"
              element={
                <RequireAdmin>
                  <Usuarios />
                </RequireAdmin>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

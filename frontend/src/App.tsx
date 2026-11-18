import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, RequireAdmin, RequireAuth } from './auth'
import { Shell } from './layout/Shell'
import { Envio } from './pages/Envio'
import { Login } from './pages/Login'
import { VisaoGeral } from './pages/VisaoGeral'

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
            <Route index element={<VisaoGeral />} />
            <Route
              path="admin/envio"
              element={
                <RequireAdmin>
                  <Envio />
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

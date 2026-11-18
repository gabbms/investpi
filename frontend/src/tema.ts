import { useSyncExternalStore } from 'react'

// Tema claro/escuro. O index.html aplica a mesma regra antes do React, para a página não piscar.
export type Tema = 'claro' | 'escuro'
const CHAVE = 'asg_tema'

/** Escolha salva (se válida) vence o tema do sistema. */
export function temaInicial(salvo: string | null, sistemaEscuro: boolean): Tema {
  if (salvo === 'claro' || salvo === 'escuro') return salvo
  return sistemaEscuro ? 'escuro' : 'claro'
}

const ouvintes = new Set<() => void>()

function atual(): Tema {
  return document.documentElement.dataset.tema === 'escuro' ? 'escuro' : 'claro'
}

/** Aplica o tema na página e guarda a escolha neste navegador. */
export function aplicarTema(t: Tema): void {
  document.documentElement.dataset.tema = t
  try {
    localStorage.setItem(CHAVE, t)
  } catch {
    // navegação privada sem localStorage: o tema vale só até fechar a aba
  }
  ouvintes.forEach((o) => o())
}

function assinar(o: () => void) {
  ouvintes.add(o)
  return () => ouvintes.delete(o)
}

/** Tema atual e a função que alterna entre claro e escuro. */
export function useTema(): [Tema, () => void] {
  const tema = useSyncExternalStore(assinar, atual, () => 'claro' as Tema)
  return [tema, () => aplicarTema(tema === 'escuro' ? 'claro' : 'escuro')]
}

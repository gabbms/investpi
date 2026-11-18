import { useSyncExternalStore } from 'react'

// Tema claro/escuro. O index.html aplica a mesma regra antes do React, para a página não piscar.
export type Tema = 'claro' | 'escuro'
const CHAVE = 'asg_tema'
const CONSULTA = '(prefers-color-scheme: dark)'

/** Escolha salva (se válida) vence o tema do sistema. */
export function temaInicial(salvo: string | null, sistemaEscuro: boolean): Tema {
  if (salvo === 'claro' || salvo === 'escuro') return salvo
  return sistemaEscuro ? 'escuro' : 'claro'
}

/** Sem escolha válida guardada, a página acompanha o tema do sistema ao vivo. */
export function seguirSistema(salvo: string | null): boolean {
  return salvo !== 'claro' && salvo !== 'escuro'
}

/** Evento `storage` (troca feita em outra aba) → tema a aplicar nesta aba, ou null se não é do tema. */
export function temaDoEvento(chave: string | null, novo: string | null, sistemaEscuro: boolean): Tema | null {
  return chave === CHAVE ? temaInicial(novo, sistemaEscuro) : null
}

const ouvintes = new Set<() => void>()

function atual(): Tema {
  return document.documentElement.dataset.tema === 'escuro' ? 'escuro' : 'claro'
}

function lerSalvo(): string | null {
  try {
    return localStorage.getItem(CHAVE)
  } catch {
    return null // navegação privada sem localStorage
  }
}

function sistemaEscuro(): boolean {
  return typeof matchMedia === 'function' && matchMedia(CONSULTA).matches
}

function mostrar(t: Tema) {
  document.documentElement.dataset.tema = t
  ouvintes.forEach((o) => o())
}

/** Aplica o tema na página e guarda a escolha neste navegador. */
export function aplicarTema(t: Tema): void {
  try {
    localStorage.setItem(CHAVE, t)
  } catch {
    // sem localStorage: o tema vale só até fechar a aba
  }
  mostrar(t)
}

// Escuta, uma vez por página: troca do tema do sistema (se não há escolha) e troca feita em outra aba.
if (typeof window !== 'undefined') {
  if (typeof matchMedia === 'function') {
    matchMedia(CONSULTA).addEventListener?.('change', (e) => {
      if (seguirSistema(lerSalvo())) mostrar(e.matches ? 'escuro' : 'claro')
    })
  }
  window.addEventListener('storage', (e) => {
    const t = temaDoEvento(e.key, e.newValue, sistemaEscuro())
    if (t) mostrar(t)
  })
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

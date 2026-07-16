import type { ADM, ADMListItem, DecisionRecord } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }
  return res.json() as Promise<T>
}

export const listAdms = () => request<ADMListItem[]>('/adm')

export const getAdm = (admId: string) => request<ADM>(`/adm/${admId}`)

export const runAgent = (admId: string) =>
  request<DecisionRecord>(`/agent/run/${admId}`, { method: 'POST' })

export const getDecision = (decisionId: string) =>
  request<DecisionRecord>(`/decision/${decisionId}`)

export const agentWsUrl = (admId: string) =>
  `${API_BASE.replace(/^http/, 'ws')}/ws/agent/${admId}`

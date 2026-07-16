import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, CircleDollarSign, Mail, ShieldAlert, type LucideIcon } from 'lucide-react'
import type { ADM, AgentStepKey, Decision, DecisionRecord, StepStatus, WsAgentMessage } from '../lib/types'
import { agentWsUrl, ApiError, getDecision, runAgent } from '../lib/api'
import { AGENT_STEPS, AgentTimeline } from './AgentTimeline'

export type AgentStatus = 'idle' | 'running' | 'done' | 'not_implemented' | 'error'

interface Props {
  adm: ADM | null
}

const DECISION_META: Record<
  Decision,
  { icon: LucideIcon; headline: string; card: string; icon_bg: string; bar: string; text: string }
> = {
  DISPUTE: {
    icon: ShieldAlert,
    headline: 'Dispute recommended',
    card: 'from-indigo-50 to-white border-indigo-200',
    icon_bg: 'bg-indigo-600 text-white',
    bar: 'bg-indigo-600',
    text: 'text-indigo-700',
  },
  PAY: {
    icon: CircleDollarSign,
    headline: 'Pay recommended',
    card: 'from-emerald-50 to-white border-emerald-200',
    icon_bg: 'bg-emerald-600 text-white',
    bar: 'bg-emerald-600',
    text: 'text-emerald-700',
  },
  ESCALATE: {
    icon: AlertTriangle,
    headline: 'Escalate to human',
    card: 'from-amber-50 to-white border-amber-200',
    icon_bg: 'bg-amber-600 text-white',
    bar: 'bg-amber-600',
    text: 'text-amber-700',
  },
}

const GENERATE_OUTPUT_NODES = new Set(['draft_letter', 'draft_pay_auth', 'open_case'])

function timelineKeyForNode(node: string): AgentStepKey | null {
  if (GENERATE_OUTPUT_NODES.has(node)) return 'generate_output'
  if (AGENT_STEPS.some((s) => s.key === node)) return node as AgentStepKey
  return null
}

function summarizeStep(node: string, data: Record<string, any>): string {
  switch (node) {
    case 'parse_adm':
      return `Parsed ADM #${data.adm_id}, amount $${Number(data.amount_claimed).toFixed(2)}`
    case 'lookup_booking':
      return data.pnr_id
        ? `Loaded PNR ${data.pnr_id}, fare basis ${data.fare_basis_code}`
        : 'No PNR found for this ticket'
    case 'retrieve_rule':
      return `Retrieved ${data.n_chunks} chunks from ${data.airline_code} corpus (top sim: ${Number(data.top_score).toFixed(2)})`
    case 'verify_calculation': {
      const ap = data.advance_purchase ?? {}
      const bc = data.booking_class ?? {}
      const tax = data.tax_calculation ?? {}
      const apStr = ap.applicable === false || ap.applicable === undefined ? 'n/a' : ap.satisfied ? 'ok' : 'fail'
      const bcStr = bc.match === undefined ? 'n/a' : bc.match ? 'ok' : 'fail'
      const taxStr = tax.applicable ? `$${Number(tax.shortfall).toFixed(2)}` : 'n/a'
      return `Advance purchase: ${apStr}, class match: ${bcStr}, tax delta: ${taxStr}`
    }
    case 'analyze':
      return `Model proposed ${data.decision} @ ${Math.round(Number(data.confidence) * 100)}%`
    case 'draft_letter':
      return 'Drafted dispute letter'
    case 'draft_pay_auth':
      return 'Drafted pay authorization memo'
    case 'open_case':
      return 'Drafted escalation ticket'
    case 'submit_decision':
      return `Decision #${data.decision_id} logged`
    case 'notify_reviewer':
      return data.sent_to ? `Email sent to ${data.sent_to}` : `Email failed: ${data.error ?? 'unknown error'}`
    default:
      return ''
  }
}

function emptySteps(): Record<AgentStepKey, StepStatus> {
  const steps = {} as Record<AgentStepKey, StepStatus>
  for (const s of AGENT_STEPS) steps[s.key] = { state: 'pending' }
  return steps
}

function timeAgo(iso: string): string {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} min ago`
  return `${Math.floor(minutes / 60)}h ago`
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  return (
    <button
      type="button"
      onClick={async () => {
        await navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
      }}
      className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
    >
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

function ReviewerStatusCard({
  sentTo,
  decision,
}: {
  sentTo: string | null
  decision: DecisionRecord
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide">Reviewer Status</h3>
      <div className="mt-2.5 space-y-1.5 text-sm text-slate-700">
        <p className="flex items-center gap-1.5">
          <Mail className="h-3.5 w-3.5 text-slate-400" />
          {sentTo ? `Email sent to ${sentTo}` : 'Reviewer notified'}
        </p>
        {decision.reviewer_action === null && (
          <p className="text-slate-500">⏳ Awaiting review</p>
        )}
        {decision.reviewer_action === 'approved' && (
          <p className="text-emerald-600">
            ✅ Approved {decision.reviewer_action_at ? timeAgo(decision.reviewer_action_at) : ''}
          </p>
        )}
        {decision.reviewer_action === 'rejected' && (
          <p className="text-rose-600">
            ❌ Rejected {decision.reviewer_action_at ? timeAgo(decision.reviewer_action_at) : ''}
          </p>
        )}
        {decision.reviewer_action === 'request_info' && (
          <p className="text-amber-600">
            ✋ More info requested {decision.reviewer_action_at ? timeAgo(decision.reviewer_action_at) : ''}
          </p>
        )}
      </div>
    </div>
  )
}

export function AgentPanel({ adm }: Props) {
  const [status, setStatus] = useState<AgentStatus>('idle')
  const [decision, setDecision] = useState<DecisionRecord | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [steps, setSteps] = useState<Record<AgentStepKey, StepStatus>>(emptySteps())
  const [reviewerSentTo, setReviewerSentTo] = useState<string | null>(null)
  const [showTimeline, setShowTimeline] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  const fellBackRef = useRef(false)

  useEffect(() => {
    // Selecting a different ADM invalidates any in-flight run.
    wsRef.current?.close()
    wsRef.current = null
    setStatus('idle')
    setDecision(null)
    setErrorMessage(null)
    setSteps(emptySteps())
    setReviewerSentTo(null)
    setShowTimeline(false)
  }, [adm?.adm_id])

  // Poll the reviewer status while it's unresolved.
  useEffect(() => {
    if (status !== 'done' || !decision || decision.reviewer_action !== null) return
    const interval = setInterval(async () => {
      try {
        const updated = await getDecision(decision.decision_id)
        setDecision(updated)
      } catch {
        // transient — next tick retries
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [status, decision])

  const runViaPost = async (admId: string) => {
    try {
      const result = await runAgent(admId)
      setDecision(result)
      setStatus('done')
    } catch (err) {
      if (err instanceof ApiError && err.status === 501) {
        setStatus('not_implemented')
      } else {
        setErrorMessage(err instanceof Error ? err.message : 'Unknown error')
        setStatus('error')
      }
    }
  }

  const handleRun = () => {
    if (!adm) return
    setStatus('running')
    setErrorMessage(null)
    setDecision(null)
    setSteps(emptySteps())
    setReviewerSentTo(null)
    setShowTimeline(true)
    fellBackRef.current = false

    let receivedAnyMessage = false
    const fallback = () => {
      if (fellBackRef.current) return
      fellBackRef.current = true
      setShowTimeline(false)
      runViaPost(adm.adm_id)
    }

    let ws: WebSocket
    try {
      ws = new WebSocket(agentWsUrl(adm.adm_id))
    } catch {
      fallback()
      return
    }
    wsRef.current = ws

    ws.onmessage = (event) => {
      receivedAnyMessage = true
      const msg: WsAgentMessage = JSON.parse(event.data)

      if (msg.type === 'step_start') {
        const key = timelineKeyForNode(msg.node)
        if (key) setSteps((prev) => ({ ...prev, [key]: { state: 'running' } }))
        return
      }

      if (msg.type === 'step') {
        const key = timelineKeyForNode(msg.node)
        const data = msg.events[0]?.data ?? {}
        if (msg.node === 'notify_reviewer' && data.sent_to) {
          setReviewerSentTo(data.sent_to as string)
        }
        if (key) {
          setSteps((prev) => ({ ...prev, [key]: { state: 'complete', summary: summarizeStep(msg.node, data) } }))
        }
        return
      }

      if (msg.type === 'done') {
        getDecision(msg.decision_id)
          .then((d) => {
            setDecision(d)
            setStatus('done')
          })
          .catch(() => fallback())
        return
      }

      if (msg.type === 'error') {
        setErrorMessage(msg.message)
        setStatus('error')
      }
    }

    ws.onerror = () => {
      if (!receivedAnyMessage) fallback()
    }

    ws.onclose = () => {
      if (!receivedAnyMessage) fallback()
    }
  }

  return (
    <div className="w-96 shrink-0 border-l border-slate-200 bg-white overflow-y-auto p-7">
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
        Agent
      </h2>

      <button
        type="button"
        disabled={!adm || status === 'running'}
        onClick={handleRun}
        className="mt-4 w-full rounded-md bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {status === 'running' ? 'Running…' : 'Run Agent'}
      </button>

      <div className="mt-6 space-y-6">
        {status === 'idle' && (
          <p className="text-sm text-slate-500">Run the agent to evaluate this ADM.</p>
        )}

        {status === 'not_implemented' && (
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
            Agent not implemented yet — the LangGraph state machine is Day 2 work. This
            button is wired to the real endpoint and will work once that ships.
          </div>
        )}

        {status === 'error' && (
          <div className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
            {errorMessage}
          </div>
        )}

        {showTimeline && (status === 'running' || status === 'done') && (
          <AgentTimeline steps={steps} />
        )}

        {status === 'done' && decision && (
          <div className="space-y-6">
            {(() => {
              const meta = DECISION_META[decision.decision]
              const Icon = meta.icon
              const pct = Math.round(decision.confidence * 100)
              return (
                <div className={`rounded-xl border bg-linear-to-b p-6 text-center shadow-sm ${meta.card}`}>
                  <div className={`mx-auto flex h-12 w-12 items-center justify-center rounded-full ${meta.icon_bg}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <p className="mt-3 text-2xl font-bold tracking-tight text-slate-900">
                    {decision.decision}
                  </p>
                  <p className={`text-sm font-medium ${meta.text}`}>{meta.headline}</p>

                  <div className="mx-auto mt-5 max-w-55">
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200/70">
                      <div
                        className={`h-full rounded-full ${meta.bar}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <p className="mt-1.5 text-xs font-semibold text-slate-500">
                      {pct}% confidence
                    </p>
                  </div>
                </div>
              )
            })()}

            <div>
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Output Artifact
                </h3>
                <CopyButton text={decision.output_artifact} />
              </div>
              <pre className="mt-2 max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-800">
                {decision.output_artifact}
              </pre>
            </div>

            <ReviewerStatusCard sentTo={reviewerSentTo} decision={decision} />
          </div>
        )}
      </div>
    </div>
  )
}

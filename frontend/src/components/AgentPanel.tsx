import { useState } from 'react'
import type { ADM, DecisionRecord } from '../lib/types'

export type AgentStatus = 'idle' | 'running' | 'done' | 'not_implemented' | 'error'

interface Props {
  adm: ADM | null
  status: AgentStatus
  decision: DecisionRecord | null
  errorMessage: string | null
  onRun: () => void
}

const DECISION_STYLES: Record<string, string> = {
  DISPUTE: 'bg-indigo-100 text-indigo-700',
  PAY: 'bg-emerald-100 text-emerald-700',
  ESCALATE: 'bg-amber-100 text-amber-700',
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

export function AgentPanel({ adm, status, decision, errorMessage, onRun }: Props) {
  return (
    <div className="w-96 shrink-0 border-l border-slate-200 bg-white overflow-y-auto p-6">
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
        Agent
      </h2>

      <button
        type="button"
        disabled={!adm || status === 'running'}
        onClick={onRun}
        className="mt-4 w-full rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {status === 'running' ? 'Running…' : 'Run Agent'}
      </button>

      <div className="mt-4">
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

        {status === 'done' && decision && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${DECISION_STYLES[decision.decision]}`}
              >
                {decision.decision}
              </span>
              <span className="text-xs text-slate-500">
                confidence {(decision.confidence * 100).toFixed(0)}%
              </span>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Output Artifact
                </h3>
                <CopyButton text={decision.output_artifact} />
              </div>
              <pre className="mt-1 whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800">
                {decision.output_artifact}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import {
  Brain,
  Calculator,
  CheckCircle,
  Database,
  FileText,
  Mail,
  PenTool,
  Search,
  type LucideIcon,
} from 'lucide-react'
import type { AgentStepKey, StepStatus } from '../lib/types'

export const AGENT_STEPS: { key: AgentStepKey; label: string; icon: LucideIcon }[] = [
  { key: 'parse_adm', label: 'Parsing ADM notice', icon: FileText },
  { key: 'lookup_booking', label: 'Pulling PNR from booking DB', icon: Database },
  { key: 'retrieve_rule', label: 'Retrieving fare rule (RAG)', icon: Search },
  { key: 'verify_calculation', label: 'Verifying dates and tax math', icon: Calculator },
  { key: 'analyze', label: 'Reasoning over evidence', icon: Brain },
  { key: 'generate_output', label: 'Drafting output artifact', icon: PenTool },
  { key: 'submit_decision', label: 'Logging decision', icon: CheckCircle },
  { key: 'notify_reviewer', label: 'Emailing human reviewer', icon: Mail },
]

interface Props {
  steps: Record<AgentStepKey, StepStatus>
}

export function AgentTimeline({ steps }: Props) {
  return (
    <div className="space-y-0">
      {AGENT_STEPS.map((step, i) => {
        const status = steps[step.key] ?? { state: 'pending' as const }
        const Icon = step.icon
        const isLast = i === AGENT_STEPS.length - 1

        return (
          <div key={step.key} className="relative flex gap-3 pb-4">
            {!isLast && (
              <div
                className={`absolute left-[15px] top-8 h-[calc(100%-1.5rem)] w-px ${
                  status.state === 'complete' ? 'bg-emerald-400' : 'bg-slate-200'
                }`}
              />
            )}

            <div
              className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${
                status.state === 'complete'
                  ? 'border-emerald-400 bg-emerald-50 text-emerald-600'
                  : status.state === 'running'
                    ? 'animate-pulse border-indigo-400 bg-indigo-50 text-indigo-600 ring-2 ring-indigo-200'
                    : 'border-slate-200 bg-slate-50 text-slate-400'
              }`}
            >
              {status.state === 'complete' ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <Icon className="h-4 w-4" />
              )}
            </div>

            <div className="min-w-0 flex-1 pt-1">
              <p
                className={`text-sm font-medium ${
                  status.state === 'pending' ? 'text-slate-400' : 'text-slate-800'
                }`}
              >
                {step.label}
              </p>
              {status.state === 'running' && (
                <p className="text-xs text-indigo-500">Running…</p>
              )}
              {status.state === 'complete' && status.summary && (
                <p className="truncate text-xs text-slate-500">{status.summary}</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

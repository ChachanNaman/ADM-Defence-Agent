import {
  Brain,
  Calculator,
  Check,
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
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {AGENT_STEPS.map((step, i) => {
        const status = steps[step.key] ?? { state: 'pending' as const }
        const Icon = step.icon
        const isLast = i === AGENT_STEPS.length - 1

        return (
          <div key={step.key} className="relative flex gap-3.5 pb-5 last:pb-0">
            {/* Connector: static track + a fill that grows when the step completes */}
            {!isLast && (
              <div className="absolute left-3.75 top-9 h-[calc(100%-1.9rem)] w-0.5 rounded bg-slate-100">
                <div
                  className={`w-full origin-top rounded bg-emerald-400 transition-transform duration-500 ease-out ${
                    status.state === 'complete' ? 'h-full scale-y-100' : 'h-full scale-y-0'
                  }`}
                />
              </div>
            )}

            <div
              className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-colors duration-300 ${
                status.state === 'complete'
                  ? 'border-emerald-400 bg-emerald-50 text-emerald-600'
                  : status.state === 'running'
                    ? 'border-indigo-400 bg-indigo-50 text-indigo-600 ring-4 ring-indigo-100'
                    : 'border-slate-200 bg-slate-50 text-slate-300'
              }`}
            >
              {status.state === 'complete' ? (
                <Check className="animate-pop-in h-4 w-4" strokeWidth={3} />
              ) : status.state === 'running' ? (
                <Icon className="animate-pulse-soft h-4 w-4" />
              ) : (
                <Icon className="h-4 w-4" />
              )}
            </div>

            <div className="min-w-0 flex-1 pt-1.5">
              <p
                className={`text-sm font-medium transition-colors duration-300 ${
                  status.state === 'pending' ? 'text-slate-400' : 'text-slate-800'
                }`}
              >
                {step.label}
              </p>
              {status.state === 'running' && (
                <p className="animate-pulse-soft mt-0.5 text-xs font-medium text-indigo-500">
                  Running…
                </p>
              )}
              {status.state === 'complete' && status.summary && (
                <p className="animate-fade-up mt-0.5 truncate font-mono text-[11px] text-slate-500">
                  {status.summary}
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

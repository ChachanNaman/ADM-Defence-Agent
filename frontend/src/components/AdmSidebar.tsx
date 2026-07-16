import { CalendarClock } from 'lucide-react'
import type { ADMListItem } from '../lib/types'

interface Props {
  items: ADMListItem[]
  selectedId: string | null
  onSelect: (admId: string) => void
}

function daysUntil(iso: string): number {
  const ms = new Date(iso + 'T23:59:59').getTime() - Date.now()
  return Math.ceil(ms / 86_400_000)
}

function DeadlineChip({ deadline }: { deadline: string }) {
  const days = daysUntil(deadline)
  const tone =
    days <= 2
      ? 'bg-rose-50 text-rose-700 ring-rose-200'
      : days <= 5
        ? 'bg-amber-50 text-amber-700 ring-amber-200'
        : 'bg-slate-100 text-slate-500 ring-slate-200'
  const label = days < 0 ? 'expired' : days === 0 ? 'due today' : `${days}d left`

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-mono text-[10px] font-medium ring-1 ring-inset ${tone}`}
    >
      <CalendarClock className="h-3 w-3" />
      {label}
    </span>
  )
}

export function AdmSidebar({ items, selectedId, onSelect }: Props) {
  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-5 py-3.5">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400">
          Incoming ADMs
        </h2>
      </div>
      <ul className="flex-1 overflow-y-auto p-2.5">
        {items.map((item, i) => {
          const selected = item.adm_id === selectedId
          return (
            <li
              key={item.adm_id}
              className="animate-fade-up mb-1.5"
              style={{ animationDelay: `${Math.min(i * 45, 400)}ms` }}
            >
              <button
                type="button"
                onClick={() => onSelect(item.adm_id)}
                className={`w-full rounded-lg border px-3.5 py-3 text-left transition-all duration-200 ${
                  selected
                    ? 'border-indigo-300 bg-indigo-50/60 shadow-sm ring-1 ring-indigo-200'
                    : 'border-transparent hover:border-slate-200 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-medium text-slate-500">
                    {item.adm_id}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 font-mono text-[10px] font-bold tracking-wide ${
                      selected
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-800 text-slate-100'
                    }`}
                  >
                    {item.airline_code}
                  </span>
                </div>
                <div className="mt-1.5 flex items-baseline justify-between">
                  <span className="font-mono text-base font-semibold tracking-tight text-slate-900">
                    ${item.amount_claimed.toFixed(2)}
                  </span>
                  <DeadlineChip deadline={item.dispute_deadline} />
                </div>
                <p className="mt-1 truncate font-mono text-[10px] text-slate-400">
                  TKT {item.ticket_number}
                </p>
              </button>
            </li>
          )
        })}
      </ul>
    </aside>
  )
}

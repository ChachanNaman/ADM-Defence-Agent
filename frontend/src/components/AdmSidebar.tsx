import type { ADMListItem } from '../lib/types'

interface Props {
  items: ADMListItem[]
  selectedId: string | null
  onSelect: (admId: string) => void
}

export function AdmSidebar({ items, selectedId, onSelect }: Props) {
  return (
    <aside className="w-72 shrink-0 border-r border-slate-200 bg-slate-50 overflow-y-auto">
      <div className="px-4 py-3 border-b border-slate-200">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
          Incoming ADMs
        </h2>
      </div>
      <ul>
        {items.map((item) => (
          <li key={item.adm_id}>
            <button
              type="button"
              onClick={() => onSelect(item.adm_id)}
              className={`w-full text-left px-4 py-3 border-b border-slate-100 transition-colors ${
                item.adm_id === selectedId
                  ? 'bg-white border-l-4 border-l-indigo-600'
                  : 'hover:bg-slate-100 border-l-4 border-l-transparent'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-slate-500">{item.adm_id}</span>
                <span className="text-xs font-medium text-slate-500">{item.airline_code}</span>
              </div>
              <div className="mt-1 text-sm font-semibold text-slate-900">
                ${item.amount_claimed.toFixed(2)}
              </div>
              <div className="mt-0.5 text-xs text-slate-500">
                Deadline {item.dispute_deadline}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}

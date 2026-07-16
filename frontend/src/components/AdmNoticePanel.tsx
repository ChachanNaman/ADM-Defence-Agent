import { FileWarning, TicketsPlane } from 'lucide-react'
import type { ADM } from '../lib/types'

interface Props {
  adm: ADM | null
  loading: boolean
}

function Field({ label, value, mono = true }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
        {label}
      </dt>
      <dd className={`mt-1 text-sm text-slate-900 ${mono ? 'font-mono' : ''}`}>{value}</dd>
    </div>
  )
}

export function AdmNoticePanel({ adm, loading }: Props) {
  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center p-6 text-sm text-slate-400">
        <span className="animate-pulse-soft">Loading ADM…</span>
      </div>
    )
  }

  if (!adm) {
    return (
      <div className="flex flex-1 items-center justify-center p-6 text-sm text-slate-400">
        Select an ADM to view the notice.
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-7">
      {/* The memo, styled as the formal document it represents */}
      <div
        key={adm.adm_id}
        className="animate-fade-up overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
      >
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-950 px-6 py-4">
          <div className="flex items-center gap-3">
            <FileWarning className="h-4.5 w-4.5 text-amber-400" />
            <div>
              <h2 className="text-sm font-bold uppercase tracking-widest text-white">
                Agency Debit Memo
              </h2>
              <p className="font-mono text-[11px] text-slate-400">
                {adm.adm_id} · issued {adm.issue_date}
              </p>
            </div>
          </div>
          <span className="rounded bg-white/10 px-2.5 py-1 font-mono text-sm font-bold tracking-wide text-white ring-1 ring-inset ring-white/20">
            {adm.airline_code}
          </span>
        </div>

        <div className="px-6 py-5">
          <div className="flex items-end justify-between border-b border-dashed border-slate-200 pb-5">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
                Amount claimed
              </p>
              <p className="mt-1 font-mono text-3xl font-bold tracking-tight text-slate-900">
                ${adm.amount_claimed.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
                Dispute deadline
              </p>
              <p className="mt-1 font-mono text-lg font-semibold text-rose-600">
                {adm.dispute_deadline}
              </p>
            </div>
          </div>

          <dl className="mt-5 grid grid-cols-3 gap-x-4 gap-y-5">
            <Field label="Ticket Number" value={adm.ticket_number} />
            <Field label="Reason Code" value={adm.reason_code} />
            <Field label="Issue Date" value={adm.issue_date} />
          </dl>

          <div className="mt-5 rounded-lg border border-amber-200/70 bg-amber-50/50 px-4 py-3">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-amber-700">
              Stated reason
            </p>
            <p className="mt-1.5 text-sm leading-relaxed text-slate-800">{adm.reason_text}</p>
          </div>
        </div>
      </div>

      {adm.pnr && (
        <div
          key={adm.pnr.pnr_id}
          className="animate-fade-up mt-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          style={{ animationDelay: '90ms' }}
        >
          <div className="flex items-center gap-2.5 border-b border-slate-100 pb-4">
            <TicketsPlane className="h-4.5 w-4.5 text-indigo-500" />
            <h3 className="text-sm font-bold text-slate-900">Booking Record</h3>
            <span className="ml-auto font-mono text-xs text-slate-400">{adm.pnr.pnr_id}</span>
          </div>

          <div className="mt-4 flex items-center gap-3 rounded-lg bg-slate-50 px-4 py-3">
            <span className="font-mono text-lg font-bold tracking-tight text-slate-900">
              {adm.pnr.origin}
            </span>
            <span className="h-px flex-1 border-t border-dashed border-slate-300" />
            <span className="rounded-full bg-white px-2 py-0.5 font-mono text-[10px] font-semibold text-slate-500 ring-1 ring-slate-200">
              {adm.pnr.booking_class} · {adm.pnr.fare_basis_code}
            </span>
            <span className="h-px flex-1 border-t border-dashed border-slate-300" />
            <span className="font-mono text-lg font-bold tracking-tight text-slate-900">
              {adm.pnr.destination}
            </span>
          </div>

          <dl className="mt-5 grid grid-cols-4 gap-x-4 gap-y-5">
            <Field label="Passenger" value={adm.pnr.passenger_name} mono={false} />
            <Field label="Fare" value={`$${adm.pnr.fare_amount.toFixed(2)}`} />
            <Field label="Taxes" value={`$${adm.pnr.taxes.toFixed(2)}`} />
            <Field label="GDS" value={adm.pnr.gds} />
            <Field label="Booked" value={adm.pnr.booking_date} />
            <Field label="Departure" value={adm.pnr.departure_date} />
            <Field label="Agent" value={adm.pnr.agent_id} />
          </dl>
        </div>
      )}
    </div>
  )
}

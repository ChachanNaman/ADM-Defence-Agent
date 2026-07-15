import type { ADM } from '../lib/types'

interface Props {
  adm: ADM | null
  loading: boolean
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</dt>
      <dd className="mt-0.5 text-sm text-slate-900">{value}</dd>
    </div>
  )
}

export function AdmNoticePanel({ adm, loading }: Props) {
  if (loading) {
    return <div className="flex-1 p-6 text-sm text-slate-500">Loading ADM…</div>
  }

  if (!adm) {
    return (
      <div className="flex-1 p-6 text-sm text-slate-500">Select an ADM to view the notice.</div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Agency Debit Memo</h2>
          <span className="font-mono text-xs text-slate-500">{adm.adm_id}</span>
        </div>
        <dl className="mt-4 grid grid-cols-2 gap-4">
          <Field label="Ticket Number" value={adm.ticket_number} />
          <Field label="Airline" value={adm.airline_code} />
          <Field label="Reason Code" value={adm.reason_code} />
          <Field label="Amount Claimed" value={`$${adm.amount_claimed.toFixed(2)}`} />
          <Field label="Issue Date" value={adm.issue_date} />
          <Field label="Dispute Deadline" value={adm.dispute_deadline} />
        </dl>
        <div className="mt-4">
          <dt className="text-xs font-medium text-slate-500 uppercase tracking-wide">
            Reason
          </dt>
          <dd className="mt-0.5 text-sm text-slate-900">{adm.reason_text}</dd>
        </div>
      </div>

      {adm.pnr && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold text-slate-900">Booking Record — {adm.pnr.pnr_id}</h3>
          <dl className="mt-4 grid grid-cols-2 gap-4">
            <Field label="Passenger" value={adm.pnr.passenger_name} />
            <Field label="Route" value={`${adm.pnr.origin} → ${adm.pnr.destination}`} />
            <Field label="Fare Basis" value={adm.pnr.fare_basis_code} />
            <Field label="Booking Class" value={adm.pnr.booking_class} />
            <Field label="Fare Amount" value={`$${adm.pnr.fare_amount.toFixed(2)}`} />
            <Field label="Taxes" value={`$${adm.pnr.taxes.toFixed(2)}`} />
            <Field label="Booking Date" value={adm.pnr.booking_date} />
            <Field label="Departure Date" value={adm.pnr.departure_date} />
            <Field label="Agent" value={adm.pnr.agent_id} />
            <Field label="GDS" value={adm.pnr.gds} />
          </dl>
        </div>
      )}
    </div>
  )
}

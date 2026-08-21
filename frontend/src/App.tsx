import { useEffect, useState } from 'react'
import { Plane } from 'lucide-react'
import { AdmSidebar } from './components/AdmSidebar'
import { AdmNoticePanel } from './components/AdmNoticePanel'
import { AgentPanel } from './components/AgentPanel'
import { getAdm, listAdms } from './lib/api'
import type { ADM, ADMListItem } from './lib/types'
//
function App() {
  const [admList, setAdmList] = useState<ADMListItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedAdm, setSelectedAdm] = useState<ADM | null>(null)
  const [admLoading, setAdmLoading] = useState(false)

  useEffect(() => {
    listAdms().then((items) => {
      setAdmList(items)
      if (items.length > 0) setSelectedId(items[0].adm_id)
    })
  }, [])

  useEffect(() => {
    if (!selectedId) return
    setAdmLoading(true)
    getAdm(selectedId)
      .then(setSelectedAdm)
      .finally(() => setAdmLoading(false))
  }, [selectedId])

  return (
    <div className="flex h-screen flex-col bg-slate-100 font-sans antialiased">
      <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-7 py-4">
        <div className="flex items-center gap-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/15 ring-1 ring-inset ring-indigo-400/30">
            <Plane className="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white">
              ADM Defense Agent
            </h1>
            <p className="text-xs text-slate-400">
              Autonomous dispute · pay · escalate decisions on Agency Debit Memos
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden items-center gap-4 text-right sm:flex">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-widest text-slate-500">
                Queue
              </p>
              <p className="font-mono text-sm font-semibold text-slate-200">
                {admList.length} memos
              </p>
            </div>
            <div className="h-8 w-px bg-slate-800" />
            <div>
              <p className="font-mono text-[11px] uppercase tracking-widest text-slate-500">
                Exposure
              </p>
              <p className="font-mono text-sm font-semibold text-slate-200">
                ${admList.reduce((s, a) => s + a.amount_claimed, 0).toFixed(2)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            <span className="text-xs font-medium text-slate-300">Agent online</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <AdmSidebar items={admList} selectedId={selectedId} onSelect={setSelectedId} />
        <AdmNoticePanel adm={selectedAdm} loading={admLoading} />
        <AgentPanel adm={selectedAdm} />
      </div>
    </div>
  )
}

export default App

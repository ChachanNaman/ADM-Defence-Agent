import { useEffect, useState } from 'react'
import { AdmSidebar } from './components/AdmSidebar'
import { AdmNoticePanel } from './components/AdmNoticePanel'
import { AgentPanel } from './components/AgentPanel'
import { getAdm, listAdms } from './lib/api'
import type { ADM, ADMListItem } from './lib/types'

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
    <div className="flex h-screen flex-col bg-slate-100">
      <header className="border-b border-slate-200 bg-white px-7 py-5">
        <h1 className="text-xl font-bold tracking-tight text-slate-900">ADM Defense Agent</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Autonomous dispute / pay / escalate decisions on incoming Agency Debit Memos
        </p>
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

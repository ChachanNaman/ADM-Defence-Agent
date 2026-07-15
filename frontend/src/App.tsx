import { useEffect, useState } from 'react'
import { AdmSidebar } from './components/AdmSidebar'
import { AdmNoticePanel } from './components/AdmNoticePanel'
import { AgentPanel, type AgentStatus } from './components/AgentPanel'
import { ApiError, getAdm, listAdms, runAgent } from './lib/api'
import type { ADM, ADMListItem, DecisionRecord } from './lib/types'

function App() {
  const [admList, setAdmList] = useState<ADMListItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedAdm, setSelectedAdm] = useState<ADM | null>(null)
  const [admLoading, setAdmLoading] = useState(false)

  const [agentStatus, setAgentStatus] = useState<AgentStatus>('idle')
  const [decision, setDecision] = useState<DecisionRecord | null>(null)
  const [agentError, setAgentError] = useState<string | null>(null)

  useEffect(() => {
    listAdms().then((items) => {
      setAdmList(items)
      if (items.length > 0) setSelectedId(items[0].adm_id)
    })
  }, [])

  useEffect(() => {
    if (!selectedId) return
    setAdmLoading(true)
    setAgentStatus('idle')
    setDecision(null)
    setAgentError(null)
    getAdm(selectedId)
      .then(setSelectedAdm)
      .finally(() => setAdmLoading(false))
  }, [selectedId])

  const handleRun = async () => {
    if (!selectedId) return
    setAgentStatus('running')
    setAgentError(null)
    try {
      const result = await runAgent(selectedId)
      setDecision(result)
      setAgentStatus('done')
    } catch (err) {
      if (err instanceof ApiError && err.status === 501) {
        setAgentStatus('not_implemented')
      } else {
        setAgentError(err instanceof Error ? err.message : 'Unknown error')
        setAgentStatus('error')
      }
    }
  }

  return (
    <div className="flex h-screen flex-col bg-slate-100">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-lg font-semibold text-slate-900">ADM Defense Agent</h1>
        <p className="text-sm text-slate-500">
          Autonomous dispute / pay / escalate decisions on incoming Agency Debit Memos
        </p>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <AdmSidebar items={admList} selectedId={selectedId} onSelect={setSelectedId} />
        <AdmNoticePanel adm={selectedAdm} loading={admLoading} />
        <AgentPanel
          adm={selectedAdm}
          status={agentStatus}
          decision={decision}
          errorMessage={agentError}
          onRun={handleRun}
        />
      </div>
    </div>
  )
}

export default App

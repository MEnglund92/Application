import { useState } from 'react'
import { create } from 'zustand'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Terminal, Upload, Play, FileText } from 'lucide-react'

const useStore = create((set) => ({
  xp: 0,
  level: 1,
  addXp: (amount) => set((state) => ({ xp: state.xp + amount, level: Math.floor((state.xp + amount) / 100) + 1 }))
}))

export default function App() {
  const { xp, level, addXp } = useStore()
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setStatus('UPLOADING...')
    const formData = new FormData()
    formData.append('file', file)
    try {
        setLoading(true)
        const res = await axios.post('/api/upload', formData)
        addXp(res.data.xp_gained)
        setStatus('UPLOAD COMPLETE')
        alert('File Processed Successfully')
    } catch (err) { 
        setStatus('ERROR')
        alert('Upload Failed') 
    } finally { setLoading(false) }
  }

  const handleChat = async () => {
    if (!query) return
    const newHist = [...history, { role: 'user', content: query }]
    setHistory(newHist)
    setQuery('')
    try {
        setLoading(true)
        const res = await axios.post('/api/chat', { question: query })
        setHistory([...newHist, { role: 'bot', content: res.data.response }])
        addXp(res.data.xp_gained)
    } catch (err) { 
        setHistory([...newHist, { role: 'err', content: "Connection Error" }]) 
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 p-6 font-mono">
      <div className="border-b border-green-800 pb-4 mb-6 flex justify-between">
        <h1 className="text-xl font-bold flex gap-2"><Terminal/> GEMINI_RAG</h1>
        <div>LVL {level} | {xp} XP</div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-4 border border-green-800 rounded bg-green-900/10">
            <h2 className="mb-4 font-bold flex gap-2"><Upload size={16}/> INGEST</h2>
            <div className="border-2 border-dashed border-green-800 p-4 text-center cursor-pointer relative">
                <input type="file" onChange={handleUpload} className="absolute inset-0 opacity-0 cursor-pointer"/>
                <FileText className="mx-auto mb-2"/>
                <div className="text-xs">DROP PDF HERE</div>
            </div>
            <div className="mt-2 text-xs text-center">{status}</div>
        </div>

        <div className="md:col-span-3 border border-green-800 rounded h-[600px] flex flex-col">
            <div className="flex-1 overflow-auto p-4 space-y-4">
                {history.map((m, i) => (
                    <div key={i} className={`p-3 text-sm ${m.role === 'user' ? 'text-right text-white' : 'text-green-400'}`}>
                        <div className="text-[10px] opacity-50">{m.role}</div>
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                ))}
            </div>
            <div className="p-4 border-t border-green-800 flex gap-2">
                <input value={query} onChange={e => setQuery(e.target.value)} 
                       onKeyDown={e => e.key === 'Enter' && handleChat()}
                       className="flex-1 bg-green-900/20 border border-green-800 p-2 outline-none" placeholder="Ask query..."/>
                <button onClick={handleChat} className="bg-green-700 text-black font-bold px-4">SEND</button>
            </div>
        </div>
      </div>
    </div>
  )
}
import React, { useState, useEffect } from 'react'
import { Upload, MessageCircle, Trophy, FileText, Zap } from 'lucide-react'
import { useStore } from './store'
import { uploadFile, chat, generateQuiz, getStats } from './api'
import ChatInterface from './components/ChatInterface'
import QuizInterface from './components/QuizInterface'
import toast from 'react-hot-toast'

function App() {
  const { xp, level, addXP } = useStore()
  const [activeTab, setActiveTab] = useState('upload')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  useEffect(() => {
    // Fetch initial stats
    getStats().catch(err => {
      if (err.response?.status === 500) {
        toast.error('Please set GEMINI_API_KEY in .env file')
      }
    })
  }, [])

  const handleFileUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await uploadFile(formData)
      addXP(response.xp_gained)
      toast.success(`✨ +${response.xp_gained} XP gained!`)
      setFile(null)
      setUploadProgress(100)
      setTimeout(() => setUploadProgress(0), 1000)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const xpPercentage = (xp / 100) * 100

  return (
    <div className="min-h-screen p-8">
      {/* Header with XP Bar */}
      <header className="mb-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyber-blue to-cyber-pink bg-clip-text text-transparent">
            RAG Gamified Platform
          </h1>
          
          {/* XP System */}
          <div className="cyber-border rounded-lg p-4 bg-black/50 backdrop-blur">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyber-green" />
                <span className="font-bold">Level {level}</span>
              </div>
              <span className="text-cyber-green">{xp}/100 XP</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
              <div 
                className="xp-bar h-full rounded-full"
                style={{ width: `${xpPercentage}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-6xl mx-auto mb-6">
        <div className="flex gap-4 border-b border-cyber-blue/30">
          {[
            { id: 'upload', label: 'Upload', icon: Upload },
            { id: 'chat', label: 'Chat', icon: MessageCircle },
            { id: 'quiz', label: 'Quiz', icon: Trophy },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-4 py-2 font-semibold transition-all ${
                activeTab === id
                  ? 'text-cyber-blue border-b-2 border-cyber-blue'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-6xl mx-auto">
        {activeTab === 'upload' && (
          <div className="cyber-border rounded-lg p-8 bg-black/50 backdrop-blur">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <FileText className="w-6 h-6 text-cyber-blue" />
              Upload Documents
            </h2>
            
            <form onSubmit={handleFileUpload} className="space-y-6">
              <div className="border-2 border-dashed border-cyber-pink/50 rounded-lg p-8 text-center hover:border-cyber-pink transition-colors">
                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files[0])}
                  accept=".pdf,.txt"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer block"
                >
                  <Upload className="w-12 h-12 mx-auto mb-4 text-cyber-pink" />
                  <p className="text-lg mb-2">Click to upload or drag and drop</p>
                  <p className="text-gray-400">PDF or TXT files only</p>
                  {file && (
                    <p className="mt-4 text-cyber-green">
                      Selected: {file.name}
                    </p>
                  )}
                </label>
              </div>

              {uploadProgress > 0 && (
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-cyber-blue h-full rounded-full transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={!file || loading}
                className="w-full py-3 bg-gradient-to-r from-cyber-blue to-cyber-pink font-bold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-80 transition-opacity"
              >
                {loading ? 'Uploading...' : 'Upload & Gain 10 XP'}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'quiz' && <QuizInterface />}
      </div>
    </div>
  )
}

export default App

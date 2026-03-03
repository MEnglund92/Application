import React, { useState } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { chat } from '../api'
import { useStore } from '../store'
import toast from 'react-hot-toast'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const { addXP } = useStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await chat(input)
      const botMessage = { role: 'bot', content: response.response }
      setMessages(prev => [...prev, botMessage])
      addXP(response.xp_gained)
      toast.success(`✨ +${response.xp_gained} XP gained!`)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Chat failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cyber-border rounded-lg p-6 bg-black/50 backdrop-blur">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
        <Bot className="w-6 h-6 text-cyber-blue" />
        AI Chat Assistant
      </h2>

      <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-900/50 rounded-lg">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            Start a conversation with your documents!
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'bot' && <Bot className="w-8 h-8 text-cyber-blue flex-shrink-0" />}
              <div
                className={`max-w-xs p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-cyber-blue to-cyber-pink'
                    : 'bg-gray-800'
                }`}
              >
                {msg.content}
              </div>
              {msg.role === 'user' && <User className="w-8 h-8 text-cyber-green flex-shrink-0" />}
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-center gap-2 text-gray-400">
            <Bot className="w-8 h-8" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your documents..."
          className="flex-1 px-4 py-3 bg-gray-900 border border-cyber-blue/50 rounded-lg focus:outline-none focus:border-cyber-blue"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-cyber-blue to-cyber-pink rounded-lg disabled:opacity-50 hover:opacity-80 transition-opacity"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  )
}

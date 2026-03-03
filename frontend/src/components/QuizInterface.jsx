import React, { useState, useEffect } from 'react'
import { Trophy, RotateCcw } from 'lucide-react'
import { generateQuiz } from '../api'
import { useStore } from '../store'
import toast from 'react-hot-toast'

export default function QuizInterface() {
  const [quiz, setQuiz] = useState(null)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showResult, setShowResult] = useState(false)
  const [loading, setLoading] = useState(false)
  const { addXP } = useStore()

  const loadQuiz = async () => {
    setLoading(true)
    try {
      const newQuiz = await generateQuiz()
      setQuiz(newQuiz)
      setSelectedAnswer(null)
      setShowResult(false)
      addXP(newQuiz.xp_gained)
      toast.success(`✨ +${newQuiz.xp_gained} XP for generating quiz!`)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQuiz()
  }, [])

  const handleSubmit = () => {
    if (selectedAnswer === null) return
    setShowResult(true)
    if (selectedAnswer === quiz.correct_answer) {
      toast.success('🎉 Correct Answer! +20 XP')
      addXP(20)
    } else {
      toast.error('❌ Incorrect. Try again!')
    }
  }

  return (
    <div className="cyber-border rounded-lg p-6 bg-black/50 backdrop-blur">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-3">
          <Trophy className="w-6 h-6 text-cyber-pink" />
          Knowledge Quiz
        </h2>
        <button
          onClick={loadQuiz}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyber-blue to-cyber-pink rounded-lg disabled:opacity-50 hover:opacity-80 transition-opacity"
        >
          <RotateCcw className="w-4 h-4" />
          {loading ? 'Loading...' : 'New Quiz'}
        </button>
      </div>

      {quiz ? (
        <div className="space-y-6">
          <div className="p-6 bg-gray-900/50 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">{quiz.question}</h3>
            
            <div className="space-y-3">
              {quiz.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => !showResult && setSelectedAnswer(idx)}
                  disabled={showResult}
                  className={`w-full text-left p-4 rounded-lg border transition-all ${
                    showResult
                      ? idx === quiz.correct_answer
                        ? 'bg-green-900/50 border-green-500'
                        : selectedAnswer === idx
                        ? 'bg-red-900/50 border-red-500'
                        : 'bg-gray-800/50 border-gray-700'
                      : selectedAnswer === idx
                      ? 'bg-cyber-blue/20 border-cyber-blue'
                      : 'bg-gray-900/30 border-gray-700 hover:border-cyber-blue/50'
                  }`}
                >
                  <span className="font-semibold mr-3">{String.fromCharCode(65 + idx)}.</span>
                  {option}
                </button>
              ))}
            </div>
          </div>

          {!showResult && selectedAnswer !== null && (
            <button
              onClick={handleSubmit}
              className="w-full py-3 bg-gradient-to-r from-cyber-green to-cyber-blue font-bold rounded-lg hover:opacity-80 transition-opacity"
            >
              Submit Answer
            </button>
          )}

          {showResult && (
            <div className="p-4 bg-gray-900/50 rounded-lg text-center">
              <p className="text-lg">
                {selectedAnswer === quiz.correct_answer ? (
                  <span className="text-green-400">🎉 Correct! Well done!</span>
                ) : (
                  <span className="text-red-400">
                    ❌ Incorrect. The correct answer was {String.fromCharCode(65 + quiz.correct_answer)}
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          Loading quiz...
        </div>
      )}
    </div>
  )
}

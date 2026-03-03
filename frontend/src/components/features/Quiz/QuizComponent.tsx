import React, { useState, useEffect } from 'react'
import { useUser } from '../../../hooks/useUser'
import { useApi } from '../../../hooks/useApi'
import { apiService } from '../../../services/api'
import { QuizResponse } from '../../../types'  // Removed unused QuizQuestion import
import Card from '../../../components/ui/Card'
import Button from '../../../components/ui/Button'
import Badge from '../../../components/ui/Badge'
import { Brain, CheckCircle, Trophy, Clock, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'

const QuizComponent: React.FC = () => {
    const { addXp } = useUser()
    const { loading, execute } = useApi()
    const [quiz, setQuiz] = useState<QuizResponse | null>(null)
    const [currentQuestion, setCurrentQuestion] = useState(0)
    const [answers, setAnswers] = useState<number[]>([])
    const [showResults, setShowResults] = useState(false)
    const [score, setScore] = useState(0)

    useEffect(() => {
        generateNewQuiz()
    }, [])

    const generateNewQuiz = () => {
        execute(
            () => apiService.generateQuiz(),
            (response) => {
                setQuiz(response)
                setCurrentQuestion(0)
                setAnswers([])
                setShowResults(false)
                setScore(0)
            }
        )
    }

    const handleAnswer = (selectedAnswer: number) => {
        const newAnswers = [...answers]
        newAnswers[currentQuestion] = selectedAnswer
        setAnswers(newAnswers)
    }

    const nextQuestion = () => {
        if (currentQuestion < quiz!.questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1)
        } else {
            submitQuiz()
        }
    }

    const previousQuestion = () => {
        if (currentQuestion > 0) {
            setCurrentQuestion(currentQuestion - 1)
        }
    }

    const submitQuiz = () => {
        if (!quiz) return

        const submissions = answers.map((answer, index) => ({
            questionId: index,
            selectedAnswer: answer,
        }))

        execute(
            () => apiService.submitQuiz(submissions),
            (result: any) => {  // Added type annotation for result
                const correctCount = answers.filter((answer, index) =>
                    answer === quiz.questions[index].correctAnswer
                ).length
                setScore(correctCount)
                setShowResults(true)
                addXp(result.xpGained || 25)  // Added fallback value
                toast.success(`Quiz completed! Score: ${correctCount}/${quiz.questions.length} | +${result.xpGained || 25} XP`)
            }
        )
    }

    if (!quiz) {
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Mode</h2>
                    <p className="text-primary-600">
                        Test your knowledge with AI-generated questions from your documents
                    </p>
                </div>

                <Card variant="glass" className="p-8">
                    <div className="flex items-center justify-center min-h-[300px]">
                        {loading ? (
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-500"></div>
                        ) : (
                            <div className="text-center">
                                <Brain className="h-16 w-16 text-primary-400 mx-auto mb-4" />
                                <p className="text-primary-600 mb-4">Loading quiz questions...</p>
                                <Button onClick={generateNewQuiz} loading={loading}>
                                    Generate Quiz
                                </Button>
                            </div>
                        )}
                    </div>
                </Card>
            </div>
        )
    }

    if (showResults) {
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Results</h2>
                    <p className="text-primary-600">
                        Here's how you performed on the quiz
                    </p>
                </div>

                <Card variant="glass" className="p-8">
                    <div className="text-center mb-6">
                        <div className="w-24 h-24 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Trophy className="h-12 w-12 text-white" />
                        </div>

                        <h3 className="text-2xl font-bold text-primary-900 mb-2">
                            Score: {score}/{quiz.questions.length}
                        </h3>

                        <Badge variant="success" className="mb-4">
                            {((score / quiz.questions.length) * 100).toFixed(0)}% Correct
                        </Badge>

                        <p className="text-primary-600">
                            {score === quiz.questions.length
                                ? "Perfect score! You're a master!"
                                : score >= quiz.questions.length / 2
                                    ? "Good job! Keep learning!"
                                    : "Keep practicing! You'll get better!"}
                        </p>
                    </div>

                    <div className="space-y-3 mb-6">
                        {quiz.questions.map((question, index) => (
                            <div
                                key={index}
                                className={`
                  p-4 rounded-lg border-2
                  ${answers[index] === question.correctAnswer
                                        ? 'border-success bg-success/10'
                                        : 'border-danger bg-danger/10'}
                `}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <p className="font-medium text-primary-900">
                                        Question {index + 1}
                                    </p>
                                    {answers[index] === question.correctAnswer ? (
                                        <CheckCircle className="h-5 w-5 text-success" />
                                    ) : (
                                        <span className="text-danger text-sm font-medium">
                                            Correct: {question.options[question.correctAnswer]}
                                        </span>
                                    )}
                                </div>

                                <p className="text-primary-600 text-sm mb-2">{question.question}</p>

                                <p className="text-primary-700 text-sm">
                                    Your answer: {answers[index] !== undefined ? question.options[answers[index]] : 'Not answered'}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-center space-x-4">
                        <Button onClick={generateNewQuiz} variant="accent">
                            <RotateCcw className="h-4 w-4 mr-2" />
                            New Quiz
                        </Button>
                    </div>
                </Card>
            </div>
        )
    }

    const currentQ = quiz.questions[currentQuestion]
    const progress = ((currentQuestion + 1) / quiz.questions.length) * 100

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Mode</h2>
                <p className="text-primary-600">
                    Test your knowledge with questions from your documents
                </p>
            </div>

            {/* Progress Bar */}
            <Card variant="glass" className="p-4">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                        <Brain className="h-5 w-5 text-accent-500" />
                        <span className="text-primary-900 font-medium">
                            Question {currentQuestion + 1} of {quiz.questions.length}
                        </span>
                    </div>

                    <Badge variant="accent">
                        {Math.round(progress)}% Complete
                    </Badge>
                </div>

                <div className="w-full h-3 bg-primary-200 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            </Card>

            {/* Current Question */}
            <Card variant="glass" className="p-6">
                <div className="mb-6">
                    <div className="flex items-center space-x-2 mb-4">
                        <Clock className="h-5 w-5 text-primary-600" />
                        <span className="text-primary-600 font-medium">
                            Context from your documents
                        </span>
                    </div>

                    <div className="p-4 rounded-lg bg-primary-100/30 mb-6">
                        <p className="text-primary-700 italic">
                            "{quiz.contextUsed}"
                        </p>
                    </div>
                </div>

                <h3 className="text-xl font-semibold text-primary-900 mb-6">
                    {currentQ.question}
                </h3>

                <div className="space-y-3 mb-8">
                    {currentQ.options.map((option, index) => (
                        <button
                            key={index}
                            onClick={() => handleAnswer(index)}
                            className={`
                w-full text-left p-4 rounded-lg border-2 transition-all duration-200
                ${answers[currentQuestion] === index
                                    ? 'border-accent-500 bg-accent-500/10'
                                    : 'border-primary-300 hover:border-primary-400 hover:bg-primary-100/30'}
              `}
                        >
                            <div className="flex items-center space-x-3">
                                <div className={`
                  w-6 h-6 rounded-full border-2 flex items-center justify-center
                  ${answers[currentQuestion] === index
                                        ? 'border-accent-500 bg-accent-500'
                                        : 'border-primary-400'}
                `}>
                                    {answers[currentQuestion] === index && (
                                        <div className="w-2 h-2 bg-white rounded-full" />
                                    )}
                                </div>
                                <span className="text-primary-900">{option}</span>
                            </div>
                        </button>
                    ))}
                </div>

                <div className="flex justify-between">
                    <Button
                        variant="secondary"
                        onClick={previousQuestion}
                        disabled={currentQuestion === 0}
                    >
                        Previous
                    </Button>

                    <Button
                        variant="accent"
                        onClick={nextQuestion}
                        disabled={answers[currentQuestion] === undefined}
                    >
                        {currentQuestion === quiz.questions.length - 1 ? 'Submit Quiz' : 'Next'}
                    </Button>
                </div>
            </Card>

            <Card variant="glass" className="p-4">
                <div className="flex items-center justify-between">
                    <p className="text-primary-600">
                        Complete the quiz to earn up to 50 XP
                    </p>
                    <Badge variant="accent">+50 XP</Badge>
                </div>
            </Card>
        </div>
    )
}

export default QuizComponent

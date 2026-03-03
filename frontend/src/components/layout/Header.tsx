import React from 'react'
import { useUser } from '../../hooks/useUser'
import { Trophy, Zap, Brain, BookOpen } from 'lucide-react'
import Card from '../ui/Card'

const Header: React.FC = () => {
    const { user } = useUser()

    return (
        <Card variant="glass" className="mb-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <Brain className="h-8 w-8 text-accent-500" />
                        <div>
                            <h1 className="text-2xl font-bold text-primary-900">
                                RAG Learning Platform
                            </h1>
                            <p className="text-sm text-primary-600">
                                Master knowledge through AI-powered learning
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    {/* XP Progress */}
                    <div className="flex items-center space-x-3">
                        <Zap className="h-5 w-5 text-accent-500" />
                        <div>
                            <p className="text-sm font-semibold text-primary-900">
                                Level {user.level}
                            </p>
                            <div className="flex items-center space-x-2">
                                <div className="w-24 h-2 bg-primary-200 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500"
                                        style={{
                                            width: `${((100 - user.xpToNextLevel) / 100) * 100}%`,
                                        }}
                                    />
                                </div>
                                <span className="text-xs text-primary-600">
                                    {100 - user.xpToNextLevel} XP
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Total XP */}
                    <div className="flex items-center space-x-2">
                        <Trophy className="h-5 w-5 text-warning" />
                        <span className="font-semibold text-primary-900">
                            {user.totalXp} Total XP
                        </span>
                    </div>
                </div>
            </div>
        </Card>
    )
}

export default Header

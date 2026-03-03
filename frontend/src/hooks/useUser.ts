import { useState, useEffect } from 'react'
import { User } from '../types'

const STORAGE_KEY = 'rag-learning-user'

export const useUser = () => {
    const [user, setUser] = useState<User>(() => {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
            return JSON.parse(stored)
        }

        return {
            level: 1,
            totalXp: 0,
            xpToNextLevel: 100,
            achievements: [],
        }
    })

    const addXp = (amount: number) => {
        setUser(prev => {
            const newTotalXp = prev.totalXp + amount
            const newLevel = Math.floor(newTotalXp / 100) + 1
            const newXpToNextLevel = (newLevel * 100) - newTotalXp

            const updatedUser = {
                ...prev,
                totalXp: newTotalXp,
                level: newLevel,
                xpToNextLevel: newXpToNextLevel,
            }

            localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedUser))
            return updatedUser
        })
    }

    const resetUser = () => {
        const defaultUser: User = {
            level: 1,
            totalXp: 0,
            xpToNextLevel: 100,
            achievements: [],
        }
        setUser(defaultUser)
        localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUser))
    }

    return {
        user,
        addXp,
        resetUser,
    }
}

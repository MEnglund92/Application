import { create } from 'zustand'

export const useStore = create((set) => ({
  xp: 0,
  level: 1,
  addXP: (amount) => set((state) => {
    const newXp = state.xp + amount
    const newLevel = state.level + Math.floor(newXp / 100)
    return {
      xp: newXp % 100,
      level: newLevel,
    }
  }),
}))

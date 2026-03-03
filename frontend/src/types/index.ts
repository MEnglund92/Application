export interface User {
    level: number
    totalXp: number
    xpToNextLevel: number
    achievements: string[]
}

export interface SearchResult {
    content: string
    source: string
    page?: number
    score: number
}

export interface SearchResponse {
    query: string
    results: SearchResult[]
    xpGained: number
}

export interface QuizQuestion {
    question: string
    options: string[]
    correctAnswer: number
}

export interface QuizResponse {
    questions: QuizQuestion[]
    contextUsed: string
}

export interface SystemStats {
    documentsCount: number
    vectorDbSizeMb: number
    lastQueries: Array<{
        query: string
        timestamp: string
    }>
    systemHealth: {
        cpuPercent: number
        memoryPercent: number
        diskPercent: number
    }
}

export interface UploadResponse {
    message: string
    filename: string
    chunksProcessed: number
    xpGained: number
}

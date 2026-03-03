import axios from 'axios'
import { SearchResponse, QuizResponse, SystemStats, UploadResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error.response?.data || error)
    }
)

export const apiService = {
    // Upload
    uploadDocument: async (file: File): Promise<UploadResponse> => {
        const formData = new FormData()
        formData.append('file', file)

        return api.post('/api/v1/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },

    // Search
    searchDocuments: async (query: string, maxResults: number = 5): Promise<SearchResponse> => {
        return api.post('/api/v1/search', {
            query,
            maxResults,
        })
    },

    // Quiz
    generateQuiz: async (): Promise<QuizResponse> => {
        return api.get('/api/v1/quiz')
    },

    submitQuiz: async (answers: Array<{ questionId: number; selectedAnswer: number }>) => {
        return api.post('/api/v1/quiz/submit', answers)
    },

    // Stats
    getSystemStats: async (): Promise<SystemStats> => {
        return api.get('/api/v1/stats')
    },

    // Health
    healthCheck: async () => {
        return api.get('/health')
    },
}

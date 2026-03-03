import { useState, useCallback } from 'react'
import { apiService } from '../services/api'
import toast from 'react-hot-toast'

export const useApi = () => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const execute = useCallback(async <T,>(
        apiCall: () => Promise<T>,
        onSuccess?: (data: T) => void,
        onError?: (error: any) => void
    ) => {
        setLoading(true)
        setError(null)

        try {
            const result = await apiCall()
            onSuccess?.(result)
            return result
        } catch (err: any) {
            const errorMessage = err.detail || err.message || 'An error occurred'
            setError(errorMessage)
            onError?.(err)

            if (!onError) {
                toast.error(errorMessage)
            }

            throw err
        } finally {
            setLoading(false)
        }
    }, [])

    return {
        loading,
        error,
        execute,
        clearError: () => setError(null),
    }
}

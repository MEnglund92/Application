import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: '/api',
})

export const uploadFile = async (formData) => {
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const chat = async (question) => {
  const response = await api.post('/chat', { question })
  return response.data
}

export const generateQuiz = async () => {
  const response = await api.get('/quiz')
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}

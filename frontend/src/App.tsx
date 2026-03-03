import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import DashboardView from './components/features/Dashboard/DashboardView'
import UploadZone from './components/features/Upload/UploadZone'
import SearchBar from './components/features/Search/SearchBar'
import QuizComponent from './components/features/Quiz/QuizComponent'

function App() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-primary-100 to-primary-50">
            <Layout>
                <Routes>
                    <Route path="/" element={<DashboardView />} />
                    <Route path="/upload" element={<UploadZone />} />
                    <Route path="/search" element={<SearchBar />} />
                    <Route path="/quiz" element={<QuizComponent />} />
                </Routes>
            </Layout>
        </div>
    )
}

export default App

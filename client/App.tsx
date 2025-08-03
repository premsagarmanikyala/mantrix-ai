import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useAuth } from '@/hooks/useAuth'
import Layout from '@/components/Layout'
import LoginForm from '@/components/Auth/LoginForm'
import Dashboard from '@/pages/Dashboard'
import RoadmapView from '@/pages/RoadmapView'
import RoadmapCreate from '@/pages/RoadmapCreate'
import RoadmapMerge from '@/pages/RoadmapMerge'
import ProgressTracker from '@/pages/ProgressTracker'
import ResumeBuilder from '@/pages/ResumeBuilder'
import RecommendationCenter from '@/pages/RecommendationCenter'
import { Toaster } from 'react-hot-toast'
import { queryClient } from '@/lib/queryClient'

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Mantrix Learning Platform...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm />
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route path="/roadmap/view" element={<RoadmapView />} />
        <Route path="/roadmap/create" element={<RoadmapCreate />} />
        <Route path="/roadmap/merge" element={<RoadmapMerge />} />
        <Route path="/progress" element={<ProgressTracker />} />
        <Route path="/resume" element={<ResumeBuilder />} />
        <Route path="/recommendations" element={<RecommendationCenter />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Checking...')
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const backendUrl = import.meta.env.VITE_API_URL || 'http://192.168.10.101:3547'

  useEffect(() => {
    // Check backend API health
    fetch(`${backendUrl}/health`)
      .then(res => res.json())
      .then(data => {
        setApiStatus(`✅ ${data.app || 'Backend'} v${data.version} (${data.environment})`)
      })
      .catch(() => {
        setApiStatus('❌ Backend API is not running')
      })
  }, [backendUrl])

  const handleLogin = (newToken: string) => {
    setToken(newToken)
    localStorage.setItem('token', newToken)
  }

  const handleLogout = () => {
    setToken(null)
    localStorage.removeItem('token')
  }

  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12">
            <div className="text-center">
              <h1 className="text-5xl font-bold text-gray-900 mb-4">
                🎯 ATS Platform
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Applicant Tracking System
              </p>

              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-8">
                <p className="text-lg font-semibold text-blue-900 mb-2">
                  Backend Status:
                </p>
                <p className="text-blue-700">{apiStatus}</p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg">
                  <h3 className="text-2xl font-bold mb-2">Frontend</h3>
                  <p className="text-blue-100">React + TypeScript + Vite</p>
                  <p className="text-sm text-blue-200 mt-4">Running on port 5173</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-xl shadow-lg">
                  <h3 className="text-2xl font-bold mb-2">Backend</h3>
                  <p className="text-green-100">Python + FastAPI</p>
                  <p className="text-sm text-green-200 mt-4">Running on port 8000</p>
                </div>
              </div>

              <div className="text-center">
                <button
                  onClick={() => window.location.href = '/login'}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-lg text-lg font-medium shadow-lg"
                >
                  Get Started - Sign In
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/login"
          element={
            token ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
          }
        />
        <Route
          path="/dashboard"
          element={
            token ? <Dashboard token={token} onLogout={handleLogout} /> : <Navigate to="/login" />
          }
        />
      </Routes>
    </Router>
  )
}

export default App

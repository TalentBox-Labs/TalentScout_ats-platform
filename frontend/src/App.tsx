import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Checking...')
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

  return (
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

              <div className="text-left bg-gray-50 rounded-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">🚀 Next Steps:</h3>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">1.</span>
                    <span>Install dependencies: <code className="bg-gray-200 px-2 py-1 rounded text-sm">cd frontend && npm install</code></span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">2.</span>
                    <span>Install backend dependencies: <code className="bg-gray-200 px-2 py-1 rounded text-sm">cd backend && npm install</code></span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">3.</span>
                    <span>Configure environment variables (see <code className="bg-gray-200 px-2 py-1 rounded text-sm">.env.example</code>)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">4.</span>
                    <span>Set up PostgreSQL database</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">5.</span>
                    <span>Start building your ATS features!</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

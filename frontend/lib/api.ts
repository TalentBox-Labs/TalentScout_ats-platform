import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  private setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token)
    }
  }

  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token')
    }
    return null
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Auth methods
  async login(email: string, password: string) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    const response = await this.client.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    this.setToken(response.data.access_token)
    if (response.data.refresh_token) {
      this.setRefreshToken(response.data.refresh_token)
    }
    return response.data
  }

  async register(data: {
    email: string
    password: string
    fullName: string
    organizationName: string
  }) {
    const response = await this.client.post('/api/v1/auth/register', {
      email: data.email,
      password: data.password,
      full_name: data.fullName,
      organization_name: data.organizationName,
    })
    this.setToken(response.data.access_token)
    if (response.data.refresh_token) {
      this.setRefreshToken(response.data.refresh_token)
    }
    return response.data
  }

  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await this.client.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    this.setToken(response.data.access_token)
    return response.data
  }

  async forgotPassword(email: string) {
    const response = await this.client.post('/api/v1/auth/forgot-password', {
      email,
    })
    return response.data
  }

  async resetPassword(token: string, newPassword: string) {
    const response = await this.client.post('/api/v1/auth/reset-password', {
      token,
      new_password: newPassword,
    })
    return response.data
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/v1/auth/me')
    return response.data
  }

  async logout() {
    this.clearToken()
  }

  // Jobs
  async getJobs(params?: any) {
    const response = await this.client.get('/api/v1/jobs', { params })
    return response.data
  }

  async getJob(id: string) {
    const response = await this.client.get(`/api/v1/jobs/${id}`)
    return response.data
  }

  async createJob(data: any) {
    const response = await this.client.post('/api/v1/jobs', data)
    return response.data
  }

  async updateJob(id: string, data: any) {
    const response = await this.client.patch(`/api/v1/jobs/${id}`, data)
    return response.data
  }

  async deleteJob(id: string) {
    await this.client.delete(`/api/v1/jobs/${id}`)
  }

  // Candidates
  async getCandidates(params?: any) {
    const response = await this.client.get('/api/v1/candidates', { params })
    return response.data
  }

  async getCandidate(id: string) {
    const response = await this.client.get(`/api/v1/candidates/${id}`)
    return response.data
  }

  async createCandidate(data: any) {
    const response = await this.client.post('/api/v1/candidates', data)
    return response.data
  }

  async updateCandidate(id: string, data: any) {
    const response = await this.client.patch(`/api/v1/candidates/${id}`, data)
    return response.data
  }

  async uploadResume(candidateId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.client.post(
      `/api/v1/candidates/${candidateId}/resume`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  // Applications
  async getApplications(params?: any) {
    const response = await this.client.get('/api/v1/applications', { params })
    return response.data
  }

  async getApplication(id: string) {
    const response = await this.client.get(`/api/v1/applications/${id}`)
    return response.data
  }

  async createApplication(data: any) {
    const response = await this.client.post('/api/v1/applications', data)
    return response.data
  }

  async updateApplicationStage(id: string, stageId: string) {
    const response = await this.client.patch(`/api/v1/applications/${id}/stage`, {
      current_stage: stageId,
    })
    return response.data
  }

  // Analytics
  async getAnalytics() {
    const response = await this.client.get('/api/v1/analytics')
    return response.data
  }

  // Interviews
  async getInterviews() {
    const response = await this.client.get('/api/v1/interviews')
    return response.data
  }

  // Integrations
  async getIntegrations() {
    const response = await this.client.get('/api/v1/integrations')
    return response.data
  }

  async connectIntegration(integrationId: string) {
    const response = await this.client.post(`/api/v1/integrations/${integrationId}/connect`)
    return response.data
  }

  async disconnectIntegration(integrationId: string) {
    const response = await this.client.post(`/api/v1/integrations/${integrationId}/disconnect`)
    return response.data
  }

  async updateIntegrationConfig(integrationId: string, config: any) {
    const response = await this.client.put(`/api/v1/integrations/${integrationId}/config`, config)
    return response.data
  }

  // Onboarding
  async getOnboardingStatus() {
    const response = await this.client.get('/api/v1/onboarding/status')
    return response.data
  }

  async completeOnboardingStep(stepId: string) {
    const response = await this.client.post(`/api/v1/onboarding/complete/${stepId}`)
    return response.data
  }

  async updateCompany(companyInfo: any) {
    const response = await this.client.put('/api/v1/company', companyInfo)
    return response.data
  }

  // AI Services
  async parseResume(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.client.post('/api/v1/ai/parse-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async screenCandidate(applicationId: string) {
    const response = await this.client.post(
      `/api/v1/ai/screen/${applicationId}`
    )
    return response.data
  }

  async generateEmail(data: {
    candidate_name: string
    job_title: string
    company_name: string
    email_type: string
    tone?: string
  }) {
    const response = await this.client.post('/api/v1/ai/generate-email', {
      template_type: data.email_type,
      context: {
        candidate_name: data.candidate_name,
        job_title: data.job_title,
        company_name: data.company_name,
      },
      tone: data.tone,
    })
    return response.data
  }
}

export const apiClient = new APIClient()

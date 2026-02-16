// Core types for the ATS Platform

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name?: string
  phone?: string
  avatar_url?: string
  title?: string
  bio?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Organization {
  id: string
  name: string
  domain?: string
  logo_url?: string
  website?: string
  industry?: string
  size?: string
  is_active: boolean
  created_at: string
}

export interface Job {
  id: string
  organization_id: string
  title: string
  description: string
  requirements?: string
  responsibilities?: string
  benefits?: string
  department?: string
  location?: string
  is_remote: boolean
  job_type: 'full_time' | 'part_time' | 'contract' | 'internship' | 'temporary'
  experience_level: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'principal'
  salary_min?: number
  salary_max?: number
  salary_currency: string
  status: 'draft' | 'open' | 'closed' | 'on_hold' | 'cancelled'
  openings: number
  skills_required?: string[]
  skills_preferred?: string[]
  created_at: string
  updated_at: string
  // Public job features
  is_public?: boolean
  public_slug?: string
  share_count?: number
  share_metadata?: Record<string, any>
  og_image_url?: string
  published_at?: string
  view_count?: number
  show_salary_public?: boolean
}

export interface JobStage {
  id: string
  job_id: string
  name: string
  description?: string
  order: number
  color: string
  is_system: boolean
  created_at: string
}

export interface Candidate {
  id: string
  organization_id: string
  email: string
  first_name: string
  last_name: string
  full_name?: string
  phone?: string
  location?: string
  headline?: string
  summary?: string
  avatar_url?: string
  resume_url?: string
  linkedin_url?: string
  github_url?: string
  total_experience_years?: number
  quality_score?: number
  tags?: string[]
  created_at: string
  updated_at: string
}

export interface CandidateExperience {
  id: string
  candidate_id: string
  company: string
  title: string
  location?: string
  start_date?: string
  end_date?: string
  is_current: boolean
  description?: string
}

export interface CandidateEducation {
  id: string
  candidate_id: string
  institution: string
  degree?: string
  field_of_study?: string
  start_date?: string
  end_date?: string
  grade?: string
}

export interface CandidateSkill {
  id: string
  candidate_id: string
  name: string
  category?: string
  proficiency_level?: number
  years_of_experience?: number
  is_verified: boolean
}

export interface Application {
  id: string
  job_id: string
  candidate_id: string
  status: 'active' | 'hired' | 'rejected' | 'withdrawn' | 'on_hold'
  current_stage?: string
  cover_letter?: string
  resume_url?: string
  ai_match_score?: number
  ai_recommendation?: string
  ai_strengths?: string[]
  ai_concerns?: string[]
  manual_score?: number
  applied_at?: string
  created_at: string
  updated_at: string
  
  // Relations
  job?: Job
  candidate?: Candidate
}

export interface Interview {
  id: string
  application_id: string
  title: string
  description?: string
  interview_type: 'phone' | 'video' | 'onsite' | 'technical' | 'behavioral' | 'panel'
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled' | 'no_show'
  scheduled_at: string
  duration_minutes: number
  location?: string
  meeting_link?: string
  created_at: string
}

export interface EmailTemplate {
  id: string
  organization_id: string
  name: string
  subject: string
  body: string
  category?: string
  stage?: string
  is_public: boolean
  tone?: string
  created_at: string
}

export interface ParsedResume {
  contact: {
    email?: string
    phone?: string
    location?: string
    linkedin?: string
    github?: string
  }
  summary?: string
  experience: Array<{
    company: string
    title: string
    location?: string
    start_date?: string
    end_date?: string
    is_current: boolean
    description?: string
  }>
  education: Array<{
    institution: string
    degree?: string
    field_of_study?: string
    start_date?: string
    end_date?: string
    grade?: string
  }>
  skills: string[]
  certifications?: string[]
  total_experience_years: number
}

export interface AIScreeningResult {
  fit_score: number
  recommendation: 'strong_fit' | 'maybe' | 'not_fit'
  strengths: string[]
  concerns: string[]
  summary: string
  suggested_questions: string[]
}

export interface GeneratedEmail {
  subject: string
  body: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// Public Job Types
export interface PublicJob {
  id: string
  title: string
  description: string
  requirements?: string
  responsibilities?: string
  department?: string
  location?: string
  job_type: 'full_time' | 'part_time' | 'contract' | 'internship' | 'temporary'
  experience_level: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'principal'
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  skills_required: string[]
  organization_name?: string
  created_at: string
  published_at?: string
  view_count: number
  share_count: number
}

export interface ShareLink {
  platform: string
  url: string
  text: string
}

export interface ShareLinksResponse {
  job_id: string
  job_title: string
  public_url: string
  share_links: ShareLink[]
}

export interface TrackShareRequest {
  platform: 'linkedin' | 'twitter' | 'facebook' | 'email' | 'copy'
}

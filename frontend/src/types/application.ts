export interface JobApplication {
  id: number
  user_id: number
  resume_id: number
  resume_version_id?: number | null
  company: string
  job_title: string
  job_url?: string | null
  location?: string | null
  status: string
  application_date: string
  interview_date?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface ApplicationSummary {
  id: number
  resume_id: number
  resume_version_id?: number | null
  company: string
  job_title: string
  status: string
  application_date: string
  interview_date?: string | null
  updated_at: string
}

export interface ApplicationInput {
  resume_id: number
  resume_version_id?: number | null
  company: string
  job_title: string
  job_url?: string
  location?: string
  status?: string
  application_date?: string
  interview_date?: string
  notes?: string
}

export interface ApplicationListParams {
  status?: string
  q?: string
  sort_by?: string
  order?: string
}

export const APPLICATION_STATUSES = ['applied', 'interview', 'offer', 'rejected', 'withdrawn']

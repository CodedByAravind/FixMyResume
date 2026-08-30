import { Education, Experience, Project, Skill, Certification } from './resume'

export interface VersionProfile {
  title?: string | null
  full_name?: string | null
  email?: string | null
  phone?: string | null
  location?: string | null
  website?: string | null
  linkedin?: string | null
  github?: string | null
  summary?: string | null
}

export interface VersionSnapshot {
  profile: VersionProfile
  education: Education[]
  experience: Experience[]
  projects: Project[]
  skills: Skill[]
  certifications: Certification[]
}

export interface TailoredVersion {
  id: number
  resume_id: number
  name: string
  analysis_score?: number | null
  tailored_score?: number | null
  created_at: string
  source: VersionSnapshot
  tailored: VersionSnapshot
  changed_sections: string[]
  recommendations: string[]
  warnings: string[]
}

export interface VersionSummary {
  id: number
  resume_id: number
  name: string
  analysis_score?: number | null
  tailored_score?: number | null
  created_at: string
}

export interface VersionDetail {
  id: number
  resume_id: number
  name: string
  analysis_score?: number | null
  tailored_score?: number | null
  created_at: string
  source: VersionSnapshot
  tailored: VersionSnapshot
}

export interface CompareResult {
  resume_id: number
  version_id: number
  version_name: string
  analysis_score?: number | null
  tailored_score?: number | null
  changed_sections: string[]
  source: VersionSnapshot
  tailored: VersionSnapshot
  recommendations: string[]
  warnings: string[]
}

export interface TailorRequest {
  job_description: string
  name?: string
}

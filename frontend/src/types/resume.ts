export interface Education {
  id: number
  institution: string
  degree?: string | null
  field_of_study?: string | null
  start_date?: string | null
  end_date?: string | null
  description?: string | null
  position: number
}

export interface Experience {
  id: number
  company: string
  title: string
  location?: string | null
  start_date?: string | null
  end_date?: string | null
  description?: string | null
  position: number
}

export interface Project {
  id: number
  name: string
  description?: string | null
  url?: string | null
  position: number
}

export interface Skill {
  id: number
  name: string
  category?: string | null
  position: number
}

export interface Certification {
  id: number
  name: string
  issuer?: string | null
  date_obtained?: string | null
  url?: string | null
  position: number
}

export interface Resume {
  id: number
  title: string
  full_name?: string | null
  email?: string | null
  phone?: string | null
  location?: string | null
  website?: string | null
  linkedin?: string | null
  github?: string | null
  summary?: string | null
  created_at: string
  updated_at: string
  education: Education[]
  experience: Experience[]
  projects: Project[]
  skills: Skill[]
  certifications: Certification[]
}

export interface ResumeSummary {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface ResumeInput {
  title?: string
  full_name?: string
  email?: string
  phone?: string
  location?: string
  website?: string
  linkedin?: string
  github?: string
  summary?: string
}

export interface EducationInput {
  institution: string
  degree?: string
  field_of_study?: string
  start_date?: string
  end_date?: string
  description?: string
}

export interface ExperienceInput {
  company: string
  title: string
  location?: string
  start_date?: string
  end_date?: string
  description?: string
}

export interface ProjectInput {
  name: string
  description?: string
  url?: string
}

export interface SkillInput {
  name: string
  category?: string
}

export interface CertificationInput {
  name: string
  issuer?: string
  date_obtained?: string
  url?: string
}

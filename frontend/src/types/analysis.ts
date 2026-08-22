export interface SkillMatch {
  name: string
  category?: string | null
}

export interface ScoreDetails {
  skill_score: number
  keyword_score: number
  role_domain_score: number
  overall: number
}

export interface AnalysisResult {
  score: number
  score_details: ScoreDetails
  matched_skills: SkillMatch[]
  missing_skills: SkillMatch[]
  job_keywords: string[]
  matched_keywords: string[]
  missing_keywords: string[]
  recommendations: string[]
  summary: string
  provider: string
}

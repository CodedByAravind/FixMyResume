import apiClient from './client'
import type { AnalysisResult } from '../types/analysis'

export async function analyzeResume(resumeId: number, jobDescription: string): Promise<AnalysisResult> {
  const resp = await apiClient.post<AnalysisResult>(`/api/v1/resumes/${resumeId}/analyze`, {
    job_description: jobDescription,
  })
  return resp.data
}

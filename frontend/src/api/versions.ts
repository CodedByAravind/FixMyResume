import apiClient from './client'
import type {
  CompareResult,
  TailoredVersion,
  TailorRequest,
  VersionDetail,
  VersionSummary,
} from '../types/resume_version'

export async function tailorResume(resumeId: number, data: TailorRequest): Promise<TailoredVersion> {
  const resp = await apiClient.post<TailoredVersion>(`/api/v1/resumes/${resumeId}/tailor`, data)
  return resp.data
}

export async function listVersions(resumeId: number): Promise<VersionSummary[]> {
  const resp = await apiClient.get<VersionSummary[]>(`/api/v1/resumes/${resumeId}/versions`)
  return resp.data
}

export async function getVersion(resumeId: number, versionId: number): Promise<VersionDetail> {
  const resp = await apiClient.get<VersionDetail>(`/api/v1/resumes/${resumeId}/versions/${versionId}`)
  return resp.data
}

export async function compareVersion(resumeId: number, versionId: number): Promise<CompareResult> {
  const resp = await apiClient.get<CompareResult>(`/api/v1/resumes/${resumeId}/versions/${versionId}/compare`)
  return resp.data
}

export async function deleteVersion(resumeId: number, versionId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/versions/${versionId}`)
}

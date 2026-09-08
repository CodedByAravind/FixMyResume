import apiClient from './client'
import type {
  ApplicationInput,
  ApplicationListParams,
  ApplicationSummary,
  JobApplication,
} from '../types/application'

export async function listApplications(params: ApplicationListParams): Promise<ApplicationSummary[]> {
  const resp = await apiClient.get<ApplicationSummary[]>('/api/v1/applications', { params })
  return resp.data
}

export async function createApplication(data: ApplicationInput): Promise<JobApplication> {
  const resp = await apiClient.post<JobApplication>('/api/v1/applications', data)
  return resp.data
}

export async function getApplication(id: number): Promise<JobApplication> {
  const resp = await apiClient.get<JobApplication>(`/api/v1/applications/${id}`)
  return resp.data
}

export async function updateApplication(id: number, data: Partial<ApplicationInput>): Promise<JobApplication> {
  const resp = await apiClient.put<JobApplication>(`/api/v1/applications/${id}`, data)
  return resp.data
}

export async function deleteApplication(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/applications/${id}`)
}

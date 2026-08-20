import apiClient from './client'
import type {
  Certification,
  CertificationInput,
  Education,
  EducationInput,
  Experience,
  ExperienceInput,
  Project,
  ProjectInput,
  Resume,
  ResumeInput,
  ResumeSummary,
  Skill,
  SkillInput,
} from '../types/resume'

export async function listResumes(): Promise<ResumeSummary[]> {
  const resp = await apiClient.get<ResumeSummary[]>('/api/v1/resumes')
  return resp.data
}

export async function createResume(data: ResumeInput): Promise<Resume> {
  const resp = await apiClient.post<Resume>('/api/v1/resumes', data)
  return resp.data
}

export async function getResume(id: number): Promise<Resume> {
  const resp = await apiClient.get<Resume>(`/api/v1/resumes/${id}`)
  return resp.data
}

export async function updateResume(id: number, data: ResumeInput): Promise<Resume> {
  const resp = await apiClient.put<Resume>(`/api/v1/resumes/${id}`, data)
  return resp.data
}

export async function deleteResume(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${id}`)
}

// Sections: education
export async function createEducation(resumeId: number, data: EducationInput): Promise<Education> {
  const resp = await apiClient.post<Education>(`/api/v1/resumes/${resumeId}/education`, data)
  return resp.data
}
export async function updateEducation(resumeId: number, entryId: number, data: Partial<EducationInput>): Promise<Education> {
  const resp = await apiClient.put<Education>(`/api/v1/resumes/${resumeId}/education/${entryId}`, data)
  return resp.data
}
export async function deleteEducation(resumeId: number, entryId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/education/${entryId}`)
}

// Sections: experience
export async function createExperience(resumeId: number, data: ExperienceInput): Promise<Experience> {
  const resp = await apiClient.post<Experience>(`/api/v1/resumes/${resumeId}/experience`, data)
  return resp.data
}
export async function updateExperience(resumeId: number, entryId: number, data: Partial<ExperienceInput>): Promise<Experience> {
  const resp = await apiClient.put<Experience>(`/api/v1/resumes/${resumeId}/experience/${entryId}`, data)
  return resp.data
}
export async function deleteExperience(resumeId: number, entryId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/experience/${entryId}`)
}

// Sections: projects
export async function createProject(resumeId: number, data: ProjectInput): Promise<Project> {
  const resp = await apiClient.post<Project>(`/api/v1/resumes/${resumeId}/projects`, data)
  return resp.data
}
export async function updateProject(resumeId: number, entryId: number, data: Partial<ProjectInput>): Promise<Project> {
  const resp = await apiClient.put<Project>(`/api/v1/resumes/${resumeId}/projects/${entryId}`, data)
  return resp.data
}
export async function deleteProject(resumeId: number, entryId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/projects/${entryId}`)
}

// Sections: skills
export async function createSkill(resumeId: number, data: SkillInput): Promise<Skill> {
  const resp = await apiClient.post<Skill>(`/api/v1/resumes/${resumeId}/skills`, data)
  return resp.data
}
export async function updateSkill(resumeId: number, entryId: number, data: Partial<SkillInput>): Promise<Skill> {
  const resp = await apiClient.put<Skill>(`/api/v1/resumes/${resumeId}/skills/${entryId}`, data)
  return resp.data
}
export async function deleteSkill(resumeId: number, entryId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/skills/${entryId}`)
}

// Sections: certifications
export async function createCertification(resumeId: number, data: CertificationInput): Promise<Certification> {
  const resp = await apiClient.post<Certification>(`/api/v1/resumes/${resumeId}/certifications`, data)
  return resp.data
}
export async function updateCertification(resumeId: number, entryId: number, data: Partial<CertificationInput>): Promise<Certification> {
  const resp = await apiClient.put<Certification>(`/api/v1/resumes/${resumeId}/certifications/${entryId}`, data)
  return resp.data
}
export async function deleteCertification(resumeId: number, entryId: number): Promise<void> {
  await apiClient.delete(`/api/v1/resumes/${resumeId}/certifications/${entryId}`)
}

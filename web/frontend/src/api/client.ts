import axios from 'axios'
import type { Job, JobCreate, UploadResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
})

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post<UploadResponse>('/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return data
}

export async function uploadYoutube(url: string): Promise<UploadResponse> {
  const { data } = await api.post<UploadResponse>('/upload/youtube', { url })
  return data
}

export async function createJob(payload: JobCreate): Promise<Job> {
  const { data } = await api.post<Job>('/jobs/', payload)
  return data
}

export async function listJobs(): Promise<Job[]> {
  const { data } = await api.get<{ jobs: Job[] }>('/jobs')
  return data.jobs
}

export async function getJob(id: string): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}`)
  return data
}

export async function deleteJob(id: string): Promise<void> {
  await api.delete(`/jobs/${id}`)
}

export function getDownloadUrl(jobId: string, filename: string): string {
  return `/api/jobs/${jobId}/download/${encodeURIComponent(filename)}`
}

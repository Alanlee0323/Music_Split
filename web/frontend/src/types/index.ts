export interface UploadResponse {
  file_id: string
  filename: string
  size: number
}

export interface JobCreate {
  file_id: string
  model: string
  stems: string
}

export interface Job {
  id: string
  filename: string
  status: 'pending' | 'downloading' | 'processing' | 'completed' | 'failed'
  model: string
  stems: string
  created_at: string
  completed_at: string | null
  error: string | null
  output_files: string[]
}

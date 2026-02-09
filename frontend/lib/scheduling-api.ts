/**
 * SCHEDULING API CLIENT MODULE
 * ============================
 * This module extends the main API client with scheduling-specific
 * functionality for creating schedules, uploading files, and managing
 * complex scheduling preferences.
 */

import { apiClient } from "./api"

// Type definitions for scheduling
export interface TimeSlot {
  start: string
  end: string
}

export interface DayAvailability {
  day: string
  available: boolean
  time_slots: TimeSlot[]
}

export interface SchedulingPreferences {
  subject_count: number
  strategy: string
  prioritize_dependencies: boolean
  include_saturday: boolean
  weekly_availability: DayAvailability[]
  additional_notes: string
  uploaded_subjects: UploadedSubject[]
}

export interface UploadedSubject {
  name: string
  schedule: string
  credits: number
  difficulty: number
  category?: string
  prerequisites?: string[]
  teacher?: string
  description?: string
}

export interface ScheduleResult {
  success: boolean
  schedule?: any[]
  analysis?: {
    total_subjects: number
    total_credits: number
    total_hours: number
    average_difficulty: number
    difficulty_distribution: Record<number, number>
    category_distribution: Record<string, number>
    warnings: string[]
    recommendations: string[]
    schedule_efficiency: number
  }
  error?: string
  timestamp: string
}

export interface FileUploadResult {
  success: boolean
  subjects?: UploadedSubject[]
  count?: number
  file_type?: string
  error?: string
}

export interface BulkPreferenceUpdate {
  subject_id: number
  interest_level: number
  priority?: number
  notes?: string
  status?: string
}

/**
 * Extended API client for scheduling functionality
 */
// class SchedulingAPI {
//   /**
//    * Create an optimized schedule based on preferences
//    */
//   async createSchedule(preferences: SchedulingPreferences): Promise<ScheduleResult> {
//     return apiClient.makeRequest<ScheduleResult>("/schedule/create", {
//       method: "POST",
//       body: JSON.stringify(preferences),
//     })
//   }

//   /**
//    * Upload and parse a subject file
//    */
//   async uploadSubjectFile(file: File): Promise<FileUploadResult> {
//     const formData = new FormData()
//     formData.append("file", file)

//     // Use fetch directly for file upload (multipart/form-data)
//     const token = apiClient.getToken()
//     const headers: HeadersInit = {}

//     if (token) {
//       headers["Authorization"] = `Bearer ${token}`
//     }

//     try {
//       const response = await fetch(`${apiClient.baseURL}/files/upload`, {
//         method: "POST",
//         headers,
//         body: formData,
//       })

//       if (!response.ok) {
//         const errorData = await response.json().catch(() => ({}))
//         throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
//       }

//       return await response.json()
//     } catch (error) {
//       console.error("File upload failed:", error)
//       throw error
//     }
//   }

//   /**
//    * Get sample file formats for reference
//    */
//   async getSampleFormats(): Promise<{
//     success: boolean
//     sample_formats: Record<string, string>
//     supported_extensions: string[]
//   }> {
//     return apiClient.makeRequest<{
//       success: boolean
//       sample_formats: Record<string, string>
//       supported_extensions: string[]
//     }>("/files/sample-formats")
//   }

//   /**
//    * Update multiple preferences at once
//    */
//   async bulkUpdatePreferences(preferences: BulkPreferenceUpdate[]): Promise<{
//     success: boolean
//     message: string
//     results: Array<{
//       subject_id: number
//       success: boolean
//       preference_id?: number
//       error?: string
//     }>
//   }> {
//     return apiClient.makeRequest<{
//       success: boolean
//       message: string
//       results: Array<{
//         subject_id: number
//         success: boolean
//         preference_id?: number
//         error?: string
//       }>
//     }>("/preferences/bulk", {
//       method: "POST",
//       body: JSON.stringify({ preferences }),
//     })
//   }

//   /**
//    * Get detailed schedule analysis
//    */
//   async getScheduleAnalysis(scheduleId: number): Promise<any> {
//     return apiClient.makeRequest<any>(`/schedule/analysis/${scheduleId}`)
//   }
// }

// Create and export scheduling API instance
// export const schedulingAPI = new SchedulingAPI()

// // Export for custom instances if needed
// export default SchedulingAPI

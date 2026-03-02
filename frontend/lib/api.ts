/**
 * API CLIENT MODULE
 * =================
 * This module provides a centralized API client for communicating with the
 * Python Flask backend. It handles authentication, request/response formatting,
 * and error handling for all API interactions.
 *
 * Features:
 * - Automatic token management
 * - Request/response interceptors
 * - Type-safe API calls
 * - Error handling and retry logic
 * - Authentication state management
 */

// API configuration constants
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api"

// Type definitions for API responses and requests
export interface Student {
  id: number
  email: string
  first_name: string
  last_name: string
  grade_level: number
  date_of_birth?: string
  phone_number?: string
  guardian_email?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Subject {
  id: number
  name: string
  code?: string
  description?: string
  category: string
  difficulty_level: number
  credits: number
  prerequisites?: string
  teacher_name?: string
  max_students?: number
  semester?: string
  is_active: boolean
  created_at: string
}

export interface StudentPreference {
  id: number
  student_id: number
  subject_id: number
  subject_name: string
  subject_code?: string
  category: string
  difficulty_level: number
  interest_level: number
  priority?: number
  notes?: string
  status: string
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  grade_level: number
  date_of_birth?: string
  phone_number?: string
  guardian_email?: string
}

export interface PreferenceRequest {
  subject_id: number
  interest_level: number
  priority?: number
  notes?: string
  status?: string
}

export interface AIRecommendationRequest {
  additional_context?: string
}

export interface AISubjectAnalysisRequest {
  subject_name: string
}

export interface AICareerAdviceRequest {
  career_interest: string
}

export interface AIStudyPlanRequest {
  selected_subjects: string[]
  semester?: string
}

export interface GradeHoraria {
  id: number
  student_id: number
  semester?: string
  status: string
  created_at: string
  updated_at: string
  subjects?: Subject[]
}

export interface GradeHorariaRequest {
  semester?: string
  status?: string
}

/**
 * API Client class that handles all communication with the backend
 */
class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL

    // Load token from localStorage on initialization
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token")
    }
  }

  /**
   * Set the authentication token for API requests
   */
  setToken(token: string | null) {
    this.token = token

    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("auth_token", token)
      } else {
        localStorage.removeItem("auth_token")
      }
    }
  }

  /**
   * Get the current authentication token
   */
  getToken(): string | null {
    return this.token
  }

  /**
   * Check if user is currently authenticated
   */
  isAuthenticated(): boolean {
    return !!this.token
  }

  /**
   * Make an authenticated API request with proper error handling
   */
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    // Prepare headers
    const headers: HeadersInit = {
      "Content-Type": "application/json"
    }

    // Add authentication token if available
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      // Handle different response types
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
      }

      // Parse JSON response
      const data = await response.json()
      return data as T
    } catch (error) {
      console.error(`API Request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // ==========================================
  // AUTHENTICATION METHODS
  // ==========================================

  /**
   * Authenticate a student with email and password
   */
  async login(
    credentials: LoginRequest
  ): Promise<{ success: boolean; token: string; student: Student }> {

    const response = await this.makeRequest<{
      success: boolean
      token: string
      student: Student
    }>("/auth/login", {   // 👈 BARRA ADICIONADA
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    })

    if (response.success && response.token) {
      this.setToken(response.token)
    }

    return response
  }

  /**
   * Register a new student account
   */
  async register(userData: RegisterRequest): Promise<{ success: boolean; student_id: number }> {
    return this.makeRequest<{ success: boolean; student_id: number }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }

  /**
   * Logout the current student
   */
  async logout(): Promise<{ success: boolean }> {
    const response = await this.makeRequest<{ success: boolean }>("/auth/logout", {
      method: "POST",
    })

    // Clear the stored token
    this.setToken(null)

    return response
  }

  // ==========================================
  // STUDENT PROFILE METHODS
  // ==========================================

  /**
   * Get the current student's profile
   */
  async getProfile(): Promise<{ success: boolean; student: Student }> {
    return this.makeRequest<{ success: boolean; student: Student }>("/students/profile")
  }

  /**
   * Update the current student's profile
   */
  async updateProfile(updates: Partial<Student>): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>("/students/profile", {
      method: "PUT",
      body: JSON.stringify(updates),
    })
  }

  // ==========================================
  // SUBJECT METHODS
  // ==========================================

  /**
   * Get all available subjects, optionally filtered by category
   */
  async getSubjects(category?: string): Promise<{ success: boolean; subjects: Subject[] }> {
    const endpoint = category ? `/subjects?category=${encodeURIComponent(category)}` : "/subjects"
    return this.makeRequest<{ success: boolean; subjects: Subject[] }>(endpoint)
  }

  /**
   * Get detailed information about a specific subject
   */
  async getSubject(subjectId: number): Promise<{ success: boolean; subject: Subject }> {
    return this.makeRequest<{ success: boolean; subject: Subject }>(`/subjects/${subjectId}`)
  }

  /**
   * Get all available subject categories
   */
  async getCategories(): Promise<{ success: boolean; categories: string[] }> {
    return this.makeRequest<{ success: boolean; categories: string[] }>("/subjects/categories")
  }

  // ==========================================
  // PREFERENCE METHODS
  // ==========================================

  /**
   * Get all preferences for the current student
   */
  async getPreferences(): Promise<{ success: boolean; preferences: StudentPreference[] }> {
    return this.makeRequest<{ success: boolean; preferences: StudentPreference[] }>("/preferences")
  }

  /**
   * Add or update a student preference
   */
  async addPreference(preference: PreferenceRequest): Promise<{ success: boolean; preference_id: number }> {
    return this.makeRequest<{ success: boolean; preference_id: number }>("/preferences", {
      method: "POST",
      body: JSON.stringify(preference),
    })
  }

  /**
   * Remove a student preference
   */
  async removePreference(preferenceId: number): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/preferences/${preferenceId}`, {
      method: "DELETE",
    })
  }

  // ==========================================
  // AI-POWERED METHODS
  // ==========================================

  /**
   * Get AI-powered subject recommendations
   */
  async getAIRecommendations(request: AIRecommendationRequest): Promise<any> {
    return this.makeRequest<any>("/ai/recommendations", {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  /**
   * Analyze how well a subject fits the student
   */
  async analyzeSubjectFit(request: AISubjectAnalysisRequest): Promise<any> {
    return this.makeRequest<any>("/ai/subject-analysis", {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  /**
   * Get career pathway advice
   */
  async getCareerAdvice(request: AICareerAdviceRequest): Promise<any> {
    return this.makeRequest<any>("/ai/career-advice", {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  /**
   * Generate a personalized study plan
   */
  async generateStudyPlan(request: AIStudyPlanRequest): Promise<any> {
    return this.makeRequest<any>("/ai/study-plan", {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  // ==========================================
  // GRADE HORARIA METHODS
  // ==========================================

  /**
   * Get the current student's grade horaria
   */
  async getGradeHoraria(): Promise<{ success: boolean; grade: GradeHoraria }> {
    return this.makeRequest<{ success: boolean; grade: GradeHoraria }>("/grade-horaria")
  }

  /**
   * Create a new grade horaria
   */
  async createGradeHoraria(data: GradeHorariaRequest): Promise<{ success: boolean; grade_id: number }> {
    return this.makeRequest<{ success: boolean; grade_id: number }>("/grade-horaria", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  /**
   * Update grade horaria
   */
  async updateGradeHoraria(gradeId: number, data: GradeHorariaRequest): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/grade-horaria/${gradeId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  /**
   * Delete grade horaria
   */
  async deleteGradeHoraria(gradeId: number): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/grade-horaria/${gradeId}`, {
      method: "DELETE",
    })
  }

  /**
   * Add subject to grade horaria
   */
  async addSubjectToGrade(gradeId: number, subjectId: number): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/grade-horaria/${gradeId}/subjects`, {
      method: "POST",
      body: JSON.stringify({ subject_id: subjectId }),
    })
  }

  /**
   * Remove subject from grade horaria
   */
  async removeSubjectFromGrade(gradeId: number, subjectId: number): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/grade-horaria/${gradeId}/subjects/${subjectId}`, {
      method: "DELETE",
    })
  }

  // ==========================================
  // UTILITY METHODS
  // ==========================================

  /**
   * Check API health status
   */
  async healthCheck(): Promise<any> {
    return this.makeRequest<any>("/health")
  }
}

// Create and export a singleton API client instance
export const apiClient = new APIClient()

// Export the class for custom instances if needed
export default APIClient

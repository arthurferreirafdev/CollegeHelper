"use client"

/**
 * STUDENT LOGIN COMPONENT
 * =======================
 * This component provides the main login interface for students.
 * It integrates with the Python backend API for authentication
 * and handles the complete login flow including error handling,
 * loading states, and successful authentication.
 *
 * Features:
 * - Real authentication with backend API
 * - Form validation and error handling
 * - Loading states and user feedback
 * - Password visibility toggle
 * - Responsive design
 * - Integration with authentication context
 */
import MainForm from "@/components/main-form"
import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { BookOpen, GraduationCap, Eye, EyeOff, Loader2 } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api"

export default function StudentLogin() {
  // Component state management
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // Next.js router for navigation
  const router = useRouter()

  /**
   * Handle form submission and authentication
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")
    setSuccess("")

    // Extract form data
    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    // Basic client-side validation
    if (!email || !password) {
      setError("Please fill in all fields")
      setIsLoading(false)
      return
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address")
      setIsLoading(false)
      return
    }

    try {
// Fazendo a chamada real para a API Flask
      const response = await apiClient.login({ email, password })

      if (response && response.success) { 
        setSuccess("Login efetuado com sucesso! Redirecionando...")

        // SALVANDO O TOKEN (O Crachá de acesso!)
        if (response.token) {
          try {
            // Usa o método oficial do ApiClient, conforme documentado
            apiClient.setToken(response.token)
          } catch (e) {
            // Plano B caso o método esteja estruturado de forma diferente
            localStorage.setItem("token", response.token)
          }
        }

        // Salvando os dados do aluno no storage
        if (response.student) {
            localStorage.setItem("student_data", JSON.stringify(response.student))
        }

        // Redirecionamento
        setTimeout(() => {
          router.push("/main")
        }, 1500)
      } else {
        setError("Login failed. Please check your credentials.")
      }
    } catch (err) {
      // Handle different types of errors
      if (err instanceof Error) {
        if (err.message.includes("401")) {
          setError("Invalid email or password. Please try again.")
        } else if (err.message.includes("500")) {
          setError("Server error. Please try again later.")
        } else if (err.message.includes("fetch")) {
          setError("Unable to connect to server. Please check your internet connection.")
        } else {
          setError(err.message || "An unexpected error occurred.")
        }
      } else {
        setError("An unexpected error occurred. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Toggle password visibility
   */
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        {/* Application Header and Branding */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-2 mb-4">
            <div className="p-2 bg-blue-600 rounded-full">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
            <BookOpen className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">CollegeHelper</h1>
          <p className="text-gray-600">Find your perfect subjects based on your interests</p>
        </div>

        {/* Main Login Card */}
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl text-center text-gray-900">Welcome Back</CardTitle>
            <CardDescription className="text-center text-gray-600">
              Sign in to continue your academic journey
            </CardDescription>
          </CardHeader>

          <CardContent>
            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Success Message Display */}
              {success && (
                <Alert className="border-green-200 bg-green-50">
                  <AlertDescription className="text-green-800">{success}</AlertDescription>
                </Alert>
              )}

              {/* Error Message Display */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Email Input Field */}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email Address
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="student@school.edu"
                  required
                  disabled={isLoading}
                  className="h-11"
                  autoComplete="email"
                />
              </div>

              {/* Password Input Field with Visibility Toggle */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    required
                    disabled={isLoading}
                    className="h-11 pr-10"
                    autoComplete="current-password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-11 w-11 hover:bg-transparent"
                    onClick={togglePasswordVisibility}
                    disabled={isLoading}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-500" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-500" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Forgot Password Link */}
              <div className="flex items-center justify-between">
                <Link href="/forgot-password" className="text-sm text-blue-600 hover:text-blue-800 hover:underline">
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button with Loading State */}
              <Button
                type="submit"
                className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white font-medium"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>

            {/* Registration Link */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                {"Don't have an account? "}
                <Link href="/register" className="text-blue-600 hover:text-blue-800 font-medium hover:underline">
                  Sign up here
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Footer Support Link */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Need help? Contact{" "}
            <Link href="/support" className="text-blue-600 hover:underline">
              student support
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

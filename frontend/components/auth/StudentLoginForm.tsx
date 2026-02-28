"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { apiClient } from "@/lib/api"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { BookOpen, GraduationCap, Eye, EyeOff, Loader2 } from "lucide-react"

export default function StudentLoginForm() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")
    setSuccess("")

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

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
      const response = await apiClient.login({ email, password })
      console.log(response)
      if (response.success) {
        setSuccess("Login successful! Redirecting...")

        setTimeout(() => {
          router.push("/main")
        }, 1200)
      } else {
        setError("Login failed. Please check your credentials.")
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes("401")) {
          setError("Invalid email or password.")
        } else if (err.message.includes("500")) {
          setError("Server error. Try again later.")
        } else {
          setError(err.message)
        }
      } else {
        setError("Unexpected error occurred.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-2 mb-4">
            <div className="p-2 bg-blue-600 rounded-full">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
            <BookOpen className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">EduChoice</h1>
          <p className="text-gray-600">Sign in to continue</p>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Welcome Back</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">

              {success && (
                <Alert className="border-green-200 bg-green-50">
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              )}

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label>Email</Label>
                <Input name="email" type="email" required disabled={isLoading} />
              </div>

              <div className="space-y-2">
                <Label>Password</Label>
                <div className="relative">
                  <Input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    disabled={isLoading}
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </Button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>

              <div className="text-center text-sm">
                <Link href="/register" className="text-blue-600 hover:underline">
                  Don’t have an account? Sign up
                </Link>
              </div>

            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
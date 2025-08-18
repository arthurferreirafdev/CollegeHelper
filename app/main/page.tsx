"use client"

/**
 * MAIN PAGE COMPONENT
 * ==================
 * This page serves as the main entry point for students to configure
 * their subject selection preferences. It includes authentication check
 * and renders the main form component.
 */

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import MainForm from "@/components/main-form"
import { apiClient } from "@/lib/api"
import { Loader2 } from "lucide-react"

export default function MainPage() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [studentData, setStudentData] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    // Check authentication status
    const checkAuth = async () => {
      try {
        if (apiClient.isAuthenticated()) {
          const response = await apiClient.getProfile()
          if (response.success) {
            setStudentData(response.student)
            setIsAuthenticated(true)
          } else {
            setIsAuthenticated(false)
            router.push("/login")
          }
        } else {
          setIsAuthenticated(false)
          router.push("/login")
        }
      } catch (error) {
        setIsAuthenticated(false)
        router.push("/login")
      }
    }

    checkAuth()
  }, [router])

  // Show loading while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Show main form if authenticated
  if (isAuthenticated) {
    return <MainForm />
  }

  // This shouldn't render due to redirect, but just in case
  return null
}

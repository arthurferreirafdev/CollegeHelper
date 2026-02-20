"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Calendar, BookOpen, Clock, RefreshCw, Loader2 } from "lucide-react"

const DAY_ORDER = [
  "Segunda-feira", "Segunda",
  "Terça-feira", "Terca-feira", "Terça", "Terca",
  "Quarta-feira", "Quarta",
  "Quinta-feira", "Quinta",
  "Sexta-feira", "Sexta",
  "Sábado", "Sabado",
  "Domingo",
]

function getDayIndex(day: string): number {
  const normalized = day.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  for (let i = 0; i < DAY_ORDER.length; i++) {
    const orderNormalized = DAY_ORDER[i].normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    if (normalized === orderNormalized || normalized.startsWith(orderNormalized)) {
      return i
    }
  }
  return 999
}

type Schedule = Record<string, string[]>

export default function ResultsPage() {
  const router = useRouter()
  const [schedule, setSchedule] = useState<Schedule | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    try {
      const stored = localStorage.getItem("scheduleResult")
      if (!stored) {
        setError("Nenhuma grade horária encontrada. Por favor, envie suas preferências primeiro.")
        setLoading(false)
        return
      }
      const parsed = JSON.parse(stored)
      setSchedule(parsed)
    } catch {
      setError("Erro ao carregar a grade horária.")
    } finally {
      setLoading(false)
    }
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 text-lg">Carregando grade horária...</p>
        </div>
      </div>
    )
  }

  if (error || !schedule) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center space-y-4">
            <Calendar className="h-16 w-16 text-gray-400 mx-auto" />
            <p className="text-gray-600">{error || "Nenhuma grade encontrada."}</p>
            <Button onClick={() => router.push("/main")}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Voltar ao Formulário
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const sortedDays = Object.entries(schedule)
    .filter(([, subjects]) => subjects && subjects.length > 0)
    .sort(([a], [b]) => getDayIndex(a) - getDayIndex(b))

  const totalSubjects = new Set(
    sortedDays.flatMap(([, subjects]) =>
      subjects.map((entry) => entry.split(" - ")[0]?.trim())
    )
  ).size

  const daysWithClasses = sortedDays.length

  const totalWeeklyClasses = sortedDays.reduce(
    (sum, [, subjects]) => sum + subjects.length,
    0
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Sua Grade Horária</h1>
            <p className="text-gray-600">Grade gerada com base nas suas preferências</p>
          </div>
          <Button variant="outline" onClick={() => router.push("/main")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6 flex items-center gap-4">
              <BookOpen className="h-10 w-10 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{totalSubjects}</p>
                <p className="text-sm text-gray-500">Disciplinas</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 flex items-center gap-4">
              <Calendar className="h-10 w-10 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{daysWithClasses}</p>
                <p className="text-sm text-gray-500">Dias com aula</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 flex items-center gap-4">
              <Clock className="h-10 w-10 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">{totalWeeklyClasses}</p>
                <p className="text-sm text-gray-500">Aulas na semana</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Schedule Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {sortedDays.map(([day, subjects]) => (
            <Card key={day} className="overflow-hidden">
              <CardHeader className="bg-blue-600 text-white py-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {day}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-3">
                  {subjects.map((entry, idx) => {
                    const parts = entry.split(" - ")
                    const subjectName = parts[0]?.trim() || entry
                    const time = parts.slice(1).join(" - ")?.trim()
                    return (
                      <div
                        key={idx}
                        className="flex items-start justify-between gap-2 p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                      >
                        <span className="font-medium text-sm text-gray-800">{subjectName}</span>
                        {time && (
                          <Badge variant="secondary" className="whitespace-nowrap text-xs">
                            {time}
                          </Badge>
                        )}
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 pb-8">
          <Button variant="outline" size="lg" onClick={() => router.push("/main")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar ao Formulário
          </Button>
          <Button
            size="lg"
            onClick={() => {
              localStorage.removeItem("scheduleResult")
              router.push("/main")
            }}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Gerar Nova Grade
          </Button>
        </div>
      </div>
    </div>
  )
}

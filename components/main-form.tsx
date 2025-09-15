"use client"

import type React from "react"
import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
  Clock,
  Upload,
  Calendar,
  BookOpen,
  Settings,
  AlertCircle,
  CheckCircle,
  Loader2,
  FileText,
  X,
} from "lucide-react"

interface TimeSlot {
  start: string
  end: string
}

interface DaySchedule {
  day: string
  available: boolean
  timeSlots: TimeSlot[]
}

interface FormData {
  subjectCount: number
  preferenceStrategy: string
  prioritizeDependencies: boolean
  includeSaturday: boolean
  weeklySchedule: DaySchedule[]
  additionalNotes: string
  uploadedFile: File | null
}

interface UploadedSubject {
  name: string
  schedule: string
  credits: number
  difficulty: number
}

const DAYS_OF_WEEK = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]

const PREFERENCE_STRATEGIES = [
  {
    value: "maximize_subjects",
    label: "Maximizar Número de Disciplinas",
    description: "Obtenha o máximo de disciplinas dentro das restrições de horário",
  },
  {
    value: "clear_dependencies",
    label: "Priorizar Pré-requisitos",
    description: "Priorize disciplinas que desbloqueiam outras disciplinas",
  },
  {
    value: "balanced_difficulty",
    label: "Dificuldade Balanceada",
    description: "Mistura de disciplinas fáceis e desafiadoras para aprendizado ideal",
  },
  {
    value: "interest_based",
    label: "Baseado em Interesse",
    description: "Foque em disciplinas que combinam com seus interesses e carreira",
  },
  {
    value: "high_value_credits",
    label: "Créditos de Alto Valor",
    description: "Priorize disciplinas com maior valor de créditos",
  },
]

export default function MainForm() {
  const [formData, setFormData] = useState<FormData>({
    subjectCount: 5,
    preferenceStrategy: "",
    prioritizeDependencies: true,
    includeSaturday: false,
    weeklySchedule: DAYS_OF_WEEK.map((day) => ({
      day,
      available: day !== "Sábado",
      timeSlots: day !== "Sábado" ? [{ start: "09:00", end: "17:00" }] : [],
    })),
    additionalNotes: "",
    uploadedFile: null,
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const [uploadedSubjects, setUploadedSubjects] = useState<UploadedSubject[]>([])
  const [dragActive, setDragActive] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubjectCountChange = (value: string) => {
    const count = Number.parseInt(value)
    if (count >= 1 && count <= 12) {
      setFormData((prev) => ({ ...prev, subjectCount: count }))
    }
  }

  const handleStrategyChange = (value: string) => {
    setFormData((prev) => ({ ...prev, preferenceStrategy: value }))
  }

  const handleSaturdayToggle = (checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      includeSaturday: checked,
      weeklySchedule: prev.weeklySchedule.map((schedule) =>
        schedule.day === "Sábado"
          ? { ...schedule, available: checked, timeSlots: checked ? [{ start: "09:00", end: "13:00" }] : [] }
          : schedule,
      ),
    }))
  }

  const handleDayToggle = (dayIndex: number, available: boolean) => {
    setFormData((prev) => ({
      ...prev,
      weeklySchedule: prev.weeklySchedule.map((schedule, index) =>
        index === dayIndex
          ? {
              ...schedule,
              available,
              timeSlots:
                available && schedule.timeSlots.length === 0
                  ? [{ start: "09:00", end: "17:00" }]
                  : available
                  ? schedule.timeSlots
                  : [],
            }
          : schedule,
      ),
    }))
  }

  const handleTimeSlotChange = (dayIndex: number, slotIndex: number, field: "start" | "end", value: string) => {
    setFormData((prev) => ({
      ...prev,
      weeklySchedule: prev.weeklySchedule.map((schedule, dIndex) =>
        dIndex === dayIndex
          ? {
              ...schedule,
              timeSlots: schedule.timeSlots.map((slot, sIndex) =>
                sIndex === slotIndex ? { ...slot, [field]: value } : slot,
              ),
            }
          : schedule,
      ),
    }))
  }

  const addTimeSlot = (dayIndex: number) => {
    setFormData((prev) => ({
      ...prev,
      weeklySchedule: prev.weeklySchedule.map((schedule, index) =>
        index === dayIndex
          ? {
              ...schedule,
              timeSlots: [...schedule.timeSlots, { start: "09:00", end: "17:00" }],
            }
          : schedule,
      ),
    }))
  }

  const removeTimeSlot = (dayIndex: number, slotIndex: number) => {
    setFormData((prev) => ({
      ...prev,
      weeklySchedule: prev.weeklySchedule.map((schedule, index) =>
        index === dayIndex
          ? {
              ...schedule,
              timeSlots: schedule.timeSlots.filter((_, sIndex) => sIndex !== slotIndex),
            }
          : schedule,
      ),
    }))
  }

  const handleFileUpload = (file: File) => {
    if (!file) return

    const allowedTypes = [".csv", ".json", ".txt", ".xlsx"]
    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()

    if (!allowedTypes.includes(fileExtension)) {
      setErrorMessage("Por favor, envie um arquivo CSV, JSON, TXT ou Excel")
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage("O tamanho do arquivo deve ser menor que 5MB")
      return
    }

    setFormData((prev) => ({ ...prev, uploadedFile: file }))
    setErrorMessage("")

    parseUploadedFile(file)
  }

  const parseUploadedFile = (file: File) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const content = e.target?.result as string
        if (file.name.endsWith(".csv")) {
          const lines = content.split("\n")
          const subjects: UploadedSubject[] = []
          for (let i = 1; i < lines.length; i++) {
            const [name, schedule, credits, difficulty] = lines[i].split(",")
            if (name && schedule) {
              subjects.push({
                name: name.trim(),
                schedule: schedule.trim(),
                credits: Number.parseInt(credits) || 3,
                difficulty: Number.parseInt(difficulty) || 3,
              })
            }
          }
          setUploadedSubjects(subjects)
        } else if (file.name.endsWith(".json")) {
          const jsonData = JSON.parse(content)
          if (Array.isArray(jsonData)) setUploadedSubjects(jsonData)
        }
      } catch (error) {
        setErrorMessage("Erro ao processar o arquivo. Verifique o formato.")
      }
    }

    reader.readAsText(file)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true)
    else if (e.type === "dragleave") setDragActive(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0])
  }

  const validateForm = (): boolean => {

    if (formData.subjectCount < 1 || formData.subjectCount > 12) {
      setErrorMessage("O número de disciplinas deve estar entre 1 e 12")
      return false
    }

    const hasAvailableDays = formData.weeklySchedule.some(
      (schedule) => schedule.available && schedule.timeSlots.length > 0,
    )

    if (!hasAvailableDays) {
      setErrorMessage("Selecione pelo menos um dia disponível com horários")
      return false
    }

    for (const schedule of formData.weeklySchedule) {
      if (schedule.available) {
        for (const slot of schedule.timeSlots) {
          if (slot.start >= slot.end) {
            setErrorMessage(`Intervalo de horário inválido em ${schedule.day}: o horário de início deve ser antes do horário de término`)
            return false
          }
        }
      }
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    setIsSubmitting(true)
    setSubmitStatus("idle")
    setErrorMessage("")

    try {
      const submissionData = {
        ...formData,
        uploadedSubjects,
        totalAvailableHours: calculateTotalAvailableHours(),
      }

      console.log("Submitting form data:", submissionData)
      await new Promise((resolve) => setTimeout(resolve, 2000))
      setSubmitStatus("success")
      setTimeout(() => setSubmitStatus("idle"), 3000)
    } catch (error) {
      setSubmitStatus("error")
      setErrorMessage("Falha ao enviar preferências. Por favor, tente novamente.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const calculateTotalAvailableHours = (): number => {
    return formData.weeklySchedule.reduce((total, schedule) => {
      if (!schedule.available) return total
      return (
        total +
        schedule.timeSlots.reduce((dayTotal, slot) => {
          const start = new Date(`2000-01-01T${slot.start}:00`)
          const end = new Date(`2000-01-01T${slot.end}:00`)
          return dayTotal + (end.getTime() - start.getTime()) / (1000 * 60 * 60)
        }, 0)
      )
    }, 0)
  }

  const removeUploadedFile = () => {
    setFormData((prev) => ({ ...prev, uploadedFile: null }))
    setUploadedSubjects([])
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Preferências de Seleção de Disciplinas</h1>
          <p className="text-gray-600">Configure suas preferências para um agendamento de disciplinas otimizado</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Preferências de Disciplinas
              </CardTitle>
              <CardDescription>Defina quantas disciplinas você deseja e sua estratégia de seleção</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="subjectCount">Número de Disciplinas neste Período</Label>
                  <Input
                    id="subjectCount"
                    type="number"
                    min="1"
                    max="12"
                    value={formData.subjectCount}
                    onChange={(e) => handleSubjectCountChange(e.target.value)}
                    className="w-full"
                  />
                  <p className="text-sm text-gray-500">Escolha entre 1 e 12 disciplinas</p>
                </div>

                <div className="space-y-2">
                  <Label>Total de Horas Disponíveis/Semana</Label>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <span className="text-2xl font-bold text-blue-600">
                      {calculateTotalAvailableHours().toFixed(1)}
                    </span>
                    <span className="text-gray-600 ml-1">horas</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="strategy">Estratégia de seleção</Label>
                <Select value={formData.preferenceStrategy} onValueChange={handleStrategyChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione sua estratégia de seleção" />
                  </SelectTrigger>
                  <SelectContent>
                    {PREFERENCE_STRATEGIES.map((strategy) => (
                      <SelectItem key={strategy.value} value={strategy.value}>
                        <div>
                          <div className="font-medium">{strategy.label}</div>
                          <div className="text-sm text-gray-500">{strategy.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="dependencies"
                    checked={formData.prioritizeDependencies}
                    onCheckedChange={(checked) =>
                      setFormData((prev) => ({ ...prev, prioritizeDependencies: checked as boolean }))
                    }
                  />
                  <Label htmlFor="dependencies" className="text-sm">
                    Priorizar disciplinas que desbloqueiam outras (pré-requisitos)
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox id="saturday" checked={formData.includeSaturday} onCheckedChange={handleSaturdayToggle} />
                  <Label htmlFor="saturday" className="text-sm">
                    Incluir aulas aos sábados na minha grade
                  </Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Card: Weekly Availability */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Disponibilidade Semanal
              </CardTitle>
              <CardDescription>Defina suas horas disponíveis para cada dia da semana</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {formData.weeklySchedule.map((schedule, dayIndex) => (
                  <div key={schedule.day} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Checkbox
                          checked={schedule.available}
                          onCheckedChange={(checked) => handleDayToggle(dayIndex, checked as boolean)}
                          disabled={schedule.day === "Sábado" && !formData.includeSaturday}
                        />
                        <Label className="font-medium">{schedule.day}</Label>
                        {schedule.available && (
                          <Badge variant="secondary">
                            {schedule.timeSlots.length} intervalo{schedule.timeSlots.length !== 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>

                      {schedule.available && (
                        <Button type="button" variant="outline" size="sm" onClick={() => addTimeSlot(dayIndex)}>
                          Adicionar Intervalo de Horário
                        </Button>
                      )}
                    </div>

                    {schedule.available && (
                      <div className="space-y-2">
                        {schedule.timeSlots.map((slot, slotIndex) => (
                          <div key={slotIndex} className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-gray-400" />
                            <Input
                              type="time"
                              value={slot.start}
                              onChange={(e) => handleTimeSlotChange(dayIndex, slotIndex, "start", e.target.value)}
                              className="w-32"
                            />
                            <span className="text-gray-500">até</span>
                            <Input
                              type="time"
                              value={slot.end}
                              onChange={(e) => handleTimeSlotChange(dayIndex, slotIndex, "end", e.target.value)}
                              className="w-32"
                            />
                            {schedule.timeSlots.length > 1 && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeTimeSlot(dayIndex, slotIndex)}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Card: File Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Arquivo de Grade de Disciplinas
              </CardTitle>
              <CardDescription>Envie um arquivo contendo informações das disciplinas e seus horários semanais</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {formData.uploadedFile ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-center gap-2">
                      <FileText className="h-8 w-8 text-green-600" />
                      <div>
                        <p className="font-medium">{formData.uploadedFile.name}</p>
                        <p className="text-sm text-gray-500">{(formData.uploadedFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <Button type="button" variant="outline" size="sm" onClick={removeUploadedFile}>
                      Remover Arquivo
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                    <div>
                      <p className="text-lg font-medium">Solte seu arquivo aqui</p>
                      <p className="text-gray-500">ou clique para selecionar</p>
                    </div>
                    <Button type="button" variant="outline" onClick={() => fileInputRef.current?.click()}>
                      Escolher Arquivo
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.json,.txt,.xlsx"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </div>
                )}
              </div>

              <div className="mt-4 text-sm text-gray-600">
                <p className="font-medium mb-2">Formatos suportados:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>CSV: nome_da_disciplina, horário, créditos, dificuldade</li>
                  <li>JSON: Array de objetos de disciplina</li>
                  <li>Excel: Dados estruturados das disciplinas</li>
                </ul>
              </div>

              {uploadedSubjects.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Disciplinas Enviadas ({uploadedSubjects.length})</h4>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {uploadedSubjects.map((subject, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium">{subject.name}</span>
                        <div className="flex gap-2 text-sm text-gray-600">
                          <span>{subject.schedule}</span>
                          <Badge variant="outline">{subject.credits} créditos</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Additional Preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Preferências Adicionais
              </CardTitle>
              <CardDescription>Quaisquer observações ou requisitos específicos</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Digite quaisquer preferências adicionais, restrições ou observações sobre sua seleção de disciplinas..."
                value={formData.additionalNotes}
                onChange={(e) => setFormData((prev) => ({ ...prev, additionalNotes: e.target.value }))}
                rows={4}
                className="w-full"
              />
            </CardContent>
          </Card>

          {errorMessage && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {submitStatus === "success" && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Preferências enviadas com sucesso! Processaremos sua solicitação e retornaremos em breve.
              </AlertDescription>
            </Alert>
          )}

          <div className="flex justify-center">
            <Button type="submit" size="lg" disabled={isSubmitting} className="w-full md:w-auto px-8">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processando Preferências...
                </>
              ) : (
                "Enviar Preferências"
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

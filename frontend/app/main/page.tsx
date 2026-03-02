"use client"

/**
 * MAIN STUDENT PREFERENCES FORM
 * =============================
 * This component provides a comprehensive form for students to input their
 * subject selection preferences, schedule availability, and upload subject files.
 *
 * Features:
 * - Subject quantity selection
 * - Preference strategy selection
 * - Weekly schedule input
 * - Saturday classes option
 * - Subject file upload
 * - Form validation and submission
 * - Integration with backend API
 */

import type React from "react"
import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
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
import * as pdfjsLib from "pdfjs-dist";
// @ts-ignore
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.mjs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api"

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.mjs",
  import.meta.url
).toString();



// Type definitions for form data
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

const DAYS_OF_WEEK = ["Monday", "Tuesday"]

// export default function MainForm() {
//   // Form state management
//   const [formData, setFormData] = useState<FormData>({
//     subjectCount: 5,
//     preferenceStrategy: "",
//     prioritizeDependencies: true,
//     includeSaturday: false,
//     weeklySchedule: DAYS_OF_WEEK.map((day) => ({
//       day,
//       available: day !== "Saturday",
//       timeSlots: day !== "Saturday" ? [{ start: "09:00", end: "17:00" }] : [],
//     })),
//     additionalNotes: "",
//     uploadedFile: null,
//   })

export default function MainForm() {
  const router = useRouter()
  const [formData, setFormData] = useState<FormData>({
    subjectCount: 2,
    preferenceStrategy: "",
    prioritizeDependencies: true,
    includeSaturday: false,
    weeklySchedule: DAYS_OF_WEEK.map((day) => ({
      day,
      available: true,
      timeSlots: [{ start: "19:00", end: "20:40" }],
    })),
    additionalNotes: "",
    uploadedFile: null,
  });

  const handleDayChange = (index: number, newDay: string) => {
    setFormData((prev) => {
      const updatedSchedule = [...prev.weeklySchedule];
      updatedSchedule[index] = { ...updatedSchedule[index], day: newDay };
      return { ...prev, weeklySchedule: updatedSchedule };
    });
  };

  // Track used days so we can disable duplicates
  const usedDays = formData.weeklySchedule.map((s) => s.day);

  // UI state management
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const [uploadedSubjects, setUploadedSubjects] = useState<UploadedSubject[]>([])
  const [dragActive, setDragActive] = useState(false)

  // File upload reference
  const fileInputRef = useRef<HTMLInputElement>(null)

  /**
   * Handle subject count change with validation
   */
  const handleSubjectCountChange = (value: string) => {
    const count = Number.parseInt(value)
    if (count >= 1 && count <= 12) {
      setFormData((prev) => ({ ...prev, subjectCount: count }))
    }
  }

  /**
   * Handle preference strategy selection
   */
  const handleStrategyChange = (value: string) => {
    setFormData((prev) => ({ ...prev, preferenceStrategy: value }))
  }

  /**
   * Handle Saturday inclusion toggle
   */
  const handleSaturdayToggle = (checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      includeSaturday: checked,
      weeklySchedule: prev.weeklySchedule.map((schedule) =>
        schedule.day === "Saturday"
          ? { ...schedule, available: checked, timeSlots: checked ? [{ start: "09:00", end: "13:00" }] : [] }
          : schedule,
      ),
    }))
  }

  /**
   * Handle day availability toggle
   */
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
                ? [{ start: "19:00", end: "20:40" }]
                : available
                  ? schedule.timeSlots
                  : [],
          }
          : schedule,
      ),
    }))
  }

  /**
   * Handle time slot changes for a specific day
   */
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

  /**
   * Add new time slot to a day
   */
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

  /**
   * Remove time slot from a day
   */
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

  /**
   * Handle file upload via drag and drop or file input
   */
  const handleFileUpload = (file: File) => {
    if (!file) return

    // Validate file type
    const allowedTypes = [".csv", ".json", ".txt", ".xlsx", ".pdf"]
    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()

    if (!allowedTypes.includes(fileExtension)) {
      setErrorMessage("Please upload a CSV, JSON, TXT, or Excel file")
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage("File size must be less than 5MB")
      return
    }

    setFormData((prev) => ({ ...prev, uploadedFile: file }))
    setErrorMessage("")

    // Parse file content (simplified example)
    parseUploadedFile(file)
  }

  /**
   * Parse uploaded file to extract subject information
   */
  const parseUploadedFile = async (file: File) => {
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const content = e.target?.result;

        // Handle CSV
        if (file.name.endsWith(".csv") && typeof content === "string") {
          const lines = content.split("\n");
          const subjects: UploadedSubject[] = [];

          for (let i = 1; i < lines.length; i++) {
            const [name, schedule, credits, difficulty] = lines[i].split(",");
            if (name && schedule) {
              subjects.push({
                name: name.trim(),
                schedule: schedule.trim(),
                credits: Number.parseInt(credits) || 3,
                difficulty: Number.parseInt(difficulty) || 3,
              });
            }
          }

          setUploadedSubjects(subjects);
        }
        // Handle JSON
        else if (file.name.endsWith(".json") && typeof content === "string") {
          const jsonData = JSON.parse(content);
          if (Array.isArray(jsonData)) {
            setUploadedSubjects(jsonData);
          }
        }
        // Handle PDF
        else if (file.name.endsWith(".pdf")) {
          const typedArray = new Uint8Array(content as ArrayBuffer);
          const pdf = await pdfjsLib.getDocument(typedArray).promise;

          let text = "";
          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const pageText = await page.getTextContent();
            pageText.items.forEach((item: any) => {
              text += item.str + " ";
            });
          }

          // Now `text` contains all PDF text; you can parse it similarly to CSV or JSON
          console.log(text);

          // Example: simple line split
          const lines = text.split("\n");
          const subjects: UploadedSubject[] = [];

          lines.forEach((line) => {
            const [name, schedule, credits, difficulty] = line.split(",");
            if (name && schedule) {
              subjects.push({
                name: name.trim(),
                schedule: schedule.trim(),
                credits: Number.parseInt(credits) || 3,
                difficulty: Number.parseInt(difficulty) || 3,
              });
            }
          });

          setUploadedSubjects(subjects);
        }
      } catch (error) {
        setErrorMessage("Error parsing file. Please check the format. " + error);
        console.error(error);
      }
    };

    if (file.name.endsWith(".pdf")) {
      reader.readAsArrayBuffer(file); // PDF requires ArrayBuffer
    } else {
      reader.readAsText(file);
    }
  };


  /**
   * Handle drag and drop events
   */
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  /**
   * Validate form data before submission
   */
  const validateForm = (): boolean => {

    if (formData.subjectCount < 1 || formData.subjectCount > 12) {
      setErrorMessage("Subject count must be between 1 and 12")
      return false
    }

    // Check if at least one day is available
    const hasAvailableDays = formData.weeklySchedule.some(
      (schedule) => schedule.available && schedule.timeSlots.length > 0,
    )

    if (!hasAvailableDays) {
      setErrorMessage("Please select at least one available day with time slots")
      return false
    }

    // Validate time slots
    for (const schedule of formData.weeklySchedule) {
      if (schedule.available) {
        for (const slot of schedule.timeSlots) {
          if (slot.start >= slot.end) {
            setErrorMessage(`Invalid time slot on ${schedule.day}: start time must be before end time`)
            return false
          }
        }
      }
    }

    return true
  }

  /**
   * Handle form submission
   */
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

      const response = await fetch(
        `${API_BASE_URL}/ai/recommendations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(submissionData),
        }
      )

      const result = await response.json()

      if (result.success) {
        setSubmitStatus("success")
        localStorage.setItem('scheduleResult', JSON.stringify(result.schedule))
        router.push('/results')
      } else {
        setSubmitStatus("error")
        setErrorMessage(result.message || "Failed to submit preferences")
      }
    } catch (error) {
      setSubmitStatus("error")
      setErrorMessage("Failed to submit preferences. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }


  /**
   * Calculate total available hours per week
   */
  const calculateTotalAvailableHours = (): number => {
    return formData.weeklySchedule.reduce((total, schedule) => {
      if (!schedule.available) return total

      return (
        total +
        schedule.timeSlots.reduce((dayTotal, slot) => {
          const start = new Date(`2000-01-01T${slot.start}:00`)
          const end = new Date(`2000-01-01T${slot.end}:00`)
          const hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
          return dayTotal + hours
        }, 0)
      )
    }, 0)
  }

  /**
   * Remove uploaded file
   */
  const removeUploadedFile = () => {
    setFormData((prev) => ({ ...prev, uploadedFile: null }))
    setUploadedSubjects([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Subject Selection Preferences</h1>
          <p className="text-gray-600">Configure your preferences for optimal subject scheduling</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Subject Count and Strategy */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Subject Preferences
              </CardTitle>
              <CardDescription>Defina quantas disciplinas você deseja e sua estratégia de seleção</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Period Select */}
              <div className="space-y-2">
                <Label>Período</Label>
                <select
                  className="w-full p-3 bg-gray-50 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  value={formData.subjectCount}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      subjectCount: Number(e.target.value),
                    }))
                  }
                >
                  {Array.from({ length: 8 }, (_, i) => i + 1).map((period) => (
                    <option key={period} value={period}>
                      {period}
                    </option>
                  ))}
                </select>
              </div>
              {/* <div className="flex items-center space-x-2">
                <Checkbox id="saturday" checked={formData.includeSaturday} onCheckedChange={handleSaturdayToggle} />
                <Label htmlFor="saturday" className="text-sm">
                  Include Saturday classes in my schedule
                </Label>
              </div>
            </div> */}
            </CardContent>
          </Card>

          {/* Weekly Schedule */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Disponibilidade
              </CardTitle>
              <CardDescription>Selecione seus 2 dias disponíveis e defina intervalos de tempo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {formData.weeklySchedule.map((schedule, dayIndex) => (
                  <div key={dayIndex} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Checkbox
                          checked={schedule.available}
                          onCheckedChange={(checked) => handleDayToggle(dayIndex, checked as boolean)}
                        />

                        {/* ✅ Day select with full week, no duplicates */}
                        <Select value={schedule.day} onValueChange={(value) => handleDayChange(dayIndex, value)}>
                          <SelectTrigger className="w-[150px]">
                            <SelectValue placeholder="Select a day" />
                          </SelectTrigger>
                          <SelectContent>
                            {[
                              "Segunda-feira",
                              "Terça-feira",
                              "Quarta-feira",
                              "Quinta-feira",
                              "Sexta-feira",
                            ].map((day) => (
                              <SelectItem
                                key={day}
                                value={day}
                                disabled={formData.weeklySchedule.some((s, i) => i !== dayIndex && s.day === day)}
                              >
                                {day}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        {schedule.available && (
                          <Badge variant="secondary">
                            {schedule.timeSlots.length} slot{schedule.timeSlots.length !== 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>

                      {schedule.available && (
                        <Button type="button" variant="outline" size="sm" onClick={() => addTimeSlot(dayIndex)}>
                          Add Time Slot
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
                              onChange={(e) =>
                                handleTimeSlotChange(dayIndex, slotIndex, "start", e.target.value)
                              }
                              className="w-32"
                            />
                            <span className="text-gray-500">to</span>
                            <Input
                              type="time"
                              value={slot.end}
                              onChange={(e) =>
                                handleTimeSlotChange(dayIndex, slotIndex, "end", e.target.value)
                              }
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

          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Enviar Plano de Disciplinas
              </CardTitle>
              <CardDescription>Envie um arquivo que tenha das disciplinas e os horarios do seu curso</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300"
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
                        <p className="text-sm text-gray-500">
                          {(formData.uploadedFile.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <Button type="button" variant="outline" size="sm" onClick={removeUploadedFile}>
                      Remove File
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                    <div>
                      <p className="text-lg font-medium">Arraste e solte seu arquivo</p>
                      <p className="text-gray-500">ou clique em escolher arquivo</p>
                    </div>
                    <Button type="button" variant="outline" onClick={() => fileInputRef.current?.click()}>
                      Escolher Arquivo
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.json,.txt,.xlsx,.pdf"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </div>
                )}
              </div>

              <div className="mt-4 text-sm text-gray-600">
                <p className="font-medium mb-2">Supported formats:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>CSV: subject_name, schedule_time, credits, difficulty</li>
                  <li>JSON: Array of subject objects</li>
                  <li>Excel: Structured subject data</li>
                </ul>
              </div>

              {/* Display uploaded subjects */}
              {uploadedSubjects.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Uploaded Subjects ({uploadedSubjects.length})</h4>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {uploadedSubjects.map((subject, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium">{subject.name}</span>
                        <div className="flex gap-2 text-sm text-gray-600">
                          <span>{subject.schedule}</span>
                          <Badge variant="outline">{subject.credits} credits</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Additional Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Additional Preferences
              </CardTitle>
              <CardDescription>Any additional notes or specific requirements</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder=""
                value={formData.additionalNotes}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, additionalNotes: e.target.value }))
                }
                rows={4}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Status Messages */}
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
                Preferences submitted successfully! We'll process your request and get back to you soon.
              </AlertDescription>
            </Alert>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <Button type="submit" size="lg" disabled={isSubmitting} className="w-full md:w-auto px-8">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing Preferences...
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
"""
CHATGPT INTEGRATION MODULE
=========================
This module provides AI-powered subject advisory services using OpenAI's ChatGPT.
It integrates with the student database to provide personalized recommendations,
subject analysis, career guidance, and study planning.

Key Features:
- Personalized subject recommendations based on student profile
- Subject compatibility analysis
- Career pathway guidance
- Study plan generation
- Integration with existing CRUD operations
- Comprehensive error handling

Usage:
    from chatgpt_integration import ChatGPTSubjectAdvisor
    advisor = ChatGPTSubjectAdvisor(api_key)
    recommendations = advisor.get_subject_recommendations(student_id)
"""

from openai import OpenAI

# backend/main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI()

# Allow your React frontend to access the API
origins = [
    "http://localhost:3000",  # your React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],   # ⚠️ não use em produção
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Pydantic models
class TimeSlot(BaseModel):
    start: str
    end: str

class DaySchedule(BaseModel):
    day: str
    available: bool
    timeSlots: List[TimeSlot]

class UploadedSubject(BaseModel):
    name: str
    schedule: str
    credits: int
    difficulty: int

class FormData(BaseModel):
    subjectCount: int
    preferenceStrategy: str
    prioritizeDependencies: bool
    includeSaturday: bool
    weeklySchedule: List[DaySchedule]
    additionalNotes: Optional[str] = ""
    uploadedSubjects: List[UploadedSubject]
    totalAvailableHours: float

# Endpoint to receive form data
@app.post("/submit-preferences")
async def submit_preferences(form_data: FormData):
    # Example: print data to console
    subject_count = form_data.subjectCount
    strategy = form_data.preferenceStrategy
    prioritize = form_data.prioritizeDependencies
    saturday = form_data.includeSaturday
    notes = form_data.additionalNotes
    total_hours = form_data.totalAvailableHours
    print(form_data.model_dump())
    # for day in form_data.weeklySchedule:
    #     print(f"Day: {day.day}, Available: {day.available}")
    #     for slot in day.timeSlots:
    #         print(f"  Slot from {slot.start} to {slot.end}")

    #     client = OpenAI(
    #     api_key="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"
    #     )

    #     response = client.responses.create(
    #     model="gpt-4o-mini",
    #     input=json.dumps(form_data.model_dump(), indent=2),
    #     store=True,
    #     )

        # print(response.output_text);
    
    return {"success": True, "message": "Preferences submitted successfully"}
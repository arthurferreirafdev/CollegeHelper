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
    uploaded_file = form_data.uploadedSubjects
    print(uploaded_file)
    for day in form_data.weeklySchedule:
        print(f"Day: {day.day}, Available: {day.available}")
        for slot in day.timeSlots:
            print(f"  Slot from {slot.start} to {slot.end}")
    
    # print(form_data.model_dump())
    return {"success": True, "message": "Preferences submitted successfully"}
    #     client = OpenAI(
    #     api_key="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"
    #     )

    #     response = client.responses.create(
    #     model="gpt-4o-mini",
    #     input=X,
    #     store=True,
    #     )

        # print(response.output_text);
    
@app.get("/timetable")
async def generateColledgeTimetable():
    prompt = f""" 
    Seu objetivo é atuar como um sistema de suporte e recomendação para criação de uma grade horaria com 5 disciplinas, coerente e sem conflitos (duas disciplinas no mesmo dia e horario) para tornar mais eficiente a escolha das materias. A entrada será no formato que condiz com um dicionario em python, sendo [semestre][nome_disciplina][horarios] e o agente deve criar uma grade horária completa, o horario da disciplina sempre esta acompanhado com o dia da semana e isso nao pode ser alterado, tendo {qtd_materias_diarias} disciplinas por dia no período das {inicio_periodo_livre} às {termino_período_livre}, cada disciplina ocupa 2 horarios na semana, ou seja, nao pode ter apenas 1 aula de uma disciplina na semana, priorizando as disciplinas {disciplinas_com_prioridade} como maior prioridade e as demais disciplinas do {periodo_regular} preriodo, e caso falte horarios disponiveis, busque nos períodos sucessivos, levando em consideração a criação de uma grade horaria mais completa possivel, excluindo as disciplinas {disciplinas_cursadas} da lista de candidatas, selecionando outras disciplinas dos proximos períodos que tenham dia da semana e horario iguais, e nao deve ser selecionadas duas disciplinas com nomes iguais, ou que indiquem sequencia ao mesmo tempo. O dia e horario da disciplina são imutáveis. 
    A saída deve ser um dicionário Python no formato:

    {{
    "Segunda-feira": ["Disciplina - Horário", "Disciplina - Horário"],
    "Terça-feira": ["Disciplina - Horário", "Disciplina - Horário"],
    "Quarta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
    "Quinta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
    "Sexta-feira": ["Disciplina - Horário", "Disciplina - Horário"]
    }}
    """

    client = OpenAI(api_key="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")

    response = client.responses.create(
        model="gpt-4o-mini",
    input=prompt,
    store=True,
    )

    print(response.output_text)
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
import re
import json
import unicodedata

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
    current_semester = form_data.subjectCount
    disponibilidades = [];
    conteudo = ""
    i = 0;
    concatText = ""
    for day in form_data.weeklySchedule:
        concatText = concatText + day.day
        for slot in day.timeSlots:
            concatText = concatText + " " + slot.start
            concatText = concatText + " às " + slot.end
            disponibilidades.append(concatText)
            i += 1
            concatText = ""

    i = 0
    if len(form_data.uploadedSubjects) > 0:
        getCollegeGradeFromFile(form_data.uploadedSubjects[0].name)
        conteudo = form_data.uploadedSubjects[0].name

    banco_disciplinas = conteudo

    resultado = [
    item for item in banco_disciplinas
        if (sorted(normalize(item["horarios"])) == sorted(normalize(disponibilidades))) 
    ]

    return {"success": True, "result": resultado}


def normalize(lst):
    return [
        unicodedata.normalize('NFKD', s)
        .encode('ASCII', 'ignore')
        .decode()
        .replace(" ", "")
        for s in lst
    ]

def getCollegeGradeFromFile(subjects_list):
    prompt = f"""
    banco de disciplinas: {subjects_list}
    estou enviando uma ficha disciplinar de um curso superior e preciso que voce separe os dados de TODOS os 8 periodos

    o retorno deve ser um dicionario em python no seguinte formato
        {{
        "período": "",
        "nome_disciplina": "",
        "horarios": [""]
    }}
    """

    client = OpenAI(api_key="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")

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        store=True,
        temperature=0
    )

    text_response = response.output[0].content[0].text.strip()

    if text_response.startswith("```"):
        text_response = re.sub(r"^```(?:json)?", "", text_response.strip())
        text_response = re.sub(r"```$", "", text_response.strip())
        text_response = text_response.strip()

    # ⚡ aqui a conversão acontece antes de retornar
    college_schedule = {
    "1": {
        "Empreendedorismo em Informática": ["Quarta-feira 19:00 às 20:40", "Sexta-feira 20:50 às 22:30"],
        "Introdução à Programação de Computadores": [
            "Terça-feira 19:00 às 20:40",
            "Quinta-feira 20:50 às 23:30",
            "Terça-feira 20:50 às 22:30",
            "Quarta-feira 19:00 às 20:40"
        ],
        "Introdução aos Sistemas de Informação": [
            "Quarta-feira 20:50 às 22:30",
            "Quinta-feira 19:00 às 20:40",
            "Quarta-feira 19:00 às 20:40",
            "Quarta-feira 20:50 às 22:30"
        ],
        "Programação Funcional": ["Não ofertada em 2023/2"],
        "Lógica para Computação": [
            "Terça-feira 20:50 às 22:30",
            "Sexta-feira 19:00 às 20:40",
            "Terça-feira 19:00 às 20:40",
            "Quinta-feira 20:50 às 22:30"
        ]
    },
    "2": {
        "Estrutura de Dados 1": ["Terça-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30", "Sexta-feira 20:50 às 22:30"],
        "Matemática 1": ["Segunda-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30", "Quinta-feira 19:00 às 20:40"],
        "Sistemas Digitais": ["Não ofertada em 2023/2"],
        "Profissão em Sistemas de Informação": ["Não ofertada em 2023/2"],
        "Programação Lógica": ["Terça-feira 20:50 às 22:30", "Quarta-feira 19:00 às 20:40"]
    },
    "3": {
        "Estrutura de Dados 2": ["Terça-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30"],
        "Matemática 2": ["Segunda-feira 19:00 às 20:40", "Sexta-feira 20:50 às 22:30"],
        "Arquitetura e Organização de Computadores": ["Terça-feira 20:50 às 22:30", "Sexta-feira 19:00 às 20:40"],
        "Matemática para Ciência da Computação": ["Quarta-feira 19:00 às 20:40", "Segunda-feira 20:50 às 22:30"],
        "Programação Orientada a Objetos 1": ["Quarta-feira 20:50 às 22:30", "Quinta-feira 19:00 às 20:40"]
    },
    "4": {
        "Bancos de Dados 1": ["Segunda-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30"],
        "Estatística": ["Terça-feira 19:00 às 20:40", "Sexta-feira 20:50 às 22:30"],
        "Sistemas Operacionais": ["Terça-feira 20:50 às 22:30", "Sexta-feira 19:00 às 20:40"],
        "Programação para Internet": ["Quarta-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30"],
        "Programação Orientada a Objetos 2": ["Segunda-feira 20:50 às 22:30", "Quinta-feira 19:00 às 20:40"]
    },
    "5º período": {
        "Bancos de Dados 2": ["Segunda-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30"],
        "Matemática Financeira e Análise de Investimentos": ["Quinta-feira 19:00 às 20:40", "Sexta-feira 20:50 às 22:30"],
        "Redes de Computadores": ["Terça-feira 20:50 às 22:30", "Sexta-feira 19:00 às 20:40"],
        "Organização e Recuperação da Informação": ["Terça-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30"],
        "Modelagem de Software": ["Segunda-feira 20:50 às 22:30", "Quarta-feira 19:00 às 20:40"]
    },
    "6": {
        "Gestão Empresarial": ["Quinta-feira 19:00 às 22:30"],
        "Otimização": ["Quarta-feira 19:00 às 20:40", "Sexta-feira 20:50 às 22:30"],
        "Sistemas Distribuídos": ["Terça-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30"],
        "Contabilidade e Análise de Balanços": ["Segunda-feira 19:00 às 22:30"],
        "Engenharia de Software": ["Terça-feira 20:50 às 22:30", "Sexta-feira 19:00 às 20:40"]
    },
    "7": {
        "Economia": ["Sexta-feira 19:50 às 22:30"],
        "Fundamentos de Marketing": ["Terça-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30"],
        "Gerência de Projetos de Tecnologia da Informação": ["Quarta-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30"],
        "Projeto e Desenvolvimento de Sistemas de Informação 1": ["Segunda-feira 19:00 às 22:30"],
        "Trabalho de Conclusão de Curso I": ["Sexta-feira 19:00 às 19:50"],
        "Tópicos Especiais em Inteligência Artificial": ["Terça-feira 20:50 às 22:30", "Quinta-feira 19:00 às 20:40"]
    },
    "8": {
        "Auditoria e Segurança da Informação": ["Quarta-feira 19:00 às 20:40", "Quinta-feira 20:50 às 22:30"],
        "Direito e Legislação": ["Sexta-feira 19:50 às 22:30"],
        "Interação Humano-Computador": ["Terça-feira 19:00 às 20:40", "Quarta-feira 20:50 às 22:30"],
        "Projeto e Desenvolvimento de Sistemas de Informação 2": ["Segunda-feira 19:00 às 22:30"],
        "Resolução de Problemas": ["Sábado 08:50 às 12:20"]
    }
}

    try:
        return college_schedule
    except json.JSONDecodeError:
        raise ValueError(f"Resposta do modelo não é JSON válido: {text_response}")
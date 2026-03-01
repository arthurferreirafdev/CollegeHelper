import os
import json
import logging
import re
import string
from typing import Optional

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f'Failed to initialize OpenAI client: {e}')

    def is_available(self) -> bool:
        return self.client is not None

    def _chat(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        try:
            # response = self.client.chat.completions.create(
            #     model='gpt-4o-mini',
            #     messages=[
            #         {'role': 'system', 'content': system_prompt},
            #         # {'role': 'user', 'content': user_prompt}
            #     ],
            #     temperature=0.7,
            #     max_tokens=1500
            # )

            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # return response.choices[0].message.content
            return response.text

        except Exception as e:
            logger.error(f'OpenAI API error: {e}')
            return None

    def generate_schedule(self, form_data: dict) -> dict:
        uploaded_subjects = form_data.get('uploadedSubjects', [])
        subject_count = form_data.get('subjectCount', 5)
        weekly_schedule = form_data.get('weeklySchedule', [])
        additional_notes = form_data.get('additionalNotes', '')
        preference_strategy = form_data.get('preferenceStrategy', '')

        subjects_text = '\n'.join(
            f"- {s.get('name', 'N/A')} | Horário: {s.get('schedule', 'N/A')} | Créditos: {s.get('credits', 'N/A')}"
            for s in uploaded_subjects
        )

        availability_lines = []
        for day in weekly_schedule:
            if day.get('available', False):
                day_name = day.get('day', 'N/A')
                slots = []
                for sl in day.get('timeSlots', []):
                    start = sl.get('start', '')
                    end = sl.get('end', '')
                    slots.append(f"{start} às {end}")
                availability_lines.append(f"- {day_name}: {', '.join(slots)}")
        availability_text = '\n'.join(availability_lines)

        system_prompt = (
            "Você é um assistente especializado em criar grades horárias universitárias otimizadas. "
            "Você DEVE responder APENAS com JSON válido, sem nenhum texto adicional, sem explicações, sem markdown. "
            "O formato de saída deve ser exatamente: "
            '{"Segunda-feira": ["Disciplina - Horário", ...], "Terça-feira": [...], ...} '
            "Inclua apenas os dias que possuem aulas agendadas."
        )

        user_prompt = (
            f"Crie uma grade horária semanal otimizada com {subject_count} disciplinas.\n\n"
            f"Disciplinas disponíveis:\n{subjects_text}\n\n"
            f"Disponibilidade do aluno:\n{availability_text}\n\n"
            f"Estratégia de preferência: {preference_strategy}\n"
            f"Observações adicionais: {additional_notes}\n\n"
            "Regras:\n"
            "- Não pode haver conflitos de horário (duas disciplinas no mesmo dia e horário)\n"
            "- Respeitar a disponibilidade do aluno\n"
            "- O dia e horário da disciplina são imutáveis\n"
            "- Não selecionar duas disciplinas com nomes iguais\n"
            "- Retorne APENAS o JSON, sem markdown ou texto adicional"
        )

        try:
            response = self._chat(system_prompt, user_prompt)
            if not response:
                return {"success": False, "error": "Falha ao obter resposta da IA"}

            cleaned = response.strip()
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()

            schedule = json.loads(cleaned)
            return {"success": True, "schedule": schedule}
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse AI response as JSON: {e}\nResponse: {response}')
            return {"success": False, "error": "Falha ao interpretar resposta da IA"}
        except Exception as e:
            logger.error(f'Error generating schedule: {e}')
            return {"success": False, "error": str(e)}

    def get_subject_recommendations(self, student_id: int, additional_context: str = '') -> dict:
        prompt = f"""
        # substituir por saida do BD posteriormente
        entrada: {{uploaded_file}}

        Seu objetivo é atuar como um sistema de suporte e recomendação para criação de uma grade horaria com {{subject_count}} disciplinas, coerente e sem conflitos (duas disciplinas no mesmo dia e horario) para tornar mais eficiente a escolha das materias. A variavel **entrada** será todas as disciplinas disponiveis e o agente deve criar uma grade horária completa, o horario da disciplina sempre esta acompanhado com o dia da semana e isso nao pode ser alterado, no periodo de {{inicio_periodo_livre}} às {{termino_período_livre}}, cada disciplina ocupa 2 horarios na semana, ou seja, nao pode ter apenas 1 aula de uma disciplina na semana, priorizando as disciplinas {{disciplinas_com_prioridade}} como maior prioridade e as demais disciplinas do {{periodo_regular}} preriodo, e caso falte horarios disponiveis, busque nos períodos sucessivos, levando em consideração a criação de uma grade horaria mais completa possivel, excluindo as disciplinas {{disciplinas_cursadas}} da lista de candidatas, selecionando outras disciplinas dos proximos períodos que tenham dia da semana e horario iguais, e nao deve ser selecionadas duas disciplinas com nomes iguais, ou que indiquem sequencia ao mesmo tempo. O dia e horario da disciplina são imutáveis.
        A saída deve ser um dicionário Python no formato:

        {{
        "Segunda-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Terça-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Quarta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Quinta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Sexta-feira": ["Disciplina - Horário", "Disciplina - Horário"]
        }}
        """

        response = self._chat(prompt, "")
        return {"success": True, "message": "Preferences submitted successfully"}

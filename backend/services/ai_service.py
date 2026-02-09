import os
import json
import logging
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
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f'OpenAI API error: {e}')
            return None

    def get_subject_recommendations(self, student_id: int, additional_context: str = '') -> dict:
        from backend.models.student import StudentRepository
        from backend.models.preference import PreferenceRepository

        student = StudentRepository.find_by_id(student_id)
        preferences = PreferenceRepository.get_by_student(student_id)

        if not student:
            return {'success': False, 'error': 'Student not found'}

        pref_names = [p['subject_name'] for p in preferences] if preferences else []
        system_prompt = 'You are an academic advisor helping students choose subjects. Respond in JSON format with a "recommendations" array.'
        user_prompt = f"""Student: {student['first_name']} {student['last_name']}, Grade {student.get('grade_level', 'N/A')}.
Current interests: {', '.join(pref_names) if pref_names else 'None specified'}.
Additional context: {additional_context or 'None'}.
Suggest 5 subjects with reasons."""

        result = self._chat(system_prompt, user_prompt)
        if result:
            return {'success': True, 'recommendations': result}
        return {'success': False, 'error': 'Failed to get recommendations'}

    def analyze_subject_fit(self, student_id: int, subject_name: str) -> dict:
        from backend.models.student import StudentRepository
        student = StudentRepository.find_by_id(student_id)
        if not student:
            return {'success': False, 'error': 'Student not found'}

        system_prompt = 'You are an academic advisor. Analyze how well a subject fits a student. Respond in JSON.'
        user_prompt = f"""Student: {student['first_name']} {student['last_name']}, Grade {student.get('grade_level', 'N/A')}.
Subject: {subject_name}.
Provide fit analysis, pros, cons, and a score from 1-10."""

        result = self._chat(system_prompt, user_prompt)
        if result:
            return {'success': True, 'analysis': result}
        return {'success': False, 'error': 'Failed to analyze subject fit'}

    def get_career_advice(self, student_id: int, career_interest: str) -> dict:
        from backend.models.student import StudentRepository
        student = StudentRepository.find_by_id(student_id)
        if not student:
            return {'success': False, 'error': 'Student not found'}

        system_prompt = 'You are a career counselor. Provide career pathway advice. Respond in JSON.'
        user_prompt = f"""Student: {student['first_name']} {student['last_name']}, Grade {student.get('grade_level', 'N/A')}.
Career interest: {career_interest}.
Suggest relevant subjects, skills to develop, and career pathways."""

        result = self._chat(system_prompt, user_prompt)
        if result:
            return {'success': True, 'advice': result}
        return {'success': False, 'error': 'Failed to get career advice'}

    def generate_study_plan(self, student_id: int, selected_subjects: list, semester: str = 'Current Semester') -> dict:
        from backend.models.student import StudentRepository
        student = StudentRepository.find_by_id(student_id)
        if not student:
            return {'success': False, 'error': 'Student not found'}

        system_prompt = 'You are an academic planner. Create a study plan. Respond in JSON.'
        user_prompt = f"""Student: {student['first_name']} {student['last_name']}, Grade {student.get('grade_level', 'N/A')}.
Selected subjects: {', '.join(selected_subjects)}.
Semester: {semester}.
Create a weekly study plan with time allocation and tips."""

        result = self._chat(system_prompt, user_prompt)
        if result:
            return {'success': True, 'study_plan': result}
        return {'success': False, 'error': 'Failed to generate study plan'}

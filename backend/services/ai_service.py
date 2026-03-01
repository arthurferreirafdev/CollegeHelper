import os
import json
import logging
import string
from typing import Optional

from openai import chat

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
                    # {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # return response.choices[0].message.content
            return response.text

        except Exception as e:
            logger.error(f'OpenAI API error: {e}')
            return None

    def get_subject_recommendations(self, student_id: string, additional_context: str = '') -> dict:
        prompt = f"""
        # substituir por saida do BD posteriormente
        entrada: uploaded_file

        Seu objetivo é atuar como um sistema de suporte e recomendação para criação de uma grade horaria com subject_count disciplinas, coerente e sem conflitos (duas disciplinas no mesmo dia e horario) para tornar mais eficiente a escolha das materias. A variavel **entrada** será todas as disciplinas disponiveis e o agente deve criar uma grade horária completa, o horario da disciplina sempre esta acompanhado com o dia da semana e isso nao pode ser alterado, no periodo de inicio_periodo_livre às termino_periodo_livre, cada disciplina ocupa 2 horarios na semana, ou seja, nao pode ter apenas 1 aula de uma disciplina na semana, priorizando as disciplinas disciplinas_com_prioridade como maior prioridade e as demais disciplinas do periodo_regular preriodo, e caso falte horarios disponiveis, busque nos períodos sucessivos, levando em consideração a criação de uma grade horaria mais completa possivel, excluindo as disciplinas disciplinas_cursadas da lista de candidatas, selecionando outras disciplinas dos proximos períodos que tenham dia da semana e horario iguais, e nao deve ser selecionadas duas disciplinas com nomes iguais, ou que indiquem sequencia ao mesmo tempo. O dia e horario da disciplina são imutáveis. 
        A saída deve ser um dicionário Python no formato:

        {{
        "Segunda-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Terça-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Quarta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Quinta-feira": ["Disciplina - Horário", "Disciplina - Horário"],
        "Sexta-feira": ["Disciplina - Horário", "Disciplina - Horário"]
        }}
        """


        response = self._chat(prompt, "");
        
        print(response)    
        return {"success": True, "message": "Preferences submitted successfully"}

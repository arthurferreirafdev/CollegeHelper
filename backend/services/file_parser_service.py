import csv
import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FileParserService:
    SUPPORTED_FORMATS = ['.csv', '.json', '.txt']

    def parse_file(self, file_path: str, file_content: str = None) -> Dict[str, Any]:
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                return {'success': False, 'error': f'Unsupported format: {ext}', 'supported_formats': self.SUPPORTED_FORMATS}

            if ext == '.csv':
                subjects = self._parse_csv(file_path, file_content)
            elif ext == '.json':
                subjects = self._parse_json(file_path, file_content)
            elif ext == '.txt':
                subjects = self._parse_text(file_path, file_content)
            else:
                return {'success': False, 'error': f'No parser for {ext}'}

            validated = self._validate(subjects)
            return {'success': True, 'subjects': validated, 'count': len(validated), 'file_type': ext}
        except Exception as e:
            logger.error(f'File parse error: {e}')
            return {'success': False, 'error': str(e)}

    def _parse_csv(self, path: str, content: str = None) -> List[Dict]:
        subjects = []
        if content:
            lines = content.strip().split('\n')
            reader = csv.DictReader(lines)
            for row in reader:
                subj = {
                    'name': row.get('name', '').strip(),
                    'schedule': row.get('schedule', '').strip(),
                    'credits': self._safe_int(row.get('credits', 3), 3),
                    'difficulty': self._safe_int(row.get('difficulty', 3), 3),
                    'category': row.get('category', 'General').strip(),
                }
                if subj['name'] and subj['schedule']:
                    subjects.append(subj)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subj = {
                        'name': row.get('name', '').strip(),
                        'schedule': row.get('schedule', '').strip(),
                        'credits': self._safe_int(row.get('credits', 3), 3),
                        'difficulty': self._safe_int(row.get('difficulty', 3), 3),
                        'category': row.get('category', 'General').strip(),
                    }
                    if subj['name'] and subj['schedule']:
                        subjects.append(subj)
        return subjects

    def _parse_json(self, path: str, content: str = None) -> List[Dict]:
        if content:
            data = json.loads(content)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        subjects = []
        for item in data:
            if not isinstance(item, dict):
                continue
            subj = {
                'name': item.get('name', '').strip(),
                'schedule': item.get('schedule', '').strip(),
                'credits': self._safe_int(item.get('credits', 3), 3),
                'difficulty': self._safe_int(item.get('difficulty', 3), 3),
                'category': item.get('category', 'General').strip(),
            }
            if subj['name'] and subj['schedule']:
                subjects.append(subj)
        return subjects

    def _parse_text(self, path: str, content: str = None) -> List[Dict]:
        if content:
            text = content
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        subjects = []
        for block in text.split('---'):
            block = block.strip()
            if not block:
                continue
            subj = {'name': '', 'schedule': '', 'credits': 3, 'difficulty': 3, 'category': 'General'}
            for line in block.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip().lower()
                    val = val.strip()
                    if key in ('subject', 'name'):
                        subj['name'] = val
                    elif key == 'schedule':
                        subj['schedule'] = val
                    elif key == 'credits':
                        subj['credits'] = self._safe_int(val, 3)
                    elif key == 'difficulty':
                        subj['difficulty'] = self._safe_int(val, 3)
                    elif key == 'category':
                        subj['category'] = val
            if subj['name'] and subj['schedule']:
                subjects.append(subj)
        return subjects

    def _validate(self, subjects: List[Dict]) -> List[Dict]:
        result = []
        for s in subjects:
            if not s.get('name') or not s.get('schedule'):
                continue
            s['credits'] = max(1, min(10, s.get('credits', 3)))
            s['difficulty'] = max(1, min(5, s.get('difficulty', 3)))
            result.append(s)
        return result

    def _safe_int(self, val, default: int) -> int:
        try:
            return int(float(str(val).strip()))
        except (ValueError, TypeError):
            return default

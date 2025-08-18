"""
FILE PARSER MODULE
=================
This module handles parsing of uploaded subject files in various formats.
It supports CSV, JSON, Excel, and text files containing subject information
and schedules.

Supported formats:
- CSV: subject_name, schedule, credits, difficulty, category, prerequisites
- JSON: Array of subject objects
- Excel: Structured subject data in spreadsheet format
- TXT: Simple text format with structured data

Usage:
    from file_parser import FileParser
    parser = FileParser()
    subjects = parser.parse_file(file_path, file_type)
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

class FileParser:
    """
    Handles parsing of various file formats containing subject information
    """
    
    def __init__(self):
        """Initialize the file parser"""
        self.supported_formats = ['.csv', '.json', '.xlsx', '.xls', '.txt']
        self.required_fields = ['name', 'schedule']
        self.optional_fields = ['credits', 'difficulty', 'category', 'prerequisites', 'teacher', 'description']
    
    def parse_file(self, file_path: str, file_content: str = None) -> Dict[str, Any]:
        """
        Parse uploaded file and extract subject information
        
        Args:
            file_path: Path to the uploaded file
            file_content: File content as string (for web uploads)
            
        Returns:
            Dict containing parsed subjects and metadata
        """
        try:
            # Determine file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}",
                    "supported_formats": self.supported_formats
                }
            
            # Parse based on file type
            if file_extension == '.csv':
                subjects = self._parse_csv(file_path, file_content)
            elif file_extension == '.json':
                subjects = self._parse_json(file_path, file_content)
            elif file_extension in ['.xlsx', '.xls']:
                subjects = self._parse_excel(file_path)
            elif file_extension == '.txt':
                subjects = self._parse_text(file_path, file_content)
            else:
                return {
                    "success": False,
                    "error": f"Parser not implemented for {file_extension}"
                }
            
            # Validate parsed subjects
            validated_subjects = self._validate_subjects(subjects)
            
            return {
                "success": True,
                "subjects": validated_subjects,
                "count": len(validated_subjects),
                "timestamp": datetime.now().isoformat(),
                "file_type": file_extension
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse file: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_csv(self, file_path: str, file_content: str = None) -> List[Dict[str, Any]]:
        """
        Parse CSV file containing subject information
        
        Expected format:
        name,schedule,credits,difficulty,category,prerequisites,teacher,description
        
        Args:
            file_path: Path to CSV file
            file_content: CSV content as string
            
        Returns:
            List of subject dictionaries
        """
        subjects = []
        
        try:
            if file_content:
                # Parse from string content
                lines = file_content.strip().split('\n')
                reader = csv.DictReader(lines)
            else:
                # Parse from file
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
            
            for row in reader:
                # Clean and process each row
                subject = {}
                
                # Required fields
                subject['name'] = row.get('name', '').strip()
                subject['schedule'] = row.get('schedule', '').strip()
                
                # Optional fields with defaults
                subject['credits'] = self._safe_int(row.get('credits', '3'), 3)
                subject['difficulty'] = self._safe_int(row.get('difficulty', '3'), 3)
                subject['category'] = row.get('category', 'General').strip()
                subject['prerequisites'] = self._parse_prerequisites_field(row.get('prerequisites', ''))
                subject['teacher'] = row.get('teacher', '').strip()
                subject['description'] = row.get('description', '').strip()
                
                # Only add if required fields are present
                if subject['name'] and subject['schedule']:
                    subjects.append(subject)
                    
        except Exception as e:
            raise Exception(f"CSV parsing error: {str(e)}")
        
        return subjects
    
    def _parse_json(self, file_path: str, file_content: str = None) -> List[Dict[str, Any]]:
        """
        Parse JSON file containing subject information
        
        Expected format:
        [
            {
                "name": "Mathematics",
                "schedule": "Mon 09:00-11:00, Wed 14:00-16:00",
                "credits": 4,
                "difficulty": 4,
                "category": "STEM",
                "prerequisites": ["Basic Algebra"],
                "teacher": "Dr. Smith",
                "description": "Advanced mathematics course"
            }
        ]
        
        Args:
            file_path: Path to JSON file
            file_content: JSON content as string
            
        Returns:
            List of subject dictionaries
        """
        try:
            if file_content:
                data = json.loads(file_content)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            
            subjects = []
            
            # Handle both single object and array formats
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise Exception("JSON must contain an array of subjects or a single subject object")
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                subject = {
                    'name': item.get('name', '').strip(),
                    'schedule': item.get('schedule', '').strip(),
                    'credits': self._safe_int(item.get('credits', 3), 3),
                    'difficulty': self._safe_int(item.get('difficulty', 3), 3),
                    'category': item.get('category', 'General').strip(),
                    'prerequisites': self._normalize_prerequisites(item.get('prerequisites', [])),
                    'teacher': item.get('teacher', '').strip(),
                    'description': item.get('description', '').strip()
                }
                
                # Only add if required fields are present
                if subject['name'] and subject['schedule']:
                    subjects.append(subject)
            
            return subjects
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise Exception(f"JSON parsing error: {str(e)}")
    
    def _parse_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Excel file containing subject information
        
        Expected columns:
        name, schedule, credits, difficulty, category, prerequisites, teacher, description
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List of subject dictionaries
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            subjects = []
            
            for _, row in df.iterrows():
                subject = {
                    'name': str(row.get('name', '')).strip(),
                    'schedule': str(row.get('schedule', '')).strip(),
                    'credits': self._safe_int(row.get('credits', 3), 3),
                    'difficulty': self._safe_int(row.get('difficulty', 3), 3),
                    'category': str(row.get('category', 'General')).strip(),
                    'prerequisites': self._parse_prerequisites_field(str(row.get('prerequisites', ''))),
                    'teacher': str(row.get('teacher', '')).strip(),
                    'description': str(row.get('description', '')).strip()
                }
                
                # Only add if required fields are present
                if subject['name'] and subject['schedule']:
                    subjects.append(subject)
            
            return subjects
            
        except Exception as e:
            raise Exception(f"Excel parsing error: {str(e)}")
    
    def _parse_text(self, file_path: str, file_content: str = None) -> List[Dict[str, Any]]:
        """
        Parse text file with structured subject information
        
        Expected format:
        Subject: Mathematics
        Schedule: Mon 09:00-11:00, Wed 14:00-16:00
        Credits: 4
        Difficulty: 4
        Category: STEM
        Prerequisites: Basic Algebra
        Teacher: Dr. Smith
        Description: Advanced mathematics course
        ---
        
        Args:
            file_path: Path to text file
            file_content: Text content as string
            
        Returns:
            List of subject dictionaries
        """
        try:
            if file_content:
                content = file_content
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            
            subjects = []
            
            # Split by subject separator
            subject_blocks = content.split('---')
            
            for block in subject_blocks:
                block = block.strip()
                if not block:
                    continue
                
                subject = {
                    'name': '',
                    'schedule': '',
                    'credits': 3,
                    'difficulty': 3,
                    'category': 'General',
                    'prerequisites': [],
                    'teacher': '',
                    'description': ''
                }
                
                # Parse each line in the block
                lines = block.split('\n')
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key in ['subject', 'name']:
                            subject['name'] = value
                        elif key == 'schedule':
                            subject['schedule'] = value
                        elif key == 'credits':
                            subject['credits'] = self._safe_int(value, 3)
                        elif key == 'difficulty':
                            subject['difficulty'] = self._safe_int(value, 3)
                        elif key == 'category':
                            subject['category'] = value
                        elif key == 'prerequisites':
                            subject['prerequisites'] = self._parse_prerequisites_field(value)
                        elif key == 'teacher':
                            subject['teacher'] = value
                        elif key == 'description':
                            subject['description'] = value
                
                # Only add if required fields are present
                if subject['name'] and subject['schedule']:
                    subjects.append(subject)
            
            return subjects
            
        except Exception as e:
            raise Exception(f"Text parsing error: {str(e)}")
    
    def _validate_subjects(self, subjects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean parsed subjects
        
        Args:
            subjects: List of parsed subject dictionaries
            
        Returns:
            List of validated subject dictionaries
        """
        validated_subjects = []
        
        for subject in subjects:
            # Validate required fields
            if not subject.get('name') or not subject.get('schedule'):
                continue
            
            # Validate and constrain numeric fields
            subject['credits'] = max(1, min(10, subject.get('credits', 3)))
            subject['difficulty'] = max(1, min(5, subject.get('difficulty', 3)))
            
            # Ensure prerequisites is a list
            if not isinstance(subject.get('prerequisites'), list):
                subject['prerequisites'] = []
            
            # Clean string fields
            for field in ['name', 'category', 'teacher', 'description']:
                if field in subject:
                    subject[field] = str(subject[field]).strip()
            
            # Validate schedule format
            if self._validate_schedule_format(subject['schedule']):
                validated_subjects.append(subject)
        
        return validated_subjects
    
    def _validate_schedule_format(self, schedule: str) -> bool:
        """
        Validate that schedule string is in correct format
        
        Args:
            schedule: Schedule string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not schedule:
            return False
        
        try:
            # Basic validation - should contain day and time
            schedule_parts = schedule.split(',')
            
            for part in schedule_parts:
                part = part.strip()
                if not part:
                    continue
                
                # Should have at least day and time
                tokens = part.split()
                if len(tokens) < 2:
                    return False
                
                # Time should contain a dash
                time_part = tokens[1]
                if '-' not in time_part:
                    return False
                
                # Try to parse time format
                start_str, end_str = time_part.split('-')
                datetime.strptime(start_str.strip(), '%H:%M')
                datetime.strptime(end_str.strip(), '%H:%M')
            
            return True
            
        except Exception:
            return False
    
    def _parse_prerequisites_field(self, prerequisites_str: str) -> List[str]:
        """
        Parse prerequisites field into list of strings
        
        Args:
            prerequisites_str: Prerequisites as string
            
        Returns:
            List of prerequisite names
        """
        if not prerequisites_str or prerequisites_str.strip() == '':
            return []
        
        # Handle different delimiter formats
        prerequisites = []
        for delimiter in [',', ';', '|', '\n']:
            if delimiter in prerequisites_str:
                prerequisites = [p.strip() for p in prerequisites_str.split(delimiter)]
                break
        
        # If no delimiters found, treat as single prerequisite
        if not prerequisites:
            prerequisites = [prerequisites_str.strip()]
        
        # Filter out empty strings
        return [p for p in prerequisites if p]
    
    def _normalize_prerequisites(self, prerequisites: Any) -> List[str]:
        """
        Normalize prerequisites to list format
        
        Args:
            prerequisites: Prerequisites in various formats
            
        Returns:
            List of prerequisite names
        """
        if isinstance(prerequisites, list):
            return [str(p).strip() for p in prerequisites if str(p).strip()]
        elif isinstance(prerequisites, str):
            return self._parse_prerequisites_field(prerequisites)
        else:
            return []
    
    def _safe_int(self, value: Any, default: int) -> int:
        """
        Safely convert value to integer with default fallback
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Integer value or default
        """
        try:
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                return int(float(value.strip()))
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    def get_sample_formats(self) -> Dict[str, str]:
        """
        Get sample file formats for user reference
        
        Returns:
            Dictionary with sample formats for each file type
        """
        return {
            "csv": """name,schedule,credits,difficulty,category,prerequisites,teacher,description
Mathematics,Mon 09:00-11:00 Wed 14:00-16:00,4,4,STEM,Basic Algebra,Dr. Smith,Advanced mathematics course
Physics,Tue 10:00-12:00 Thu 13:00-15:00,4,5,STEM,Mathematics,Prof. Johnson,Fundamental physics principles
English Literature,Mon 13:00-15:00 Fri 09:00-11:00,3,3,Humanities,,Ms. Davis,Analysis of literary works""",
            
            "json": """[
    {
        "name": "Mathematics",
        "schedule": "Mon 09:00-11:00, Wed 14:00-16:00",
        "credits": 4,
        "difficulty": 4,
        "category": "STEM",
        "prerequisites": ["Basic Algebra"],
        "teacher": "Dr. Smith",
        "description": "Advanced mathematics course"
    },
    {
        "name": "Physics",
        "schedule": "Tue 10:00-12:00, Thu 13:00-15:00",
        "credits": 4,
        "difficulty": 5,
        "category": "STEM",
        "prerequisites": ["Mathematics"],
        "teacher": "Prof. Johnson",
        "description": "Fundamental physics principles"
    }
]""",
            
            "text": """Subject: Mathematics
Schedule: Mon 09:00-11:00, Wed 14:00-16:00
Credits: 4
Difficulty: 4
Category: STEM
Prerequisites: Basic Algebra
Teacher: Dr. Smith
Description: Advanced mathematics course
---
Subject: Physics
Schedule: Tue 10:00-12:00, Thu 13:00-15:00
Credits: 4
Difficulty: 5
Category: STEM
Prerequisites: Mathematics
Teacher: Prof. Johnson
Description: Fundamental physics principles
---"""
        }

# Example usage and testing
if __name__ == "__main__":
    print("📄 Testing File Parser")
    print("=" * 40)
    
    parser = FileParser()
    
    # Display sample formats
    print("📋 Sample file formats:")
    samples = parser.get_sample_formats()
    
    for format_type, sample in samples.items():
        print(f"\n{format_type.upper()} Format:")
        print("-" * 20)
        print(sample[:200] + "..." if len(sample) > 200 else sample)
    
    print("\n💡 File Parser is ready for use")
    print("📚 Import this module to parse uploaded subject files")

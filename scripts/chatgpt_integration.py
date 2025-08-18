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

import openai
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from student_crud import StudentCRUD

class ChatGPTSubjectAdvisor:
    """
    AI-powered subject advisor using OpenAI's ChatGPT for personalized academic guidance.
    Integrates with the student database to provide contextual recommendations.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the ChatGPT integration with API key and database connection.
        
        Args:
            api_key (str, optional): OpenAI API key. Uses environment variable if not provided.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize database operations
        self.crud = StudentCRUD()
        
        # Configuration for AI responses
        self.default_model = "gpt-4"
        self.max_tokens = 1200
        self.temperature = 0.7
    
    def get_subject_recommendations(self, student_id: int, additional_context: str = "") -> Dict[str, Any]:
        """
        Generate personalized subject recommendations for a student using AI analysis.
        
        Args:
            student_id (int): Student's unique identifier
            additional_context (str, optional): Additional context about student interests or goals
        
        Returns:
            Dict[str, Any]: AI recommendation response with success status and content
        """
        try:
            # Retrieve student information from database
            student = self.crud.get_student(student_id)
            if not student:
                return {"success": False, "error": "Student not found"}
            
            # Get student's current preferences
            preferences = self.crud.get_student_preferences(student_id)
            
            # Get all available subjects for context
            all_subjects = self.crud.get_all_subjects()
            
            # Build comprehensive context for AI analysis
            context = self._build_recommendation_context(student, preferences, all_subjects, additional_context)
            
            # Generate AI recommendations using ChatGPT
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_recommendation_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            recommendation = response.choices[0].message.content
            
            return {
                "success": True,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "grade_level": student['grade_level'],
                "recommendation": recommendation,
                "timestamp": self._get_timestamp(),
                "context_used": additional_context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate recommendations: {str(e)}"
            }
    
    def analyze_subject_fit(self, student_id: int, subject_name: str) -> Dict[str, Any]:
        """
        Analyze how well a specific subject matches a student's profile and interests.
        
        Args:
            student_id (int): Student's unique identifier
            subject_name (str): Name of the subject to analyze
        
        Returns:
            Dict[str, Any]: Analysis results with compatibility assessment
        """
        try:
            # Retrieve student information
            student = self.crud.get_student(student_id)
            if not student:
                return {"success": False, "error": "Student not found"}
            
            # Get student preferences for context
            preferences = self.crud.get_student_preferences(student_id)
            
            # Find the target subject in the database
            all_subjects = self.crud.get_all_subjects()
            target_subject = next((s for s in all_subjects if s['name'].lower() == subject_name.lower()), None)
            
            if not target_subject:
                return {"success": False, "error": f"Subject '{subject_name}' not found in catalog"}
            
            # Build analysis context
            context = self._build_analysis_context(student, preferences, target_subject)
            
            # Generate AI analysis
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_analysis_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "subject": target_subject['name'],
                "subject_details": target_subject,
                "analysis": analysis,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze subject fit: {str(e)}"
            }
    
    def get_career_pathway_advice(self, student_id: int, career_interest: str) -> Dict[str, Any]:
        """
        Provide career-focused academic guidance for subject selection.
        
        Args:
            student_id (int): Student's unique identifier
            career_interest (str): Student's career interest or goal
        
        Returns:
            Dict[str, Any]: Career pathway advice with subject recommendations
        """
        try:
            # Retrieve student information
            student = self.crud.get_student(student_id)
            if not student:
                return {"success": False, "error": "Student not found"}
            
            # Get current preferences and available subjects
            preferences = self.crud.get_student_preferences(student_id)
            all_subjects = self.crud.get_all_subjects()
            
            # Build career guidance context
            context = self._build_career_context(student, preferences, all_subjects, career_interest)
            
            # Generate career advice using AI
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_career_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            advice = response.choices[0].message.content
            
            return {
                "success": True,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "career_interest": career_interest,
                "advice": advice,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate career advice: {str(e)}"
            }
    
    def generate_study_plan(self, student_id: int, selected_subjects: List[str], semester: str = "Current Semester") -> Dict[str, Any]:
        """
        Generate a personalized study plan for selected subjects.
        
        Args:
            student_id (int): Student's unique identifier
            selected_subjects (List[str]): List of subject names for the study plan
            semester (str, optional): Target semester for the plan
        
        Returns:
            Dict[str, Any]: Comprehensive study plan with schedules and strategies
        """
        try:
            # Retrieve student information
            student = self.crud.get_student(student_id)
            if not student:
                return {"success": False, "error": "Student not found"}
            
            # Get details for selected subjects
            all_subjects = self.crud.get_all_subjects()
            subject_details = []
            
            for subject_name in selected_subjects:
                subject = next((s for s in all_subjects if s['name'].lower() == subject_name.lower()), None)
                if subject:
                    subject_details.append(subject)
            
            if not subject_details:
                return {"success": False, "error": "No valid subjects found for study plan"}
            
            # Build study plan context
            context = self._build_study_plan_context(student, subject_details, semester)
            
            # Generate study plan using AI
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_study_plan_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=1500,
                temperature=0.6
            )
            
            study_plan = response.choices[0].message.content
            
            return {
                "success": True,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "semester": semester,
                "subjects": selected_subjects,
                "subject_count": len(subject_details),
                "study_plan": study_plan,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate study plan: {str(e)}"
            }
    
    # ==========================================
    # CONTEXT BUILDING METHODS
    # ==========================================
    
    def _build_recommendation_context(self, student: Dict, preferences: List[Dict], 
                                    all_subjects: List[Dict], additional_context: str) -> str:
        """
        Build comprehensive context for subject recommendations.
        
        Args:
            student (Dict): Student information
            preferences (List[Dict]): Current student preferences
            all_subjects (List[Dict]): All available subjects
            additional_context (str): Additional context provided by user
        
        Returns:
            str: Formatted context for AI analysis
        """
        context = f"""
STUDENT PROFILE ANALYSIS REQUEST
===============================

Student Information:
- Name: {student['first_name']} {student['last_name']}
- Grade Level: {student['grade_level']}
- Email: {student['email']}
- Account Status: {'Active' if student['is_active'] else 'Inactive'}

Current Subject Preferences:
{self._format_preferences(preferences)}

Available Subject Catalog:
{self._format_available_subjects(all_subjects)}

Additional Context from Student:
{additional_context if additional_context else 'No additional context provided.'}

ANALYSIS REQUEST:
Please provide comprehensive subject recommendations that consider:
1. Student's current grade level and academic progression
2. Existing preferences and interest patterns
3. Balanced curriculum across different subject categories
4. Appropriate difficulty progression
5. Prerequisite requirements and logical sequencing
6. Potential career pathway alignment
7. Academic skill development opportunities

Provide specific, actionable recommendations with clear reasoning for each suggestion.
        """
        
        return context.strip()
    
    def _build_analysis_context(self, student: Dict, preferences: List[Dict], target_subject: Dict) -> str:
        """
        Build context for individual subject compatibility analysis.
        
        Args:
            student (Dict): Student information
            preferences (List[Dict]): Student's current preferences
            target_subject (Dict): Subject to analyze
        
        Returns:
            str: Formatted context for subject analysis
        """
        context = f"""
SUBJECT COMPATIBILITY ANALYSIS REQUEST
====================================

Student Profile:
- Name: {student['first_name']} {student['last_name']}
- Grade Level: {student['grade_level']}

Current Academic Interests:
{self._format_preferences(preferences)}

Subject to Analyze:
- Name: {target_subject['name']}
- Code: {target_subject.get('code', 'N/A')}
- Category: {target_subject['category']}
- Difficulty Level: {target_subject['difficulty_level']}/5
- Credits: {target_subject['credits']}
- Description: {target_subject.get('description', 'No description available')}
- Prerequisites: {target_subject.get('prerequisites', 'None specified')}
- Teacher: {target_subject.get('teacher_name', 'TBD')}
- Max Students: {target_subject.get('max_students', 'No limit')}

ANALYSIS REQUEST:
Please provide a detailed compatibility assessment including:
1. Compatibility Score (1-10 scale)
2. Alignment with student's current interests
3. Appropriateness for student's grade level
4. Potential benefits and learning outcomes
5. Challenges the student might face
6. Preparation recommendations
7. How this subject fits into a broader academic plan
        """
        
        return context.strip()
    
    def _build_career_context(self, student: Dict, preferences: List[Dict], 
                            all_subjects: List[Dict], career_interest: str) -> str:
        """
        Build context for career-focused academic guidance.
        
        Args:
            student (Dict): Student information
            preferences (List[Dict]): Current preferences
            all_subjects (List[Dict]): Available subjects
            career_interest (str): Target career field
        
        Returns:
            str: Formatted context for career guidance
        """
        context = f"""
CAREER PATHWAY GUIDANCE REQUEST
==============================

Student Profile:
- Name: {student['first_name']} {student['last_name']}
- Grade Level: {student['grade_level']}

Current Academic Preferences:
{self._format_preferences(preferences)}

Available Subject Options:
{self._format_available_subjects(all_subjects)}

Target Career Interest: {career_interest}

GUIDANCE REQUEST:
Please provide comprehensive career pathway advice including:
1. Essential subjects for this career path
2. Recommended elective subjects that would be beneficial
3. Subject sequencing and timing recommendations
4. Skills to develop outside formal coursework
5. Alternative career paths with similar subject requirements
6. Next steps for career exploration (internships, projects, etc.)
7. Long-term academic planning considerations
8. Industry-specific preparation recommendations
        """
        
        return context.strip()
    
    def _build_study_plan_context(self, student: Dict, subject_details: List[Dict], semester: str) -> str:
        """
        Build context for personalized study plan generation.
        
        Args:
            student (Dict): Student information
            subject_details (List[Dict]): Selected subjects with full details
            semester (str): Target semester
        
        Returns:
            str: Formatted context for study plan generation
        """
        context = f"""
PERSONALIZED STUDY PLAN REQUEST
==============================

Student Information:
- Name: {student['first_name']} {student['last_name']}
- Grade Level: {student['grade_level']}
- Planning Period: {semester}

Selected Subjects for Study Plan:
{self._format_selected_subjects(subject_details)}

STUDY PLAN REQUEST:
Please create a comprehensive, personalized study plan that includes:
1. Weekly time allocation for each subject
2. Subject-specific study strategies and techniques
3. Milestone goals and checkpoints throughout the semester
4. Balance recommendations to prevent academic burnout
5. Resource suggestions (textbooks, online materials, tools)
6. Assessment preparation timeline and strategies
7. Tips for managing workload across multiple subjects
8. Integration opportunities between subjects
9. Flexibility recommendations for schedule adjustments
10. Progress tracking and evaluation methods

Focus on practical, actionable advice that a {student['grade_level']}th grade student can implement effectively.
        """
        
        return context.strip()
    
    # ==========================================
    # FORMATTING HELPER METHODS
    # ==========================================
    
    def _format_preferences(self, preferences: List[Dict]) -> str:
        """
        Format student preferences for AI context.
        
        Args:
            preferences (List[Dict]): List of student preferences
        
        Returns:
            str: Formatted preference information
        """
        if not preferences:
            return "No current subject preferences recorded."
        
        formatted = []
        for pref in preferences:
            priority_text = f" (Priority: {pref['priority']})" if pref['priority'] else ""
            notes_text = f"\n    Notes: {pref['notes']}" if pref['notes'] else ""
            status_text = f" [{pref['status'].title()}]" if pref['status'] != 'interested' else ""
            
            formatted.append(
                f"- {pref['subject_name']} ({pref['category']}): "
                f"Interest Level {pref['interest_level']}/5{priority_text}{status_text}{notes_text}"
            )
        
        return "\n".join(formatted)
    
    def _format_available_subjects(self, subjects: List[Dict]) -> str:
        """
        Format available subjects by category for AI context.
        
        Args:
            subjects (List[Dict]): List of available subjects
        
        Returns:
            str: Formatted subject catalog
        """
        # Group subjects by category
        categories = {}
        for subject in subjects:
            category = subject['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(subject)
        
        formatted = []
        for category, category_subjects in sorted(categories.items()):
            formatted.append(f"\n{category.upper()}:")
            for subject in sorted(category_subjects, key=lambda x: x['name']):
                prereq_text = f" (Prerequisites: {subject['prerequisites']})" if subject['prerequisites'] else ""
                teacher_text = f" - {subject['teacher_name']}" if subject.get('teacher_name') else ""
                
                formatted.append(
                    f"  • {subject['name']} "
                    f"(Difficulty: {subject['difficulty_level']}/5, "
                    f"Credits: {subject['credits']}){prereq_text}{teacher_text}"
                )
        
        return "\n".join(formatted)
    
    def _format_selected_subjects(self, subjects: List[Dict]) -> str:
        """
        Format selected subjects with detailed information.
        
        Args:
            subjects (List[Dict]): List of selected subjects
        
        Returns:
            str: Formatted subject details
        """
        formatted = []
        total_credits = 0
        
        for subject in subjects:
            prereq_text = f"\n    Prerequisites: {subject['prerequisites']}" if subject['prerequisites'] else ""
            teacher_text = f"\n    Teacher: {subject['teacher_name']}" if subject.get('teacher_name') else ""
            
            formatted.append(f"""
{subject['name']} ({subject['category']})
    Code: {subject.get('code', 'N/A')}
    Difficulty Level: {subject['difficulty_level']}/5
    Credits: {subject['credits']}
    Description: {subject.get('description', 'No description available')}{prereq_text}{teacher_text}
            """.strip())
            
            total_credits += subject['credits']
        
        formatted.append(f"\nTotal Credits: {total_credits}")
        return "\n".join(formatted)
    
    # ==========================================
    # SYSTEM PROMPT METHODS
    # ==========================================
    
    def _get_recommendation_system_prompt(self) -> str:
        """
        Get the system prompt for subject recommendations.
        
        Returns:
            str: System prompt for AI recommendations
        """
        return """You are an experienced high school academic advisor specializing in personalized subject selection. 
        
Your expertise includes:
- Understanding high school curriculum requirements and progressions
- Matching student interests with appropriate academic challenges
- Balancing course loads for optimal learning outcomes
- Preparing students for college and career pathways
- Recognizing individual learning styles and preferences

Provide thoughtful, personalized recommendations that:
1. Consider the student's current academic level and interests
2. Suggest a balanced mix of subjects across different categories
3. Explain the reasoning behind each recommendation
4. Account for prerequisite requirements and logical progression
5. Encourage academic growth while being realistic about capabilities
6. Connect subject choices to potential future opportunities

Format your response with clear sections and actionable advice. Be encouraging but honest about challenges."""
    
    def _get_analysis_system_prompt(self) -> str:
        """
        Get the system prompt for subject compatibility analysis.
        
        Returns:
            str: System prompt for subject analysis
        """
        return """You are an academic counselor specializing in subject compatibility analysis for high school students.

Your role is to provide detailed, honest assessments that help students make informed decisions about their course selections.

For each analysis, provide:
1. A clear compatibility score (1-10) with justification
2. Specific reasons supporting your assessment
3. Potential benefits the student would gain
4. Realistic challenges they might encounter
5. Concrete preparation recommendations
6. How this subject fits into their broader academic journey

Be thorough, balanced, and constructive in your analysis. Help students understand both opportunities and challenges."""
    
    def _get_career_system_prompt(self) -> str:
        """
        Get the system prompt for career pathway advice.
        
        Returns:
            str: System prompt for career guidance
        """
        return """You are a career counselor and academic advisor with expertise in connecting high school subject choices to career outcomes.

Your knowledge spans:
- Industry requirements and trends
- Educational pathways to various careers
- Skills development through academic subjects
- Alternative career paths and transferable skills
- Post-secondary education requirements

Provide comprehensive, practical advice that:
1. Identifies essential subjects for the target career
2. Suggests beneficial electives and supplementary learning
3. Outlines logical subject sequencing
4. Recommends skill development outside formal coursework
5. Presents alternative career options with similar foundations
6. Suggests concrete next steps for career exploration

Be realistic about career requirements while encouraging exploration and growth."""
    
    def _get_study_plan_system_prompt(self) -> str:
        """
        Get the system prompt for study plan generation.
        
        Returns:
            str: System prompt for study planning
        """
        return """You are an educational consultant specializing in creating personalized, effective study plans for high school students.

Your expertise includes:
- Time management and scheduling strategies
- Subject-specific study techniques
- Workload balancing and stress management
- Assessment preparation methods
- Learning optimization techniques

Create study plans that are:
1. Realistic and achievable for the student's grade level
2. Balanced to prevent burnout while maximizing learning
3. Specific with actionable steps and timelines
4. Flexible to accommodate individual learning styles
5. Comprehensive covering all aspects of academic success

Focus on practical strategies that students can implement immediately. Include specific time allocations, study techniques, and progress tracking methods."""
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp for response tracking.
        
        Returns:
            str: Formatted timestamp
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the OpenAI API connection and return status.
        
        Returns:
            Dict[str, Any]: Connection test results
        """
        try:
            # Make a simple API call to test connection
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "OpenAI API connection successful",
                "model_used": "gpt-3.5-turbo",
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API connection failed: {str(e)}",
                "timestamp": self._get_timestamp()
            }

# Example usage and testing (only runs when script is executed directly)
if __name__ == "__main__":
    print("🤖 Testing ChatGPT Subject Advisor")
    print("=" * 40)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found")
        print("💡 Set the OPENAI_API_KEY environment variable")
        print("🔗 Get your API key from: https://platform.openai.com/api-keys")
        exit(1)
    
    try:
        # Initialize the advisor
        advisor = ChatGPTSubjectAdvisor(api_key)
        
        # Test API connection
        connection_test = advisor.test_connection()
        if connection_test["success"]:
            print("✅ OpenAI API connection successful")
        else:
            print(f"❌ API connection failed: {connection_test['error']}")
            exit(1)
        
        print("\n💡 ChatGPT Subject Advisor is ready for use")
        print("📚 Import this module to use AI-powered academic guidance")
        
    except Exception as e:
        print(f"❌ Error initializing ChatGPT advisor: {e}")

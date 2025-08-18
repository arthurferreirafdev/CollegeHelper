"""
FLASK API SERVER MODULE
======================
This module provides a REST API server that bridges the Python backend
with the React frontend. It handles authentication, student management,
subject operations, and AI-powered recommendations.

Endpoints:
- POST /api/auth/login - Student authentication
- POST /api/auth/register - Student registration
- GET /api/students/profile - Get student profile
- GET /api/subjects - Get available subjects
- POST /api/preferences - Add/update student preferences
- GET /api/preferences - Get student preferences
- POST /api/ai/recommendations - Get AI recommendations

Usage:
    python scripts/api_server.py
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Import our custom modules
from student_crud import StudentCRUD
from chatgpt_integration import ChatGPTSubjectAdvisor

class StudentSubjectAPI:
    """
    Flask API server for the student subject selection system.
    Provides RESTful endpoints for frontend integration.
    """
    
    def __init__(self):
        """
        Initialize the Flask application with all necessary configurations.
        """
        # Initialize Flask app
        self.app = Flask(__name__)
        
        # Configure CORS for React frontend
        CORS(self.app, origins=["http://localhost:3000"], supports_credentials=True)
        
        # Configure session and JWT
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
        
        # Initialize database operations
        self.crud = StudentCRUD()
        
        # Initialize AI advisor (if API key is available)
        openai_key = os.getenv('OPENAI_API_KEY')
        self.ai_advisor = ChatGPTSubjectAdvisor(openai_key) if openai_key else None
        
        # Register all API routes
        self._register_routes()
    
    def _register_routes(self):
        """
        Register all API endpoints with their corresponding handler methods.
        """
        # Authentication routes
        self.app.route('/api/auth/login', methods=['POST'])(self.login)
        self.app.route('/api/auth/register', methods=['POST'])(self.register)
        self.app.route('/api/auth/logout', methods=['POST'])(self.logout)
        
        # Student profile routes
        self.app.route('/api/students/profile', methods=['GET'])(self.get_profile)
        self.app.route('/api/students/profile', methods=['PUT'])(self.update_profile)
        
        # Subject routes
        self.app.route('/api/subjects', methods=['GET'])(self.get_subjects)
        self.app.route('/api/subjects/<int:subject_id>', methods=['GET'])(self.get_subject)
        self.app.route('/api/subjects/categories', methods=['GET'])(self.get_categories)
        
        # Preference routes
        self.app.route('/api/preferences', methods=['GET'])(self.get_preferences)
        self.app.route('/api/preferences', methods=['POST'])(self.add_preference)
        self.app.route('/api/preferences/<int:preference_id>', methods=['DELETE'])(self.remove_preference)
        
        # AI-powered routes (if OpenAI key is available)
        if self.ai_advisor:
            self.app.route('/api/ai/recommendations', methods=['POST'])(self.get_ai_recommendations)
            self.app.route('/api/ai/subject-analysis', methods=['POST'])(self.analyze_subject_fit)
            self.app.route('/api/ai/career-advice', methods=['POST'])(self.get_career_advice)
            self.app.route('/api/ai/study-plan', methods=['POST'])(self.generate_study_plan)
        
        # Health check route
        self.app.route('/api/health', methods=['GET'])(self.health_check)
    
    # ==========================================
    # AUTHENTICATION ENDPOINTS
    # ==========================================
    
    def login(self):
        """
        Handle student login authentication.
        
        Expected JSON payload:
        {
            "email": "student@school.edu",
            "password": "password123"
        }
        
        Returns:
            JSON response with authentication token or error
        """
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Authenticate student
            student = self.crud.authenticate_student(data['email'], data['password'])
            
            if student:
                # Generate JWT token
                token = self._generate_token(student['id'])
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'student': {
                        'id': student['id'],
                        'email': student['email'],
                        'first_name': student['first_name'],
                        'last_name': student['last_name'],
                        'grade_level': student['grade_level']
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
                
        except Exception as e:
            return jsonify({'error': f'Login failed: {str(e)}'}), 500
    
    def register(self):
        """
        Handle new student registration.
        
        Expected JSON payload:
        {
            "email": "student@school.edu",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "grade_level": 11
        }
        
        Returns:
            JSON response with success status or error
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'password', 'first_name', 'last_name', 'grade_level']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Validate grade level
            if not (9 <= data['grade_level'] <= 12):
                return jsonify({'error': 'Grade level must be between 9 and 12'}), 400
            
            # Create new student
            student_id = self.crud.create_student(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                grade_level=data['grade_level'],
                date_of_birth=data.get('date_of_birth'),
                phone_number=data.get('phone_number'),
                guardian_email=data.get('guardian_email')
            )
            
            if student_id > 0:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'student_id': student_id
                }), 201
            else:
                return jsonify({'error': 'Registration failed - email may already exist'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    
    def logout(self):
        """
        Handle student logout (client-side token removal).
        
        Returns:
            JSON response confirming logout
        """
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    
    # ==========================================
    # STUDENT PROFILE ENDPOINTS
    # ==========================================
    
    @self._require_auth
    def get_profile(self, current_student_id):
        """
        Get the current student's profile information.
        
        Returns:
            JSON response with student profile data
        """
        try:
            student = self.crud.get_student(current_student_id)
            
            if student:
                # Remove sensitive information
                student.pop('password_hash', None)
                return jsonify({'success': True, 'student': student}), 200
            else:
                return jsonify({'error': 'Student not found'}), 404
                
        except Exception as e:
            return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500
    
    @self._require_auth
    def update_profile(self, current_student_id):
        """
        Update the current student's profile information.
        
        Expected JSON payload:
        {
            "first_name": "Updated Name",
            "phone_number": "123-456-7890"
        }
        
        Returns:
            JSON response with success status
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Update student profile
            success = self.crud.update_student(current_student_id, **data)
            
            if success:
                return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
            else:
                return jsonify({'error': 'Failed to update profile'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Profile update failed: {str(e)}'}), 500
    
    # ==========================================
    # SUBJECT ENDPOINTS
    # ==========================================
    
    def get_subjects(self):
        """
        Get all available subjects, optionally filtered by category.
        
        Query parameters:
        - category: Filter by subject category
        
        Returns:
            JSON response with list of subjects
        """
        try:
            category = request.args.get('category')
            
            if category:
                subjects = self.crud.get_subjects_by_category(category)
            else:
                subjects = self.crud.get_all_subjects()
            
            return jsonify({'success': True, 'subjects': subjects}), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get subjects: {str(e)}'}), 500
    
    def get_subject(self, subject_id):
        """
        Get detailed information about a specific subject.
        
        Args:
            subject_id (int): Subject ID from URL parameter
        
        Returns:
            JSON response with subject details
        """
        try:
            # This would require a get_subject method in CRUD
            # For now, get all subjects and filter
            subjects = self.crud.get_all_subjects()
            subject = next((s for s in subjects if s['id'] == subject_id), None)
            
            if subject:
                return jsonify({'success': True, 'subject': subject}), 200
            else:
                return jsonify({'error': 'Subject not found'}), 404
                
        except Exception as e:
            return jsonify({'error': f'Failed to get subject: {str(e)}'}), 500
    
    def get_categories(self):
        """
        Get all available subject categories.
        
        Returns:
            JSON response with list of categories
        """
        try:
            subjects = self.crud.get_all_subjects()
            categories = list(set(subject['category'] for subject in subjects))
            categories.sort()
            
            return jsonify({'success': True, 'categories': categories}), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get categories: {str(e)}'}), 500
    
    # ==========================================
    # PREFERENCE ENDPOINTS
    # ==========================================
    
    @self._require_auth
    def get_preferences(self, current_student_id):
        """
        Get all preferences for the current student.
        
        Returns:
            JSON response with student preferences
        """
        try:
            preferences = self.crud.get_student_preferences(current_student_id)
            return jsonify({'success': True, 'preferences': preferences}), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get preferences: {str(e)}'}), 500
    
    @self._require_auth
    def add_preference(self, current_student_id):
        """
        Add or update a student preference.
        
        Expected JSON payload:
        {
            "subject_id": 1,
            "interest_level": 5,
            "priority": 1,
            "notes": "Very interested in this subject"
        }
        
        Returns:
            JSON response with success status
        """
        try:
            data = request.get_json()
            
            if not data or not data.get('subject_id') or not data.get('interest_level'):
                return jsonify({'error': 'subject_id and interest_level are required'}), 400
            
            # Validate interest level
            if not (1 <= data['interest_level'] <= 5):
                return jsonify({'error': 'Interest level must be between 1 and 5'}), 400
            
            # Add preference
            preference_id = self.crud.add_student_preference(
                student_id=current_student_id,
                subject_id=data['subject_id'],
                interest_level=data['interest_level'],
                priority=data.get('priority'),
                notes=data.get('notes'),
                status=data.get('status', 'interested')
            )
            
            if preference_id > 0:
                return jsonify({
                    'success': True,
                    'message': 'Preference added successfully',
                    'preference_id': preference_id
                }), 201
            else:
                return jsonify({'error': 'Failed to add preference'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Failed to add preference: {str(e)}'}), 500
    
    @self._require_auth
    def remove_preference(self, current_student_id, preference_id):
        """
        Remove a student preference.
        
        Args:
            preference_id (int): Preference ID from URL parameter
        
        Returns:
            JSON response with success status
        """
        try:
            # First verify the preference belongs to the current student
            preferences = self.crud.get_student_preferences(current_student_id)
            preference = next((p for p in preferences if p['id'] == preference_id), None)
            
            if not preference:
                return jsonify({'error': 'Preference not found or access denied'}), 404
            
            # Remove the preference
            success = self.crud.remove_student_preference(current_student_id, preference['subject_id'])
            
            if success:
                return jsonify({'success': True, 'message': 'Preference removed successfully'}), 200
            else:
                return jsonify({'error': 'Failed to remove preference'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Failed to remove preference: {str(e)}'}), 500
    
    # ==========================================
    # AI-POWERED ENDPOINTS
    # ==========================================
    
    @self._require_auth
    def get_ai_recommendations(self, current_student_id):
        """
        Get AI-powered subject recommendations for the current student.
        
        Expected JSON payload:
        {
            "additional_context": "Student is interested in technology careers"
        }
        
        Returns:
            JSON response with AI recommendations
        """
        if not self.ai_advisor:
            return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503
        
        try:
            data = request.get_json() or {}
            additional_context = data.get('additional_context', '')
            
            recommendations = self.ai_advisor.get_subject_recommendations(
                student_id=current_student_id,
                additional_context=additional_context
            )
            
            return jsonify(recommendations), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get AI recommendations: {str(e)}'}), 500
    
    @self._require_auth
    def analyze_subject_fit(self, current_student_id):
        """
        Analyze how well a specific subject fits the current student.
        
        Expected JSON payload:
        {
            "subject_name": "Computer Science"
        }
        
        Returns:
            JSON response with subject fit analysis
        """
        if not self.ai_advisor:
            return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503
        
        try:
            data = request.get_json()
            
            if not data or not data.get('subject_name'):
                return jsonify({'error': 'subject_name is required'}), 400
            
            analysis = self.ai_advisor.analyze_subject_fit(
                student_id=current_student_id,
                subject_name=data['subject_name']
            )
            
            return jsonify(analysis), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to analyze subject fit: {str(e)}'}), 500
    
    @self._require_auth
    def get_career_advice(self, current_student_id):
        """
        Get career pathway advice for the current student.
        
        Expected JSON payload:
        {
            "career_interest": "Software Engineering"
        }
        
        Returns:
            JSON response with career advice
        """
        if not self.ai_advisor:
            return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503
        
        try:
            data = request.get_json()
            
            if not data or not data.get('career_interest'):
                return jsonify({'error': 'career_interest is required'}), 400
            
            advice = self.ai_advisor.get_career_pathway_advice(
                student_id=current_student_id,
                career_interest=data['career_interest']
            )
            
            return jsonify(advice), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get career advice: {str(e)}'}), 500
    
    @self._require_auth
    def generate_study_plan(self, current_student_id):
        """
        Generate a personalized study plan for the current student.
        
        Expected JSON payload:
        {
            "selected_subjects": ["Mathematics", "Computer Science"],
            "semester": "Fall 2024"
        }
        
        Returns:
            JSON response with study plan
        """
        if not self.ai_advisor:
            return jsonify({'error': 'AI features not available - OpenAI API key not configured'}), 503
        
        try:
            data = request.get_json()
            
            if not data or not data.get('selected_subjects'):
                return jsonify({'error': 'selected_subjects is required'}), 400
            
            study_plan = self.ai_advisor.generate_study_plan(
                student_id=current_student_id,
                selected_subjects=data['selected_subjects'],
                semester=data.get('semester', 'Current Semester')
            )
            
            return jsonify(study_plan), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to generate study plan: {str(e)}'}), 500
    
    # ==========================================
    # UTILITY ENDPOINTS
    # ==========================================
    
    def health_check(self):
        """
        Health check endpoint to verify API is running.
        
        Returns:
            JSON response with system status
        """
        try:
            stats = self.crud.get_database_stats()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database_stats': stats,
                'ai_enabled': self.ai_advisor is not None
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # ==========================================
    # AUTHENTICATION UTILITIES
    # ==========================================
    
    def _generate_token(self, student_id: int) -> str:
        """
        Generate a JWT token for authenticated sessions.
        
        Args:
            student_id (int): Student's unique ID
        
        Returns:
            str: JWT token
        """
        payload = {
            'student_id': student_id,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def _verify_token(self, token: str) -> Optional[int]:
        """
        Verify and decode a JWT token.
        
        Args:
            token (str): JWT token to verify
        
        Returns:
            Optional[int]: Student ID if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload['student_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _require_auth(self, f):
        """
        Decorator to require authentication for protected endpoints.
        
        Args:
            f: Function to wrap with authentication requirement
        
        Returns:
            Wrapped function that checks for valid authentication
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            token = auth_header.split(' ')[1]
            student_id = self._verify_token(token)
            
            if not student_id:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Pass student_id to the wrapped function
            return f(student_id, *args, **kwargs)
        
        return decorated_function
    
    def run(self, host='localhost', port=5000, debug=True):
        """
        Start the Flask development server.
        
        Args:
            host (str): Host address to bind to
            port (int): Port number to listen on
            debug (bool): Enable debug mode
        """
        print(f"🚀 Starting Student Subject API Server")
        print(f"📍 Server URL: http://{host}:{port}")
        print(f"🤖 AI Features: {'Enabled' if self.ai_advisor else 'Disabled (no OpenAI key)'}")
        print(f"🗄️  Database: {self.crud.db_path}")
        print("=" * 50)
        
        self.app.run(host=host, port=port, debug=debug)

# Create and configure the API server
def create_app():
    """
    Factory function to create and configure the Flask application.
    
    Returns:
        StudentSubjectAPI: Configured API server instance
    """
    return StudentSubjectAPI()

# Run the server if this script is executed directly
if __name__ == "__main__":
    # Load environment variables from .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("💡 Install python-dotenv for .env file support: pip install python-dotenv")
    
    # Create and run the API server
    api = create_app()
    api.run(
        host=os.getenv('API_HOST', 'localhost'),
        port=int(os.getenv('API_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )

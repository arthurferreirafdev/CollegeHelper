"""
ADDITIONAL API ENDPOINTS MODULE
==============================
This module extends the main API server with additional endpoints
for handling subject scheduling, file uploads, and preference management.

New endpoints:
- POST /api/schedule/create - Create optimized schedule
- POST /api/files/upload - Handle file uploads
- GET /api/schedule/analysis - Get schedule analysis
- POST /api/preferences/bulk - Bulk preference updates

Usage:
    This module is imported by api_server.py to extend functionality
"""

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from typing import Dict, Any

from subject_scheduler import SubjectScheduler, SchedulingPreferences, SchedulingStrategy, StudentAvailability, TimeSlot
from file_parser import FileParser
from datetime import time

class SchedulingAPIEndpoints:
    """
    Additional API endpoints for scheduling functionality
    """
    
    def __init__(self, app, crud, require_auth_decorator):
        """
        Initialize scheduling endpoints
        
        Args:
            app: Flask application instance
            crud: StudentCRUD instance
            require_auth_decorator: Authentication decorator
        """
        self.app = app
        self.crud = crud
        self.require_auth = require_auth_decorator
        self.scheduler = SubjectScheduler()
        self.file_parser = FileParser()
        
        # Register endpoints
        self._register_endpoints()
    
    def _register_endpoints(self):
        """Register all scheduling-related endpoints"""
        self.app.route('/api/schedule/create', methods=['POST'])(self.create_schedule)
        self.app.route('/api/files/upload', methods=['POST'])(self.upload_file)
        self.app.route('/api/schedule/analysis/<int:schedule_id>', methods=['GET'])(self.get_schedule_analysis)
        self.app.route('/api/preferences/bulk', methods=['POST'])(self.bulk_update_preferences)
        self.app.route('/api/files/sample-formats', methods=['GET'])(self.get_sample_formats)
    
    @self.require_auth
    def create_schedule(self, current_student_id: int):
        """
        Create an optimized schedule based on student preferences
        
        Expected JSON payload:
        {
            "subject_count": 5,
            "strategy": "maximize_subjects",
            "prioritize_dependencies": true,
            "include_saturday": false,
            "weekly_availability": [
                {
                    "day": "Monday",
                    "available": true,
                    "time_slots": [
                        {"start": "09:00", "end": "17:00"}
                    ]
                }
            ],
            "additional_notes": "Prefer morning classes",
            "uploaded_subjects": [...]
        }
        
        Returns:
            JSON response with optimized schedule
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['subject_count', 'strategy', 'weekly_availability']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Parse scheduling preferences
            preferences = self._parse_scheduling_preferences(current_student_id, data)
            
            # Create optimized schedule
            schedule_result = self.scheduler.create_optimal_schedule(preferences)
            
            if schedule_result['success']:
                # Store schedule in database (you might want to add a schedules table)
                # For now, we'll return the result directly
                return jsonify(schedule_result), 200
            else:
                return jsonify(schedule_result), 400
                
        except Exception as e:
            return jsonify({'error': f'Failed to create schedule: {str(e)}'}), 500
    
    @self.require_auth
    def upload_file(self, current_student_id: int):
        """
        Handle file upload and parsing
        
        Expects multipart/form-data with file upload
        
        Returns:
            JSON response with parsed subjects
        """
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension not in self.file_parser.supported_formats:
                return jsonify({
                    'error': f'Unsupported file format: {file_extension}',
                    'supported_formats': self.file_parser.supported_formats
                }), 400
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            try:
                # Parse the file
                parse_result = self.file_parser.parse_file(temp_file_path)
                
                if parse_result['success']:
                    return jsonify({
                        'success': True,
                        'message': f'File parsed successfully',
                        'subjects': parse_result['subjects'],
                        'count': parse_result['count'],
                        'file_type': parse_result['file_type']
                    }), 200
                else:
                    return jsonify(parse_result), 400
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 500
    
    def get_schedule_analysis(self, schedule_id: int):
        """
        Get detailed analysis of a created schedule
        
        Args:
            schedule_id: Schedule ID from URL parameter
            
        Returns:
            JSON response with schedule analysis
        """
        try:
            # This would typically fetch from a schedules table
            # For now, return a placeholder response
            return jsonify({
                'success': True,
                'message': 'Schedule analysis endpoint - implementation pending',
                'schedule_id': schedule_id
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get schedule analysis: {str(e)}'}), 500
    
    @self.require_auth
    def bulk_update_preferences(self, current_student_id: int):
        """
        Update multiple student preferences at once
        
        Expected JSON payload:
        {
            "preferences": [
                {
                    "subject_id": 1,
                    "interest_level": 5,
                    "priority": 1,
                    "notes": "Very interested"
                }
            ]
        }
        
        Returns:
            JSON response with update results
        """
        try:
            data = request.get_json()
            
            if not data or 'preferences' not in data:
                return jsonify({'error': 'Preferences array is required'}), 400
            
            preferences = data['preferences']
            results = []
            
            for pref in preferences:
                if not isinstance(pref, dict):
                    continue
                
                if 'subject_id' not in pref or 'interest_level' not in pref:
                    results.append({
                        'subject_id': pref.get('subject_id', 'unknown'),
                        'success': False,
                        'error': 'subject_id and interest_level are required'
                    })
                    continue
                
                # Add/update preference
                preference_id = self.crud.add_student_preference(
                    student_id=current_student_id,
                    subject_id=pref['subject_id'],
                    interest_level=pref['interest_level'],
                    priority=pref.get('priority'),
                    notes=pref.get('notes'),
                    status=pref.get('status', 'interested')
                )
                
                results.append({
                    'subject_id': pref['subject_id'],
                    'success': preference_id > 0,
                    'preference_id': preference_id if preference_id > 0 else None
                })
            
            successful_updates = sum(1 for r in results if r['success'])
            
            return jsonify({
                'success': True,
                'message': f'Updated {successful_updates} out of {len(results)} preferences',
                'results': results
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Bulk update failed: {str(e)}'}), 500
    
    def get_sample_formats(self):
        """
        Get sample file formats for user reference
        
        Returns:
            JSON response with sample formats
        """
        try:
            samples = self.file_parser.get_sample_formats()
            
            return jsonify({
                'success': True,
                'sample_formats': samples,
                'supported_extensions': self.file_parser.supported_formats
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get sample formats: {str(e)}'}), 500
    
    def _parse_scheduling_preferences(self, student_id: int, data: Dict[str, Any]) -> SchedulingPreferences:
        """
        Parse request data into SchedulingPreferences object
        
        Args:
            student_id: Current student ID
            data: Request data dictionary
            
        Returns:
            SchedulingPreferences object
        """
        # Parse strategy
        strategy_map = {
            'maximize_subjects': SchedulingStrategy.MAXIMIZE_SUBJECTS,
            'clear_dependencies': SchedulingStrategy.CLEAR_DEPENDENCIES,
            'balanced_difficulty': SchedulingStrategy.BALANCED_DIFFICULTY,
            'interest_based': SchedulingStrategy.INTEREST_BASED,
            'high_value_credits': SchedulingStrategy.HIGH_VALUE_CREDITS
        }
        
        strategy = strategy_map.get(data['strategy'], SchedulingStrategy.INTEREST_BASED)
        
        # Parse weekly availability
        weekly_availability = []
        for day_data in data['weekly_availability']:
            time_slots = []
            
            if day_data.get('available', False):
                for slot_data in day_data.get('time_slots', []):
                    start_time = time.fromisoformat(slot_data['start'])
                    end_time = time.fromisoformat(slot_data['end'])
                    
                    time_slot = TimeSlot(
                        day=day_data['day'],
                        start_time=start_time,
                        end_time=end_time
                    )
                    time_slots.append(time_slot)
            
            availability = StudentAvailability(
                day=day_data['day'],
                available=day_data.get('available', False),
                time_slots=time_slots
            )
            weekly_availability.append(availability)
        
        return SchedulingPreferences(
            student_id=student_id,
            subject_count=data['subject_count'],
            strategy=strategy,
            prioritize_dependencies=data.get('prioritize_dependencies', False),
            include_saturday=data.get('include_saturday', False),
            weekly_availability=weekly_availability,
            additional_notes=data.get('additional_notes', ''),
            uploaded_subjects=data.get('uploaded_subjects', [])
        )

# Function to register endpoints with the main Flask app
def register_scheduling_endpoints(app, crud, require_auth_decorator):
    """
    Register scheduling endpoints with the Flask application
    
    Args:
        app: Flask application instance
        crud: StudentCRUD instance
        require_auth_decorator: Authentication decorator function
    """
    SchedulingAPIEndpoints(app, crud, require_auth_decorator)

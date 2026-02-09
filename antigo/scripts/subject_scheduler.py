"""
SUBJECT SCHEDULER MODULE
=======================
This module handles the complex logic of scheduling subjects based on
student preferences, availability, dependencies, and uploaded subject data.

Features:
- Conflict detection and resolution
- Dependency analysis and ordering
- Schedule optimization algorithms
- Multiple scheduling strategies
- Integration with student preferences

Usage:
    from subject_scheduler import SubjectScheduler
    scheduler = SubjectScheduler()
    schedule = scheduler.create_optimal_schedule(student_id, preferences)
"""

import json
import csv
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, time, timedelta
from dataclasses import dataclass
from enum import Enum
import itertools

from student_crud import StudentCRUD

class SchedulingStrategy(Enum):
    """Enumeration of available scheduling strategies"""
    MAXIMIZE_SUBJECTS = "maximize_subjects"
    CLEAR_DEPENDENCIES = "clear_dependencies"
    BALANCED_DIFFICULTY = "balanced_difficulty"
    INTEREST_BASED = "interest_based"
    HIGH_VALUE_CREDITS = "high_value_credits"

@dataclass
class TimeSlot:
    """Represents a time slot in the schedule"""
    day: str
    start_time: time
    end_time: time
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another"""
        if self.day != other.day:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def duration_hours(self) -> float:
        """Calculate duration in hours"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        return (end_datetime - start_datetime).total_seconds() / 3600

@dataclass
class Subject:
    """Represents a subject with all its properties"""
    id: int
    name: str
    code: str
    category: str
    credits: int
    difficulty_level: int
    prerequisites: List[str]
    time_slots: List[TimeSlot]
    teacher_name: Optional[str] = None
    max_students: Optional[int] = None
    description: Optional[str] = None

@dataclass
class StudentAvailability:
    """Represents a student's weekly availability"""
    day: str
    available: bool
    time_slots: List[TimeSlot]

@dataclass
class SchedulingPreferences:
    """Container for all student scheduling preferences"""
    student_id: int
    subject_count: int
    strategy: SchedulingStrategy
    prioritize_dependencies: bool
    include_saturday: bool
    weekly_availability: List[StudentAvailability]
    additional_notes: str
    uploaded_subjects: List[Dict[str, Any]]

class SubjectScheduler:
    """
    Main scheduler class that handles subject scheduling optimization
    """
    
    def __init__(self):
        """Initialize the scheduler with database connection"""
        self.crud = StudentCRUD()
    
    def create_optimal_schedule(self, preferences: SchedulingPreferences) -> Dict[str, Any]:
        """
        Create an optimal schedule based on student preferences
        
        Args:
            preferences: Student scheduling preferences
            
        Returns:
            Dict containing the optimized schedule and analysis
        """
        try:
            # Get available subjects from database and uploaded file
            available_subjects = self._get_available_subjects(preferences)
            
            # Filter subjects based on student availability
            compatible_subjects = self._filter_compatible_subjects(
                available_subjects, preferences.weekly_availability
            )
            
            # Apply scheduling strategy
            recommended_subjects = self._apply_scheduling_strategy(
                compatible_subjects, preferences
            )
            
            # Create final schedule with conflict resolution
            final_schedule = self._create_conflict_free_schedule(
                recommended_subjects, preferences
            )
            
            # Generate schedule analysis
            analysis = self._analyze_schedule(final_schedule, preferences)
            
            return {
                "success": True,
                "schedule": final_schedule,
                "analysis": analysis,
                "total_subjects": len(final_schedule),
                "total_credits": sum(subject.credits for subject in final_schedule),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create schedule: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_available_subjects(self, preferences: SchedulingPreferences) -> List[Subject]:
        """
        Get all available subjects from database and uploaded data
        
        Args:
            preferences: Student preferences containing uploaded subjects
            
        Returns:
            List of available Subject objects
        """
        subjects = []
        
        # Get subjects from database
        db_subjects = self.crud.get_all_subjects()
        
        for db_subject in db_subjects:
            # Parse time slots from database (assuming stored as JSON or structured format)
            time_slots = self._parse_subject_schedule(db_subject.get('schedule', ''))
            
            subject = Subject(
                id=db_subject['id'],
                name=db_subject['name'],
                code=db_subject.get('code', ''),
                category=db_subject['category'],
                credits=db_subject['credits'],
                difficulty_level=db_subject['difficulty_level'],
                prerequisites=self._parse_prerequisites(db_subject.get('prerequisites', '')),
                time_slots=time_slots,
                teacher_name=db_subject.get('teacher_name'),
                max_students=db_subject.get('max_students'),
                description=db_subject.get('description')
            )
            subjects.append(subject)
        
        # Add subjects from uploaded file
        for uploaded_subject in preferences.uploaded_subjects:
            time_slots = self._parse_subject_schedule(uploaded_subject.get('schedule', ''))
            
            subject = Subject(
                id=len(subjects) + 1000,  # Use high ID to avoid conflicts
                name=uploaded_subject['name'],
                code=uploaded_subject.get('code', ''),
                category=uploaded_subject.get('category', 'Uploaded'),
                credits=uploaded_subject.get('credits', 3),
                difficulty_level=uploaded_subject.get('difficulty', 3),
                prerequisites=[],
                time_slots=time_slots,
                description=f"Uploaded subject: {uploaded_subject['name']}"
            )
            subjects.append(subject)
        
        return subjects
    
    def _parse_subject_schedule(self, schedule_str: str) -> List[TimeSlot]:
        """
        Parse subject schedule string into TimeSlot objects
        
        Args:
            schedule_str: Schedule string (e.g., "Mon 09:00-11:00, Wed 14:00-16:00")
            
        Returns:
            List of TimeSlot objects
        """
        time_slots = []
        
        if not schedule_str:
            return time_slots
        
        try:
            # Parse different schedule formats
            # Format: "Mon 09:00-11:00, Wed 14:00-16:00"
            schedule_parts = schedule_str.split(',')
            
            for part in schedule_parts:
                part = part.strip()
                if not part:
                    continue
                
                # Extract day and time range
                tokens = part.split()
                if len(tokens) >= 2:
                    day = tokens[0].strip()
                    time_range = tokens[1].strip()
                    
                    # Parse time range (e.g., "09:00-11:00")
                    if '-' in time_range:
                        start_str, end_str = time_range.split('-')
                        start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                        end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                        
                        time_slot = TimeSlot(
                            day=self._normalize_day_name(day),
                            start_time=start_time,
                            end_time=end_time
                        )
                        time_slots.append(time_slot)
        
        except Exception as e:
            print(f"Warning: Could not parse schedule '{schedule_str}': {e}")
        
        return time_slots
    
    def _normalize_day_name(self, day: str) -> str:
        """
        Normalize day names to standard format
        
        Args:
            day: Day name in various formats
            
        Returns:
            Standardized day name
        """
        day_mapping = {
            'mon': 'Monday', 'monday': 'Monday',
            'tue': 'Tuesday', 'tuesday': 'Tuesday',
            'wed': 'Wednesday', 'wednesday': 'Wednesday',
            'thu': 'Thursday', 'thursday': 'Thursday',
            'fri': 'Friday', 'friday': 'Friday',
            'sat': 'Saturday', 'saturday': 'Saturday',
            'sun': 'Sunday', 'sunday': 'Sunday'
        }
        
        return day_mapping.get(day.lower(), day.title())
    
    def _parse_prerequisites(self, prerequisites_str: str) -> List[str]:
        """
        Parse prerequisites string into list of subject names
        
        Args:
            prerequisites_str: Prerequisites string
            
        Returns:
            List of prerequisite subject names
        """
        if not prerequisites_str:
            return []
        
        # Split by common delimiters
        prerequisites = []
        for delimiter in [',', ';', '|']:
            if delimiter in prerequisites_str:
                prerequisites = [p.strip() for p in prerequisites_str.split(delimiter)]
                break
        
        if not prerequisites:
            prerequisites = [prerequisites_str.strip()]
        
        return [p for p in prerequisites if p]
    
    def _filter_compatible_subjects(self, subjects: List[Subject], 
                                  availability: List[StudentAvailability]) -> List[Subject]:
        """
        Filter subjects that are compatible with student availability
        
        Args:
            subjects: List of all available subjects
            availability: Student's weekly availability
            
        Returns:
            List of compatible subjects
        """
        compatible_subjects = []
        
        # Create availability lookup
        availability_map = {av.day: av for av in availability if av.available}
        
        for subject in subjects:
            is_compatible = True
            
            # Check if all subject time slots fit within student availability
            for subject_slot in subject.time_slots:
                if subject_slot.day not in availability_map:
                    is_compatible = False
                    break
                
                student_availability = availability_map[subject_slot.day]
                slot_fits = False
                
                # Check if subject slot fits in any of the student's available slots
                for available_slot in student_availability.time_slots:
                    if (available_slot.start_time <= subject_slot.start_time and 
                        available_slot.end_time >= subject_slot.end_time):
                        slot_fits = True
                        break
                
                if not slot_fits:
                    is_compatible = False
                    break
            
            if is_compatible:
                compatible_subjects.append(subject)
        
        return compatible_subjects
    
    def _apply_scheduling_strategy(self, subjects: List[Subject], 
                                 preferences: SchedulingPreferences) -> List[Subject]:
        """
        Apply the selected scheduling strategy to prioritize subjects
        
        Args:
            subjects: List of compatible subjects
            preferences: Student preferences
            
        Returns:
            List of subjects ordered by strategy priority
        """
        if preferences.strategy == SchedulingStrategy.MAXIMIZE_SUBJECTS:
            return self._strategy_maximize_subjects(subjects, preferences)
        elif preferences.strategy == SchedulingStrategy.CLEAR_DEPENDENCIES:
            return self._strategy_clear_dependencies(subjects, preferences)
        elif preferences.strategy == SchedulingStrategy.BALANCED_DIFFICULTY:
            return self._strategy_balanced_difficulty(subjects, preferences)
        elif preferences.strategy == SchedulingStrategy.INTEREST_BASED:
            return self._strategy_interest_based(subjects, preferences)
        elif preferences.strategy == SchedulingStrategy.HIGH_VALUE_CREDITS:
            return self._strategy_high_value_credits(subjects, preferences)
        else:
            # Default to interest-based
            return self._strategy_interest_based(subjects, preferences)
    
    def _strategy_maximize_subjects(self, subjects: List[Subject], 
                                  preferences: SchedulingPreferences) -> List[Subject]:
        """
        Strategy: Maximize the number of subjects that can fit in the schedule
        
        Args:
            subjects: Available subjects
            preferences: Student preferences
            
        Returns:
            Subjects ordered to maximize count
        """
        # Sort by total time commitment (ascending) and credits (descending)
        def sort_key(subject):
            total_hours = sum(slot.duration_hours() for slot in subject.time_slots)
            return (total_hours, -subject.credits)
        
        return sorted(subjects, key=sort_key)
    
    def _strategy_clear_dependencies(self, subjects: List[Subject], 
                                   preferences: SchedulingPreferences) -> List[Subject]:
        """
        Strategy: Prioritize subjects that clear dependencies for other subjects
        
        Args:
            subjects: Available subjects
            preferences: Student preferences
            
        Returns:
            Subjects ordered by dependency clearing priority
        """
        # Create dependency graph
        subject_names = {s.name for s in subjects}
        dependency_count = {}
        
        for subject in subjects:
            count = 0
            # Count how many other subjects depend on this one
            for other_subject in subjects:
                if subject.name in other_subject.prerequisites:
                    count += 1
            dependency_count[subject.name] = count
        
        # Sort by dependency count (descending) and difficulty (ascending)
        def sort_key(subject):
            return (-dependency_count.get(subject.name, 0), subject.difficulty_level)
        
        return sorted(subjects, key=sort_key)
    
    def _strategy_balanced_difficulty(self, subjects: List[Subject], 
                                    preferences: SchedulingPreferences) -> List[Subject]:
        """
        Strategy: Create a balanced mix of difficulty levels
        
        Args:
            subjects: Available subjects
            preferences: Student preferences
            
        Returns:
            Subjects ordered for balanced difficulty
        """
        # Group subjects by difficulty level
        difficulty_groups = {}
        for subject in subjects:
            level = subject.difficulty_level
            if level not in difficulty_groups:
                difficulty_groups[level] = []
            difficulty_groups[level].append(subject)
        
        # Interleave subjects from different difficulty levels
        balanced_subjects = []
        max_per_level = preferences.subject_count // len(difficulty_groups) + 1
        
        for level in sorted(difficulty_groups.keys()):
            group = sorted(difficulty_groups[level], key=lambda s: -s.credits)
            balanced_subjects.extend(group[:max_per_level])
        
        return balanced_subjects
    
    def _strategy_interest_based(self, subjects: List[Subject], 
                               preferences: SchedulingPreferences) -> List[Subject]:
        """
        Strategy: Prioritize subjects based on student interests
        
        Args:
            subjects: Available subjects
            preferences: Student preferences
            
        Returns:
            Subjects ordered by interest level
        """
        # Get student preferences from database
        student_preferences = self.crud.get_student_preferences(preferences.student_id)
        
        # Create interest mapping
        interest_map = {}
        for pref in student_preferences:
            interest_map[pref['subject_name']] = pref['interest_level']
        
        # Sort by interest level (descending) and credits (descending)
        def sort_key(subject):
            interest = interest_map.get(subject.name, 0)
            return (-interest, -subject.credits)
        
        return sorted(subjects, key=sort_key)
    
    def _strategy_high_value_credits(self, subjects: List[Subject], 
                                   preferences: SchedulingPreferences) -> List[Subject]:
        """
        Strategy: Prioritize subjects with higher credit values
        
        Args:
            subjects: Available subjects
            preferences: Student preferences
            
        Returns:
            Subjects ordered by credit value
        """
        # Sort by credits (descending) and difficulty (ascending for tie-breaking)
        def sort_key(subject):
            return (-subject.credits, subject.difficulty_level)
        
        return sorted(subjects, key=sort_key)
    
    def _create_conflict_free_schedule(self, subjects: List[Subject], 
                                     preferences: SchedulingPreferences) -> List[Subject]:
        """
        Create a final schedule without time conflicts
        
        Args:
            subjects: Prioritized subjects
            preferences: Student preferences
            
        Returns:
            Final conflict-free schedule
        """
        final_schedule = []
        used_time_slots = []
        
        for subject in subjects:
            if len(final_schedule) >= preferences.subject_count:
                break
            
            # Check for conflicts with already scheduled subjects
            has_conflict = False
            for subject_slot in subject.time_slots:
                for used_slot in used_time_slots:
                    if subject_slot.overlaps_with(used_slot):
                        has_conflict = True
                        break
                if has_conflict:
                    break
            
            # Check prerequisites
            if preferences.prioritize_dependencies:
                missing_prerequisites = []
                for prereq in subject.prerequisites:
                    if not any(s.name == prereq for s in final_schedule):
                        missing_prerequisites.append(prereq)
                
                if missing_prerequisites:
                    # Skip this subject for now, might be added later
                    continue
            
            # Add subject to schedule if no conflicts
            if not has_conflict:
                final_schedule.append(subject)
                used_time_slots.extend(subject.time_slots)
        
        return final_schedule
    
    def _analyze_schedule(self, schedule: List[Subject], 
                         preferences: SchedulingPreferences) -> Dict[str, Any]:
        """
        Analyze the created schedule and provide insights
        
        Args:
            schedule: Final schedule
            preferences: Student preferences
            
        Returns:
            Schedule analysis
        """
        if not schedule:
            return {
                "total_subjects": 0,
                "total_credits": 0,
                "total_hours": 0,
                "difficulty_distribution": {},
                "category_distribution": {},
                "warnings": ["No subjects could be scheduled with current constraints"]
            }
        
        # Calculate basic statistics
        total_subjects = len(schedule)
        total_credits = sum(s.credits for s in schedule)
        total_hours = sum(sum(slot.duration_hours() for slot in s.time_slots) for s in schedule)
        
        # Difficulty distribution
        difficulty_dist = {}
        for subject in schedule:
            level = subject.difficulty_level
            difficulty_dist[level] = difficulty_dist.get(level, 0) + 1
        
        # Category distribution
        category_dist = {}
        for subject in schedule:
            category = subject.category
            category_dist[category] = category_dist.get(category, 0) + 1
        
        # Generate warnings and recommendations
        warnings = []
        recommendations = []
        
        if total_subjects < preferences.subject_count:
            warnings.append(f"Only {total_subjects} subjects scheduled out of requested {preferences.subject_count}")
        
        if total_hours > 40:
            warnings.append("Schedule exceeds 40 hours per week - consider reducing subjects")
        
        avg_difficulty = sum(s.difficulty_level for s in schedule) / len(schedule)
        if avg_difficulty > 4:
            warnings.append("High average difficulty level - ensure adequate study time")
        
        # Check for balanced categories
        if len(category_dist) < 2:
            recommendations.append("Consider adding subjects from different categories for a balanced curriculum")
        
        return {
            "total_subjects": total_subjects,
            "total_credits": total_credits,
            "total_hours": round(total_hours, 1),
            "average_difficulty": round(avg_difficulty, 1),
            "difficulty_distribution": difficulty_dist,
            "category_distribution": category_dist,
            "warnings": warnings,
            "recommendations": recommendations,
            "schedule_efficiency": round((total_subjects / preferences.subject_count) * 100, 1) if preferences.subject_count > 0 else 0
        }

# Example usage and testing
if __name__ == "__main__":
    print("🗓️  Testing Subject Scheduler")
    print("=" * 40)
    
    # This would typically be called from the API with real data
    print("💡 Subject Scheduler is ready for use")
    print("📚 Import this module to use scheduling functionality")

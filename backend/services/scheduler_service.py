import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    MAXIMIZE_SUBJECTS = "maximize_subjects"
    CLEAR_DEPENDENCIES = "clear_dependencies"
    BALANCED_DIFFICULTY = "balanced_difficulty"
    INTEREST_BASED = "interest_based"
    HIGH_VALUE_CREDITS = "high_value_credits"


@dataclass
class TimeSlot:
    day: str
    start_time: time
    end_time: time

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        if self.day != other.day:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    def duration_hours(self) -> float:
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        return (end_dt - start_dt).total_seconds() / 3600


@dataclass
class Subject:
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
    day: str
    available: bool
    time_slots: List[TimeSlot]


@dataclass
class SchedulingPreferences:
    student_id: int
    subject_count: int
    strategy: SchedulingStrategy
    prioritize_dependencies: bool
    include_saturday: bool
    weekly_availability: List[StudentAvailability]
    additional_notes: str
    uploaded_subjects: List[Dict[str, Any]]


class SchedulerService:
    def create_optimal_schedule(self, preferences: SchedulingPreferences) -> Dict[str, Any]:
        try:
            available_subjects = self._get_available_subjects(preferences)
            compatible = self._filter_compatible(available_subjects, preferences.weekly_availability)
            prioritized = self._apply_strategy(compatible, preferences)
            final = self._resolve_conflicts(prioritized, preferences)
            analysis = self._analyze(final, preferences)

            return {
                'success': True,
                'schedule': [{'name': s.name, 'code': s.code, 'category': s.category,
                              'credits': s.credits, 'difficulty': s.difficulty_level} for s in final],
                'analysis': analysis,
                'total_subjects': len(final),
                'total_credits': sum(s.credits for s in final),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'Scheduling error: {e}')
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    def _get_available_subjects(self, preferences: SchedulingPreferences) -> List[Subject]:
        from backend.repository.subject import SubjectRepository
        subjects = []
        for s in SubjectRepository.get_all():
            time_slots = self._parse_schedule(s.get('schedule', ''))
            subjects.append(Subject(
                id=s['id'], name=s['name'], code=s.get('code', ''),
                category=s['category'], credits=s['credits'],
                difficulty_level=s['difficulty_level'],
                prerequisites=self._parse_prereqs(s.get('prerequisites', '')),
                time_slots=time_slots, teacher_name=s.get('teacher_name'),
                max_students=s.get('max_students'), description=s.get('description')
            ))
        for u in preferences.uploaded_subjects:
            time_slots = self._parse_schedule(u.get('schedule', ''))
            subjects.append(Subject(
                id=len(subjects) + 1000, name=u['name'], code='',
                category=u.get('category', 'Uploaded'),
                credits=u.get('credits', 3), difficulty_level=u.get('difficulty', 3),
                prerequisites=[], time_slots=time_slots
            ))
        return subjects

    def _parse_schedule(self, schedule_str: str) -> List[TimeSlot]:
        if not schedule_str:
            return []
        slots = []
        try:
            for part in schedule_str.split(','):
                part = part.strip()
                if not part:
                    continue
                tokens = part.split()
                if len(tokens) >= 2 and '-' in tokens[1]:
                    start_s, end_s = tokens[1].split('-')
                    slots.append(TimeSlot(
                        day=tokens[0].strip(),
                        start_time=datetime.strptime(start_s.strip(), '%H:%M').time(),
                        end_time=datetime.strptime(end_s.strip(), '%H:%M').time()
                    ))
        except Exception as e:
            logger.warning(f'Could not parse schedule "{schedule_str}": {e}')
        return slots

    def _parse_prereqs(self, prereqs: str) -> List[str]:
        if not prereqs:
            return []
        for delim in [',', ';', '|']:
            if delim in prereqs:
                return [p.strip() for p in prereqs.split(delim) if p.strip()]
        return [prereqs.strip()] if prereqs.strip() else []

    def _filter_compatible(self, subjects: List[Subject], availability: List[StudentAvailability]) -> List[Subject]:
        avail_map = {a.day: a for a in availability if a.available}
        result = []
        for subj in subjects:
            ok = True
            for slot in subj.time_slots:
                if slot.day not in avail_map:
                    ok = False
                    break
                fits = any(
                    a.start_time <= slot.start_time and a.end_time >= slot.end_time
                    for a in avail_map[slot.day].time_slots
                )
                if not fits:
                    ok = False
                    break
            if ok:
                result.append(subj)
        return result

    def _apply_strategy(self, subjects: List[Subject], prefs: SchedulingPreferences) -> List[Subject]:
        strat = prefs.strategy
        if strat == SchedulingStrategy.MAXIMIZE_SUBJECTS:
            return sorted(subjects, key=lambda s: (sum(sl.duration_hours() for sl in s.time_slots), -s.credits))
        elif strat == SchedulingStrategy.CLEAR_DEPENDENCIES:
            dep_count = {}
            for s in subjects:
                dep_count[s.name] = sum(1 for o in subjects if s.name in o.prerequisites)
            return sorted(subjects, key=lambda s: (-dep_count.get(s.name, 0), s.difficulty_level))
        elif strat == SchedulingStrategy.BALANCED_DIFFICULTY:
            return sorted(subjects, key=lambda s: (s.difficulty_level, -s.credits))
        elif strat == SchedulingStrategy.HIGH_VALUE_CREDITS:
            return sorted(subjects, key=lambda s: (-s.credits, s.difficulty_level))
        else:
            return sorted(subjects, key=lambda s: (-s.credits))

    def _resolve_conflicts(self, subjects: List[Subject], prefs: SchedulingPreferences) -> List[Subject]:
        final = []
        used_slots = []
        for subj in subjects:
            if len(final) >= prefs.subject_count:
                break
            conflict = any(
                ss.overlaps_with(us) for ss in subj.time_slots for us in used_slots
            )
            if not conflict:
                final.append(subj)
                used_slots.extend(subj.time_slots)
        return final

    def _analyze(self, schedule: List[Subject], prefs: SchedulingPreferences) -> Dict[str, Any]:
        if not schedule:
            return {'total_subjects': 0, 'total_credits': 0, 'warnings': ['No subjects could be scheduled']}
        total_hours = sum(sum(sl.duration_hours() for sl in s.time_slots) for s in schedule)
        avg_diff = sum(s.difficulty_level for s in schedule) / len(schedule)
        warnings = []
        if len(schedule) < prefs.subject_count:
            warnings.append(f'Only {len(schedule)} subjects scheduled out of {prefs.subject_count}')
        if total_hours > 40:
            warnings.append('Schedule exceeds 40 hours per week')
        return {
            'total_subjects': len(schedule),
            'total_credits': sum(s.credits for s in schedule),
            'total_hours': round(total_hours, 1),
            'average_difficulty': round(avg_diff, 1),
            'warnings': warnings
        }

"""
Objective Function for Course Scheduling Optimization.
Evaluates schedule quality based on student time conflicts (MINIMIZATION).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from core.registry import Registry
    from core.schedule import Schedule


class ScheduleObjective:
    """Evaluates schedule by counting student time conflicts."""
    
    def __init__(self, registry: Registry):
        self.registry = registry
    
    def evaluate(self, schedule: Schedule) -> float:
        """Returns objective value (lower is better)."""
        return self.calculate_student_time_conflicts(schedule)
    
    def calculate_student_time_conflicts(self, schedule: Schedule) -> float:
        """
        Count time conflicts for students.
        Example: If student has 2 meetings at same hour → +2 conflicts
        """
        total_conflicts = 0
        student_timeslot_usage: Dict[Tuple, Dict[str, int]] = {}
        
        # Count meetings per student per timeslot
        for meeting_id, (day, hour, room_code) in schedule.where_is.items():
            time_slot = (day, hour)
            students = self.registry.students_of_meeting.get(meeting_id, [])
            
            if time_slot not in student_timeslot_usage:
                student_timeslot_usage[time_slot] = {}
            
            for student_nim in students:
                student_timeslot_usage[time_slot][student_nim] = \
                    student_timeslot_usage[time_slot].get(student_nim, 0) + 1
        
        # Count conflicts
        for time_slot, student_counts in student_timeslot_usage.items():
            for student_nim, count in student_counts.items():
                if count > 1:
                    total_conflicts += count
        
        return total_conflicts
    
    def get_detailed_breakdown(self, schedule: Schedule) -> Dict[str, float]:
        """Returns breakdown of objective components."""
        total = self.calculate_student_time_conflicts(schedule)
        return {"total_objective": total}


def create_objective(registry: Registry) -> ScheduleObjective:
    """Factory function to create objective function."""
    return ScheduleObjective(registry)

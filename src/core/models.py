from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class DAY(Enum):
    """Enumeration for days of the week."""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"

@dataclass
class Course:
    """Represents a course/subject with its basic information."""
    code: str           # Course identifier (e.g., "CS101")
    student_count: int  # Number of students enrolled
    credits: int        # Credit hours/weight of the course

@dataclass
class Classroom:
    """Represents a physical classroom with capacity."""
    code: str       # Room identifier (e.g., "R101")
    capacity: int   # Maximum number of students the room can hold

@dataclass
class Student:
    """Represents a student with their course preferences."""
    nim: str                    # Student ID number
    course_list: list[str]      # List of course codes the student wants to take
    priority: list[int]         # Priority ranking for each course (same order as course_list)

@dataclass
class TimeSlot:
    """Represents a time period from start to end."""
    start_time: tuple[DAY, int]  # (day, hour) when the slot starts
    stop_time: tuple[DAY, int]   # (day, hour) when the slot ends

    def duration(self) -> int:
        """Calculate duration in hours between start and stop time."""
        sd, sh = self.start_time    # start day, start hour
        ed, eh = self.stop_time     # end day, end hour
        
        # Validate that start and end are on the same day
        if sd != ed:
            raise ValueError("Cross-day time slot is not supported")
        
        # Validate that end time is after start time
        if eh <= sh:
            raise ValueError("stop_time has to be bigger than start_time")
        
        return eh - sh  # Return duration in hours

@dataclass(frozen=True)
class ClassMeeting:
    """Represents a single class meeting/session (immutable once created)."""
    meeting_id: int                     # Unique identifier for this meeting
    course_code: str                    # Which course this meeting belongs to
    classroom_code: str | None          # Which room is assigned (None if not yet assigned)
    duration_hours: int                 # How long the meeting lasts
    student_count: int                  # Number of students attending
    students: Optional[List[str]] = None # List of student IDs attending (optional)
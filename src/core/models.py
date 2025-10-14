from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

# @dataclass automatically provides:
# 1. __init__()
# 2.__repr__()
# 3. __eq__()

class DAY(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"

@dataclass
class Course:
    code: str
    student_count:int
    credits: int 

@dataclass
class Classroom:
    code: str
    capacity: int

@dataclass
class Student:
    nim: str
    course_list: list[str]
    priority: list[int]

@dataclass
class TimeSlot:
    start_time: tuple[DAY, int]
    stop_time: tuple[DAY, int]

    def duration(self) -> int:
        sd, sh = self.start_time
        ed, eh = self.stop_time
        if sd != ed:
            raise ValueError("Cross-day timem slot is not supported")
        if eh <= sh:
            raise ValueError("stop_time has to be bigger than start_time")
        return eh - sh

@dataclass(frozen=True) # frozen=True will make objects from this class be immutable (have the attribute be unchangeable)
class ClassMeeting:
    meeting_id: int
    course_code: str
    classroom_code: str | None
    # time_slot: TimeSlot
    duration_hours: int
    student_count: int
    students: Optional[List[str]] = None


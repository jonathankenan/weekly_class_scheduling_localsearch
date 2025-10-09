from dataclasses import dataclass
from typing import List, Optional

# @dataclass automatically provides:
# 1. __init__()
# 2.__repr__()
# 3. __eq__()

@dataclass
class Course:
    code: str
    student_count:int
    credits: int 

@dataclass
class Class:
    code: str
    capacity: int

@dataclass
class Student:
    nim: str
    course_list: list[str]
    priority: list[int]

@dataclass(frozen=True) # frozen=True will make objects from this class be immutable (have the attribute be unchangeable)
class ClassMeeting:
    meeting_id: int
    course_code: str
    room_code: str | None
    duration_hours: int
    student_count: int
    students: Optional[List[str]] = None

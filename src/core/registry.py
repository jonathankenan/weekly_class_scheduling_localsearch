from core.models import Course, Classroom, Student, ClassMeeting
from dataclasses import dataclass, field
from typing import Dict, List
from utils.input_parser import load_json

@dataclass
class Registry:
    # Use default_factory so each instance has its own dict
    courses: Dict[str, Course] = field(default_factory=dict)
    classrooms: Dict[str, Classroom] = field(default_factory=dict)
    students: Dict[str, Student] = field(default_factory=dict)
    meetings: Dict[int, ClassMeeting] = field(default_factory=dict)

    meetings_of_student: Dict[str, List[int]] = field(default_factory=dict)
    students_of_meeting: Dict[int, List[str]] = field(default_factory=dict)
    legal_classrooms_by_meeting: Dict[int, List[str]] = field(default_factory=dict)
    meetings_of_course: Dict[str, List[int]] = field(default_factory=dict)  # added

    def load_from_json(self, file_path: str) -> None:
        """Load and parse input JSON file, then call generate_meetings() and build_indices()."""
        self.courses, self.classrooms, self.students = load_json(file_path)
        self.validate()
        self.generate_meetings()
        self.build_indices()

    def validate(self):
        for student in self.students.values():
            if len(student.course_list) != len(student.priority):
                raise ValueError(f"Priority length mismatch for student {student.nim}")
            for code in student.course_list:
                if code not in self.courses:
                    raise ValueError(f"Student {student.nim} references unknown course {code}")
        print("Validation passed.")

    def generate_meetings(self) -> None:
        """Expand each course into ClassMeeting units (1 per SKS)."""
        meeting_id = 0
        for code in sorted(self.courses.keys()):  # deterministic order
            course = self.courses[code]
            for i in range(course.credits):
                self.meetings[meeting_id] = ClassMeeting(
                    meeting_id=meeting_id,
                    course_code=course.code,
                    classroom_code=course.code.split("_")[1] if "_" in course.code else None,
                    duration_hours=1,
                    student_count=course.student_count
                )
                # add to lookup
                self.meetings_of_course.setdefault(course.code, []).append(meeting_id)
                meeting_id += 1
        print(f"Generated {len(self.meetings)} meetings.")

    def build_indices(self) -> None:
        """Precompute relationships for faster conflict checking."""
        self.meetings_of_student.clear()
        self.students_of_meeting.clear()
        self.legal_classrooms_by_meeting.clear()

        # 1. Meeting <-> Student mapping
        for student in self.students.values():
            mids = []
            for course_code in student.course_list:
                mids.extend(self.meetings_of_course.get(course_code, []))
            self.meetings_of_student[student.nim] = mids
            for mid in mids:
                self.students_of_meeting.setdefault(mid, []).append(student.nim)

        # 2. Legal classroom mapping
        for mid, meeting in self.meetings.items():
            valid_classrooms = [
                classroom.code
                for classroom in self.classrooms.values()
                if classroom.capacity >= meeting.student_count
            ]
            self.legal_classrooms_by_meeting[mid] = valid_classrooms

        print("Lookup indices built.")

    # Utility getters
    def get_meeting(self, mid: int) -> ClassMeeting:
        return self.meetings[mid]

    def get_classroom(self, code: str) -> Classroom:
        return self.classrooms[code]

    def get_student(self, nim: str) -> Student:
        return self.students[nim]
    
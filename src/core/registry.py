from models import Course, Classroom, Student, ClassMeeting
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Registry:
    courses: Dict[str, Course]
    classrooms: Dict[str, Classroom]
    students: Dict[str, Student]
    meetings: Dict[str, ClassMeeting]

    # Look up indices
    meeting_of_student: Dict[str, List[int]]
    students_of_meeting: Dict[int, List[str]]
    legal_classrooms_by_meeting: Dict[int, List[str]]

    def load_from_json(self, file_path: str) -> None:
        """Load and parse input JSON file, then call generate_meetings() and build_indices()."""
        ...

    def generate_meetings(self) -> None:
        """Expand each course into ClassMeeting units (1 per SKS)."""
        meeting_id = 0
        for course in self.courses.values():
            for i in range(course.credits):
                self.meetings[meeting_id] = ClassMeeting(
                    meeting_id=meeting_id,
                    course_code=course.code,
                    class_code=course.code.split("_")[1] if "_" in course.code else None,
                    duration_hours=1,
                    student_count=course.student_count
                )
                meeting_id += 1
        print(f"Generated {len(self.meetings)} meetings.")


    def build_indices(self) -> None:
        """Precompute relationships for faster conflict checking."""
        # Clear previous data
        self.meeting_of_student.clear()
        self.students_of_meeting.clear()
        self.legal_classrooms_by_meeting.clear()

        # 1. Meeting <-> Student mapping
        for student in self.students.values():
            self.meeting_of_student[student.nim] = []
            for course_code in student.course_list:
                for mid, meeting in self.meetings.items():
                    if meeting.course_code == course_code:
                        self.meeting_of_student[student.nim].append(mid)
                        self.students_of_meeting.setdefault(mid, []).append(student.nim)
        # 2. Legal class mapping
        for mid, meeting in self.meetings.items():
            valid_classrooms = [
                classroom.code for classroom in self.classrooms.values()
                if classroom.capacity >= meeting.student_count
            ]
            self.legal_classrooms_by_meeting[mid] = valid_classrooms
        print("Lookup indices built.")

        

    # utility getters
    def get_meeting(self, mid: int) -> ClassMeeting:
        return self.meetings[mid]

    def get_room(self, code: str) -> Classroom:
        return self.rooms[code]

    def get_student(self, nim: str) -> Student:
        return self.students[nim]

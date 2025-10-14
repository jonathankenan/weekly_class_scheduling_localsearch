from utils.input_parser import load_json

file_path = (
    "C:/Users/Mahesa/OneDrive/ITB/Coding/College/Academic/IF/"
    "Smt-5/AI/tugas/tubes/Tubes1_AI_ngermnkibols/data/input/example.json"
)

courses, classrooms, students = load_json(file_path)

print(f"Total courses: {len(courses)}")
print(f"Total classrooms: {len(classrooms)}")
print(f"Total students: {len(students)}")

print("\nSample Course:")
for c in list(courses.values())[:1]:
    print(c)

print("\nSample Classroom:")
for r in list(classrooms.values())[:1]:
    print(r)

print("\nSample Student:")
for s in list(students.values())[:1]:
    print(s)

# Test Registry
from core.registry import Registry

# 1️⃣  Init registry and load data
reg = Registry()
reg.load_from_json(file_path)

# 2️⃣  Print summary
print(f"\nCourses: {len(reg.courses)}")
print(f"Classrooms: {len(reg.classrooms)}")
print(f"Students: {len(reg.students)}")
print(f"Meetings generated: {len(reg.meetings)}")

# 3️⃣  Spot check: 1 student’s meetings
sample_nim = list(reg.students.keys())[0]
print(f"\nMeetings of student {sample_nim}: {reg.meetings_of_student[sample_nim]}")

# 4️⃣  Spot check: 1 meeting’s legal classrooms
mid = list(reg.meetings.keys())[0]
print(f"Legal classrooms for meeting {mid}: {reg.legal_classrooms_by_meeting[mid]}")

# 5️⃣  Spot check: 1 meeting’s students
print(f"Students of meeting {mid}: {reg.students_of_meeting[mid]}")

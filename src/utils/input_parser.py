import json
import os
from core.models import Classroom, Course, Student

def load_json(file_path: str):
    """
    Parse JSON file from the official AI Lab 2025/2026 format.
    Returns:
        courses_dict, classrooms_dict, students_dict
    """

    try:
        with open(file_path, 'r') as file:
            data_json = json.load(file)
            file_name = os.path.basename(file_path)
        print(f"Successfully loaded data from {file_name}")

        # Extract top-level keys (based on the spec)
        raw_courses = data_json["kelas_mata_kuliah"]
        raw_classrooms = data_json["ruangan"]
        raw_students = data_json["mahasiswa"]

        courses = {}
        classrooms = {}
        students = {}

        # ---- Load Courses ----
        for course in raw_courses:
            code = course["kode"]
            student_count = course["jumlah_mahasiswa"]
            credits = course["sks"]
            new_course = Course(code, student_count, credits)
            courses[code] = new_course

        # ---- Load Classrooms ----
        for cls in raw_classrooms:
            class_code = cls["kode"]
            capacity = cls["kuota"]
            new_classroom = Classroom(class_code, capacity)
            classrooms[class_code] = new_classroom

        # ---- Load Students ----
        for student in raw_students:
            nim = student["nim"]
            course_list = student["daftar_mk"]
            priority = student["prioritas"]
            new_student = Student(nim, course_list, priority)
            students[nim] = new_student

        return courses, classrooms, students

    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format.")

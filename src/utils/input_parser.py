import json
import os
from core.models import Classroom, Course, Student

def load_json(file_path: str):
    """
    Parse JSON file from the official AI Lab 2025/2026 format.
    
    Args:
        file_path: Path to the JSON file containing course scheduling data
        
    Returns:
        tuple: (courses_dict, classrooms_dict, students_dict)
            - courses_dict: Dictionary mapping course codes to Course objects
            - classrooms_dict: Dictionary mapping room codes to Classroom objects  
            - students_dict: Dictionary mapping student NIMs to Student objects
    """

    try:
        # Load and parse JSON file
        with open(file_path, 'r') as file:
            data_json = json.load(file)
            file_name = os.path.basename(file_path)
        print(f"Successfully loaded data from {file_name}")

        # Extract top-level keys from JSON structure
        raw_courses = data_json["kelas_mata_kuliah"]      # Course data array
        raw_classrooms = data_json["ruangan"]             # Classroom data array
        raw_students = data_json["mahasiswa"]             # Student data array

        # Initialize empty dictionaries for parsed data
        courses = {}
        classrooms = {}
        students = {}

        # Parse courses data into Course objects
        for course in raw_courses:
            code = course["kode"]                         # Course code identifier
            student_count = course["jumlah_mahasiswa"]    # Number of enrolled students
            credits = course["sks"]                       # Credit hours
            new_course = Course(code, student_count, credits)
            courses[code] = new_course

        # Parse classrooms data into Classroom objects
        for cls in raw_classrooms:
            class_code = cls["kode"]                      # Room identifier
            capacity = cls["kuota"]                       # Maximum capacity
            new_classroom = Classroom(class_code, capacity)
            classrooms[class_code] = new_classroom

        # Parse students data into Student objects
        for student in raw_students:
            nim = student["nim"]                          # Student ID number
            course_list = student["daftar_mk"]            # List of courses student wants
            priority = student["prioritas"]               # Priority ranking for each course
            new_student = Student(nim, course_list, priority)
            students[nim] = new_student

        return courses, classrooms, students

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None, None, None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return None, None, None
    except KeyError as e:
        print(f"Error: Missing required key in JSON: {e}")
        return None, None, None
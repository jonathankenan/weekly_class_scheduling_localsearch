import json
import os
from models import Class, Course, Student

def load_json(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data_json = json.load(file)
            file_name = os.path.basename(file_path)
        print(f"Successfully loaded data from {file_name}")

        # Extract each feature
        courses = data_json['courses']
        classes = data_json['classes']
        students = data_json['students']

        course_list, class_list, student_list = [], [], []

        for course in courses:
            code = course['code']
            student_count = course['student_count']
            credits = course['credits']
            new_course = Course(code, student_count, credits)
            print(new_course)
            course_list.append(new_course)

        for cls in classes:
             class_code = cls['code']
             capacity = cls['capacity']
             new_class = Class(class_code, capacity)
             print(new_class)
             class_list.append(new_class)

        for student in students:
            nim = student['nim']
            course_list = student['course_list'] 
            priority = student['priority']
            new_student = Student(nim, course_list, priority)
            print(new_student)
            student_list.append(new_student)
        
        return course_list, class_list, student_list
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")

    
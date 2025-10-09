class Course:
    def __init__(self, code: str, student_count: int, credits: int):
        self.code = code
        self.student_count = student_count
        self.credits = credits

class Class:
    def __init__(self, code: str, capacity: int):
        self.code = code
        self.capacity = capacity


class Student:
    def __init__(self, nim: str, course_list: list[str], priority: list[int]):
        self.nim = nim
        self.course_list = course_list
        self.priority = priority
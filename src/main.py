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

# ==== SCHEDULE TESTS ====
from core.schedule import Schedule
from core.models import DAY  # ganti sesuai lokasi enum DAY kamu

# domain kecil biar mudah diverifikasi
days = [DAY.MONDAY, DAY.TUESDAY]
hours = [7, 8, 9]
classroom_codes = list(reg.classrooms.keys())  # dari Registry yang sudah kamu buat

sched = Schedule(days, hours, classroom_codes)

# --- 1) Inisialisasi occupancy ---
total_positions = len(days) * len(hours) * len(classroom_codes)
print("\n[SCHEDULE] total_positions:", total_positions)
print("[SCHEDULE] sample cell (MONDAY,7):", sched.occupancy[(DAY.MONDAY, 7)])

# --- 2) place + is_empty + who_at + get_position ---
m1 = list(reg.meetings.keys())[0]  # ambil meeting_id pertama
legal_rooms_m1 = reg.legal_classrooms_by_meeting[m1]
room1 = legal_rooms_m1[0] if legal_rooms_m1 else classroom_codes[0]

ok_place = sched.place(m1, DAY.MONDAY, 7, room1)
print("\nPlace m1:", ok_place)
print("who_at(MONDAY,7,room1):", sched.who_at(DAY.MONDAY, 7, room1))
print("get_position(m1):", sched.get_position(m1))
print("is_empty(MONDAY,7,room1):", sched.is_empty(DAY.MONDAY, 7, room1))

# --- 3) place lagi di posisi lain (auto-relocate dari posisi lama) ---
ok_place_reloc = sched.place(m1, DAY.TUESDAY, 8, room1)  # harus pindah dari (MONDAY,7,room1)
print("\nRelocate m1 to (TUESDAY,8,room1):", ok_place_reloc)
print("who_at(MONDAY,7,room1) after relocate:", sched.who_at(DAY.MONDAY, 7, room1))
print("get_position(m1) after relocate:", sched.get_position(m1))

# --- 4) place m2, lalu move m2 ---
m2 = list(reg.meetings.keys())[1]
legal_rooms_m2 = reg.legal_classrooms_by_meeting[m2]
room2 = legal_rooms_m2[0] if legal_rooms_m2 else classroom_codes[-1]

ok_place2 = sched.place(m2, DAY.MONDAY, 9, room2)
print("\nPlace m2:", ok_place2, "at (MONDAY,9,", room2, ")")
print("get_position(m2):", sched.get_position(m2))

# move m2 ke slot kosong
ok_move = sched.move((DAY.MONDAY, 9, room2), (DAY.MONDAY, 7, room2))
print("Move m2 to (MONDAY,7,", room2, "):", ok_move)
print("who_at(MONDAY,7,room2):", sched.who_at(DAY.MONDAY, 7, room2))
print("get_position(m2) after move:", sched.get_position(m2))

# --- 5) swap antara posisi m1 dan m2 ---
pos_m1 = sched.get_position(m1)  # (TUESDAY,8,room1)
pos_m2 = sched.get_position(m2)  # (MONDAY,7,room2)
ok_swap = sched.swap(pos_m1, pos_m2)
print("\nSwap m1<->m2:", ok_swap)
print("get_position(m1) after swap:", sched.get_position(m1))
print("get_position(m2) after swap:", sched.get_position(m2))

# --- 6) remove ---
pos_m1_after = sched.get_position(m1)
removed_mid = sched.remove(*pos_m1_after)  # unpack (day,hour,room)
print("\nRemoved mid:", removed_mid)
print("who_at(pos_m1_after) now:", sched.who_at(pos_m1_after[0], pos_m1_after[1], pos_m1_after[2]))
print("get_position(m1) after remove:", sched.get_position(m1))

# --- 7) all_free_positions & iter_assignments sanity ---
free_positions = sched.all_free_positions()
assignments = sched.iter_assignments()
print("\nfree_positions count:", len(free_positions), "/", total_positions)
print("assignments:", assignments)

# --- 8) Assertions untuk sanity check (boleh kamu comment kalau nggak mau assert) ---
assert sched.get_position(m1) is None, "m1 harus sudah terhapus dari jadwal"
assert all(len(row) == len(classroom_codes) for row in [sched.occupancy[(d, h)] for d in days for h in hours])
assert len(assignments) >= 1, "minimal m2 masih ditempatkan"

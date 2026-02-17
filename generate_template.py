import pandas as pd
import json
import os

# Configuration
os.makedirs("data", exist_ok=True)

# 1. SALLES (Compatible models.py + run_scheduler.py)
# On met assez de salles pour ne pas bloquer le moteur
rooms = [
    {"id": "R1", "name": "Amphi Principal", "capacity": 200, "type": "amphitheatre", "equipment": ["Projector"], "building": "A", "floor": 0},
    {"id": "R2", "name": "Amphi Secondaire", "capacity": 100, "type": "amphitheatre", "equipment": ["Projector"], "building": "A", "floor": 1},
    {"id": "R3", "name": "Salle TD 101", "capacity": 40, "type": "td_room", "equipment": ["Whiteboard"], "building": "B", "floor": 1},
    {"id": "R4", "name": "Salle TD 102", "capacity": 40, "type": "td_room", "equipment": ["Whiteboard"], "building": "B", "floor": 1},
    {"id": "R5", "name": "Labo Info 1", "capacity": 30, "type": "lab", "equipment": ["25 PC"], "building": "C", "floor": 2},
    {"id": "R6", "name": "Labo Info 2", "capacity": 30, "type": "lab", "equipment": ["25 PC"], "building": "C", "floor": 2}
]
with open("data/rooms.json", "w", encoding='utf-8') as f: json.dump(rooms, f, indent=4)

# 2. ENSEIGNANTS (Compatible models.py)
teachers = [
    {"id": "T1", "name": "Dr. Turing (Info)", "specialties": ["Algo"], "can_teach": [], "max_hours_per_week": 20, "unavailable_slots": [], "preferred_slots": []},
    {"id": "T2", "name": "Pr. Hopper (Dev)", "specialties": ["Web"], "can_teach": [], "max_hours_per_week": 20, "unavailable_slots": [], "preferred_slots": []},
    {"id": "T3", "name": "Dr. Lovelace (Maths)", "specialties": ["Maths"], "can_teach": [], "max_hours_per_week": 20, "unavailable_slots": [], "preferred_slots": []},
    {"id": "T4", "name": "M. Boole (Logique)", "specialties": ["Systeme"], "can_teach": [], "max_hours_per_week": 20, "unavailable_slots": [], "preferred_slots": []}
]
with open("data/teachers.json", "w", encoding='utf-8') as f: json.dump(teachers, f, indent=4)

# 3. GROUPES (Compatible models.py)
groups = [
    {"id": "G1", "size": 30, "semester": 1, "courses": [], "preferences": {}},
    {"id": "G2", "size": 30, "semester": 1, "courses": [], "preferences": {}}
]
with open("data/groups.json", "w", encoding='utf-8') as f: json.dump(groups, f, indent=4)

# 4. TIMESLOTS (Standard)
timeslots = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
for d in days:
    for h in [8, 10, 14, 16]:
        timeslots.append({"id": f"TS_{d}_{h}", "day": d, "start": f"{h:02}:00", "end": f"{h+2:02}:00", "duration": 2, "category": "standard"})
with open("data/timeslots.json", "w", encoding='utf-8') as f: json.dump(timeslots, f, indent=4)

# 5. COURS (Excel Compatible models.py + run_scheduler.py)
# Structure logique : Fondamentaux (CM) -> Travaux Dirigés (TD) -> Travaux Pratiques (TP)
courses_list = []

# Matière 1 : Algorithmique (T1)
courses_list.append({"id": "ALGO_CM_G1", "name": "Algo (CM)", "type": "CM", "teacher": "T1", "group": "G1", "expected_students": 30, "prerequisites": "", "ects": 3, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})
courses_list.append({"id": "ALGO_TD_G1", "name": "Algo (TD)", "type": "TD", "teacher": "T1", "group": "G1", "expected_students": 30, "prerequisites": "ALGO_CM_G1", "ects": 2, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})
courses_list.append({"id": "ALGO_TP_G1", "name": "Algo (TP)", "type": "TP", "teacher": "T1", "group": "G1", "expected_students": 30, "prerequisites": "ALGO_TD_G1", "ects": 2, "weekly_hours": 2, "semester": 1, "required_equipment": ["PC"], "incompatible_courses": []})

# Matière 2 : Développement Web (T2)
courses_list.append({"id": "WEB_CM_G1", "name": "Web (CM)", "type": "CM", "teacher": "T2", "group": "G1", "expected_students": 30, "prerequisites": "", "ects": 3, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})
courses_list.append({"id": "WEB_TP_G1", "name": "Web (TP)", "type": "TP", "teacher": "T2", "group": "G1", "expected_students": 30, "prerequisites": "WEB_CM_G1", "ects": 2, "weekly_hours": 2, "semester": 1, "required_equipment": ["PC"], "incompatible_courses": []})

# Matière 3 : Mathématiques (T3) - Pour Groupe 2 cette fois
courses_list.append({"id": "MATH_CM_G2", "name": "Maths (CM)", "type": "CM", "teacher": "T3", "group": "G2", "expected_students": 30, "prerequisites": "", "ects": 3, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})
courses_list.append({"id": "MATH_TD_G2", "name": "Maths (TD)", "type": "TD", "teacher": "T3", "group": "G2", "expected_students": 30, "prerequisites": "MATH_CM_G2", "ects": 2, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})

# Matière 4 : Système (T4) - Mixte
courses_list.append({"id": "SYS_CM_G1", "name": "Système (CM)", "type": "CM", "teacher": "T4", "group": "G1", "expected_students": 30, "prerequisites": "", "ects": 3, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})
courses_list.append({"id": "SYS_CM_G2", "name": "Système (CM)", "type": "CM", "teacher": "T4", "group": "G2", "expected_students": 30, "prerequisites": "", "ects": 3, "weekly_hours": 2, "semester": 1, "required_equipment": [], "incompatible_courses": []})

# Génération Excel
df = pd.DataFrame(courses_list)
df.to_excel("final_compatible_list.xlsx", index=False)

print("✅ Fichier 'final_compatible_list.xlsx' généré avec succès !")
print("✅ JSONs de configuration (teachers, rooms, groups) synchronisés.")
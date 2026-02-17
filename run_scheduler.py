import json
import os
import pymzn
from main import check_logic_consistency, validate_data_feasibility

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)

# --- CORRECTION 1 : Ajout des paramètres dans la signature ---
def run_scheduler(max_slots_per_day=8, nb_jours=5):
    courses = load_json("courses.json")
    rooms = load_json("rooms.json")
    teachers = load_json("teachers.json")
    groups = load_json("groups.json")
    timeslots = load_json("timeslots.json")

    check_logic_consistency(courses) 
    if not validate_data_feasibility(courses, rooms):
        return None

    # --- FILTRAGE DYNAMIQUE ---
    day_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
    active_timeslots = [ts for ts in timeslots if day_map.get(ts['day'], 7) <= nb_jours]

    teacher_index = {t["id"]: i + 1 for i, t in enumerate(teachers)}
    group_index = {g["id"]: i + 1 for i, g in enumerate(groups)}
    type_map = {"CM": 1, "TD": 2, "TP": 3}
    room_type_map = {"amphitheatre": 1, "td_room": 2, "lab": 3}

    # --- CORRECTION 2 : Disponibilité basée sur active_timeslots ---
    teacher_available = []
    for t in teachers:
        row = []
        unavailable = set(t["unavailable_slots"])
        for ts in active_timeslots: # On boucle sur les créneaux ACTIFS uniquement
            row.append(0 if ts["id"] in unavailable else 1)
        teacher_available.append(row)

    teacher_max_hours = [t["max_hours_per_week"] for t in teachers]

    # Matrice des prérequis (inchangée)
    is_prereq = [[False for _ in range(len(courses))] for _ in range(len(courses))]
    course_id_to_idx = {c['id']: i for i, c in enumerate(courses)}
    for i, course in enumerate(courses):
        for p_id in course.get('prerequisites', []):
            if p_id in course_id_to_idx:
                is_prereq[i][course_id_to_idx[p_id]] = True

    # --- PRÉPARATION DES DONNÉES MINIZINC ---
    mzn_data = {
        'nbCours': len(courses),
        'nbSalles': len(rooms),
        'nbTeachers': len(teachers),
        'nbGroups': len(groups),
        'nbSlotsTotal': len(active_timeslots),
        'maxSlotsPerDay': max_slots_per_day,
        'maxSessions': 1,
        'slot_to_day': [day_map[ts['day']] for ts in active_timeslots],
        'is_lunch': [1 if ts['start'] == "12:00" else 0 for ts in active_timeslots],
        'slot_to_pos': [((i % max_slots_per_day) + 1) for i in range(len(active_timeslots))],
        'is_prereq': is_prereq, 
        'course_teacher': [teacher_index[c['teacher']] for c in courses],
        'course_group': [group_index[c['group']] for c in courses],
        'course_type': [type_map[c['type']] for c in courses],
        'course_expected_students': [c['expected_students'] for c in courses],
        'room_capacity': [r['capacity'] for r in rooms],
        'room_type': [room_type_map[r['type']] for r in rooms],
        'teacher_available': teacher_available,
        'teacher_max_hours': teacher_max_hours
    }

    result = pymzn.minizinc("scheduler.mzn", data=mzn_data)

    if not result:
        return None

    schedule = []
    slot_matrix = result[0]['slot_idx']
    room_matrix = result[0]['salle']

    for c_idx, c in enumerate(courses):
        slot_val = slot_matrix[c_idx]
        room_val = room_matrix[c_idx]

        if slot_val == 0:
            continue

        # --- CORRECTION 3 : Utilisation de active_timeslots pour le schedule final ---
        ts = active_timeslots[slot_val - 1]
        room = rooms[room_val - 1]

        teacher_name = teachers[mzn_data['course_teacher'][c_idx] - 1]['name']
        group_name = groups[mzn_data['course_group'][c_idx] - 1]['id']

        schedule.append({
            "Cours": c['name'],
            "Type": c['type'],
            "Prof": teacher_name,
            "Groupe": group_name,
            "Jour": ts['day'],
            "Heure": f"{ts['start']} - {ts['end']}",
            "Salle": room['name']
        })

    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
    def get_start_hour(item):
        return int(item["Heure"].split(":")[0])

    schedule.sort(key=lambda x: (day_order.get(x["Jour"], 7), get_start_hour(x)))
    return schedule
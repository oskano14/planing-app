import json
import os
import pymzn
from main import check_logic_consistency, validate_data_feasibility

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)

def run_scheduler():
    courses = load_json("courses.json")
    rooms = load_json("rooms.json")
    teachers = load_json("teachers.json")
    groups = load_json("groups.json")
    timeslots = load_json("timeslots.json")

    check_logic_consistency(courses) 
    if not validate_data_feasibility(courses, rooms):
        return None


    day_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
    slot_to_day = [day_map[ts['day']] for ts in timeslots]

    is_lunch = [1 if ts['start'] == "12:00" else 0 for ts in timeslots]

    teacher_index = {t["id"]: i + 1 for i, t in enumerate(teachers)}
    group_index = {g["id"]: i + 1 for i, g in enumerate(groups)}

    type_map = {"CM": 1, "TD": 2, "TP": 3}

    room_type_map = {
        "amphitheatre": 1,
        "td_room": 2,
        "lab": 3
    }

    teacher_available = []

    for t in teachers:
        row = []
        unavailable = set(t["unavailable_slots"])

        for ts in timeslots:
            row.append(0 if ts["id"] in unavailable else 1)

        teacher_available.append(row)

    teacher_max_hours = [t["max_hours_per_week"] for t in teachers]
    # --- GÉNÉRATION DE LA MATRICE DES PRÉREQUIS ---
    # On initialise une matrice carrée de booléens (nbCours x nbCours)
    is_prereq = [[False for _ in range(len(courses))] for _ in range(len(courses))]
    course_id_to_idx = {c['id']: i for i, c in enumerate(courses)}

    for i, course in enumerate(courses):
        for p_id in course.get('prerequisites', []):
            if p_id in course_id_to_idx:
                # On marque que le cours i dépend du cours j
                is_prereq[i][course_id_to_idx[p_id]] = True

    # --- CALCUL DES PARAMÈTRES MANQUANTS ---
    # Calcul de maxSlotsPerDay et des positions
    counts = {}
    slot_to_pos = []
    for ts in timeslots:
        d = ts['day']
        counts[d] = counts.get(d, 0) + 1
        slot_to_pos.append(counts[d])
    maxSlotsPerDay = max(counts.values()) if counts else 0

    # Dans run_scheduler.py, avant l'appel à pymzn.minizinc
    mzn_data = {
        'nbCours': len(courses),
        'nbSalles': len(rooms),
        'nbTeachers': len(teachers),
        'nbGroups': len(groups),
        'nbSlotsTotal': len(timeslots),
        'maxSessions': 1, # Pour correspondre au .mzn
        
        #  AJOUTS INDISPENSABLES :
        'maxSlotsPerDay': 4, # Valeur par défaut ou calculée
        'slot_to_day': slot_to_day,
        'slot_to_pos': [((i % 4) + 1) for i in range(len(timeslots))], # Exemple de position 1..4
        'is_lunch': is_lunch,
        
        # Matrice des prérequis (récupérée de main.py)
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
    # On récupère les résultats (ce sont maintenant des listes d'entiers simples)
    slot_matrix = result[0]['slot_idx']
    room_matrix = result[0]['salle']

    for c_idx, c in enumerate(courses):
        # --- CORRECTION ICI : Accès direct en O(1) ---
        slot_val = slot_matrix[c_idx]
        room_val = room_matrix[c_idx]

        if slot_val == 0:
            continue

        ts = timeslots[slot_val - 1]
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

    day_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5
    }

    def get_start_hour(item):
        return int(item["Heure"].split(":")[0])

    schedule.sort(key=lambda x: (day_order[x["Jour"]], get_start_hour(x)))

    return schedule


if __name__ == "__main__":
    res = run_scheduler()
    if res:
        for r in res:
            print(r)
    else:
        print("Aucune solution trouvée")

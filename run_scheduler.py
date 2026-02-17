import json
import os
import pymzn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)



def check_logic_consistency(courses):
    graph = {c["id"]: c["prerequisites"] for c in courses}

    visited = set()
    stack = set()

    def dfs(node):
        if node in stack:
            raise ValueError(f"Cycle détecté autour de {node}")
        if node in visited:
            return

        stack.add(node)
        for neigh in graph.get(node, []):
            dfs(neigh)
        stack.remove(node)
        visited.add(node)

    for course in graph:
        dfs(course)



def run_scheduler():
    courses = load_json("courses.json")
    rooms = load_json("rooms.json")
    teachers = load_json("teachers.json")
    groups = load_json("groups.json")
    timeslots = load_json("timeslots.json")

    check_logic_consistency(courses)


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


    mzn_data = {
        'nbCours': len(courses),
        'nbSalles': len(rooms),
        'nbTeachers': len(teachers),
        'nbGroups': len(groups),
        'nbSlotsTotal': len(timeslots),

        'slot_to_day': slot_to_day,
        'is_lunch': is_lunch,

        'course_teacher': [teacher_index[c['teacher']] for c in courses],
        'course_group': [group_index[c['group']] for c in courses],
        'course_type': [type_map[c['type']] for c in courses],

        'course_expected_students': [c['expected_students'] for c in courses],

        'room_capacity': [r['capacity'] for r in rooms],
        'room_type': [room_type_map[r['type']] for r in rooms],

        # ⭐ NOUVEAU
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
        for s_idx in range(len(slot_matrix[c_idx])):
            slot_val = slot_matrix[c_idx][s_idx]

            if slot_val == 0:
                continue

            room_val = room_matrix[c_idx][s_idx]

            ts = timeslots[slot_val - 1]
            room = rooms[room_val - 1]

            teacher_name = teachers[mzn_data['course_teacher'][c_idx] - 1]['name']
            group_name = groups[mzn_data['course_group'][c_idx] - 1]['id']

            schedule.append({
                "Cours": c['name'],
                "Type": c['type'],
                "Session": s_idx + 1,
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

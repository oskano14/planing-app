import json
from pyDatalog import pyDatalog
import pymzn  # Assure-toi d'avoir installé MiniZinc et pymzn

# --- ÉTAPE 1 : CONFIGURATION LOGIQUE (pyDatalog) ---
pyDatalog.create_terms('X, Y, Z, prerequis, prerequis_transitif, cycle_erreur')

def check_logic_consistency(courses):
    """Vérifie l'absence de cycles dans les prérequis (Objectif OF2)"""
    for c in courses:
        for p in c['prerequisites']:
            + prerequis(c['id'], p)
    
    # Règle de transitivité et de cycle
    prerequis_transitif(X, Y) <= prerequis(X, Y)
    prerequis_transitif(X, Y) <= prerequis(X, Z) & prerequis_transitif(Z, Y)
    cycle_erreur(X) <= prerequis_transitif(X, X)
    
    if cycle_erreur(X):
        errors = [result[0] for result in cycle_erreur(X)]
        raise ValueError(f"CRITICAL: Cycle détecté dans les prérequis : {errors}")
    print("✓ Cohérence logique des prérequis validée.")

# --- ÉTAPE 2 : CHARGEMENT ET TRADUCTION ---
def run_scheduler():
    with open('data/courses.json') as f: courses = json.load(f)
    with open('data/rooms.json') as f: rooms = json.load(f)
    with open('data/teachers.json') as f: teachers = json.load(f)
    with open('data/groups.json') as f: groups = json.load(f)
    with open('data/timeslots.json') as f: timeslots = json.load(f)

    check_logic_consistency(courses)

    # 1. Création des mappings pour les jours et les heures
    day_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
    slot_to_day = [day_map[ts['day']] for ts in timeslots]
    
    # On calcule la position du créneau dans la journée (1, 2, 3...)
    slot_to_pos = []
    counts = {}
    for ts in timeslots:
        d = ts['day']
        counts[d] = counts.get(d, 0) + 1
        slot_to_pos.append(counts[d])

    mzn_data = {
        'nbCours': len(courses),
        'nbSalles': len(rooms),
        'nbTeachers': len(teachers),
        'nbGroups': len(groups),
        'nbSlotsTotal': len(timeslots),
        'maxSlotsPerDay': max(counts.values()) if counts else 0, # Pour CS1
        
        # Envoi des nouveaux tableaux de correspondance
        'slot_to_day': slot_to_day,
        'slot_to_pos': slot_to_pos,
        'is_morning': [1 if ts['category'] == 'morning' else 0 for ts in timeslots],
        
        'course_expected_students': [c['expected_students'] for c in courses],
        'course_teacher': [int(c['id'][-1]) for c in courses],
        'course_group': [1, 2, 1, 2, 1], 
        'course_type': [1, 2, 2, 3, 3],
        'room_capacity': [r['capacity'] for r in rooms],
        'room_type': [1, 2, 3]
    }

    print("→ Lancement du solveur MiniZinc...")
    result = pymzn.minizinc('scheduler.mzn', data=mzn_data, solver=pymzn.gecode)

    # Dans ton fichier Python, après result = pymzn.minizinc(...)
    if result:
        print("\n--- EMPLOI DU TEMPS DÉTAILLÉ ---")
        for i in range(len(courses)):
            # On récupère l'index choisi par MiniZinc
            s_idx = result[0]['slot_idx'][i] - 1  # -1 car MiniZinc commence à 1
            room_id = result[0]['salle'][i] - 1
            
            # On va chercher les vraies infos dans tes JSON
            temps = timeslots[s_idx]
            salle_nom = rooms[room_id]['name']
            
            print(f"Cours: {courses[i]['id']} | {temps['day']} {temps['start']}-{temps['end']} | Salle: {salle_nom}")
    else:
        # Si MiniZinc ne renvoie rien, c'est qu'il n'y a pas de solution possible
        print("\n❌ ERREUR : Aucune solution possible avec les contraintes actuelles.")
                


if __name__ == "__main__":
    run_scheduler()
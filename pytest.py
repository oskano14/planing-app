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
    # Chargement des fichiers JSON
    with open('data/courses.json') as f: courses = json.load(f)
    with open('data/rooms.json') as f: rooms = json.load(f)
    with open('data/teachers.json') as f: teachers = json.load(f)
    with open('data/groups.json') as f: groups = json.load(f)
    

    # Validation logique (pyDatalog)
    check_logic_consistency(courses)

    # Mapping des types (Simple conversion pour le solveur)
    # 1: Amphi/CM, 2: TD, 3: Labo/TP
    type_map = {"CM": 1, "TD": 2, "TP": 3}
    room_type_map = {"amphitheatre": 1, "td_room": 2, "lab": 3}

    # Préparation des données pour MiniZinc (OT2)
    mzn_data = {
        'nbCours': len(courses),
        'nbSalles': len(rooms),
        'nbTeachers': len(teachers),
        'nbGroups': len(groups),
        
        # Caractéristiques des cours
        'course_expected_students': [c['expected_students'] for c in courses],
        'course_teacher': [int(c['id'][-1]) for c in courses], # Exemple: extrait l'ID numérique
        'course_group': [1, 2, 3, 4, 1], # À automatiser selon tes besoins
        'course_type': [type_map.get(c['type'], 2) for c in courses],
        
        # Caractéristiques des salles
        'room_capacity': [r['capacity'] for r in rooms],
        'room_type': [room_type_map.get(r['type']) for r in rooms]
    }

    print("→ Lancement du solveur MiniZinc (Solver: Gecode)...")
    # Appel effectif du solveur
    result = pymzn.minizinc('scheduler.mzn', data=mzn_data, solver=pymzn.gecode)
    


    if result:
        print("\n--- EMPLOI DU TEMPS GÉNÉRÉ ---")
        for i in range(len(courses)):
            # On récupère les index trouvés par MiniZinc
            j = result[0]['jour'][i]
            c = result[0]['creneau'][i]
            s = result[0]['salle'][i]
            
            print(f"Cours: {courses[i]['id']} -> Jour {j}, Créneau {c}, Salle: {rooms[s-1]['name']}")
    else:
        print("Aucune solution trouvée. Vérifiez les contraintes dures !")


if __name__ == "__main__":
    run_scheduler()
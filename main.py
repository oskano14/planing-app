import json
from pyDatalog import pyDatalog
import pymzn  # Assure-toi d'avoir installé MiniZinc et pymzn

# --- ÉTAPE 1 : CONFIGURATION LOGIQUE (pyDatalog) ---
from pyDatalog import pyDatalog

def check_logic_consistency(courses):
    """
    Vérifie la cohérence logique des prérequis (Objectif OF2).
    """
    # 1. On vide la mémoire pour isoler les tests
    pyDatalog.clear()
    
    # 2. On définit les termes et les règles sous forme de texte
    # Cette méthode évite les NameError car pyDatalog compile le texte lui-même.
    pyDatalog.load("""
        prerequis_transitif(X, Y) <= prerequis(X, Y)
        prerequis_transitif(X, Y) <= prerequis(X, Z) & prerequis_transitif(Z, Y)
        cycle_erreur(X) <= prerequis_transitif(X, X)
    """)
    
    # 3. On ajoute les faits dynamiquement
    for c in courses:
        for p in c['prerequisites']:
            # On utilise l'assertion par fonction pour plus de sécurité
            pyDatalog.assert_fact('prerequis', c['id'], p)
    
    # 4. On lance la requête de détection de cycle
    resultats = pyDatalog.ask('cycle_erreur(X)')
    
    if resultats:
        # resultats.answers est une liste de tuples
        errors = [str(r[0]) for r in resultats.answers]
        raise ValueError(f"CRITICAL: Cycle détecté dans les prérequis : {errors}")
    
    print("✓ Cohérence logique des prérequis validée.")

def validate_data_feasibility(courses, rooms):
    """Vérifie si chaque cours peut mathématiquement entrer dans au moins une salle."""
    type_mapping = {"CM": "amphitheatre", "TD": "td_room", "TP": "lab"}
    for course in courses:
        compatible_rooms = [
            r for r in rooms 
            if r['type'] == type_mapping[course['type']] 
            and r['capacity'] >= course['expected_students']
        ]
        if not compatible_rooms:
            return False
    return True



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
    type_map = {"CM": 1, "TD": 2, "TP": 3}
    room_type_map = {"amphitheatre": 1, "td_room": 2, "lab": 3}
    
    # On calcule la position du créneau dans la journée (1, 2, 3...)
    slot_to_pos = []
    counts = {}
    for ts in timeslots:
        d = ts['day']
        counts[d] = counts.get(d, 0) + 1
        slot_to_pos.append(counts[d])


    if not validate_data_feasibility(courses, rooms):
        print("❌ Annulation...")
        return

    
    # 1. Matrice des prérequis (pour la chronologie)
    is_prereq = [[False for _ in range(len(courses))] for _ in range(len(courses))]
    course_id_to_idx = {c['id']: i for i, c in enumerate(courses)}
    for i, course in enumerate(courses):
        for p_id in course.get('prerequisites', []):
            if p_id in course_id_to_idx:
                is_prereq[i][course_id_to_idx[p_id]] = True

    # 2. Matrice de disponibilité des profs (pour CH1)
    teacher_avail = [[1 for _ in range(len(timeslots))] for _ in range(len(teachers))]
    slot_id_to_idx = {ts['id']: i for i, ts in enumerate(timeslots)}
    for i, teacher in enumerate(teachers):
        for unavail_ts in teacher.get('unavailable_slots', []):
            if unavail_ts in slot_id_to_idx:
                teacher_avail[i][slot_id_to_idx[unavail_ts]] = 0

    mzn_data = {
    'nbCours': len(courses),
    'nbSalles': len(rooms),
    'nbTeachers': len(teachers),
    'nbGroups': len(groups),
    'nbSlotsTotal': len(timeslots),
    'maxSlotsPerDay': max(counts.values()) if counts else 0,
    
    'slot_to_day': slot_to_day,
    'slot_to_pos': slot_to_pos,
    'is_morning': [1 if ts['category'] == 'morning' else 0 for ts in timeslots],
    
    # ON RÉCUPÈRE LES VRAIES DONNÉES
    'course_expected_students': [c['expected_students'] for c in courses],
    
    # On trouve le type automatiquement (INFO209 deviendra 1 pour CM)
    'course_type': [type_map[c['type']] for c in courses],
    
    # On trouve le bon prof (On cherche quel prof peut enseigner ce cours)
    'course_teacher': [
        next((i+1 for i, t in enumerate(teachers) if c['id'] in t['can_teach']), 1)
        for c in courses
    ],
    
    # On associe un groupe (Simplifié pour le test)
    'course_group': [1, 1, 2, 2, 1], 
    
    'room_capacity': [r['capacity'] for r in rooms],
    'room_type': [room_type_map[r['type']] for r in rooms],
    'is_prereq': is_prereq,
    'teacher_availability': teacher_avail
  }

    print("→ Lancement du solveur MiniZinc...")
    result = pymzn.minizinc('scheduler.mzn', data=mzn_data, solver=pymzn.gecode)

    # Dans ton fichier Python, après result = pymzn.minizinc(...)
    if result:
        print("\n" + "="*95)
        print(f"{'ID':<8} | {'NOM DU COURS':<25} | {'GROUPE':<8} | {'ENSEIGNANT':<15} | {'HORAIRE'}")
        print("-" * 95)
        
        group_names = [g['id'] for g in groups]
        teacher_names = [t['name'] for t in teachers]
        
        for i in range(len(courses)):
            s_idx = result[0]['slot_idx'][i] - 1 
            room_id = result[0]['salle'][i] - 1
            
            # Récupération du nom complet du cours depuis JSON
            id_cours = courses[i]['id']
            nom_cours = courses[i]['name']
            
            prof_idx = mzn_data['course_teacher'][i] - 1
            nom_prof = teacher_names[prof_idx]
            
            group_idx = mzn_data['course_group'][i] - 1
            nom_groupe = group_names[group_idx]
            
            temps = timeslots[s_idx]
            salle_nom = rooms[room_id]['name']
            
            affichage_temps = f"{temps['day'][:3]}. {temps['start']}"
            
            print(f"{id_cours:<8} | {nom_cours:<25} | {nom_groupe:<8} | {nom_prof:<15} | {affichage_temps} ({salle_nom})")
        print("="*95)
    else:
        # Si MiniZinc ne renvoie rien, c'est qu'il n'y a pas de solution possible
        print("\n❌ ERREUR : Aucune solution possible avec les contraintes actuelles.")
                


if __name__ == "__main__":
    run_scheduler()
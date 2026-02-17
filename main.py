import json
from pyDatalog import pyDatalog
import pymzn  # Assure-toi d'avoir installé MiniZinc et pymzn

# --- ÉTAPE 1 : CONFIGURATION LOGIQUE (pyDatalog) ---
from pyDatalog import pyDatalog

from pyDatalog import pyDatalog

def check_logic_consistency(courses):
    # 1. Nettoyage complet
    pyDatalog.clear()
    
    # 2. Création des termes nécessaires
    pyDatalog.create_terms('X, Y, Z, prerequis, prerequis_transitif, cycle_erreur')
    
    # 3. On définit TOUT dans un seul bloc load (Règles + Fait de sécurité)
    # On définit un fait bidon pour "prerequis" pour qu'il existe toujours
    pyDatalog.load("""
        prerequis('SECURE_ID', 'EMPTY')
        prerequis_transitif(X, Y) <= prerequis(X, Y)
        prerequis_transitif(X, Y) <= prerequis(X, Z) & prerequis_transitif(Z, Y)
        cycle_erreur(X) <= prerequis_transitif(X, X)
    """)
    
    has_real_prereqs = False
    for c in courses:
        p_list = c.get('prerequisites')
        
        # On gère le cas où p_list est une liste (venant de ton JSON ou Excel)
        if isinstance(p_list, list):
            for p in p_list:
                # Filtrage strict des valeurs nulles ou chaînes "None"
                if p and str(p).strip().lower() != 'none':
                    pyDatalog.assert_fact('prerequis', str(c['id']), str(p))
                    has_real_prereqs = True
    
    # 4. On lance la requête de détection de cycles
    if has_real_prereqs:
        # On demande explicitement les résultats pour cycle_erreur
        res = pyDatalog.ask('cycle_erreur(X)')
        if res and res.answers:
            errors = [str(ans[0]) for ans in res.answers]
            raise ValueError(f"⚠️ ERREUR LOGIQUE : Cycle de prérequis détecté sur : {errors}")

    print("✓ Cohérence logique validée.")

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




import json
from pyDatalog import pyDatalog
import pymzn  # Assure-toi d'avoir installé MiniZinc et pymzn

# --- ÉTAPE 1 : CONFIGURATION LOGIQUE (pyDatalog) ---
from pyDatalog import pyDatalog

def check_logic_consistency(courses):
    """
    Vérifie la cohérence logique des prérequis (Objectif OF2).
    """
    # 1. Nettoyage de la mémoire
    pyDatalog.clear()
    
    # 2. Déclaration des termes
    pyDatalog.create_terms('X, Y, Z, prerequis, prerequis_transitif, cycle_erreur')
    
    # 3. Définition des règles sans initialisation forcée de prerequis
    pyDatalog.load("""
        prerequis_transitif(X, Y) <= prerequis(X, Y)
        prerequis_transitif(X, Y) <= prerequis(X, Z) & prerequis_transitif(Z, Y)
        cycle_erreur(X) <= prerequis_transitif(X, X)
    """)
    
    # 4. Chargement sécurisé des faits
    has_facts = False
    for c in courses:
        # On vérifie que 'prerequisites' existe et n'est pas vide
        prereqs = c.get('prerequisites')
        if prereqs:
            for p in prereqs:
                pyDatalog.assert_fact('prerequis', c['id'], p)
                has_facts = True
    
    # 5. On ne lance la requête que si au moins un fait a été chargé
    # Cela évite l'erreur "Predicate without definition"
    if has_facts:
        resultats = pyDatalog.ask('cycle_erreur(X)')
        if resultats and resultats.answers:
            errors = [str(r[0]) for r in resultats.answers]
            raise ValueError(f"CRITICAL: Cycle détecté dans les prérequis : {errors}")
    
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




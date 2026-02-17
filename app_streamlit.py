import streamlit as st
import pandas as pd
import json

from run_scheduler import run_scheduler

st.title("SmartScheduler - Version Dev")

# --- CONFIGURATION ---
STRUCTURE_ATTENDUE = {
    "id": "Identifiant unique du cours (ex: INFO101, MATH201)",
    "name": "Nom complet de la matière (ex: Algorithmique, Anglais)",
    "teacher": "Identifiant de l'enseignant (ex: T1, T2)",
    "group": "Nom de la classe ou groupe d'étudiants (ex: DA1, DA2, Groupe_A)",
    "type": "Format du cours : CM (Amphi), TD (Salle de classe) ou TP (Labo)",
    "expected_students": "Nombre d'élèves prévus (ex: 30, 120)",
    "prerequisites": "Codes des cours requis avant celui-ci, séparés par une virgule (ex: INFO101, MATH101) ou laisser vide."
}

st.title("SmartScheduler - Import & Validation")

# --- SECTION INSTRUCTIONS ---
with st.expander("📖 Consulter le guide du format de fichier", expanded=True):
    st.write("Votre fichier doit contenir exactement ces colonnes :")
    # Création d'un petit tableau d'exemple pour l'utilisateur
    df_guide = pd.DataFrame([STRUCTURE_ATTENDUE]).T
    df_guide.columns = ["Description & Exemples"]
    st.table(df_guide)

uploaded_file = st.file_uploader("Chargez votre fichier (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        # --- VALIDATION DES COLONNES ---
        colonnes_presentes = set(df.columns)
        colonnes_manquantes = [col for col in STRUCTURE_ATTENDUE if col not in colonnes_presentes]

        if colonnes_manquantes:
            st.error(f"❌ **Erreur de format** : Il manque les colonnes suivantes : `{', '.join(colonnes_manquantes)}`.")
            st.warning("Veuillez corriger votre fichier et le charger à nouveau.")
        else:
            st.success("✅ Format de fichier valide !")
            st.dataframe(df.head())

            if st.button("Valider et Convertir en JSON"):
                # Ta logique de conversion existante...
                courses_list = []
                for _, row in df.iterrows():
                    course_dict = row.to_dict()
                    # Gestion propre des prérequis (chaîne -> liste)
                    p = course_dict.get('prerequisites', "")
                    course_dict['prerequisites'] = [item.strip() for item in str(p).split(',')] if pd.notna(p) and p != "" else []
                    courses_list.append(course_dict)

                with open("data/courses.json", "w", encoding='utf-8') as f:
                    json.dump(courses_list, f, indent=4, ensure_ascii=False)
                st.success(f"Données enregistrées ({len(courses_list)} cours).")

    except Exception as e:
        st.error(f"Erreur technique : {e}")

st.divider()

# --- DANS LA SIDEBAR ---
st.sidebar.header("⚙️ Paramètres de planification")
# On capture les valeurs dans des variables
val_max_slots = st.sidebar.slider("Nombre max de créneaux par jour", 4, 10, 8)
val_nb_jours = st.sidebar.select_slider("Nombre de jours travaillés", options=[5, 6], value=5)

# --- DANS LE BOUTON DE GÉNÉRATION ---
if st.button("Lancer l'optimisation"):
    with st.spinner("Calcul en cours..."):
        # On passe les curseurs en paramètres
        schedule = run_scheduler(max_slots_per_day=val_max_slots, nb_jours=val_nb_jours)
        if schedule:
            st.table(schedule)
# 🗓️ SmartScheduler - Branch feature/app

SmartScheduler est une application avancée d'optimisation d'emplois du temps universitaires. Cette branche introduit une interface utilisateur interactive, la gestion de données massives via Pandas et un moteur de résolution par contraintes optimisé pour la performance.

## 🚀 Fonctionnalités Clés

* **Axe 1 : Importation & Interface**
Support complet du Drag & Drop pour fichiers Excel (.xlsx) et CSV. Une Sidebar interactive permet de régler en temps réel le nombre de jours (5 ou 6) et les créneaux (4 à 10).

* **Axe 2 : Validation Logique (pyDatalog)**
Vérification dynamique de l'intégrité référentielle entre les fichiers JSON et les données importées. Utilisation de faits SECURE_ID pour garantir la cohérence des prérequis sans erreurs de définition.

* **Axe 3 : Moteur de Résolution (MiniZinc)**
Modélisation CSP (Constraint Satisfaction Problem) avec la directive solve satisfy. L'architecture est découplée : les contrôleurs Streamlit pilotent directement les variables mzn_data.

* **Axe 4 : Performance & Scalabilité**
Moteur de Stress-Test capable de traiter 50 cours simultanément. Optimisation de l'accès aux données avec une complexité en O(1) pour garantir des réponses instantanées.

## 📂 Structure de la Branche
   ```bash

    planing-app/
    ├── data/                  (Fichiers de configuration JSON)
    ├── generate_template.py   (Générateur d'écosystème complet)
    ├── app_streamlit.py       (Interface et curseurs de réglage)
    ├── run_scheduler.py       (Liaison Python <-> MiniZinc)
    ├── main.py                (Validation logique pyDatalog)
    ├── scheduler.mzn          (Modèle CSP optimisé)
    └── requirements.txt       (pandas, openpyxl, pymzn, streamlit)
  ```

## 🛠️ Installation & Configuration

* **Installer les dépendances :**
    ```bash
    pip install -r requirments.txt
    ```

* **Générer les données de test :**
    ```bash
    python generate_template.py
    ```
  
* **Lancer l'application :**
    ```bash
    streamlit run app_streamlit.py
    ```

## 📋 Format de Fichier Attendu (Excel/CSV)

- Colonne : id | Description : Identifiant unique | Exemple : C001
- Colonne : name | Description : Nom de la matière | Exemple : Algorithmique
- Colonne : teacher | Description : ID du professeur | Exemple : T1
- Colonne : group | Description : Groupes d'étudiants | Exemple : DA1, G2
- Colonne : type | Description : Format (CM, TD, TP) | Exemple : CM
- Colonne : prerequisites | Description : Dépendances (IDs) | Exemple : C001, C002

## 🧠 Notes Techniques

- Résolution CSP : Temps de réponse optimisés pour la forte combinatoire.
- Robustesse : Gestion native des jeux de données sans prérequis.
- Paramétrage : Modèle totalement dynamique sans modification du code source.
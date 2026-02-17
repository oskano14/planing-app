# 📅 SmartScheduler - Hackathon 2026

**SmartScheduler** est une solution innovante pour l'automatisation des emplois du temps universitaires. Ce projet combine la puissance de la **programmation logique** et de la **programmation par contraintes** pour offrir des plannings cohérents et optimisés.

---

## 🚀 Fonctionnalités Clés

* **Validation Logique (Axe 1 & 2)** : Utilisation de `pyDatalog` pour garantir la cohérence des prérequis (détection de cycles et transitivité).
* **Moteur de Résolution (Axe 3)** : Modélisation CSP (Constraint Satisfaction Problem) via `MiniZinc` pour l'affectation automatique des ressources.
* **Optimisation Multi-Objectifs (Axe 4)** : Algorithmes de minimisation des temps morts pour les étudiants et respect des préférences horaires.

[Image of university timetable generation workflow from data to visual grid]

---

## 🛠️ Configuration du Système

### Prérequis Techniques
* **Python 3.12+**
* **MiniZinc Bundle** (comprenant les solveurs Gecode et Chuffed)
* **Bibliothèques Python** : `pyDatalog`, `pymzn`, `pytest`

### Installation
1. **Initialisation de l'environnement** :
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt

2. **lancer projet** :
    ```bash
    python verify_installation.py

3. **si tout est bien installée** :
    ```bash
   streamlit run app_streamlit.py
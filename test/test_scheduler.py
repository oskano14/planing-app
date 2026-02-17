import sys
import os
import pytest

# Cette ligne permet de remonter d'un dossier pour trouver main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import check_logic_consistency, validate_data_feasibility


# 1. Test de détection de cycle direct
def test_logic_cycle_direct():
    courses = [{"id": "A", "prerequisites": ["A"]}]
    with pytest.raises(ValueError):
        check_logic_consistency(courses)

# 2. Test de détection de cycle indirect (A->B, B->A)
def test_logic_cycle_indirect():
    courses = [
        {"id": "A", "prerequisites": ["B"]},
        {"id": "B", "prerequisites": ["A"]}
    ]
    with pytest.raises(ValueError):
        check_logic_consistency(courses)

# 3. Test de validation logique réussie
def test_logic_ok():
    courses = [{"id": "A", "prerequisites": ["B"]}, {"id": "B", "prerequisites": []}]
    # Ne doit pas lever d'exception
    check_logic_consistency(courses)

# 4. Test faisabilité : Salle trop petite
def test_feasibility_capacity():
    c = [{"id": "C1", "type": "CM", "expected_students": 100}]
    r = [{"id": "R1", "type": "amphitheatre", "capacity": 50}]
    assert validate_data_feasibility(c, r) is False

# 5. Test faisabilité : Type de salle manquant
def test_feasibility_type():
    c = [{"id": "C1", "type": "TP", "expected_students": 10}]
    r = [{"id": "R1", "type": "amphitheatre", "capacity": 50}]
    assert validate_data_feasibility(c, r) is False

# 6. Test faisabilité : OK
def test_feasibility_ok():
    c = [{"id": "C1", "type": "CM", "expected_students": 30}]
    r = [{"id": "R1", "type": "amphitheatre", "capacity": 50}]
    assert validate_data_feasibility(c, r) is True

# 7. Test de structure JSON (Vérifier si id est présent)
def test_json_structure():
    course = {"name": "Test"}
    with pytest.raises(KeyError):
        _ = course["id"]

# 8. Test mapping des types
def test_type_mapping():
    type_map = {"CM": 1, "TD": 2, "TP": 3}
    assert type_map["TP"] == 3

# 9. Test de présence des fichiers data (Integration)
def test_files_exist():
    assert os.path.exists('data/courses.json')

# 10. Test de chargement JSON
import json
def test_load_json():
    with open('data/rooms.json') as f:
        data = json.load(f)
    assert isinstance(data, list)
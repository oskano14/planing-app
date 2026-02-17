include "globals.mzn";

% --- 1. PARAMÈTRES ---
int: nbCours; int: nbSalles; int: nbTeachers; int: nbGroups;
int: nbSlotsTotal;
int: maxSlotsPerDay;
array[1..nbSlotsTotal] of int: slot_to_day;
array[1..nbSlotsTotal] of int: slot_to_pos;
array[1..nbSlotsTotal] of int: is_morning;

array[1..nbCours] of int: course_expected_students;
array[1..nbCours] of int: course_teacher;
array[1..nbCours] of int: course_group;
array[1..nbCours] of int: course_type;
array[1..nbSalles] of int: room_capacity;
array[1..nbSalles] of int: room_type;

% --- 2. VARIABLES DE DÉCISION ---
array[1..nbCours] of var 1..nbSlotsTotal: slot_idx;
array[1..nbCours] of var 1..nbSalles: salle;

% --- 3. CONTRAINTES DURES ---

% CH1-CH3 : Non-chevauchement
constraint forall(i, j in 1..nbCours where i < j)(
    (slot_idx[i] == slot_idx[j]) -> (
        course_teacher[i] != course_teacher[j] /\ 
        salle[i] != salle[j] /\                   
        course_group[i] != course_group[j]        
    )
);

% CH9 : Pause déjeuner (Exemple: Créneau de position 3 = midi)
constraint forall(g in 1..nbGroups, d in 1..5)(
    exists(s_idx in 1..nbSlotsTotal where slot_to_day[s_idx] == d /\ slot_to_pos[s_idx] == 3)(
        forall(c in 1..nbCours where course_group[c] == g)(
            slot_idx[c] != s_idx
        )
    )
);

% --- 4. OPTIMISATION ---

% CS1 : Temps morts (On utilise slot_to_pos pour calculer les écarts)
var int: temps_morts = sum(g in 1..nbGroups, d in 1..5)(
    let {
        var 0..maxSlotsPerDay: p = min([if course_group[c] == g /\ slot_to_day[slot_idx[c]] == d then slot_to_pos[slot_idx[c]] else maxSlotsPerDay endif | c in 1..nbCours]),
        var 0..maxSlotsPerDay: u = max([if course_group[c] == g /\ slot_to_day[slot_idx[c]] == d then slot_to_pos[slot_idx[c]] else 0 endif | c in 1..nbCours])
    } in (if u > 0 then u - p else 0 endif)
);

solve minimize (temps_morts * 10);

output ["Cours " ++ show(i) ++ ": Slot " ++ show(slot_idx[i]) ++ ", Salle " ++ show(salle[i]) ++ "\n" | i in 1..nbCours];
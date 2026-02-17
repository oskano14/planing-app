include "globals.mzn";

% -----------------------------
% PARAMÈTRES
% -----------------------------

int: nbCours;
int: nbSalles;
int: nbTeachers;
int: nbGroups;
int: nbSlotsTotal;

array[1..nbSlotsTotal] of int: slot_to_day;
array[1..nbSlotsTotal] of int: is_lunch;

array[1..nbCours] of int: course_teacher;
array[1..nbCours] of int: course_group;
array[1..nbCours] of int: course_type;
array[1..nbCours] of int: course_expected_students;

array[1..nbSalles] of int: room_capacity;
array[1..nbSalles] of int: room_type;
array[1..nbCours, 1..nbCours] of bool: is_prereq;
array[1..nbTeachers, 1..nbSlotsTotal] of int: teacher_availability;

% --- 2. VARIABLES DE DÉCISION ---
array[1..nbCours] of var 1..nbSlotsTotal: slot_idx;
array[1..nbCours] of var 1..nbSalles: salle;


% -----------------------------
% NOMBRE DE SESSIONS
% -----------------------------

constraint forall(c in 1..nbCours)(
    if course_type[c] == 1 then
        slot_idx[c,1] > 0 /\ slot_idx[c,2] > 0
    else
        slot_idx[c,1] > 0 /\ slot_idx[c,2] == 0
    endif
);

constraint forall(c in 1..nbCours)(
    slot_idx[c,1] > 0 /\ slot_idx[c,2] > 0 ->
    slot_idx[c,1] != slot_idx[c,2]
);

% -----------------------------
% DISPONIBILITÉ PROF
% -----------------------------

constraint forall(c in 1..nbCours, s in 1..maxSessions where slot_idx[c,s] > 0)(
    teacher_available[course_teacher[c], slot_idx[c,s]] == 1
);

% -----------------------------
% LIMITE HEURES PROF
% -----------------------------

constraint forall(t in 1..nbTeachers)(
    sum(c in 1..nbCours, s in 1..maxSessions)(
        bool2int(course_teacher[c] == t /\ slot_idx[c,s] > 0)
    ) <= teacher_max_hours[t]
);

% -----------------------------
% PAS DE CHEVAUCHEMENT
% -----------------------------

constraint forall(c1, c2 in 1..nbCours, s1, s2 in 1..maxSessions where c1 < c2)(
    (slot_idx[c1,s1] > 0 /\ slot_idx[c2,s2] > 0 /\ slot_idx[c1,s1] == slot_idx[c2,s2]) ->
    (
        course_teacher[c1] != course_teacher[c2] /\
        course_group[c1] != course_group[c2] /\
        salle[c1,s1] != salle[c2,s2]
    )
);

% -----------------------------
% PAS DE COURS À MIDI
% -----------------------------

constraint forall(c in 1..nbCours, s in 1..maxSessions where slot_idx[c,s] > 0)(
    is_lunch[slot_idx[c,s]] == 0
);

% -----------------------------
% TYPE DE SALLE
% -----------------------------

constraint forall(c in 1..nbCours, s in 1..maxSessions where slot_idx[c,s] > 0)(
    (course_type[c] == 1 -> room_type[salle[c,s]] == 1) /\
    (course_type[c] == 2 -> room_type[salle[c,s]] == 2) /\
    (course_type[c] == 3 -> room_type[salle[c,s]] == 3)
);

% CH4 : Capacité des salles
constraint forall(i in 1..nbCours)(
    room_capacity[salle[i]] >= course_expected_students[i]
);

% CH10 : Type de salle (1:Amphi, 2:TD, 3:TP)
constraint forall(i in 1..nbCours)(
    course_type[i] == room_type[salle[i]]
);

% CH9 : Pause déjeuner (Exemple: Créneau de position 3 = midi)
constraint forall(g in 1..nbGroups, d in 1..5)(
    sum(c in 1..nbCours, s in 1..maxSessions)(
        bool2int(
            course_group[c] == g /\
            slot_idx[c,s] > 0 /\
            slot_to_day[slot_idx[c,s]] == d
        )
    ) <= 4
);

% Contrainte : Le prérequis doit avoir lieu AVANT le cours
constraint forall(i, j in 1..nbCours where is_prereq[i, j])(
    slot_idx[j] < slot_idx[i]
);

% Contrainte : Le prof doit être disponible pour le slot choisi
constraint forall(i in 1..nbCours)(
    teacher_availability[course_teacher[i], slot_idx[i]] == 1
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
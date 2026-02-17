include "globals.mzn";

% -----------------------------
% PARAMÈTRES
% -----------------------------

int: nbCours;
int: nbSalles;
int: nbTeachers;
int: nbGroups;
int: nbSlotsTotal;
int: maxSlotsPerDay; % Nombre de créneaux par jour (ex: 8)
int: maxSessions;

array[1..nbSlotsTotal] of int: slot_to_day;
array[1..nbSlotsTotal] of int: slot_to_pos; % Position dans la journée (1..maxSlotsPerDay)
array[1..nbSlotsTotal] of int: is_lunch;

array[1..nbCours] of int: course_teacher;
array[1..nbCours] of int: course_group;
array[1..nbCours] of int: course_type; % 1: Amphi, 2: TD, 3: TP
array[1..nbCours] of int: course_expected_students;

array[1..nbSalles] of int: room_capacity;
array[1..nbSalles] of int: room_type;

array[1..nbCours, 1..nbCours] of bool: is_prereq; % i est prérequis de j ?
array[1..nbTeachers, 1..nbSlotsTotal] of int: teacher_available;
array[1..nbTeachers] of int: teacher_max_hours;

% -----------------------------
% VARIABLES DE DÉCISION
% -----------------------------
% On reste sur 1 session par cours pour simplifier selon tes paramètres
array[1..nbCours] of var 1..nbSlotsTotal: slot_idx;
array[1..nbCours] of var 1..nbSalles: salle;

% -----------------------------
% CONTRAINTES STRICTES 
% -----------------------------

% 1. DISPONIBILITÉ PROF
constraint forall(c in 1..nbCours)(
    teacher_available[course_teacher[c], slot_idx[c]] == 1
);

% 2. LIMITE HEURES PROF
constraint forall(t in 1..nbTeachers)(
    sum(c in 1..nbCours)(bool2int(course_teacher[c] == t)) <= teacher_max_hours[t]
);

% 3. PAS DE CHEVAUCHEMENT (Règle d'or)
% Si deux cours sont au même moment, ils doivent avoir des profs, groupes et salles différents
constraint forall(c1, c2 in 1..nbCours where c1 < c2)(
    (slot_idx[c1] == slot_idx[c2]) -> (
        course_teacher[c1] != course_teacher[c2] /\
        course_group[c1] != course_group[c2] /\
        salle[c1] != salle[c2]
    )
);

% 4. PAUSE DÉJEUNER
constraint forall(c in 1..nbCours)(
    is_lunch[slot_idx[c]] == 0
);

% 5. TYPE ET CAPACITÉ DE SALLE
constraint forall(c in 1..nbCours)(
    room_type[salle[c]] == course_type[c] /\
    room_capacity[salle[c]] >= course_expected_students[c]
);

% 6. PRÉREQUIS
% Le cours prérequis (i) doit avoir lieu strictement AVANT le cours (j)
constraint forall(i, j in 1..nbCours where is_prereq[i, j])(
    slot_idx[i] < slot_idx[j]
);

% 7. LIMITE DE CHARGE PAR GROUPE (max 4 cours par jour)
constraint forall(g in 1..nbGroups, d in 1..5)(
    sum(c in 1..nbCours)(
        bool2int(course_group[c] == g /\ slot_to_day[slot_idx[c]] == d)
    ) <= 4
);

% -----------------------------
% OPTIMISATION (Temps morts)
% -----------------------------

% On minimise l'étalement de la journée (u - p) pour chaque groupe
% var int: temps_morts = sum(g in 1..nbGroups, d in 1..5)(
%     let {
%         % Positions du premier et dernier cours du groupe g le jour d
%         var int: p = min([if course_group[c] == g /\ slot_to_day[slot_idx[c]] == d then slot_to_pos[slot_idx[c]] else maxSlotsPerDay endif | c in 1..nbCours]),
%         var int: u = max([if course_group[c] == g /\ slot_to_day[slot_idx[c]] == d then slot_to_pos[slot_idx[c]] else 0 endif | c in 1..nbCours])
%     } in (if u > 0 then u - p else 0 endif)
% );

% solve minimize temps_morts;
solve satisfy;

% -----------------------------
% AFFICHAGE
% -----------------------------
output [
    "Cours " ++ show(c) ++ " (Prof " ++ show(course_teacher[c]) ++ ") : " ++
    "Slot " ++ show(slot_idx[c]) ++ " (Jour " ++ show(slot_to_day[slot_idx[c]]) ++ ") " ++
    "en Salle " ++ show(salle[c]) ++ "\n"
    | c in 1..nbCours
];
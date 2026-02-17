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

% ---- indisponibilités profs ----
array[1..nbTeachers, 1..nbSlotsTotal] of int: teacher_available;

% ---- limite heures prof ----
array[1..nbTeachers] of int: teacher_max_hours;

% -----------------------------
% SESSIONS
% -----------------------------

int: maxSessions = 2;

array[1..nbCours, 1..maxSessions] of var 0..nbSlotsTotal: slot_idx;
array[1..nbCours, 1..maxSessions] of var 0..nbSalles: salle;

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

% -----------------------------
% CAPACITÉ SALLE
% -----------------------------

constraint forall(c in 1..nbCours, s in 1..maxSessions where slot_idx[c,s] > 0)(
    room_capacity[salle[c,s]] >= course_expected_students[c]
);

% -----------------------------
% MAX 4 COURS PAR JOUR PAR GROUPE
% -----------------------------

constraint forall(g in 1..nbGroups, d in 1..5)(
    sum(c in 1..nbCours, s in 1..maxSessions)(
        bool2int(
            course_group[c] == g /\
            slot_idx[c,s] > 0 /\
            slot_to_day[slot_idx[c,s]] == d
        )
    ) <= 4
);

% -----------------------------
% AU MOINS UN COURS JEUDI OU VENDREDI
% -----------------------------

constraint forall(g in 1..nbGroups)(
    exists(c in 1..nbCours, s in 1..maxSessions)(
        course_group[c] == g /\
        slot_idx[c,s] > 0 /\
        (slot_to_day[slot_idx[c,s]] == 4 \/ slot_to_day[slot_idx[c,s]] == 5)
    )
);

% -----------------------------
% RÉSOLUTION
% -----------------------------

solve
:: int_search(
    [slot_idx[c,s] | c in 1..nbCours, s in 1..maxSessions],
    first_fail,
    indomain_random,
    complete
)
satisfy;


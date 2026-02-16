% =============================================================================
% SMARTSCHEDULER - MOTEUR DE RÉSOLUTION CSP (MiniZinc)
% =============================================================================

include "globals.mzn"; % Inclusion des fonctions globales pour les contraintes complexes

% --- 1. PARAMÈTRES (Reçus du JSON via Python) ---
int: nbCours;
int: nbSalles;
int: nbTeachers;
int: nbGroups;
int: nbDays = 5;
int: nbSlots = 10; % 10 créneaux par jour (ex: 8h-18h)

% Caractéristiques des cours (R1)
array[1..nbCours] of int: course_expected_students;
array[1..nbCours] of int: course_teacher;
array[1..nbCours] of int: course_group;
array[1..nbCours] of int: course_type; % 1:CM, 2:TD, 3:TP

% Caractéristiques des salles (R3)
array[1..nbSalles] of int: room_capacity;
array[1..nbSalles] of int: room_type; % 1:Amphi, 2:TD, 3:Labo

% --- 2. VARIABLES DE DÉCISION ---
array[1..nbCours] of var 1..nbDays: jour;
array[1..nbCours] of var 1..nbSlots: creneau;
array[1..nbCours] of var 1..nbSalles: salle;

% --- 3. CONTRAINTES DURES (OBLIGATOIRES) ---

% CH1, CH2, CH3 : Non-chevauchement (Profs, Salles, Groupes)
% Si deux cours sont le même jour au même créneau, ils doivent différer sur tout le reste
constraint forall(i, j in 1..nbCours where i < j)(
    (jour[i] == jour[j] /\ creneau[i] == creneau[j]) -> (
        course_teacher[i] != course_teacher[j] /\  % CH1
        salle[i] != salle[j] /\                   % CH2
        course_group[i] != course_group[j]         % CH3
    )
);

% CH4 : Capacité des salles
constraint forall(i in 1..nbCours)(
    room_capacity[salle[i]] >= course_expected_students[i]
);

% CH10 : Type de salle approprié (CM -> Amphi, TD -> Salle TD, TP -> Labo)
constraint forall(i in 1..nbCours)(
    course_type[i] == room_type[salle[i]]
);

% CH9 : Pause déjeuner garantie (au moins un créneau libre entre 12h et 14h)
% Supposons que créneaux 5 et 6 = 12h-14h
constraint forall(g in 1..nbGroups, d in 1..nbDays)(
    exists(s in 5..6)(
        forall(c in 1..nbCours where course_group[c] == g)(
            not (jour[c] == d /\ creneau[c] == s)
        )
    )
);

% --- 4. CONTRAINTES SOUPLES (PRÉFÉRENCES) ---

% CS1 : Minimisation des temps morts (Poids: 10)
% (Logique simplifiée : on minimise l'écart entre le premier et dernier cours)
var int: temps_morts;
constraint temps_morts = sum(g in 1..nbGroups, d in 1..nbDays)(
    let {
        var 0..nbSlots: premier = min([if course_group[c] == g /\ jour[c] == d then creneau[c] else nbSlots endif | c in 1..nbCours]),
        var 0..nbSlots: dernier = max([if course_group[c] == g /\ jour[c] == d then creneau[c] else 0 endif | c in 1..nbCours])
    } in (if dernier > 0 then dernier - premier else 0 endif)
);

% CS6 : Éviter les cours très tôt le matin (8h = créneau 1) (Poids: 2)
var int: penalite_matin = sum(i in 1..nbCours)(bool2int(creneau[i] == 1));

% --- 5. OBJECTIF FINAUX ---
% On minimise la somme pondérée des violations
solve satisfy; 

% --- 6. AFFICHAGE ---
output [
    "Cours " ++ show(i) ++ ": Jour " ++ show(jour[i]) ++ 
    ", Créneau " ++ show(creneau[i]) ++ 
    ", Salle " ++ show(salle[i]) ++ "\n" 
    | i in 1..nbCours
];
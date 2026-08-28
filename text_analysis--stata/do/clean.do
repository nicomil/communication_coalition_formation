br
keep if label != ""
drop if group_id == .
encode treatment, generate(New_treatment)
drop treatment
rename New_treatment treatment
label define New_treatment 1 "baseline", modify
label define New_treatment 2 "slacker", modify
sort treatment group_id id_in_group
generate session = .
replace session = 1 if sessioncode == "w0k1pp1v" | sessioncode == "um435zd7" | sessioncode == "z7x47k43"
replace session = 2 if sessioncode == "e3cj2oap" | sessioncode == "vwv9fmlo" | sessioncode == "sx78hwmu"
replace session = 3 if sessioncode == "dblrbrkx" | sessioncode == "ctx9bssc" | sessioncode == "02b4rmbq"
************************** Generate Persuasion ************

generate S_ij = .
generate A_ji = .
generate persuasion_ij = .

label variable S_ij          "i signals support to j"
label variable S_ij "i signals support to j(left)"
label variable A_ji          "j actually supports i"
label variable persuasion_ij "i persuaded j (S_ij = 1 and A_ji = 1)"

generate S_ik = .
generate A_ki = .
generate persuasion_ik = .

label variable S_ik          "i signals support to k(right)"
label variable A_ki          "k actually supports i"
label variable persuasion_ik "i persuaded k (S_ik = 1 and A_ki = 1)"


/* These two variables are based on the topology of the triad in the experiment:  

P1 has on the right P2, and on the left P3;
P2 has on the right P3, and on the left P1;
P3 has on the right P1, and on the left P2;

P1 send signal "I intend to support you" to P2, signal_right_target_id == 2; 
P1 send signal "I intend to support you" to P3, signal_left_target_id == 3; 

*/
replace S_ij = 0
replace S_ik = 0
replace A_ji = 0
replace A_ki = 0

*gen decision_target_id_clean = decision_target_id
*replace decision_target_id_clean = "0" if decision_target_id_clean == "noOne"
*destring decision_target_id_clean, replace

*******************************************************************
* i = player 1 and j player left(P3)
replace S_ij = 1 if focal_player_id == 1 & signal_left_target_id == "3"
replace A_ji = 1 if focal_player_id == 3 & received_signal_right_target_id =="3" & decision_target_id == "1"
* i = player 1 and k player right(P2)
replace S_ik = 1 if focal_player_id == 1 & signal_right_target_id == "2"
replace A_ki = 1 if focal_player_id == 2 & received_signal_left_target_id == "2" & decision_target_id == "1" 

replace S_ij = 1 if focal_player_id == 2 & signal_left_target_id == "1"
replace A_ji = 1 if focal_player_id == 1 & received_signal_right_target_id == "1" & decision_target_id == "2"
replace S_ik = 1 if focal_player_id == 2 & signal_right_target_id == "3"
replace A_ki = 1 if focal_player_id == 3 & received_signal_left_target_id == "3" & decision_target_id == "2"

replace S_ij = 1 if focal_player_id == 3 & signal_left_target_id == "2"
replace A_ji = 1 if focal_player_id == 2 & received_signal_right_target_id == "2" & decision_target_id == "3"
replace S_ik = 1 if focal_player_id == 3 & signal_right_target_id == "1"
replace A_ki = 1 if focal_player_id == 1 & received_signal_left_target_id == "1" & decision_target_id == "3"


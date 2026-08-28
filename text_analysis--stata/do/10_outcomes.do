*==============================================================================
* CCF — Outcome variable construction
* Stata 19
*
* INPUT:  all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL.csv
*         6 rows per group (one per ordered pair i→partner)
*
* OUTPUT: ccf_master.dta
*         1 row per player, 3 per group
*         All outcomes in one dataset
*
* Variables constructed:
*   S_ij / S_ik           signal i sent to left/right partner (1 = "split_you")
*   A_ji / A_ki           left/right partner supports i in final decision
*   persuasion_ij / ik    S_ij × A_ji  ;  S_ik × A_ki
*   strategic_deception   S_ij=1 & S_ik=1 & final decision = NoOne
*   C_ij / C_ik           signal-choice consistency toward left/right partner
*   CC_i                  (C_ij + C_ik) / 2
*   efficiency_group      mean payoff of the 3 group members
*==============================================================================

version 19.0
clear all
set more off

* ─────────────────────────────────────────────────────────────────────────────
* 1. IMPORT AND BASIC CLEANING
* ─────────────────────────────────────────────────────────────────────────────

import delimited "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL.csv", ///
    bindquote(strict) maxquotedrows(unlimited) stringcols(_all) clear

* Rename dot-in-name columns that Stata would otherwise mangle
capture rename session.code     sessioncode
capture rename send.signal_left  sendsignal_left
capture rename send.signal_right sendsignal_right

* Destring numeric variables
quietly destring ///
    group_id id_in_group payoff group_dropped payoff_eligible ///
    focal_player_id partner_id ///
    decision_inactive signal_inactive grp_coordinate grp_drop ///
    birth_year gender uni_years ///
    guess_left_confidence guess_right_confidence ///
    time_chat time_signals time_decision time_guess chat_interrupted ///
    chat_message_count chat_message_count_focal_sent ///
    chat_message_count_partner_sent ///
    rcvd_sig_left_inactive rcvd_sig_right_inactive index_pages ///
    mach_01 mach_02 mach_03 mach_04 mach_05 mach_06 mach_07 mach_08 mach_09 ///
    narc_01 narc_02 narc_03 narc_04 narc_05 narc_06 narc_07 narc_08 narc_09 ///
    psych_01 psych_02 psych_03 psych_04 psych_05 psych_06 psych_07 psych_08 psych_09 ///
    patience risk reciprocity_positive reciprocity_negative altruism trust ///
    level_k time_falk time_levelk, replace

* Remove incomplete observations (no label = pending/dropped game)
keep if label != ""
drop if group_id == .

* Treatment as numeric
* encode assigns numbers alphabetically (private=1, private_no_dwl=2, public=3)
* which does not match the intended ordering. Assign manually.
generate byte treatment_num = .
replace treatment_num = 1 if treatment == "private"
replace treatment_num = 2 if treatment == "public"
replace treatment_num = 3 if treatment == "private_no_dwl"
assert !missing(treatment_num)       // stops if any row has an unknown string
drop treatment
rename treatment_num treatment
label define treat_lbl 1 "Baseline" 2 "Public" 3 "Slacker", replace
label values treatment treat_lbl

* Session identifier
generate byte session = .
replace session = 1 if sessioncode == "w0k1pp1v" | sessioncode == "um435zd7" | sessioncode == "z7x47k43"
replace session = 2 if sessioncode == "e3cj2oap" | sessioncode == "vwv9fmlo" | sessioncode == "sx78hwmu"
replace session = 3 if sessioncode == "dblrbrkx" | sessioncode == "ctx9bssc" | sessioncode == "02b4rmbq"

sort treatment group_id id_in_group

* ─────────────────────────────────────────────────────────────────────────────
* 2. STRUCTURAL CHECKS
*    6 ordered pairs per group: each player appears as focal twice
*    (once toward the left partner, once toward the right partner)
* ─────────────────────────────────────────────────────────────────────────────

* Standardise the two key string variables to lowercase, no spaces
generate str topology  = lower(strtrim(topology_side))
generate str final_dec = lower(strtrim(final_decision))

assert inlist(topology, "left", "right")
assert inlist(focal_player_id, 1, 2, 3)
assert focal_player_id != partner_id

bysort sessioncode group_id: assert _N == 6
bysort sessioncode group_id focal_player_id: assert _N == 2

* Group validity: not dropped, no timeout
bysort sessioncode group_id: ///
    egen byte any_timeout = max(decision_inactive == 99 | signal_inactive == 99)
generate byte group_valid = (grp_drop == 0 & any_timeout == 0)

* ─────────────────────────────────────────────────────────────────────────────
* 3. DYAD-LEVEL VARIABLES
*    These are computed while the data is still in 6-row-per-group format.
*    Each row = one ordered pair i → partner (either left or right).
* ─────────────────────────────────────────────────────────────────────────────

* --- Signal i sent to THIS partner in this row ---
* topology == "left"  → signal is in sendsignal_left
* topology == "right" → signal is in sendsignal_right
generate str signal_to_partner = ""
replace signal_to_partner = lower(strtrim(sendsignal_left))  if topology == "left"
replace signal_to_partner = lower(strtrim(sendsignal_right)) if topology == "right"

assert inlist(signal_to_partner, "split_you", "split_other", "support_none", "")

* --- S_ij: i declares intent to support this partner (1 = "split_you") ---
generate byte S_ij = (signal_to_partner == "split_you") ///
    if signal_to_partner != ""

* --- A_ij (intermediate): does i's final decision support THIS partner? ---
* final_dec == topology means i chose the side where this partner sits
generate byte A_ij = (final_dec == topology) ///
    if inlist(final_dec, "left", "right", "noone")

* --- A_ji: does this partner support i? ---
* This is NOT on i's row. It is A_ij read from the REVERSE pair (j→i).
* We save A_ij, flip focal↔partner, merge back as A_ji.
preserve
    keep sessioncode group_id focal_player_id partner_id A_ij
    rename focal_player_id  _tmp
    rename partner_id       focal_player_id
    rename _tmp             partner_id
    rename A_ij             A_ji
    tempfile reverse
    save `reverse'
restore

merge 1:1 sessioncode group_id focal_player_id partner_id ///
    using `reverse', assert(match) nogen keepusing(A_ji)

* --- persuasion_ij = S_ij × A_ji ---
generate byte persuasion_ij = S_ij * A_ji if !missing(S_ij, A_ji)

* --- C_ij: signal-choice consistency ---
* split_you    → consistent if i supports this partner     (A_ij = 1)
* split_other  → consistent if i supports the OTHER player (A_ij = 0, not NoOne)
* support_none → consistent if i supports nobody           (final = "noone")
generate byte C_ij = .
replace C_ij = 1 if signal_to_partner == "split_you"    & A_ij == 1
replace C_ij = 1 if signal_to_partner == "split_other"  & A_ij == 0 ///
                  & inlist(final_dec, "left", "right")
replace C_ij = 1 if signal_to_partner == "support_none" & final_dec == "noone"
replace C_ij = 0 if C_ij == . ///
    & signal_to_partner != "" & inlist(final_dec, "left", "right", "noone")

* ─────────────────────────────────────────────────────────────────────────────
* 3b. SAVE DYAD-LEVEL DATASET (6 ordered pairs per group)
*     Persuasion is naturally a dyad-level measure: 6 obs per group.
*     Save here, before the reshape collapses to player level.
* ─────────────────────────────────────────────────────────────────────────────
preserve
    keep sessioncode group_id session treatment ///
         focal_player_id focal_player_color ///
         partner_id partner_color topology ///
         final_decision final_dec ///
         signal_to_partner S_ij A_ij A_ji persuasion_ij C_ij ///
         payoff group_valid any_timeout grp_drop grp_coordinate group_outcome ///
         guess_left guess_right guess_left_confidence guess_right_confidence ///
         time_chat time_signals time_decision time_guess ///
         chat_interrupted decision_inactive signal_inactive ///
         rcvd_sig_left_inactive rcvd_sig_right_inactive ///
         decision_option_1 decision_option_2 decision_option_3 ///
         received_signal_left received_signal_right ///
         player_on_the_left player_on_the_right ///
         player_visual_left player_visual_right ///
         gender birth_year field_study uni_years status job ///
         mach_01 mach_02 mach_03 mach_04 mach_05 mach_06 mach_07 mach_08 mach_09 ///
         narc_01 narc_02 narc_03 narc_04 narc_05 narc_06 narc_07 narc_08 narc_09 ///
         psych_01 psych_02 psych_03 psych_04 psych_05 psych_06 psych_07 psych_08 psych_09 ///
         patience risk reciprocity_positive reciprocity_negative altruism trust ///
         level_k time_falk time_levelk index_pages ///
         chat_message_count chat_message_count_focal_sent ///
         chat_message_count_partner_sent chat_transcript
    order sessioncode group_id session treatment ///
          focal_player_id focal_player_color ///
          partner_id partner_color topology ///
          signal_to_partner S_ij A_ji A_ij persuasion_ij C_ij ///
          final_decision final_dec ///
          payoff group_valid any_timeout grp_drop grp_coordinate group_outcome ///
          guess_left guess_right guess_left_confidence guess_right_confidence ///
          received_signal_left received_signal_right ///
          decision_option_1 decision_option_2 decision_option_3 ///
          player_on_the_left player_on_the_right ///
          player_visual_left player_visual_right ///
          time_decision time_guess time_signals time_chat ///
          chat_interrupted decision_inactive signal_inactive ///
          rcvd_sig_left_inactive rcvd_sig_right_inactive ///
          gender birth_year field_study uni_years status job ///
          mach_01 mach_02 mach_03 mach_04 mach_05 mach_06 mach_07 mach_08 mach_09 ///
          narc_01 narc_02 narc_03 narc_04 narc_05 narc_06 narc_07 narc_08 narc_09 ///
          psych_01 psych_02 psych_03 psych_04 psych_05 psych_06 psych_07 psych_08 psych_09 ///
          patience risk reciprocity_positive reciprocity_negative altruism trust ///
          level_k time_falk time_levelk index_pages ///
          chat_message_count chat_message_count_focal_sent ///
          chat_message_count_partner_sent chat_transcript
    isid sessioncode group_id focal_player_id partner_id
    compress
    save `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', replace
    display as text "Saved ccf_dyad.dta  (" _N " directed pairs, 6 per group)"
restore

* ─────────────────────────────────────────────────────────────────────────────
* 4. RESHAPE: 6 rows per group → 3 rows per group
*    Pivot on topology: "left" → _j suffix, "right" → _k suffix
* ─────────────────────────────────────────────────────────────────────────────

* Keep only what we need going forward
keep ///
    sessioncode group_id session treatment focal_player_id focal_player_color ///
    id_in_session id_in_group player_color ///
    final_decision final_dec ///
    sendsignal_left sendsignal_right ///
    guess_left guess_right guess_left_confidence guess_right_confidence ///
    received_signal_left received_signal_right ///
    decision_option_1 decision_option_2 decision_option_3 ///
    player_on_the_left player_on_the_right player_visual_left player_visual_right ///
    payoff payoff_eligible group_dropped grp_drop ///
    grp_coordinate group_outcome any_timeout group_valid ///
    time_decision time_guess time_signals time_chat chat_interrupted ///
    decision_inactive signal_inactive ///
    rcvd_sig_left_inactive rcvd_sig_right_inactive ///
    birth_year gender uni_years field_study status job ///
    mach_01 mach_02 mach_03 mach_04 mach_05 mach_06 mach_07 mach_08 mach_09 ///
    narc_01 narc_02 narc_03 narc_04 narc_05 narc_06 narc_07 narc_08 narc_09 ///
    psych_01 psych_02 psych_03 psych_04 psych_05 psych_06 psych_07 psych_08 psych_09 ///
    patience risk reciprocity_positive reciprocity_negative altruism trust ///
    level_k time_falk time_levelk index_pages ///
    topology ///
    partner_id partner_color signal_to_partner ///
    S_ij A_ij A_ji persuasion_ij C_ij ///
    chat_message_count chat_message_count_focal_sent chat_message_count_partner_sent ///
    chat_transcript

* Stata variable names max 32 chars. The suffixes "left"/"right" added by reshape
* would push chat_message_count_focal_sent (30) + "left" (4) = 34 chars → error.
* chat_transcript varies by partner topology → must be a reshape stub, not background.
* Shorten before reshape, then use the short names as stubs.
rename chat_message_count              _cmc
rename chat_message_count_focal_sent   _cmcfs
rename chat_message_count_partner_sent _cmcps
rename chat_transcript                 _ctrans

* Reshape: stub variables become _left and _right, then we rename them to _j / _k
reshape wide ///
    partner_id partner_color signal_to_partner ///
    S_ij A_ij A_ji persuasion_ij C_ij ///
    _cmc _cmcfs _cmcps _ctrans, ///
    i(sessioncode group_id focal_player_id) j(topology) string

* Rename: left → j  ;  right → k
rename partner_idleft          partner_j_id
rename partner_idright         partner_k_id
rename partner_colorleft       partner_j_color
rename partner_colorright      partner_k_color
rename signal_to_partnerleft   signal_ij
rename signal_to_partnerright  signal_ik
rename S_ijleft                S_ij
rename S_ijright               S_ik
rename A_ijleft                A_ij
rename A_ijright               A_ik
rename A_jileft                A_ji
rename A_jiright               A_ki
rename persuasion_ijleft       persuasion_ij
rename persuasion_ijright      persuasion_ik
rename C_ijleft                C_ij
rename C_ijright               C_ik
rename _cmcleft                msgs_total_j
rename _cmcright               msgs_total_k
rename _cmcfsleft              msgs_sent_j
rename _cmcfsright             msgs_sent_k
rename _cmcpsleft              msgs_recv_j
rename _cmcpsright             msgs_recv_k
rename _ctransleft             chat_transcript_j
rename _ctransright            chat_transcript_k

* ─────────────────────────────────────────────────────────────────────────────
* 5. PLAYER-LEVEL OUTCOMES
*    Dataset is now 1 row per player, 3 rows per group.
* ─────────────────────────────────────────────────────────────────────────────

bysort sessioncode group_id: assert _N == 3

* --- Strategic Deception ---
* = 1 iff i signals "split_you" to BOTH partners AND supports neither
generate byte strategic_deception = ///
    (S_ij == 1 & S_ik == 1 & final_dec == "noone") ///
    if !missing(S_ij, S_ik) & final_dec != ""

* --- Choice-Signal Consistency ---
generate double CC_i = (C_ij + C_ik) / 2 if !missing(C_ij, C_ik)

* Sanity checks (stops the do-file if something went wrong)
assert inlist(CC_i, 0, .5, 1)        if !missing(CC_i)
assert persuasion_ij == S_ij * A_ji  if !missing(S_ij, A_ji)
assert persuasion_ik == S_ik * A_ki  if !missing(S_ik, A_ki)

* ─────────────────────────────────────────────────────────────────────────────
* 6. EFFICIENCY
*    Mean payoff of the 3 group members. payoff is now entered exactly once
*    per player, so there is no double-counting.
* ─────────────────────────────────────────────────────────────────────────────

bysort sessioncode group_id: egen double efficiency_group = mean(payoff)

* Treatment-level mean efficiency.
* Each group must enter exactly once: tag the first player row per group.
* bysort + cond() ensures only one obs per group contributes to the treatment mean.
bysort sessioncode group_id: gen byte _grp_tag = (_n == 1)
bysort treatment: egen double mean_efficiency_treat = mean(cond(_grp_tag == 1, efficiency_group, .))
drop _grp_tag

label variable mean_efficiency_treat "Mean group efficiency by treatment (group-weighted)"

* ─────────────────────────────────────────────────────────────────────────────
* 7. LABELS
* ─────────────────────────────────────────────────────────────────────────────

label define yesno 0 "No" 1 "Yes", replace
label values S_ij S_ik A_ji A_ki A_ij A_ik ///
             C_ij C_ik persuasion_ij persuasion_ik ///
             strategic_deception group_valid any_timeout yesno

label variable signal_ij            "Signal i sent to left partner j"
label variable signal_ik            "Signal i sent to right partner k"
label variable S_ij                 "i signals support to j (split_you = 1)"
label variable S_ik                 "i signals support to k (split_you = 1)"
label variable A_ji                 "j supports i in final decision"
label variable A_ki                 "k supports i in final decision"
label variable A_ij                 "i supports j in final decision (intermediate)"
label variable A_ik                 "i supports k in final decision (intermediate)"
label variable persuasion_ij        "Persuasion i→j: S_ij × A_ji"
label variable persuasion_ik        "Persuasion i→k: S_ik × A_ki"
label variable C_ij                 "Signal to j consistent with i's final choice"
label variable C_ik                 "Signal to k consistent with i's final choice"
label variable CC_i                 "Choice-Signal Consistency: (C_ij + C_ik) / 2"
label variable strategic_deception  "Strategic Deception: signalled support to both, chose NoOne"
label variable efficiency_group     "Efficiency: mean group payoff"
label variable group_valid          "Group valid: complete, not dropped, no timeout"

format CC_i             %4.2f
format efficiency_group %6.2f

* ─────────────────────────────────────────────────────────────────────────────
* 8. COLUMN ORDER AND SAVE
* ─────────────────────────────────────────────────────────────────────────────

order sessioncode group_id session treatment ///
      focal_player_id focal_player_color id_in_group player_color ///
      partner_j_id partner_j_color partner_k_id partner_k_color ///
      final_decision ///
      signal_ij signal_ik S_ij S_ik A_ji A_ki A_ij A_ik ///
      persuasion_ij persuasion_ik C_ij C_ik CC_i ///
      strategic_deception payoff efficiency_group ///
      grp_coordinate group_outcome group_valid

isid sessioncode group_id focal_player_id
compress

save "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_master.dta", replace

* ─────────────────────────────────────────────────────────────────────────────
* 9. QUICK DIAGNOSTICS
* ─────────────────────────────────────────────────────────────────────────────

display as result _newline "============================================"
display as result " ccf_master.dta — ready"
display as result "============================================"
display as text   " Players (rows)   : " _N
display as text   " Groups total     : " _N / 3
quietly count if group_valid == 1
display as text   " Valid groups     : " r(N) / 3

display as result _newline "--- Persuasion ---"
quietly count if S_ij == 1 | S_ik == 1
display as text " Players who signalled at least one support : " r(N)
quietly count if persuasion_ij == 1
display as text " Successful persuasion i→j : " r(N)
quietly count if persuasion_ik == 1
display as text " Successful persuasion i→k : " r(N)

display as result _newline "--- Strategic Deception ---"
tab strategic_deception, missing

display as result _newline "--- Choice-Signal Consistency ---"
tab CC_i, missing

display as result _newline "--- Efficiency by treatment (group-level N) ---"
* Collapse to one row per group so that SD and N reflect groups, not players.
preserve
    bysort sessioncode group_id: keep if _n == 1
    tabstat efficiency_group, by(treatment) stat(mean sd n)
restore

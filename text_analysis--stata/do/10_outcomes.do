
* CCF - Outcome variable construction
* Stata 19
*
* INPUT:  all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL_topicgpt_
*         with_indicators_text_analysis.csv
*         6 rows per group (one per ordered pair i->partner)
*
* OUTPUT: ccf_dyad.dta   -- dyad level (6 directed pairs per group)
*         ccf_master.dta -- player level (3 players per group)
*
* Variables constructed:
*   S_ij / S_ik           signal i sent to left/right partner (1 = "split_you")
*   A_ji / A_ki           left/right partner supports i in final decision
*   persuasion_ij / ik    S_ij x A_ji  ;  S_ik x A_ki  (. if S == 0)
*   strategic_deception   S_ij=1 & S_ik=1 & final decision = NoOne
*   C_ij / C_ik           signal-choice consistency toward left/right partner
*   CC_i                  (C_ij + C_ik) / 2
*   efficiency_group      mean payoff of the 3 group members
*   MACH / NARC / PSYCH   Dark Triad indices (9-item scales)
*==============================================================================

version 19.0
clear all
set more off

* -----------------------------------------------------------------------------
* 1. IMPORT AND BASIC CLEANING
* -----------------------------------------------------------------------------

import delimited "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL_topicgpt_with_indicators_text_analysis.csv", ///
    bindquote(strict) maxquotedrows(unlimited) stringcols(_all) clear

* Rename dot-in-name columns that Stata would otherwise mangle
capture rename session.code      sessioncode
capture rename send.signal_left  sendsignal_left
capture rename send.signal_right sendsignal_right

* Destring numeric variables -- core
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

* Destring new text-analysis and word-count variables
quietly destring ///
    number_of_words number_of_messages ///
    nlp_sent_n_topics ///
    topic_commitment topic_coalition_proposal topic_payoff_reasoning ///
    volume_continuous_words ///
    emotional_tone_continuous_0_100 ///
    sentiment_continuous_neg1_pos1 ///
    analytical_thinking_continuous_0 ///
    clout_continuous_0_100 ///
    authenticity_continuous_0_100 ///
    volume emotional_tone sentiment ///
    analytical_thinking clout authenticity, replace

* Remove incomplete observations (no label = pending/dropped game)
keep if label != ""
drop if group_id == .

* Treatment as numeric
generate byte treatment_num = .
replace treatment_num = 1 if treatment == "private"
replace treatment_num = 2 if treatment == "public"
replace treatment_num = 3 if treatment == "private_no_dwl"
assert !missing(treatment_num)
drop treatment
rename treatment_num treatment
label define treat_lbl 1 "Baseline" 2 "Public" 3 "Slacker", replace
label values treatment treat_lbl

* Session identifier
generate byte session = .
replace session = 1 if inlist(sessioncode, "w0k1pp1v", "um435zd7", "z7x47k43")
replace session = 2 if inlist(sessioncode, "e3cj2oap", "vwv9fmlo", "sx78hwmu")
replace session = 3 if inlist(sessioncode, "dblrbrkx", "ctx9bssc", "02b4rmbq")

sort treatment group_id id_in_group

* -----------------------------------------------------------------------------
* 2. STRUCTURAL CHECKS
* -----------------------------------------------------------------------------

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

* -----------------------------------------------------------------------------
* 3. DYAD-LEVEL VARIABLES
* -----------------------------------------------------------------------------

* Signal i sent to THIS partner in this row
generate str signal_to_partner = ""
replace signal_to_partner = lower(strtrim(sendsignal_left))  if topology == "left"
replace signal_to_partner = lower(strtrim(sendsignal_right)) if topology == "right"

assert inlist(signal_to_partner, "split_you", "split_other", "support_none", "")

* S_ij: i declares intent to support this partner (1 = "split_you")
generate byte S_ij = (signal_to_partner == "split_you") ///
    if signal_to_partner != ""

* A_ij (intermediate): does i final decision support THIS partner?
generate byte A_ij = (final_dec == topology) ///
    if inlist(final_dec, "left", "right", "noone")

* A_ji: does this partner support i? (merge from reverse pair)
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

* persuasion_ij = S_ij x A_ji  (. if S_ij == 0)
generate byte persuasion_ij = S_ij * A_ji if !missing(S_ij, A_ji)
replace persuasion_ij = . if S_ij == 0

* C_ij: signal-choice consistency
generate byte C_ij = .
replace C_ij = 1 if signal_to_partner == "split_you"   & A_ij == 1
replace C_ij = 1 if signal_to_partner == "split_other" & A_ij == 0 ///
                  & inlist(final_dec, "left", "right")
replace C_ij = 1 if signal_to_partner == "support_none" & final_dec == "noone"
replace C_ij = 0 if C_ij == . ///
    & signal_to_partner != "" & inlist(final_dec, "left", "right", "noone")

* -----------------------------------------------------------------------------
* 3b. DARK TRIAD INDICES (computed at dyad level, kept in both datasets)
* -----------------------------------------------------------------------------

generate double MACH = (mach_01 + mach_02 + mach_03 + mach_04 + mach_05 ///
                      + mach_06 + mach_07 + mach_08 + mach_09) / 9

generate double NARC = (narc_01 - narc_02 + narc_03 + narc_04 + narc_05 ///
                      - narc_06 + narc_07 - narc_08 + narc_09) / 9

generate double PSYCH = (psych_01 - psych_02 + psych_03 + psych_04 ///
                       + psych_06 - psych_07 + psych_08 + psych_09) / 9

label variable MACH  "Machiavellianism index (avg of 9 items)"
label variable NARC  "Narcissism index (signed avg of 9 items)"
label variable PSYCH "Psychopathy index (signed avg of 8 items, psych_05 excluded)"

* -----------------------------------------------------------------------------
* 3c. SAVE DYAD-LEVEL DATASET
* -----------------------------------------------------------------------------

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
         MACH NARC PSYCH ///
         patience risk reciprocity_positive reciprocity_negative altruism trust ///
         level_k time_falk time_levelk index_pages ///
         chat_message_count chat_message_count_focal_sent ///
         chat_message_count_partner_sent chat_transcript ///
         number_of_words number_of_messages ///
         nlp_sent_topics nlp_sent_topic_primary nlp_sent_n_topics ///
         topic_commitment topic_coalition_proposal topic_payoff_reasoning ///
         volume_continuous_words ///
         emotional_tone_continuous_0_100 ///
         sentiment_continuous_neg1_pos1 ///
         analytical_thinking_continuous_0 ///
         clout_continuous_0_100 ///
         authenticity_continuous_0_100 ///
         volume emotional_tone sentiment ///
         analytical_thinking clout authenticity

    order sessioncode group_id session treatment ///
          focal_player_id focal_player_color ///
          partner_id partner_color topology ///
          signal_to_partner S_ij A_ji A_ij persuasion_ij C_ij ///
          final_decision final_dec ///
          payoff group_valid any_timeout grp_drop grp_coordinate group_outcome ///
          MACH NARC PSYCH

    isid sessioncode group_id focal_player_id partner_id
    compress
    save `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', replace
    display as text "Saved ccf_dyad.dta  (" _N " directed pairs, 6 per group)"
restore

* -----------------------------------------------------------------------------
* 4. RESHAPE: 6 rows per group -> 3 rows per group
*    Pivot on topology: "left" -> _j suffix, "right" -> _k suffix
* -----------------------------------------------------------------------------

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
    MACH NARC PSYCH ///
    patience risk reciprocity_positive reciprocity_negative altruism trust ///
    level_k time_falk time_levelk index_pages ///
    topology ///
    partner_id partner_color signal_to_partner ///
    S_ij A_ij A_ji persuasion_ij C_ij ///
    chat_message_count chat_message_count_focal_sent chat_message_count_partner_sent ///
    chat_transcript ///
    number_of_words number_of_messages ///
    nlp_sent_topics nlp_sent_topic_primary nlp_sent_n_topics ///
    topic_commitment topic_coalition_proposal topic_payoff_reasoning ///
    volume_continuous_words ///
    emotional_tone_continuous_0_100 ///
    sentiment_continuous_neg1_pos1 ///
    analytical_thinking_continuous_0 ///
    clout_continuous_0_100 ///
    authenticity_continuous_0_100 ///
    volume emotional_tone sentiment ///
    analytical_thinking clout authenticity

* Shorten long stubs before reshape (Stata max 32 chars)
rename chat_message_count              _cmc
rename chat_message_count_focal_sent   _cmcfs
rename chat_message_count_partner_sent _cmcps
rename chat_transcript                 _ctrans
rename number_of_words                 _nwords
rename number_of_messages              _nmsgs
rename nlp_sent_topics                 _nlptop
rename nlp_sent_topic_primary          _nlprim
rename nlp_sent_n_topics               _nlpntop
rename topic_commitment                _tcommit
rename topic_coalition_proposal        _tcoal
rename topic_payoff_reasoning          _tpay
rename volume_continuous_words         _volcont
rename emotional_tone_continuous_0_100 _etcont
rename sentiment_continuous_neg1_pos1  _sentcont
rename analytical_thinking_continuous_0 _atcont
rename clout_continuous_0_100          _cloutcont
rename authenticity_continuous_0_100   _authcont
rename volume                          _vol
rename emotional_tone                  _et
rename sentiment                       _sent
rename analytical_thinking             _at
rename clout                           _clout
rename authenticity                    _auth

* Reshape wide
reshape wide ///
    partner_id partner_color signal_to_partner ///
    S_ij A_ij A_ji persuasion_ij C_ij ///
    _cmc _cmcfs _cmcps _ctrans ///
    _nwords _nmsgs ///
    _nlptop _nlprim _nlpntop ///
    _tcommit _tcoal _tpay ///
    _volcont _etcont _sentcont _atcont _cloutcont _authcont ///
    _vol _et _sent _at _clout _auth, ///
    i(sessioncode group_id focal_player_id) j(topology) string

* Rename: left -> j  ;  right -> k
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
rename _nwordsleft             words_j
rename _nwordsright            words_k
rename _nmsgsleft              msgs_j
rename _nmsgsright             msgs_k
rename _nlptopleft             nlp_topics_j
rename _nlptopright            nlp_topics_k
rename _nlprimleft             nlp_topic_primary_j
rename _nlprimright           nlp_topic_primary_k
rename _nlpntopleft            nlp_n_topics_j
rename _nlpntopright           nlp_n_topics_k
rename _tcommitleft            topic_commitment_j
rename _tcommitright           topic_commitment_k
rename _tcoalleft              topic_coalition_j
rename _tcoalright             topic_coalition_k
rename _tpayleft               topic_payoff_j
rename _tpayright              topic_payoff_k
rename _volcontleft            vol_words_j
rename _volcontright           vol_words_k
rename _etcontleft             emot_tone_j
rename _etcontright            emot_tone_k
rename _sentcontleft           sentiment_j
rename _sentcontright          sentiment_k
rename _atcontleft             analytic_j
rename _atcontright            analytic_k
rename _cloutcontleft          clout_j
rename _cloutcontright         clout_k
rename _authcontleft           authentic_j
rename _authcontright          authentic_k
rename _volleft                vol_ord_j
rename _volright               vol_ord_k
rename _etleft                 emot_tone_ord_j
rename _etright                emot_tone_ord_k
rename _sentleft               sentiment_ord_j
rename _sentright              sentiment_ord_k
rename _atleft                 analytic_ord_j
rename _atright                analytic_ord_k
rename _cloutleft              clout_ord_j
rename _cloutright             clout_ord_k
rename _authleft               authentic_ord_j
rename _authright              authentic_ord_k

* -----------------------------------------------------------------------------
* 5. PLAYER-LEVEL OUTCOMES
* -----------------------------------------------------------------------------

bysort sessioncode group_id: assert _N == 3

* Enforce persuasion = . if S == 0 (after reshape, check both directions)
replace persuasion_ij = . if S_ij == 0
replace persuasion_ik = . if S_ik == 0

* Strategic Deception
generate byte strategic_deception = ///
    (S_ij == 1 & S_ik == 1 & final_dec == "noone") ///
    if !missing(S_ij, S_ik) & final_dec != ""

* Choice-Signal Consistency
generate double CC_i = (C_ij + C_ik) / 2 if !missing(C_ij, C_ik)

* Sanity checks
assert inlist(CC_i, 0, .5, 1) if !missing(CC_i)

* -----------------------------------------------------------------------------
* 6. EFFICIENCY
* -----------------------------------------------------------------------------

bysort sessioncode group_id: egen double efficiency_group = mean(payoff)

bysort sessioncode group_id: gen byte _grp_tag = (_n == 1)
bysort treatment: egen double mean_efficiency_treat = mean(cond(_grp_tag == 1, efficiency_group, .))
drop _grp_tag

label variable mean_efficiency_treat "Mean group efficiency by treatment (group-weighted)"

* -----------------------------------------------------------------------------
* 7. LABELS
* -----------------------------------------------------------------------------

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
label variable persuasion_ij        "Persuasion i->j: S_ij x A_ji (. if S_ij=0)"
label variable persuasion_ik        "Persuasion i->k: S_ik x A_ki (. if S_ik=0)"
label variable C_ij                 "Signal to j consistent with i's final choice"
label variable C_ik                 "Signal to k consistent with i's final choice"
label variable CC_i                 "Choice-Signal Consistency: (C_ij + C_ik) / 2"
label variable strategic_deception  "Strategic Deception: signalled support to both, chose NoOne"
label variable efficiency_group     "Efficiency: mean group payoff"
label variable group_valid          "Group valid: complete, not dropped, no timeout"
label variable MACH                 "Machiavellianism index (avg of 9 items)"
label variable NARC                 "Narcissism index (signed avg of 9 items)"
label variable PSYCH                "Psychopathy index (signed avg of 8 items)"

format CC_i             %4.2f
format efficiency_group %6.2f
format MACH NARC PSYCH  %5.3f

* -----------------------------------------------------------------------------
* 8. COLUMN ORDER AND SAVE (ccf_master.dta)
* -----------------------------------------------------------------------------

order sessioncode group_id session treatment ///
      focal_player_id focal_player_color id_in_group player_color ///
      partner_j_id partner_j_color partner_k_id partner_k_color ///
      final_decision ///
      signal_ij signal_ik S_ij S_ik A_ji A_ki A_ij A_ik ///
      persuasion_ij persuasion_ik C_ij C_ik CC_i ///
      strategic_deception payoff efficiency_group ///
      grp_coordinate group_outcome group_valid ///
      MACH NARC PSYCH

isid sessioncode group_id focal_player_id
compress

save `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_master.dta"', replace

* -----------------------------------------------------------------------------
* 9. QUICK DIAGNOSTICS
* -----------------------------------------------------------------------------

display as result _newline "============================================"
display as result " ccf_master.dta -- ready"
display as result "============================================"
display as text   " Players (rows)   : " _N
display as text   " Groups total     : " _N / 3
quietly count if group_valid == 1
display as text   " Valid groups     : " r(N) / 3

display as result _newline "--- Persuasion ---"
quietly count if S_ij == 1 | S_ik == 1
display as text " Players who signalled at least one support : " r(N)
quietly count if persuasion_ij == 1
display as text " Successful persuasion i->j : " r(N)
quietly count if persuasion_ik == 1
display as text " Successful persuasion i->k : " r(N)

display as result _newline "--- Strategic Deception ---"
tab strategic_deception, missing

display as result _newline "--- Choice-Signal Consistency ---"
tab CC_i, missing

display as result _newline "--- Dark Triad (player-level means by treatment) ---"
tabstat MACH NARC PSYCH, by(treatment) stat(mean sd n) nototal col(stat)

display as result _newline "--- Efficiency by treatment (group-level N) ---"
preserve
    bysort sessioncode group_id: keep if _n == 1
    tabstat efficiency_group, by(treatment) stat(mean sd n)
restore

*==============================================================================
* 08_construct_CCF_outcomes.do
*
* Stata 19 -- construction of the defined behavioural outcomes in CCF.csv
*
* INPUT UNIT:  ordered pair i->partner, 6 rows per three-person group.
* OUTPUTS:
*   1. ccf_dyad_outcomes.dta          6 ordered pairs per group
*   2. ccf_player_outcomes.dta        3 players per group
*   3. ccf_group_efficiency.dta       1 row per group
*   4. ccf_efficiency_by_treatment.dta 1 row per treatment
*
* IMPORTANT CONVENTION IN THE PLAYER FILE:
*   j = i's topological LEFT partner; k = i's topological RIGHT partner.
*   The labels j and k have no substantive meaning; they only provide a stable,
*   reproducible ordering of the two other players.
*
* The original CSV is never modified. Existing S/A/persuasion columns in that
* CSV are renamed source_* and retained in the dyad output for audit purposes;
* none of them is used to construct the new outcomes.
*==============================================================================

version 19.0
clear all
set more off
set varabbrev off

* Set these globals before running the do-file to override either default path.
if `"$CCF_INPUT"' == "" {
    global CCF_INPUT `"C:\Users\Donat\OneDrive - Universita' degli Studi di Roma Tor Vergata\Academic_path\5_Pubblications\06_James\Experiment\STATA\CCF.csv"'
}
if `"$CCF_OUTPUT"' == "" {
    global CCF_OUTPUT `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\constructed_outcomes"'
}

local input  `"$CCF_INPUT"'
local outdir `"$CCF_OUTPUT"'

capture confirm file `"`input'"'
if _rc {
    display as error "Input file not found: `input'"
    exit 601
}

capture mkdir `"`outdir'"'
capture log close ccf_outcomes
log using `"`outdir'/08_construct_CCF_outcomes.log"', ///
    text replace name(ccf_outcomes)

* Set to 1 for the attached 2026-08-27 snapshot. These checks detect accidental
* use of a different file. Set to 0 deliberately when applying the code to a
* later data release; all structural checks below remain active.
local snapshot_audit 1

*==============================================================================
* 1. Import without type guessing
*==============================================================================

import delimited using `"`input'"', varnames(1) case(preserve) ///
    encoding("UTF-8") bindquote(strict) maxquotedrows(unlimited) ///
    stringcols(_all) clear

local required ///
    sessioncode group_id treatment id_in_session focal_player_id ///
    focal_player_color partner_id partner_color topology_side ///
    sendsignal_left sendsignal_right final_decision payoff ///
    payoff_eligible group_dropped decision_inactive signal_inactive ///
    grp_coordinate group_outcome grp_drop

foreach v of local required {
    capture confirm variable `v'
    if _rc {
        display as error "Required variable absent from CCF.csv: `v'"
        exit 111
    }
}

* Convert only variables required to be numeric. No force option is used:
* nonnumeric contamination therefore stops the pipeline rather than becoming .
local numeric_required ///
    group_id treatment id_in_session focal_player_id partner_id payoff ///
    payoff_eligible group_dropped decision_inactive signal_inactive ///
    grp_coordinate grp_drop

foreach v of local numeric_required {
    quietly destring `v', replace
    capture confirm numeric variable `v'
    if _rc {
        display as error "Variable `v' is not cleanly numeric."
        exit 459
    }
}

* Preserve, but never use, outcome columns already present in the source CSV.
foreach v in S_ij A_ji persuasion_ij S_ik A_ki persuasion_ik C_ij C_ik CC_i strategic_deception {
    capture confirm variable `v'
    if !_rc rename `v' source_`v'
}

*==============================================================================
* 2. Structural audit of the ordered-pair data
*==============================================================================

isid sessioncode group_id focal_player_id partner_id
assert !missing(sessioncode, group_id, focal_player_id, partner_id)
assert inlist(focal_player_id, 1, 2, 3)
assert inlist(partner_id, 1, 2, 3)
assert focal_player_id != partner_id

generate str5 topology_side_clean = lower(strtrim(topology_side))
generate str6 final_decision_clean = lower(strtrim(final_decision))

assert inlist(topology_side_clean, "left", "right")
assert inlist(final_decision_clean, "left", "right", "noone", "")

bysort sessioncode group_id: assert _N == 6
bysort sessioncode group_id: assert treatment == treatment[1]
bysort sessioncode group_id: assert grp_drop == grp_drop[1]
bysort sessioncode group_id: assert grp_coordinate == grp_coordinate[1]
bysort sessioncode group_id: assert group_outcome == group_outcome[1]

bysort sessioncode group_id focal_player_id: assert _N == 2
bysort sessioncode group_id focal_player_id: assert payoff == payoff[1]
bysort sessioncode group_id focal_player_id: ///
    egen byte n_left_rows = total(topology_side_clean == "left")
bysort sessioncode group_id focal_player_id: ///
    egen byte n_right_rows = total(topology_side_clean == "right")
assert n_left_rows == 1 & n_right_rows == 1
drop n_left_rows n_right_rows

* group_valid follows the project's codebook: complete triad, not dropped, and
* no member with a decision/signal timeout. Completeness is already guaranteed
* by the six-row and player-ID assertions above.
label define yesno 0 "No" 1 "Yes", replace
bysort sessioncode group_id: egen byte group_any_timeout = ///
    max(decision_inactive == 99 | signal_inactive == 99)
generate byte group_valid = (grp_drop == 0 & group_any_timeout == 0)
label values group_valid group_any_timeout yesno
label variable group_any_timeout "At least one member timed out"
label variable group_valid "Complete group, not dropped, no timeout"

if `snapshot_audit' {
    assert _N == 3042
    egen byte snapshot_group_tag = tag(sessioncode group_id)
    quietly count if snapshot_group_tag
    if r(N) != 507 {
        display as error "Snapshot audit failed: expected 507 groups, found " r(N) "."
        exit 459
    }
    drop snapshot_group_tag
    quietly count if group_valid == 1 & focal_player_id == 1 & ///
        topology_side_clean == "left"
    if r(N) != 481 {
        display as error "Snapshot audit failed: expected 481 valid groups, found " r(N) "."
        exit 459
    }
}

*==============================================================================
* 3. Ordered-pair outcomes
*==============================================================================

* signal_ij is the final signal that focal player i sent to this row's partner j.
* split_you = "I intend to support you".
generate str12 signal_ij = ""
replace signal_ij = lower(strtrim(sendsignal_left))  ///
    if topology_side_clean == "left"
replace signal_ij = lower(strtrim(sendsignal_right)) ///
    if topology_side_clean == "right"
assert inlist(signal_ij, "split_you", "split_other", "support_none", "")

generate byte S_ij = .
replace S_ij = (signal_ij == "split_you") if signal_ij != ""

* A_ij is an intermediate: i's final choice supports this row's partner j.
generate byte A_ij = .
replace A_ij = (final_decision_clean == topology_side_clean) ///
    if inlist(final_decision_clean, "left", "right", "noone")

* Consistency of i's signal to j with i's own final action:
*   split_you    is consistent iff i supports j;
*   split_other  is consistent iff i supports the third player k;
*   support_none is consistent iff i supports nobody.
generate byte C_ij = .
replace C_ij = ///
      (signal_ij == "split_you"    & A_ij == 1) ///
    | (signal_ij == "split_other"  & A_ij == 0 ///
       & inlist(final_decision_clean, "left", "right")) ///
    | (signal_ij == "support_none" & final_decision_clean == "noone") ///
    if signal_ij != "" & inlist(final_decision_clean, "left", "right", "noone")

* A_ji cannot be read from i's row. It is A_ij on the reverse ordered pair j->i.
* The 1:1 merge makes that reversal explicit and fails if a reverse pair is absent.
tempfile reverse_actions
preserve
    keep sessioncode group_id focal_player_id partner_id A_ij
    rename focal_player_id reverse_j
    rename partner_id      reverse_i
    rename reverse_i focal_player_id
    rename reverse_j partner_id
    rename A_ij A_ji
    isid sessioncode group_id focal_player_id partner_id
    save `reverse_actions'
restore

merge 1:1 sessioncode group_id focal_player_id partner_id ///
    using `reverse_actions', assert(match) nogen keepusing(A_ji)

generate byte persuasion_ij = S_ij * A_ji ///
    if !missing(S_ij, A_ji)

assert persuasion_ij == S_ij * A_ji if !missing(S_ij, A_ji)

label values S_ij A_ij A_ji persuasion_ij C_ij yesno
label variable signal_ij      "Final signal sent by i to partner j"
label variable S_ij           "i signals intended support to j"
label variable A_ij           "i's final choice supports j (intermediate)"
label variable A_ji           "j's final choice supports i"
label variable persuasion_ij  "Successful dyadic persuasion: S_ij x A_ji"
label variable C_ij           "i's signal to j is consistent with i's final choice"

order sessioncode group_id treatment focal_player_id focal_player_color ///
      partner_id partner_color topology_side_clean signal_ij ///
      S_ij A_ji persuasion_ij A_ij C_ij payoff

if `snapshot_audit' {
    quietly count if S_ij == 1
    if r(N) != 1817 {
        display as error "Snapshot audit failed for S_ij: expected 1817, found " r(N) "."
        exit 459
    }
    quietly count if A_ji == 1
    if r(N) != 1298 {
        display as error "Snapshot audit failed for A_ji: expected 1298, found " r(N) "."
        exit 459
    }
    quietly count if persuasion_ij == 1
    if r(N) != 1058 {
        display as error "Snapshot audit failed for persuasion_ij: expected 1058, found " r(N) "."
        exit 459
    }
    quietly count if C_ij == 1
    if r(N) != 2199 {
        display as error "Snapshot audit failed for C_ij: expected 2199, found " r(N) "."
        exit 459
    }
}

compress
save `"`outdir'/ccf_dyad_outcomes.dta"', replace

*==============================================================================
* 4. Player-level outcomes: j = left partner, k = right partner
*==============================================================================

preserve
    keep sessioncode group_id treatment id_in_session focal_player_id ///
         focal_player_color payoff payoff_eligible group_dropped ///
         grp_coordinate group_outcome grp_drop final_decision ///
         group_any_timeout group_valid final_decision_clean ///
         topology_side_clean partner_id partner_color ///
         signal_ij S_ij A_ji persuasion_ij C_ij

    * Variables not listed as reshape stubs must be constant across i's two rows.
    foreach v in treatment id_in_session focal_player_color payoff ///
                 payoff_eligible group_dropped grp_coordinate group_outcome ///
                 grp_drop group_any_timeout group_valid final_decision ///
                 final_decision_clean {
        bysort sessioncode group_id focal_player_id: assert `v' == `v'[1]
    }

    reshape wide partner_id partner_color signal_ij S_ij A_ji ///
        persuasion_ij C_ij, ///
        i(sessioncode group_id focal_player_id) ///
        j(topology_side_clean) string

    rename partner_idleft partner_j_id
    rename partner_idright partner_k_id
    rename partner_colorleft partner_j_color
    rename partner_colorright partner_k_color
    rename signal_ijleft signal_ij
    rename signal_ijright signal_ik
    rename S_ijleft S_ij
    rename S_ijright S_ik
    rename A_jileft A_ji
    rename A_jiright A_ki
    rename persuasion_ijleft persuasion_ij
    rename persuasion_ijright persuasion_ik
    rename C_ijleft C_ij
    rename C_ijright C_ik

    generate byte strategic_deception = .
    replace strategic_deception = ///
        (S_ij == 1 & S_ik == 1 & final_decision_clean == "noone") ///
        if !missing(S_ij, S_ik) & final_decision_clean != ""

    generate double CC_i = (C_ij + C_ik) / 2 ///
        if !missing(C_ij, C_ik)

    assert inlist(CC_i, 0, .5, 1) if !missing(CC_i)
    assert persuasion_ij == S_ij * A_ji if !missing(S_ij, A_ji)
    assert persuasion_ik == S_ik * A_ki if !missing(S_ik, A_ki)

    label values S_ij S_ik A_ji A_ki persuasion_ij persuasion_ik ///
                 C_ij C_ik strategic_deception yesno
    label variable partner_j_id       "j: i's topological left partner"
    label variable partner_k_id       "k: i's topological right partner"
    label variable signal_ij          "Final signal from i to left partner j"
    label variable signal_ik          "Final signal from i to right partner k"
    label variable S_ij               "i signals intended support to j"
    label variable S_ik               "i signals intended support to k"
    label variable A_ji               "j's final choice supports i"
    label variable A_ki               "k's final choice supports i"
    label variable persuasion_ij      "Successful persuasion of j by i"
    label variable persuasion_ik      "Successful persuasion of k by i"
    label variable C_ij               "Signal to j is consistent with i's choice"
    label variable C_ik               "Signal to k is consistent with i's choice"
    label variable CC_i               "Choice-signal consistency: (C_ij + C_ik)/2"
    label variable strategic_deception ///
        "Signals support to both partners, then supports neither"
    format CC_i %3.1f

    order sessioncode group_id treatment focal_player_id focal_player_color ///
          partner_j_id partner_j_color partner_k_id partner_k_color ///
          signal_ij signal_ik S_ij S_ik A_ji A_ki ///
          persuasion_ij persuasion_ik C_ij C_ik CC_i ///
          strategic_deception final_decision payoff

    isid sessioncode group_id focal_player_id
    bysort sessioncode group_id: assert _N == 3

    if `snapshot_audit' {
        assert _N == 1521
        quietly count if strategic_deception == 1
        if r(N) != 93 {
            display as error "Snapshot audit failed for strategic_deception: expected 93, found " r(N) "."
            exit 459
        }
        quietly count if CC_i == 0
        if r(N) != 204 {
            display as error "Snapshot audit failed for CC_i=0: expected 204, found " r(N) "."
            exit 459
        }
        quietly count if CC_i == .5
        if r(N) != 435 {
            display as error "Snapshot audit failed for CC_i=.5: expected 435, found " r(N) "."
            exit 459
        }
        quietly count if CC_i == 1
        if r(N) != 882 {
            display as error "Snapshot audit failed for CC_i=1: expected 882, found " r(N) "."
            exit 459
        }
    }

    compress
    save `"`outdir'/ccf_player_outcomes.dta"', replace

    *==========================================================================
    * 5. Efficiency: group first, treatment second
    *==========================================================================

    * payoff was duplicated in the original dyad-long CSV. At this point there
    * is one row per player, so every participant enters exactly once.
    bysort sessioncode group_id: assert treatment == treatment[1]
    bysort sessioncode group_id: egen double efficiency_group = mean(payoff)
    bysort sessioncode group_id: egen double group_total_payoff = total(payoff)
    bysort sessioncode group_id: egen byte n_payoffs_nonmissing = count(payoff)
    assert n_payoffs_nonmissing == 3

    label variable efficiency_group ///
        "Efficiency: mean payoff of the three group members"
    label variable group_total_payoff "Sum of the three group members' payoffs"
    label variable n_payoffs_nonmissing "Nonmissing player payoffs in group"

    bysort sessioncode group_id: keep if _n == 1
    isid sessioncode group_id

    * Equal group weights within treatment: one group-level observation each.
    * Both the full randomized sample and the codebook-valid sample are kept;
    * no exclusion is hidden in the construction step.
    bysort treatment: egen double mean_efficiency_all = mean(efficiency_group)
    bysort treatment: egen double sd_efficiency_all = sd(efficiency_group)
    bysort treatment: egen int n_groups_all = count(efficiency_group)
    bysort treatment: egen double mean_efficiency_valid = ///
        mean(cond(group_valid == 1, efficiency_group, .))
    bysort treatment: egen double sd_efficiency_valid = ///
        sd(cond(group_valid == 1, efficiency_group, .))
    bysort treatment: egen int n_groups_valid = ///
        total(group_valid == 1 & !missing(efficiency_group))

    label variable mean_efficiency_all ///
        "Mean group efficiency by treatment: all groups"
    label variable sd_efficiency_all ///
        "SD of group efficiency by treatment: all groups"
    label variable n_groups_all "Groups in treatment: all groups"
    label variable mean_efficiency_valid ///
        "Mean group efficiency by treatment: valid groups"
    label variable sd_efficiency_valid ///
        "SD of group efficiency by treatment: valid groups"
    label variable n_groups_valid "Groups in treatment: valid groups"

    keep sessioncode group_id treatment efficiency_group ///
         group_total_payoff n_payoffs_nonmissing ///
         mean_efficiency_all sd_efficiency_all n_groups_all ///
         mean_efficiency_valid sd_efficiency_valid n_groups_valid ///
         group_valid group_any_timeout grp_coordinate group_outcome grp_drop
    order sessioncode group_id treatment efficiency_group ///
          group_total_payoff n_payoffs_nonmissing ///
          mean_efficiency_all mean_efficiency_valid ///
          n_groups_all n_groups_valid group_valid

    if `snapshot_audit' {
        assert _N == 507
        quietly count if treatment == 1
        if r(N) != 172 exit 459
        quietly count if treatment == 2
        if r(N) != 169 exit 459
        quietly count if treatment == 3
        if r(N) != 166 exit 459
        quietly count if group_valid == 1
        if r(N) != 481 exit 459
    }

    compress
    save `"`outdir'/ccf_group_efficiency.dta"', replace

    * A compact treatment-level estimand table, based on the group-level file.
    bysort treatment: keep if _n == 1
    keep treatment mean_efficiency_all sd_efficiency_all n_groups_all ///
         mean_efficiency_valid sd_efficiency_valid n_groups_valid
    generate double se_efficiency_all = ///
        sd_efficiency_all / sqrt(n_groups_all)
    generate double se_efficiency_valid = ///
        sd_efficiency_valid / sqrt(n_groups_valid)
    label variable se_efficiency_all ///
        "SE of mean efficiency: all groups"
    label variable se_efficiency_valid ///
        "SE of mean efficiency: valid groups"
    format mean_efficiency_all sd_efficiency_all se_efficiency_all ///
           mean_efficiency_valid sd_efficiency_valid ///
           se_efficiency_valid %9.4f
    isid treatment
    sort treatment
    list treatment mean_efficiency_all se_efficiency_all n_groups_all ///
         mean_efficiency_valid se_efficiency_valid n_groups_valid, ///
         noobs clean abbreviate(32)
    save `"`outdir'/ccf_efficiency_by_treatment.dta"', replace
restore

*==============================================================================
* 6. Reproducibility report
*==============================================================================

display _newline as result "Construction completed successfully."
display as text "Dyad file:      `outdir'/ccf_dyad_outcomes.dta"
display as text "Player file:    `outdir'/ccf_player_outcomes.dta"
display as text "Group file:     `outdir'/ccf_group_efficiency.dta"
display as text "Treatment file: `outdir'/ccf_efficiency_by_treatment.dta"
display as text "Audit log:      `outdir'/08_construct_CCF_outcomes.log"

log close ccf_outcomes

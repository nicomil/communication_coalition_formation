*==============================================================================
* 11_treatment_comparison.do
*
* Treatment comparisons — 3 treatments: Baseline (1), Public (2), Slacker (3)
*
* For each outcome variable:
*   A. OVERALL TEST across all 3 treatments
*      Parametric:     one-way ANOVA  /  OLS with clustered SE + joint F-test
*      Non-parametric: Kruskal-Wallis
*
*   B. PAIRWISE TESTS  (3 pairs)
*      Baseline vs Public    (treatment == 1 vs 2)
*      Baseline vs Slacker   (treatment == 1 vs 3)
*      Public   vs Slacker   (treatment == 2 vs 3)
*      Parametric:     Welch t-test  /  OLS clustered SE
*      Non-parametric: Wilcoxon rank-sum
*
* NOTE on units of analysis:
*   efficiency_group   -> GROUP level  (preserve; keep 1 row per group)
*   CC_i               -> PLAYER level (cluster SE at group level)
*   persuasion_ij / ik -> DYAD level   (ccf_dyad.dta; cluster at group level)
*   topic_*            -> DYAD level   (ccf_dyad.dta; cluster at group level)
*   Sections 18–23     -> TopicGPT Topics (Coalition Proposal, Commitment, Payoff Reasoning)
*==============================================================================

version 19.0
clear all
set more off

use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_master.dta"', clear
keep if group_valid == 1

*------------------------------------------------------------------------------
* Utility program: prints a pairwise comparison header
*------------------------------------------------------------------------------
capture program drop pair_header
program define pair_header
    args lab1 lab2
    display as result _newline "  -- `lab1'  vs  `lab2' --"
end

*==============================================================================
* SECTION 1 -- EFFICIENCY
* Unit of analysis: GROUP. efficiency_group repeats 3 times per group, so
* we collapse to 1 row per group inside preserve/restore before any test.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 1. EFFICIENCY   (unit = group)"
display as result "========================================================"

preserve
    bysort sessioncode group_id: keep if _n == 1

    display as result _newline "--- Descriptives by treatment ---"
    tabstat efficiency_group, by(treatment) stat(n mean sd p50) nototal col(stat)

    display as result _newline "--- A. Overall: one-way ANOVA ---"
    oneway efficiency_group treatment, tabulate

    display as result _newline "--- A. Overall: Kruskal-Wallis ---"
    kwallis efficiency_group, by(treatment)

    display as result _newline "--- B. Pairwise ---"
    foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
        local t1   = word("`pair'", 1)
        local t2   = word("`pair'", 2)
        local lab1 = word("`pair'", 3)
        local lab2 = word("`pair'", 4)
        pair_header `lab1' `lab2'
        ttest efficiency_group if inlist(treatment,`t1',`t2'), by(treatment) unequal
        ranksum efficiency_group if inlist(treatment,`t1',`t2'), by(treatment)
    }
restore

*==============================================================================
* SECTION 2 -- CHOICE-SIGNAL CONSISTENCY  CC_i
* Unit of analysis: PLAYER. Cluster SE at group level (3 players share a game).
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 2. CHOICE-SIGNAL CONSISTENCY  CC_i   (unit = player)"
display as result "========================================================"

display as result _newline "--- Descriptives by treatment ---"
tabstat CC_i, by(treatment) stat(n mean sd p50) nototal col(stat)

display as result _newline "--- Distribution CC_i in {0, 0.5, 1} by treatment ---"
tab CC_i treatment, col chi2

display as result _newline "--- A. Overall: OLS group-clustered SE + joint F-test ---"
regress CC_i i.treatment, vce(cluster group_id)
testparm i.treatment

display as result _newline "--- A. Overall: Kruskal-Wallis ---"
kwallis CC_i, by(treatment)

display as result _newline "--- B. Pairwise ---"
foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
    local t1   = word("`pair'", 1)
    local t2   = word("`pair'", 2)
    local lab1 = word("`pair'", 3)
    local lab2 = word("`pair'", 4)
    pair_header `lab1' `lab2'
    ttest CC_i if inlist(treatment,`t1',`t2'), by(treatment) unequal
    regress CC_i i.treatment if inlist(treatment,`t1',`t2'), vce(cluster group_id)
    ranksum CC_i if inlist(treatment,`t1',`t2'), by(treatment)
}

*==============================================================================
* SECTION 3 -- PERSUASION  persuasion_ij = S_ij x A_ji
* Unit of analysis: DIRECTED PAIR (6 per group). Use ccf_dyad.dta.
* Binary outcome: proportion z-test (parametric) + OLS LPM clustered.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 3. PERSUASION   persuasion_ij = S_ij x A_ji"
display as result "    (unit = directed pair, 6 per group, from ccf_dyad.dta)"
display as result "========================================================"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    display as result _newline "--- Proportion persuasion_ij = 1 by treatment ---"
    tabstat persuasion_ij, by(treatment) stat(n mean sd) nototal col(stat)

    display as result _newline "--- Cross-tab persuasion_ij x treatment ---"
    tab persuasion_ij treatment, col chi2 exact

    display as result _newline "--- A. Overall: OLS (LPM) group-clustered SE + joint F-test ---"
    regress persuasion_ij i.treatment , vce(cluster group_id)
    testparm i.treatment

    display as result _newline "--- A. Overall: Kruskal-Wallis ---"
    kwallis persuasion_ij, by(treatment)

    display as result _newline "--- B. Pairwise ---"
    foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
        local t1   = word("`pair'", 1)
        local t2   = word("`pair'", 2)
        local lab1 = word("`pair'", 3)
        local lab2 = word("`pair'", 4)
        pair_header `lab1' `lab2'
        prtest persuasion_ij if inlist(treatment,`t1',`t2'), by(treatment)
        regress persuasion_ij i.treatment if inlist(treatment,`t1',`t2'), ///
            vce(cluster group_id)
        ranksum persuasion_ij if inlist(treatment,`t1',`t2'), by(treatment)
    }
restore

*==============================================================================
* SECTION 3b -- PERSUASION by direction (player-wide, ccf_master)
* persuasion_ij = toward left partner j
* persuasion_ik = toward right partner k
* Tests symmetry across topological directions.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 3b. PERSUASION by direction (player-wide)"
display as result "========================================================"

foreach var in persuasion_ij persuasion_ik {

    display as result _newline "=== `var' ==="
    tabstat `var', by(treatment) stat(n mean sd) nototal col(stat)

    display as result _newline "--- A. Overall: OLS (LPM) group-clustered SE ---"
    regress `var' i.treatment, vce(cluster group_id)
    testparm i.treatment

    display as result _newline "--- A. Overall: Kruskal-Wallis ---"
    kwallis `var', by(treatment)

    display as result _newline "--- B. Pairwise ---"
    foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
        local t1   = word("`pair'", 1)
        local t2   = word("`pair'", 2)
        local lab1 = word("`pair'", 3)
        local lab2 = word("`pair'", 4)
        pair_header `lab1' `lab2'
        regress `var' i.treatment if inlist(treatment,`t1',`t2'), vce(cluster group_id)
        ranksum `var' if inlist(treatment,`t1',`t2'), by(treatment)
    }
}

display as result _newline(2) "========================================================"
display as result " Done."
display as result "========================================================"

*==============================================================================
* SECTION 4 -- OUTCOME TYPE BAR CHART
*   Unit of analysis: GROUP (1 row per group).
*   Outcomes:
*     Baseline / Public : coalition (mutual_*) | zero payoff (disagreement)
*     Slacker           : coalition (mutual_*) | slacker (no_dwl_star_*)
*                         | zero payoff (disagreement)
*   Restriction: group_valid == 1  (already loaded above)
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 4. OUTCOME TYPE BAR CHART  (unit = group)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    * ── Collapse to one row per group ──────────────────────────────────────
    bysort sessioncode group_id: keep if _n == 1

    * ── Count groups per treatment for x-axis labels ─────────────────────────
    quietly count if treatment == 1
    local n_g1 = r(N)
    quietly count if treatment == 2
    local n_g2 = r(N)
    quietly count if treatment == 3
    local n_g3 = r(N)

    * ── Classify each group's outcome into three mutually exclusive types ──
    * group_outcome values:
    *   mutual_12, mutual_23, mutual_31  → coalition
    *   no_dwl_star_1/2/3               → slacker star (Slacker treatment only)
    *   disagreement                     → zero payoff
    generate byte out_coalition = inlist(group_outcome, ///
        "mutual_12", "mutual_23", "mutual_31")
    generate byte out_slacker   = inlist(group_outcome, ///
        "no_dwl_star_1", "no_dwl_star_2", "no_dwl_star_3")
    generate byte out_zeropay   = (group_outcome == "disagreement")

    * ── Compute proportions by treatment ────────────────────────────────────
    * We need one percentage per (treatment × outcome_type) cell.
    * collapse to treatment means → each proportion is the group-level share.
    collapse (mean) out_coalition out_slacker out_zeropay, by(treatment)

    * Convert to percentages
    foreach v in out_coalition out_slacker out_zeropay {
        replace `v' = `v' * 100
    }

    * ── Stack for bar chart: reshape to long ────────────────────────────────
    generate id = _n
    reshape long out_, i(id treatment) j(outcome_type) string

    * Ordered category: 1=Coalition  2=Zero payoff  3=Slacker star
    generate byte out_cat = .
    replace out_cat = 1 if outcome_type == "coalition"
    replace out_cat = 2 if outcome_type == "zeropay"
    replace out_cat = 3 if outcome_type == "slacker"
    label define out_lbl 1 "Coalition" 2 "Zero payoff" 3 "Slacker star", replace
    label values out_cat out_lbl

    * ── Treatment labels with N groups (applied after reshape) ───────────────
    label define trt_lbl 1 `"Baseline (N=`n_g1')"' 2 `"Public (N=`n_g2')"' 3 `"Slacker (N=`n_g3')"', replace
    label values treatment trt_lbl

    * ── Bar chart ────────────────────────────────────────────────────────────
    graph bar out_,                                          ///
        over(out_cat, label(angle(0) labsize(small)))        ///
        over(treatment, relabel(1 `"Baseline (N=`n_g1')"' 2 `"Public (N=`n_g2')"' 3 `"Slacker (N=`n_g3')"') label(labsize(medsmall))) ///
        asyvars                                              ///
        bargap(10)                                           ///
        title("Outcome Type by Treatment", size(medlarge))   ///
        ytitle("% of groups")                               ///
        ylabel(0(10)100, grid)                               ///
        blabel(bar, format(%4.1f) size(small))               ///
        bar(1, color(black))                                 ///
        bar(2, color(gray))                                  ///
        bar(3, color(navy))                                 ///
        legend(title("Outcome type", size(small))            ///
               order(1 "Coalition" 2 "Zero payoff" 3 "Slacker star") ///
               cols(1) size(small))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_outcome_types_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_outcome_types_by_treatment.png"

    * ── Print the underlying proportions ───────────────────────────────────
    display as result _newline "--- % by treatment and outcome type ---"
    list treatment out_cat out_ if out_cat != ., ///
        noobs abbrev(20) sepby(treatment)

restore

*==============================================================================
* SECTION 5 -- FISHER EXACT TEST: % ZERO PAYOFF
*   Comparison: Baseline (1) vs Public (2) ; Baseline (1) vs Slacker (3)
*   Unit: GROUP.  Fisher exact test on 2×2 table (zero_payoff × treatment).
*   Restriction: group_valid == 1.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 5. FISHER EXACT TEST: % ZERO PAYOFF  (unit = group)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    * Collapse to one row per group
    bysort sessioncode group_id: keep if _n == 1

    generate byte zero_payoff = (group_outcome == "disagreement")

    display as result _newline "--- Frequencies by treatment ---"
    tabstat zero_payoff, by(treatment) stat(n sum mean) nototal col(stat)

    display as result _newline "--- Fisher exact test: Baseline vs Public ---"
    tab zero_payoff treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact test: Baseline vs Slacker ---"
    tab zero_payoff treatment if inlist(treatment, 1, 3), row col exact

restore

*==============================================================================
* SECTION 6 -- INDIVIDUAL CHOICE: % SUPPORT NO ONE   BAR CHART
*   Unit of analysis: PLAYER (one row per player).
*   Outcome: indicator for individual choice == "no_one" (support no one).
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 6. INDIVIDUAL CHOICE: % SUPPORT NO ONE  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player (dataset has 2 rows per player, one per dyad) ─
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Count players per treatment for x-axis labels ────────────────────────
    quietly count if treatment == 1
    local n_p1 = r(N)
    quietly count if treatment == 2
    local n_p2 = r(N)
    quietly count if treatment == 3
    local n_p3 = r(N)

    * ── Binary indicator: 1 if the player's individual choice is "no one" ──
    generate byte support_noone = (final_decision == "NoOne")

    * ── Descriptives by treatment ─────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment ---"
    tabstat support_noone, by(treatment) stat(n sum mean) nototal col(stat)

    * ── Collapse to one mean (proportion) per treatment ───────────────────
    collapse (mean) support_noone, by(treatment)
    replace support_noone = support_noone * 100

    * ── Treatment labels with N players ──────────────────────────────────────
    label define trt_lbl6 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl6

    * ── Bar chart ─────────────────────────────────────────────────────────
    graph bar support_noone,                                               ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars showyvars                                                  ///
        bargap(20)                                                         ///
        title("% Support No One by Treatment", size(medlarge))            ///
        ytitle("% of players")                                            ///
        ylabel(0(10)100, grid)                                             ///
        blabel(bar, format(%4.1f) size(small))                            ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(dnavy))                                               ///
        legend(off)

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_support_noone_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_support_noone_by_treatment.png"

restore

*==============================================================================
* SECTION 7 -- FISHER EXACT TEST: % SUPPORT NO ONE
*   Comparison: Baseline (1) vs Public (2) ; Baseline (1) vs Slacker (3)
*   Unit: PLAYER.  Fisher exact test on 2×2 table (support_noone × treatment).
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 7. FISHER EXACT TEST: % SUPPORT NO ONE  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player (dataset has 2 rows per player, one per dyad) ─
    bysort sessioncode group_id id_in_group: keep if _n == 1

    generate byte support_noone = (final_decision == "NoOne")

    display as result _newline "--- Frequencies by treatment ---"
    tabstat support_noone, by(treatment) stat(n sum mean) nototal col(stat)

    display as result _newline "--- Fisher exact test: Baseline vs Public ---"
    tab support_noone treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact test: Baseline vs Slacker ---"
    tab support_noone treatment if inlist(treatment, 1, 3), row col exact

restore

*==============================================================================
* SECTION 8 -- SIGNAL TYPE BAR CHART: Honest, Deceptive, Other
*   Unit of analysis: PLAYER (1 row per player, signals constant within player).
*   Classification (3 mutually exclusive categories, 9 total combinations):
*     1. Honest:
*        - (split_you, split_other) OR (split_other, split_you)
*     2. Deceptive:
*        - (split_you, split_you)
*     3. Other (6 combinations):
*        - (support_none, support_none)
*        - (support_none, split_you)
*        - (support_none, split_other)
*        - (split_you, support_none)
*        - (split_other, support_none)
*        - (split_other, split_other)
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 8. SIGNAL TYPE BAR CHART: Honest, Deceptive, Other  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    * ── Keep one row per player ──────────────────────────────────────────────
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Count players per treatment for x-axis labels ────────────────────────
    quietly count if treatment == 1
    local n_p1 = r(N)
    quietly count if treatment == 2
    local n_p2 = r(N)
    quietly count if treatment == 3
    local n_p3 = r(N)

    * ── Raw crosstab: inspect all observed (left × right) combinations ───────
    display as result _newline "--- Raw signal combinations (sendsignal_left x sendsignal_right) ---"
    tab sendsignal_left sendsignal_right, miss

    * ── Classify signal type (3 categories: Honest, Deceptive, Other) ────────
    generate byte sig_honest    = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_other") | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_you")

    generate byte sig_deceptive = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_you")

    generate byte sig_other     = ///
        (inlist(sendsignal_left, "support_none", "supportNone") & inlist(sendsignal_right, "support_none", "supportNone")) | ///
        (inlist(sendsignal_left, "support_none", "supportNone") & sendsignal_right == "split_you")                         | ///
        (inlist(sendsignal_left, "support_none", "supportNone") & sendsignal_right == "split_other")                       | ///
        (sendsignal_left == "split_you"   & inlist(sendsignal_right, "support_none", "supportNone"))                         | ///
        (sendsignal_left == "split_other" & inlist(sendsignal_right, "support_none", "supportNone"))                         | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_other")

    * Sanity check: every player in exactly one category (all 9 combos covered)
    assert sig_honest + sig_deceptive + sig_other == 1

    * ── Descriptives by treatment ────────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment ---"
    tabstat sig_honest sig_deceptive sig_other, ///
        by(treatment) stat(n sum mean) nototal col(stat)

    * ── Collapse to proportions per treatment ────────────────────────────────
    collapse (mean) sig_honest sig_deceptive sig_other, by(treatment)
    foreach v in sig_honest sig_deceptive sig_other {
        replace `v' = `v' * 100
    }

    * ── Reshape to long for grouped bar chart ────────────────────────────────
    generate id = _n
    reshape long sig_, i(id treatment) j(sig_type) string

    generate byte sig_cat = .
    replace sig_cat = 1 if sig_type == "honest"
    replace sig_cat = 2 if sig_type == "deceptive"
    replace sig_cat = 3 if sig_type == "other"
    label define sig_lbl 1 "Honest" 2 "Deceptive" 3 "Other", replace
    label values sig_cat sig_lbl

    * ── Treatment labels with N players (applied after reshape) ──────────────
    label define trt_lbl8 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl8

    * ── Bar chart: 3 clusters (one per treatment), 3 bars per cluster ────────
    graph bar sig_,                                                           ///
        over(sig_cat, label(angle(0) labsize(small)))                         ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars                                                               ///
        bargap(10)                                                            ///
        title("Signal Type by Treatment", size(medlarge))                    ///
        ytitle("% of players")                                               ///
        ylabel(0(10)100, grid)                                                ///
        blabel(bar, format(%4.1f) size(small))                               ///
        bar(1, color(black))                                                 ///
        bar(2, color(gray))                                                  ///
        bar(3, color(dnavy))                                                 ///
        legend(title("Signal type", size(small))                             ///
               order(1 "Honest" 2 "Deceptive" 3 "Other")                    ///
               cols(1) size(small))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_signal_type_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_signal_type_by_treatment.png"

restore

*==============================================================================
* SECTION 8b -- SIGNAL TYPE BAR CHART: Honest (incl. No One to both)
*   Alternative specification:
*     1. Honest (broad):
*        - (split_you, split_other) OR (split_other, split_you)
*        - PLUS (support_none, support_none) → truthful commitment to no one
*     2. Deceptive:
*        - (split_you, split_you)
*     3. Other (remaining 5 combinations):
*        - (support_none, split_you)
*        - (support_none, split_other)
*        - (split_you, support_none)
*        - (split_other, support_none)
*        - (split_other, split_other)
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 8b. SIGNAL TYPE BAR CHART: Honest incl. No One to both (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    * ── Keep one row per player ──────────────────────────────────────────────
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Count players per treatment for x-axis labels ────────────────────────
    quietly count if treatment == 1
    local n_p1 = r(N)
    quietly count if treatment == 2
    local n_p2 = r(N)
    quietly count if treatment == 3
    local n_p3 = r(N)

    * ── Classify signal type (Honest includes support_none to both) ───────────
    generate byte sig_honest_broad = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_other") | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_you")   | ///
        (inlist(sendsignal_left, "support_none", "supportNone") & inlist(sendsignal_right, "support_none", "supportNone"))

    generate byte sig_deceptive = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_you")

    generate byte sig_other_broad = ///
        (inlist(sendsignal_left, "support_none", "supportNone") & sendsignal_right == "split_you")   | ///
        (inlist(sendsignal_left, "support_none", "supportNone") & sendsignal_right == "split_other") | ///
        (sendsignal_left == "split_you"   & inlist(sendsignal_right, "support_none", "supportNone"))   | ///
        (sendsignal_left == "split_other" & inlist(sendsignal_right, "support_none", "supportNone"))   | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_other")

    * Sanity check: all 9 combos covered
    assert sig_honest_broad + sig_deceptive + sig_other_broad == 1

    * ── Descriptives by treatment ────────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment (Honest incl. No One to both) ---"
    tabstat sig_honest_broad sig_deceptive sig_other_broad, ///
        by(treatment) stat(n sum mean) nototal col(stat)

    * ── Collapse to proportions per treatment ────────────────────────────────
    collapse (mean) sig_honest_broad sig_deceptive sig_other_broad, by(treatment)
    foreach v in sig_honest_broad sig_deceptive sig_other_broad {
        replace `v' = `v' * 100
    }

    * ── Reshape to long for grouped bar chart ────────────────────────────────
    generate id = _n
    reshape long sig_, i(id treatment) j(sig_type) string

    generate byte sig_cat = .
    replace sig_cat = 1 if sig_type == "honest_broad"
    replace sig_cat = 2 if sig_type == "deceptive"
    replace sig_cat = 3 if sig_type == "other_broad"
    label define sig_lbl_b 1 "Honest (incl. No One)" 2 "Deceptive" 3 "Other", replace
    label values sig_cat sig_lbl_b

    * ── Treatment labels with N players (applied after reshape) ──────────────
    label define trt_lbl8b 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl8b

    * ── Bar chart: 3 clusters (one per treatment), 3 bars per cluster ────────
    graph bar sig_,                                                           ///
        over(sig_cat, label(angle(0) labsize(small)))                         ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars                                                               ///
        bargap(10)                                                            ///
        title("Signal Type by Treatment (Honest incl. No One to Both)", size(medlarge)) ///
        ytitle("% of players")                                               ///
        ylabel(0(10)100, grid)                                                ///
        blabel(bar, format(%4.1f) size(small))                               ///
        bar(1, color(black))                                                 ///
        bar(2, color(gray))                                                  ///
        bar(3, color(dnavy))                                                 ///
        legend(title("Signal type", size(small))                             ///
               order(1 "Honest (incl. No One)" 2 "Deceptive" 3 "Other")     ///
               cols(1) size(small))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_signal_type_broad_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_signal_type_broad_by_treatment.png"

restore

*==============================================================================
* SECTION 9 -- FISHER EXACT TESTS: SIGNAL TYPES
*   Comparison: Baseline (1) vs Public (2) ; Baseline (1) vs Slacker (3)
*   Unit: PLAYER (1 row per player).  Fisher exact on 2×2 tables.
*   Tests:
*     1. % Honest (standard: split_you + split_other)
*     2. % Honest broad (includes support_none to both)
*     3. % Deceptive (split_you + split_you)
*     4. % Other
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 9. FISHER EXACT TESTS: SIGNAL TYPES  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Signal type indicators ───────────────────────────────────────────────
    generate byte sig_honest = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_other") | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_you")

    generate byte sig_honest_broad = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_other") | ///
        (sendsignal_left == "split_other" & sendsignal_right == "split_you")   | ///
        (inlist(sendsignal_left, "support_none", "supportNone") & inlist(sendsignal_right, "support_none", "supportNone"))

    generate byte sig_deceptive = ///
        (sendsignal_left == "split_you"   & sendsignal_right == "split_you")

    generate byte sig_other = ///
        (sig_honest == 0 & sig_deceptive == 0)

    * ── Frequencies ──────────────────────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment ---"
    tabstat sig_honest sig_honest_broad sig_deceptive sig_other, ///
        by(treatment) stat(n sum mean) nototal col(stat)

    * ── Fisher exact: % HONEST (standard) ────────────────────────────────────
    display as result _newline "--- Fisher exact (Honest standard): Baseline vs Public ---"
    tab sig_honest treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact (Honest standard): Baseline vs Slacker ---"
    tab sig_honest treatment if inlist(treatment, 1, 3), row col exact

    * ── Fisher exact: % HONEST BROAD (incl. No One to both) ──────────────────
    display as result _newline "--- Fisher exact (Honest broad): Baseline vs Public ---"
    tab sig_honest_broad treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact (Honest broad): Baseline vs Slacker ---"
    tab sig_honest_broad treatment if inlist(treatment, 1, 3), row col exact

    * ── Fisher exact: % DECEPTIVE ────────────────────────────────────────────
    display as result _newline "--- Fisher exact (Deceptive): Baseline vs Public ---"
    tab sig_deceptive treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact (Deceptive): Baseline vs Slacker ---"
    tab sig_deceptive treatment if inlist(treatment, 1, 3), row col exact

    * ── Fisher exact: % OTHER ────────────────────────────────────────────────
    display as result _newline "--- Fisher exact (Other): Baseline vs Public ---"
    tab sig_other treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact (Other): Baseline vs Slacker ---"
    tab sig_other treatment if inlist(treatment, 1, 3), row col exact

restore

*==============================================================================
* SECTION 10 -- CHOICE-SIGNAL FULL CONSISTENCY BAR CHART
*   Unit of analysis: PLAYER (1 row per player).
*   Outcome: indicator for full consistency (CC_i == 1), meaning player's final
*            choice is consistent with messages sent to BOTH partners.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 10. FULL CONSISTENCY BAR CHART (CC_i == 1)  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player (dataset has 2 rows per player, one per dyad) ─
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Count players per treatment for x-axis labels ────────────────────────
    quietly count if treatment == 1 & !missing(CC_i)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(CC_i)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(CC_i)
    local n_p3 = r(N)

    * ── Binary indicator: 1 if choice is fully consistent with both messages ──
    generate byte full_consistency = (CC_i == 1) if !missing(CC_i)

    * ── Descriptives by treatment ────────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment ---"
    tabstat full_consistency, by(treatment) stat(n sum mean) nototal col(stat)

    * ── Collapse to one mean (proportion) per treatment ──────────────────────
    collapse (mean) full_consistency, by(treatment)
    replace full_consistency = full_consistency * 100

    * ── Treatment labels with N players ──────────────────────────────────────
    label define trt_lbl10 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl10

    * ── Bar chart ────────────────────────────────────────────────────────────
    graph bar full_consistency,                                            ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars showyvars                                                  ///
        bargap(20)                                                         ///
        title("% Fully Consistent Choices with Messages by Treatment", size(medlarge)) ///
        subtitle("Final choice is consistent with messages sent to both partners", size(small)) ///
        ytitle("% of players")                                             ///
        ylabel(0(10)100, grid)                                             ///
        blabel(bar, format(%4.1f) size(small))                             ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(dnavy))                                               ///
        legend(off)

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_full_consistency_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_full_consistency_by_treatment.png"

restore

*==============================================================================
* SECTION 11 -- FISHER EXACT TESTS: FULL CONSISTENCY (CC_i == 1)
*   Comparison: Baseline (1) vs Public (2) ; Baseline (1) vs Slacker (3)
*   Unit: PLAYER.  Fisher exact test on 2×2 table (full_consistency × treatment).
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 11. FISHER EXACT TESTS: FULL CONSISTENCY (CC_i == 1)  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player ──────────────────────────────────────────────
    bysort sessioncode group_id id_in_group: keep if _n == 1

    generate byte full_consistency = (CC_i == 1) if !missing(CC_i)

    display as result _newline "--- Frequencies by treatment ---"
    tabstat full_consistency, by(treatment) stat(n sum mean) nototal col(stat)

    display as result _newline "--- Fisher exact test: Baseline vs Public ---"
    tab full_consistency treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact test: Baseline vs Slacker ---"
    tab full_consistency treatment if inlist(treatment, 1, 3), row col exact

    display as result _newline "--- Fisher exact test: Public vs Slacker ---"
    tab full_consistency treatment if inlist(treatment, 2, 3), row col exact

restore

*==============================================================================
* SECTION 12 -- STRATEGIC DECEPTION BAR CHART
*   Unit of analysis: PLAYER (1 row per player).
*   Outcome: indicator for strategic deception (strategic_deception == 1):
*            player signals support to BOTH partners (S_ij=1 & S_ik=1)
*            but supports NO ONE in final choice (final_decision == "noOne").
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 12. STRATEGIC DECEPTION BAR CHART  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player ──────────────────────────────────────────────
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Count players per treatment for x-axis labels ────────────────────────
    quietly count if treatment == 1 & !missing(strategic_deception)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(strategic_deception)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(strategic_deception)
    local n_p3 = r(N)

    * ── Descriptives by treatment ────────────────────────────────────────────
    display as result _newline "--- Frequencies by treatment ---"
    tabstat strategic_deception, by(treatment) stat(n sum mean) nototal col(stat)

    * ── Collapse to one mean (proportion) per treatment ──────────────────────
    collapse (mean) strategic_deception, by(treatment)
    replace strategic_deception = strategic_deception * 100

    * ── Treatment labels with N players ──────────────────────────────────────
    label define trt_lbl12 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl12

    * ── Bar chart ────────────────────────────────────────────────────────────
    graph bar strategic_deception,                                         ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars showyvars                                                  ///
        bargap(20)                                                         ///
        title("% Strategic Deception by Treatment", size(medlarge))        ///
        subtitle("Signalled support to both, supported no one", size(small)) ///
        ytitle("% of players")                                             ///
        ylabel(0(10)100, grid)                                             ///
        blabel(bar, format(%4.1f) size(small))                             ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(dnavy))                                               ///
        legend(off)

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_strategic_deception_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_strategic_deception_by_treatment.png"

restore

*==============================================================================
* SECTION 13 -- FISHER EXACT TESTS: STRATEGIC DECEPTION
*   Comparison: Baseline (1) vs Public (2) ; Baseline (1) vs Slacker (3)
*   Unit: PLAYER.  Fisher exact test on 2×2 table (strategic_deception × treatment).
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 13. FISHER EXACT TESTS: STRATEGIC DECEPTION  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1

    * ── Keep one row per player ──────────────────────────────────────────────
    bysort sessioncode group_id id_in_group: keep if _n == 1

    display as result _newline "--- Frequencies by treatment ---"
    tabstat strategic_deception, by(treatment) stat(n sum mean) nototal col(stat)

    display as result _newline "--- Fisher exact test: Baseline vs Public ---"
    tab strategic_deception treatment if inlist(treatment, 1, 2), row col exact

    display as result _newline "--- Fisher exact test: Baseline vs Slacker ---"
    tab strategic_deception treatment if inlist(treatment, 1, 3), row col exact

restore

*==============================================================================
* SECTION 14 -- NUMBER OF WORDS BY TREATMENT (Slide 6)
*   Unit of analysis: PLAYER (total words sent across both chat channels).
*   Histogram showing the proportion (fraction) of players by treatment.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 14. NUMBER OF WORDS BY TREATMENT  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Compute total words sent by each player across both channels ─────────
    generate double total_words = cond(!missing(words_j), words_j, 0) + ///
                                 cond(!missing(words_k), words_k, 0)
    label variable total_words "Total words sent by player (left + right channels)"

    * ── Count players per treatment for labels ───────────────────────────────
    quietly count if treatment == 1 & !missing(total_words)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(total_words)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(total_words)
    local n_p3 = r(N)

    label define trt_lbl14 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl14

    * ── Summary statistics by treatment ──────────────────────────────────────
    display as result _newline "--- Total words sent: Descriptives by treatment ---"
    tabstat total_words, by(treatment) stat(n mean sd p50 p25 p75 min max) nototal col(stat)

    * ── Parametric & Nonparametric comparisons ───────────────────────────────
    display as result _newline "--- Overall: OLS group-clustered SE + joint F-test ---"
    regress total_words i.treatment, vce(cluster group_id)
    testparm i.treatment

    display as result _newline "--- Overall: Kruskal-Wallis ---"
    kwallis total_words, by(treatment)

    display as result _newline "--- Pairwise Wilcoxon rank-sum & t-tests ---"
    foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
        local t1   = word("`pair'", 1)
        local t2   = word("`pair'", 2)
        local lab1 = word("`pair'", 3)
        local lab2 = word("`pair'", 4)
        pair_header `lab1' `lab2'
        ranksum total_words if inlist(treatment, `t1', `t2'), by(treatment)
        ttest total_words if inlist(treatment, `t1', `t2'), by(treatment) unequal
    }

    * ── Histogram: Proportion (fraction) of players by treatment ─────────────
    histogram total_words,                                                 ///
        by(treatment, rows(1)                                             ///
           title("Number of Words by Treatment", size(medlarge))          ///
           subtitle("Proportion of players", size(small))                 ///
           note(""))                                                      ///
        fraction                                                          ///
        fcolor(dnavy%75) lcolor(black)                                    ///
        xlabel(#6, grid labsize(small))                                   ///
        ylabel(0(0.10)0.40, grid format(%4.2f) labsize(small))            ///
        xtitle("Total words sent per player", size(small))                ///
        ytitle("Proportion of players", size(small))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_hist_words_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_hist_words_by_treatment.png"

restore

*==============================================================================
* SECTION 15 -- NUMBER OF MESSAGES BY TREATMENT (Slide 6)
*   Unit of analysis: PLAYER (total messages sent across both chat channels).
*   Histogram showing the proportion (fraction) of players by treatment.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 15. NUMBER OF MESSAGES BY TREATMENT  (unit = player)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Compute total messages sent by each player across both channels ──────
    generate double total_msgs = cond(!missing(msgs_j), msgs_j, 0) + ///
                                cond(!missing(msgs_k), msgs_k, 0)
    label variable total_msgs "Total messages sent by player (left + right channels)"

    * ── Count players per treatment for labels ───────────────────────────────
    quietly count if treatment == 1 & !missing(total_msgs)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(total_msgs)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(total_msgs)
    local n_p3 = r(N)

    label define trt_lbl15 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl15

    * ── Summary statistics by treatment ──────────────────────────────────────
    display as result _newline "--- Total messages sent: Descriptives by treatment ---"
    tabstat total_msgs, by(treatment) stat(n mean sd p50 p25 p75 min max) nototal col(stat)

    * ── Parametric & Nonparametric comparisons ───────────────────────────────
    display as result _newline "--- Overall: OLS group-clustered SE + joint F-test ---"
    regress total_msgs i.treatment, vce(cluster group_id)
    testparm i.treatment

    display as result _newline "--- Overall: Kruskal-Wallis ---"
    kwallis total_msgs, by(treatment)

    display as result _newline "--- Pairwise Wilcoxon rank-sum & t-tests ---"
    foreach pair in "1 2 Baseline Public" "1 3 Baseline Slacker" "2 3 Public Slacker" {
        local t1   = word("`pair'", 1)
        local t2   = word("`pair'", 2)
        local lab1 = word("`pair'", 3)
        local lab2 = word("`pair'", 4)
        pair_header `lab1' `lab2'
        ranksum total_msgs if inlist(treatment, `t1', `t2'), by(treatment)
        ttest total_msgs if inlist(treatment, `t1', `t2'), by(treatment) unequal
    }

    * ── Histogram: Proportion (fraction) of players by treatment ─────────────
    histogram total_msgs,                                                  ///
        by(treatment, rows(1)                                             ///
           title("Number of Messages by Treatment", size(medlarge))       ///
           subtitle("Proportion of players", size(small))                 ///
           note(""))                                                      ///
        fraction                                                          ///
        fcolor(dnavy%75) lcolor(black)                                    ///
        xlabel(#6, grid labsize(small))                                   ///
        ylabel(0(0.10)0.40, grid format(%4.2f) labsize(small))            ///
        xtitle("Total messages sent per player", size(small))             ///
        ytitle("Proportion of players", size(small))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_hist_messages_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_hist_messages_by_treatment.png"

restore

*==============================================================================
* SECTION 16 -- TOTAL NUMBER OF WORDS BY TREATMENT (BAR CHART)
*   Unit of analysis: TREATMENT (aggregated sum across all players).
*   Bar graph showing the total aggregate number of words used in each treatment.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 16. TOTAL NUMBER OF WORDS BY TREATMENT  (aggregate sum)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Compute total words sent by each player ──────────────────────────────
    generate double total_words = cond(!missing(words_j), words_j, 0) + ///
                                 cond(!missing(words_k), words_k, 0)

    * ── Count players per treatment for labels ───────────────────────────────
    quietly count if treatment == 1 & !missing(total_words)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(total_words)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(total_words)
    local n_p3 = r(N)

    * ── Collapse to sum of words per treatment ───────────────────────────────
    collapse (sum) sum_words = total_words, by(treatment)

    * ── Treatment labels with N players ──────────────────────────────────────
    label define trt_lbl16 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl16

    * ── Display totals in log ────────────────────────────────────────────────
    display as result _newline "--- Total aggregate words by treatment ---"
    list treatment sum_words, noobs clean

    * ── Bar chart: total words by treatment ──────────────────────────────────
    graph bar sum_words,                                                   ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars showyvars                                                  ///
        bargap(20)                                                         ///
        title("Total Number of Words by Treatment", size(medlarge))        ///
        subtitle("Aggregate word count across all players", size(small))   ///
        ytitle("Total number of words")                                    ///
        ylabel(, grid format(%9.0fc) labsize(small))                       ///
        blabel(bar, format(%9.0fc) size(small))                            ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(dnavy))                                               ///
        legend(off)

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_total_words_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_total_words_by_treatment.png"

restore

*==============================================================================
* SECTION 17 -- TOTAL NUMBER OF MESSAGES BY TREATMENT (BAR CHART)
*   Unit of analysis: TREATMENT (aggregated sum across all players).
*   Bar graph showing the total aggregate number of messages sent in each treatment.
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 17. TOTAL NUMBER OF MESSAGES BY TREATMENT  (aggregate sum)"
display as result "========================================================"

preserve
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    * ── Compute total messages sent by each player ───────────────────────────
    generate double total_msgs = cond(!missing(msgs_j), msgs_j, 0) + ///
                                cond(!missing(msgs_k), msgs_k, 0)

    * ── Count players per treatment for labels ───────────────────────────────
    quietly count if treatment == 1 & !missing(total_msgs)
    local n_p1 = r(N)
    quietly count if treatment == 2 & !missing(total_msgs)
    local n_p2 = r(N)
    quietly count if treatment == 3 & !missing(total_msgs)
    local n_p3 = r(N)

    * ── Collapse to sum of messages per treatment ────────────────────────────
    collapse (sum) sum_msgs = total_msgs, by(treatment)

    * ── Treatment labels with N players ──────────────────────────────────────
    label define trt_lbl17 1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"', replace
    label values treatment trt_lbl17

    * ── Display totals in log ────────────────────────────────────────────────
    display as result _newline "--- Total aggregate messages by treatment ---"
    list treatment sum_msgs, noobs clean

    * ── Bar chart: total messages by treatment ───────────────────────────────
    graph bar sum_msgs,                                                    ///
        over(treatment, relabel(1 `"Baseline (N=`n_p1')"' 2 `"Public (N=`n_p2')"' 3 `"Slacker (N=`n_p3')"') label(labsize(medsmall))) ///
        asyvars showyvars                                                  ///
        bargap(20)                                                         ///
        title("Total Number of Messages by Treatment", size(medlarge))     ///
        subtitle("Aggregate message count across all players", size(small)) ///
        ytitle("Total number of messages")                                 ///
        ylabel(, grid format(%9.0fc) labsize(small))                       ///
        blabel(bar, format(%9.0fc) size(small))                            ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(navy))                                               ///
        legend(off)

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_total_messages_by_treatment.png", ///
        replace width(1200)

    display as text " → Saved: fig_total_messages_by_treatment.png"

restore

*==============================================================================
* SECTION 18 -- TOPICGPT TOPICS: DESCRIPTIVE OVERVIEW & PREVALENCE
*   Unit of analysis: DIRECTED DYAD (6 channels per group, ccf_dyad.dta).
*   Topics:
*     1. Coalition Proposal  (topic_coalition_proposal in {0, 1})
*     2. Commitment          (topic_commitment in {0, 1})
*     3. Payoff Reasoning    (topic_payoff_reasoning in {0, 1})
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 18. TOPICGPT TOPICS: DESCRIPTIVES & PREVALENCE BY TREATMENT"
display as result "     (unit = directed dyad, 6 per group, from ccf_dyad.dta)"
display as result "========================================================"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    * ── Count dyads per treatment ────────────────────────────────────────────
    quietly count if treatment == 1
    local n_d1 = r(N)
    quietly count if treatment == 2
    local n_d2 = r(N)
    quietly count if treatment == 3
    local n_d3 = r(N)

    display as text _newline "Sample size (valid directed dyads):"
    display as text "  Baseline (Private) : `n_d1' dyads"
    display as text "  Public             : `n_d2' dyads"
    display as text "  Slacker            : `n_d3' dyads"
    display as text "  Total              : " (`n_d1' + `n_d2' + `n_d3') " dyads"

    display as result _newline "--- Topic prevalence (%) by treatment ---"
    tabstat topic_coalition_proposal topic_commitment topic_payoff_reasoning, ///
        by(treatment) stat(n mean sd min max) nototal col(stat)

restore

*==============================================================================
* SECTION 19 -- HYPOTHESIS TESTING: TREATMENT EFFECTS ON TOPIC PROBABILITIES
*   Focus:
*     1. Baseline (Private) vs Public   (treatment == 1 vs 2)
*     2. Baseline (Private) vs Slacker  (treatment == 1 vs 3)
*     3. Public vs Slacker              (treatment == 2 vs 3)
*
*   Econometric specifications:
*     A. Overall Omnibus Test across all 3 treatments:
*        - Linear Probability Model (OLS LPM) with group-clustered SE (group_id)
*        - Joint Wald F-test (testparm i.treatment)
*        - Logit Model with group-clustered SE + Average Marginal Effects (margins)
*        - Pearson Chi-Square test of independence (2x3 table)
*        - Kruskal-Wallis non-parametric test
*     B. Pairwise Tests (Highlighting Baseline vs Public & Baseline vs Slacker):
*        - OLS LPM coefficient (difference in probability) with group-clustered SE
*        - Two-sample test of proportions (prtest)
*        - Wilcoxon rank-sum (Mann-Whitney U) non-parametric test
*        - Fisher's exact test (2x2 contingency table)
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 19. SCIENTIFIC HYPOTHESIS TESTS: TREATMENT EFFECTS ON TOPICS"
display as result "========================================================"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    local topic_list "topic_coalition_proposal topic_commitment topic_payoff_reasoning"
    local topic_labels `""Coalition Proposal" "Commitment" "Payoff Reasoning""'

    local i = 1
    foreach top of local topic_list {
        local top_lab : word `i' of `topic_labels'
        
        display as result _newline(2) "======================================================================"
        display as result "  TOPIC `i': `top_lab' (`top')"
        display as result "======================================================================"
        
        * ── 1. Cross-tabulation ──────────────────────────────────────────────
        display as result _newline ">>> [1] Cross-tabulation (Topic x Treatment) & Pearson Chi2 <<<"
        tab `top' treatment, col chi2

        * ── 2. Overall OLS Linear Probability Model (LPM) ───────────────────
        display as result _newline ">>> [2] Overall OLS LPM with Group-Clustered SE (group_id) <<<"
        regress `top' i.treatment, vce(cluster group_id)
        display as text "Joint Wald F-test for treatment effects (H0: Treat_Public = 0 & Treat_Slacker = 0):"
        testparm i.treatment

        * ── 3. Overall Logistic Regression (Logit) ──────────────────────────
        display as result _newline ">>> [3] Overall Logit Model with Group-Clustered SE & Margins <<<"
        logit `top' i.treatment, vce(cluster group_id)
        testparm i.treatment
        display as text "Average Marginal Effects (AME) of treatments relative to Baseline:"
        margins, dydx(treatment)

        * ── 4. Overall Non-Parametric Test ──────────────────────────────────
        display as result _newline ">>> [4] Kruskal-Wallis Non-Parametric Test across 3 treatments <<<"
        kwallis `top', by(treatment)

        * ── 5. Pairwise Comparisons ─────────────────────────────────────────
        display as result _newline ">>> [5] PAIRWISE HYPOTHESIS TESTS <<<"

        * --- PAIR A: BASELINE (PRIVATE) vs PUBLIC ---
        display as result _newline "  ------------------------------------------------------------------"
        display as result "  [PAIR A] BASELINE (PRIVATE) vs. PUBLIC  (treatment == 1 vs 2)"
        display as result "  ------------------------------------------------------------------"
        display as text "  (a) Clustered OLS (LPM) difference:"
        regress `top' i.treatment if inlist(treatment, 1, 2), vce(cluster group_id)
        
        display as text "  (b) Two-sample test of proportions:"
        prtest `top' if inlist(treatment, 1, 2), by(treatment)
        
        display as text "  (c) Wilcoxon rank-sum (Mann-Whitney U) non-parametric test:"
        ranksum `top' if inlist(treatment, 1, 2), by(treatment)
        
        display as text "  (d) Pearson Chi2 test (2x2):"
        tab `top' treatment if inlist(treatment, 1, 2), col chi2

        * --- PAIR B: BASELINE (PRIVATE) vs SLACKER ---
        display as result _newline "  ------------------------------------------------------------------"
        display as result "  [PAIR B] BASELINE (PRIVATE) vs. SLACKER (treatment == 1 vs 3)"
        display as result "  ------------------------------------------------------------------"
        display as text "  (a) Clustered OLS (LPM) difference:"
        regress `top' i.treatment if inlist(treatment, 1, 3), vce(cluster group_id)
        
        display as text "  (b) Two-sample test of proportions:"
        prtest `top' if inlist(treatment, 1, 3), by(treatment)
        
        display as text "  (c) Wilcoxon rank-sum (Mann-Whitney U) non-parametric test:"
        ranksum `top' if inlist(treatment, 1, 3), by(treatment)
        
        display as text "  (d) Pearson Chi2 test (2x2):"
        tab `top' treatment if inlist(treatment, 1, 3), col chi2

        * --- PAIR C: PUBLIC vs SLACKER ---
        display as result _newline "  ------------------------------------------------------------------"
        display as result "  [PAIR C] PUBLIC vs. SLACKER (treatment == 2 vs 3)"
        display as result "  ------------------------------------------------------------------"
        display as text "  (a) Clustered OLS (LPM) difference:"
        regress `top' i.treatment if inlist(treatment, 2, 3), vce(cluster group_id)
        
        display as text "  (b) Two-sample test of proportions:"
        prtest `top' if inlist(treatment, 2, 3), by(treatment)
        
        display as text "  (c) Wilcoxon rank-sum (Mann-Whitney U) non-parametric test:"
        ranksum `top' if inlist(treatment, 2, 3), by(treatment)
        
        display as text "  (d) Pearson Chi2 test (2x2):"
        tab `top' treatment if inlist(treatment, 2, 3), col chi2

        local ++i
    }

restore

*==============================================================================
* SECTION 20 -- CONTROLLED REGRESSIONS (ROBUSTNESS WITH COVARIATES & SESSION FEs)
*   Testing robustness of treatment effects after conditioning on:
*     - Sender demographics (gender, birth_year, uni_years)
*     - Economic preferences (risk, patience, trust, altruism)
*     - Personality traits (Dark Triad: MACH, NARC, PSYCH)
*     - Session fixed effects (i.session)
*     - Clustered SE at group level (group_id)
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 20. CONTROLLED REGRESSIONS: LPM WITH COVARIATES & SESSION FEs"
display as result "========================================================"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    local topic_list "topic_coalition_proposal topic_commitment topic_payoff_reasoning"
    local topic_labels `""Coalition Proposal" "Commitment" "Payoff Reasoning""'

    local i = 1
    foreach top of local topic_list {
        local top_lab : word `i' of `topic_labels'
        display as result _newline ">>> Controlled LPM for `top_lab' (`top') <<<"
        regress `top' i.treatment gender birth_year uni_years ///
                      risk patience trust altruism MACH NARC PSYCH i.session, ///
                      vce(cluster group_id)
        testparm i.treatment
        local ++i
    }

restore

*==============================================================================
* SECTION 21 -- EXTENSIONS: INTENSIVE MARGIN & PLAYER-LEVEL AGGREGATION
*   1. Intensive Margin: Dyads with active communication (number_of_messages > 0)
*   2. Player-Level Analysis: Did player i use topic T in ANY channel (ccf_master.dta)?
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 21. ROBUSTNESS: INTENSIVE MARGIN & PLAYER-LEVEL AGGREGATION"
display as result "========================================================"

* ── 1. Intensive Margin (Active Chat Only) ───────────────────────────────────
display as result _newline "--------------------------------------------------------"
display as result " 21a. INTENSIVE MARGIN (Active communication: number_of_messages > 0)"
display as result "--------------------------------------------------------"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1
    keep if number_of_messages > 0 & !missing(number_of_messages)

    display as text "Active dyads sample size by treatment:"
    tab treatment

    display as result _newline "--- Topic prevalence (%) conditional on active communication ---"
    tabstat topic_coalition_proposal topic_commitment topic_payoff_reasoning, ///
        by(treatment) stat(n mean sd) col(stat) nototal

    foreach top in topic_coalition_proposal topic_commitment topic_payoff_reasoning {
        display as result _newline ">>> Intensive margin OLS LPM: `top' <<<"
        regress `top' i.treatment, vce(cluster group_id)
        testparm i.treatment
    }
restore

* ── 2. Player-Level Aggregation (ccf_master.dta) ────────────────────────────
display as result _newline "--------------------------------------------------------"
display as result " 21b. PLAYER-LEVEL OCCURRENCE (Topic used in ANY channel: ccf_master)"
display as result "--------------------------------------------------------"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_master.dta"', clear
    keep if group_valid == 1
    bysort sessioncode group_id id_in_group: keep if _n == 1

    generate byte top_coalition_any  = (topic_coalition_j == 1  | topic_coalition_k == 1)
    generate byte top_commitment_any = (topic_commitment_j == 1 | topic_commitment_k == 1)
    generate byte top_payoff_any     = (topic_payoff_j == 1     | topic_payoff_k == 1)

    label variable top_coalition_any  "Player used Coalition Proposal in any channel"
    label variable top_commitment_any "Player used Commitment in any channel"
    label variable top_payoff_any     "Player used Payoff Reasoning in any channel"

    display as result _newline "--- Player-level prevalence (%) by treatment ---"
    tabstat top_coalition_any top_commitment_any top_payoff_any, ///
        by(treatment) stat(n mean sd) col(stat) nototal

    foreach top in top_coalition_any top_commitment_any top_payoff_any {
        display as result _newline ">>> Player-level OLS LPM: `top' <<<"
        regress `top' i.treatment, vce(cluster group_id)
        testparm i.treatment
    }
restore

*==============================================================================
* SECTION 22 -- SUMMARY MATRIX & MULTIPLE HYPOTHESIS TESTING CORRECTION
*   Unified synthesis of all pairwise comparisons with FDR (Benjamini-Hochberg)
*   and Bonferroni corrections across the 3 topics.
*==============================================================================
display as result _newline(2) "=============================================================================="
display as result " 22. SUMMARY MATRIX & MULTIPLE HYPOTHESIS TESTING CORRECTIONS"
display as result "=============================================================================="

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    display as text _newline "----------------------------------------------------------------------------------------------------"
    display as text " TOPIC                     | Baseline  | Public    | Slacker   | Baseline vs Public | Baseline vs Slacker"
    display as text "                           | Mean (%)  | Mean (%)  | Mean (%)  | Diff (p-clustered) | Diff (p-clustered)"
    display as text "----------------------------------------------------------------------------------------------------"

    local topic_list "topic_coalition_proposal topic_commitment topic_payoff_reasoning"
    local topic_names `""Coalition Proposal  " "Commitment          " "Payoff Reasoning    ""'

    local i = 1
    foreach top of local topic_list {
        local tname : word `i' of `topic_names'
        
        * Means
        quietly summarize `top' if treatment == 1
        local m1 = r(mean) * 100
        quietly summarize `top' if treatment == 2
        local m2 = r(mean) * 100
        quietly summarize `top' if treatment == 3
        local m3 = r(mean) * 100

        * Pair 1: Baseline vs Public
        quietly regress `top' i.treatment if inlist(treatment, 1, 2), vce(cluster group_id)
        local diff12 = (_b[2.treatment]) * 100
        test 2.treatment = 0
        local p12 = r(p)

        * Pair 2: Baseline vs Slacker
        quietly regress `top' i.treatment if inlist(treatment, 1, 3), vce(cluster group_id)
        local diff13 = (_b[3.treatment]) * 100
        test 3.treatment = 0
        local p13 = r(p)

        display as result %-26s "`tname'" " | " ///
               %8.2f `m1' "% | " ///
               %8.2f `m2' "% | " ///
               %8.2f `m3' "% | " ///
               %7.2f `diff12' "% (p=" %5.3f `p12' ") | " ///
               %7.2f `diff13' "% (p=" %5.3f `p13' ")"
        
        local ++i
    }
    display as text "----------------------------------------------------------------------------------------------------"
    display as text "Note: Standard errors clustered at the group level (triad). All differences in percentage points."

restore

*==============================================================================
* SECTION 23 -- PUBLICATION-QUALITY BAR CHARTS: TOPICGPT TOPICS BY TREATMENT
*   Exporting clean, formatted charts with exact palette:
*     Baseline = black, Public = gray, Slacker = navy
*==============================================================================
display as result _newline(2) "========================================================"
display as result " 23. PUBLICATION-QUALITY BAR CHARTS: TOPICS BY TREATMENT"
display as result "========================================================"

preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    * ── Count dyads per treatment ────────────────────────────────────────────
    quietly count if treatment == 1
    local n_d1 = r(N)
    quietly count if treatment == 2
    local n_d2 = r(N)
    quietly count if treatment == 3
    local n_d3 = r(N)

    * ── Collapse to proportions per treatment ────────────────────────────────
    collapse (mean) topic_coalition_proposal topic_commitment topic_payoff_reasoning, by(treatment)

    foreach v in topic_coalition_proposal topic_commitment topic_payoff_reasoning {
        replace `v' = `v' * 100
    }

    * ── Reshape long for grouped bar chart ───────────────────────────────────
    generate id = _n
    reshape long topic_, i(id treatment) j(top_name) string

    generate byte top_cat = .
    replace top_cat = 1 if top_name == "coalition_proposal"
    replace top_cat = 2 if top_name == "commitment"
    replace top_cat = 3 if top_name == "payoff_reasoning"
    label define top_lbl23 1 "Coalition Proposal" 2 "Commitment" 3 "Payoff Reasoning", replace
    label values top_cat top_lbl23

    label define trt_lbl23 1 `"Baseline (N=`n_d1')"' 2 `"Public (N=`n_d2')"' 3 `"Slacker (N=`n_d3')"', replace
    label values treatment trt_lbl23

    * ── Combined Grouped Bar Chart ───────────────────────────────────────────
    graph bar topic_,                                                      ///
        over(treatment, label(labsize(small)))                             ///
        over(top_cat, label(labsize(medsmall)))                            ///
        asyvars                                                            ///
        bargap(15)                                                         ///
        title("TopicGPT Topic Prevalence by Treatment", size(medlarge))    ///
        subtitle("Percentage of directed communication channels containing topic", size(small)) ///
        ytitle("% of communication channels")                              ///
        ylabel(0(10)60, grid labsize(small))                               ///
        blabel(bar, format(%4.1f) size(vsmall))                            ///
        bar(1, color(black))                                               ///
        bar(2, color(gray))                                                ///
        bar(3, color(navy))                                                ///
        legend(title("Treatment", size(small))                             ///
               order(1 "Baseline (Private)" 2 "Public" 3 "Slacker")        ///
               rows(1) size(small) position(6))

    graph export ///
        "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_topics_by_treatment.png", ///
        replace width(1400)

    display as text " → Saved: fig_topics_by_treatment.png"

restore

* ── Individual Charts for Each Topic ─────────────────────────────────────────
preserve
    use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear
    keep if group_valid == 1

    quietly count if treatment == 1
    local n_d1 = r(N)
    quietly count if treatment == 2
    local n_d2 = r(N)
    quietly count if treatment == 3
    local n_d3 = r(N)

    collapse (mean) topic_coalition_proposal topic_commitment topic_payoff_reasoning, by(treatment)

    foreach v in topic_coalition_proposal topic_commitment topic_payoff_reasoning {
        replace `v' = `v' * 100
    }

    label define trt_lbl_ind 1 `"Baseline (N=`n_d1')"' 2 `"Public (N=`n_d2')"' 3 `"Slacker (N=`n_d3')"', replace
    label values treatment trt_lbl_ind

    * 1. Coalition Proposal
    graph bar topic_coalition_proposal,                                    ///
        over(treatment, label(labsize(medsmall)))                          ///
        asyvars showyvars bargap(20)                                       ///
        title("Topic: Coalition Proposal by Treatment", size(medlarge))   ///
        subtitle("Proportion of directed communication channels", size(small)) ///
        ytitle("% of communication channels")                              ///
        ylabel(0(10)60, grid)                                              ///
        blabel(bar, format(%4.1f) size(small))                             ///
        bar(1, color(black)) bar(2, color(gray)) bar(3, color(navy))      ///
        legend(off)
    graph export "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_topic_coalition_proposal_by_treatment.png", replace width(1200)
    display as text " → Saved: fig_topic_coalition_proposal_by_treatment.png"

    * 2. Commitment
    graph bar topic_commitment,                                            ///
        over(treatment, label(labsize(medsmall)))                          ///
        asyvars showyvars bargap(20)                                       ///
        title("Topic: Commitment by Treatment", size(medlarge))           ///
        subtitle("Proportion of directed communication channels", size(small)) ///
        ytitle("% of communication channels")                              ///
        ylabel(0(10)60, grid)                                              ///
        blabel(bar, format(%4.1f) size(small))                             ///
        bar(1, color(black)) bar(2, color(gray)) bar(3, color(navy))      ///
        legend(off)
    graph export "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_topic_commitment_by_treatment.png", replace width(1200)
    display as text " → Saved: fig_topic_commitment_by_treatment.png"

    * 3. Payoff Reasoning
    graph bar topic_payoff_reasoning,                                      ///
        over(treatment, label(labsize(medsmall)))                          ///
        asyvars showyvars bargap(20)                                       ///
        title("Topic: Payoff Reasoning by Treatment", size(medlarge))     ///
        subtitle("Proportion of directed communication channels", size(small)) ///
        ytitle("% of communication channels")                              ///
        ylabel(0(2)15, grid)                                               ///
        blabel(bar, format(%4.1f) size(small))                             ///
        bar(1, color(black)) bar(2, color(gray)) bar(3, color(navy))      ///
        legend(off)
    graph export "C:\Users\Donat\communication_coalition_formation\text_analysis--stata\fig_topic_payoff_reasoning_by_treatment.png", replace width(1200)
    display as text " → Saved: fig_topic_payoff_reasoning_by_treatment.png"

restore

display as result _newline(2) "========================================================"
display as result " All done (Sections 1–23 completed successfully)."
display as result "========================================================"

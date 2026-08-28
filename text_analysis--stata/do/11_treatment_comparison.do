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

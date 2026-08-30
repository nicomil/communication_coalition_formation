*==============================================================================
* FILE: 12_persuasion_regressions.do
* PURPOSE: Econometric Regressions on Persuasion: Was Player A Persuasive toward B?
*
* DESIGN & IDENTIFICATION:
*   1. Sample selection: Restricted to observations where A signaled intent to
*      support B (S_ij == 1, i.e. signal_to_partner == "split_you").
*   2. Binary Dependent Variable: A_ji = 1 if partner B actually chose A in final decision.
*   3. Explanatory Variables: TopicGPT categories, word count, sentiment,
*      emotional tone, and linguistic dimensions of the messages sent from A to B.
*   4. Controls: Treatment dummies, sender A characteristics, and receiver B characteristics
*      (demographics, economic preferences, and Dark Triad: MACH, NARC, PSYCH).
*   5. Inference: Clustered standard errors at the group level (group_id).
*
* UNIT OF ANALYSIS: Directed Dyad (i -> j), from ccf_dyad.dta.
*==============================================================================

clear all
set more off
capture log close

* -----------------------------------------------------------------------------
* 1. LOAD DYAD DATASET & MERGE RECEIVER (B) CHARACTERISTICS
* -----------------------------------------------------------------------------
use `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\ccf_dyad.dta"', clear

* Keep only valid experimental groups
keep if group_valid == 1

* ── Extract receiver (B) characteristics and merge onto dyad row ─────────────
preserve
    keep sessioncode group_id focal_player_id gender birth_year uni_years ///
         risk patience trust altruism reciprocity_positive reciprocity_negative level_k ///
         MACH NARC PSYCH
    bysort sessioncode group_id focal_player_id: keep if _n == 1
    rename focal_player_id      partner_id
    rename gender               gender_B
    rename birth_year           birth_year_B
    rename uni_years            uni_years_B
    rename risk                 risk_B
    rename patience             patience_B
    rename trust                trust_B
    rename altruism             altruism_B
    rename reciprocity_positive recip_pos_B
    rename reciprocity_negative recip_neg_B
    rename level_k              level_k_B
    rename MACH                 MACH_B
    rename NARC                 NARC_B
    rename PSYCH                PSYCH_B
    isid sessioncode group_id partner_id
    tempfile receiver_traits
    save `receiver_traits'
restore

merge m:1 sessioncode group_id partner_id using `receiver_traits', keep(match master) nogen

* Rename sender (A) characteristics for symmetry and readability
rename gender               gender_A
rename birth_year           birth_year_A
rename uni_years            uni_years_A
rename risk                 risk_A
rename patience             patience_A
rename trust                trust_A
rename altruism             altruism_A
rename reciprocity_positive recip_pos_A
rename reciprocity_negative recip_neg_A
rename level_k              level_k_A
rename MACH                 MACH_A
rename NARC                 NARC_A
rename PSYCH                PSYCH_A

* -----------------------------------------------------------------------------
* 2. SAMPLE RESTRICTION, VARIABLE TRANSFORMATIONS & CONTROL MACROS
* -----------------------------------------------------------------------------

* Filter to cases where A promised support to B (S_ij == 1)
keep if S_ij == 1
assert inlist(persuasion_ij, 0, 1)

* Define complete list of individual characteristics for Sender A and Receiver B
global SENDER_CONTROLS   gender_A birth_year_A uni_years_A risk_A patience_A recip_pos_A recip_neg_A altruism_A trust_A level_k_A MACH_A NARC_A PSYCH_A
global RECEIVER_CONTROLS gender_B birth_year_B uni_years_B risk_B patience_B recip_pos_B recip_neg_B altruism_B trust_B level_k_B MACH_B NARC_B PSYCH_B

* Explicit binary dummies for treatments (Baseline = omitted reference)
generate byte treat_public  = (treatment == 2) if !missing(treatment)
generate byte treat_slacker = (treatment == 3) if !missing(treatment)
label variable treat_public  "Public Treatment"
label variable treat_slacker "Slacker Treatment"
global TREAT_CONTROLS treat_public treat_slacker

* Compute log of words (+1 to handle zeros)
generate double ln_words = ln(number_of_words + 1)
label variable ln_words "Log(Words sent A->B + 1)"

* Standardize continuous text variables for comparable effect sizes (beta z-scores)
quietly summarize sentiment_continuous_neg1_pos1
generate double z_sentiment = (sentiment_continuous_neg1_pos1 - r(mean)) / r(sd)
label variable z_sentiment "Sentiment (std)"

quietly summarize emotional_tone_continuous_0_100
generate double z_emot_tone = (emotional_tone_continuous_0_100 - r(mean)) / r(sd)
label variable z_emot_tone "Emotional Tone (std)"

quietly summarize authenticity_continuous_0_100
generate double z_authentic = (authenticity_continuous_0_100 - r(mean)) / r(sd)
label variable z_authentic "Authenticity (std)"

quietly summarize analytical_thinking_continuous_0
generate double z_analytic = (analytical_thinking_continuous_0 - r(mean)) / r(sd)
label variable z_analytic "Analytical Thinking (std)"

quietly summarize clout_continuous_0_100
generate double z_clout = (clout_continuous_0_100 - r(mean)) / r(sd)
label variable z_clout "Clout (std)"

* -----------------------------------------------------------------------------
* 3. DESCRIPTIVE STATISTICS OF ESTIMATION SAMPLE
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " ESTIMATION SAMPLE: persuasion_ij | S_ij == 1 (N pairs where A promised support)"
display as result "========================================================"

tabstat persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
        number_of_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout, ///
        stat(n mean sd min max) col(stat)

display as result _newline "--- Persuasion rate by treatment ---"
tab treatment persuasion_ij, row chi2




* -----------------------------------------------------------------------------
* 4. LINEAR PROBABILITY MODELS (OLS with group-clustered SE)
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " 4. LINEAR PROBABILITY MODELS (OLS LPM, vce(cluster group_id))"
display as result "========================================================"

* ── Model 1: TopicGPT primary indicators ────────────────────────────────────
display as result _newline ">>> Model 1: TopicGPT Topics only"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning i.session, ///
    vce(cluster group_id)
estimates store m1_lpm

* ── Model 2: Topics + Volume (Words & Messages) ──────────────────────────────
display as result _newline ">>> Model 2: Topics + Communication Volume"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
             ln_words number_of_messages i.session, ///
             vce(cluster group_id)
estimates store m2_lpm

* ── Model 3: Topics + Volume + Sentiment & Linguistic Tone ───────────────────
display as result _newline ">>> Model 3: Topics + Volume + Text Analysis (LIWC / Tone)"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
             ln_words number_of_messages ///
             z_sentiment z_emot_tone z_authentic z_analytic z_clout i.session, ///
             vce(cluster group_id)
estimates store m3_lpm

* ── Model 4: Model 3 + Treatment Dummies ────────────────────────────────────
display as result _newline ">>> Model 4: Model 3 + Treatment Controls"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
             ln_words number_of_messages ///
             z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
             $TREAT_CONTROLS i.session, ///
             vce(cluster group_id)
estimates store m4_lpm

* ── Model 5: Model 4 + Sender A Characteristics (Demographics, Preferences & Dark Triad) ─
display as result _newline ">>> Model 5: Model 4 + Sender A Demographics, Preferences & Dark Triad"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
             ln_words number_of_messages ///
             z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
             $TREAT_CONTROLS ///
             $SENDER_CONTROLS i.session, ///
             vce(cluster group_id)
estimates store m5_lpm

* ── Model 6: Full Model (Sender A + Receiver B Characteristics) ─────────────
display as result _newline ">>> Model 6: Full Model (Text + Treatment + Sender A + Receiver B traits)"
regress persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
             ln_words number_of_messages ///
             z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
             $TREAT_CONTROLS ///
             $SENDER_CONTROLS ///
             $RECEIVER_CONTROLS i.session, ///
             vce(cluster group_id)
estimates store m6_lpm

* -----------------------------------------------------------------------------
* 5. LOGISTIC REGRESSIONS (vce(cluster group_id)) & AVERAGE MARGINAL EFFECTS
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " 5. LOGISTIC REGRESSIONS (Logit, vce(cluster group_id))"
display as result "========================================================"

* ── Logit Model 1: TopicGPT Topics only ─────────────────────────────────────
display as result _newline ">>> Logit Model 1: TopicGPT Topics only"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning i.session, ///
    vce(cluster group_id)
local m1_nclust = e(N_clust)
estimates store m1_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m1_nclust'
estimates store m1_logit_ame

* ── Logit Model 2: Topics + Volume (Words & Messages) ───────────────────────
display as result _newline ">>> Logit Model 2: Topics + Communication Volume"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages i.session, ///
         vce(cluster group_id)
local m2_nclust = e(N_clust)
estimates store m2_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m2_nclust'
estimates store m2_logit_ame

* ── Logit Model 3: Topics + Volume + Sentiment & Linguistic Tone ────────────
display as result _newline ">>> Logit Model 3: Topics + Volume + Text Analysis (LIWC / Tone)"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages ///
         z_sentiment z_emot_tone z_authentic z_analytic z_clout i.session, ///
         vce(cluster group_id)
local m3_nclust = e(N_clust)
estimates store m3_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m3_nclust'
estimates store m3_logit_ame

* ── Logit Model 4: Model 3 + Treatment Controls ─────────────────────────────
display as result _newline ">>> Logit Model 4: Model 3 + Treatment Controls"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages ///
         z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         $TREAT_CONTROLS i.session, ///
         vce(cluster group_id)
local m4_nclust = e(N_clust)
estimates store m4_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m4_nclust'
estimates store m4_logit_ame

* ── Logit Model 5: Model 4 + Sender A Demographics, Preferences & Dark Triad ─
display as result _newline ">>> Logit Model 5: Model 4 + Sender A Demographics, Preferences & Dark Triad"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages ///
         z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         $TREAT_CONTROLS ///
         $SENDER_CONTROLS i.session, ///
         vce(cluster group_id)
local m5_nclust = e(N_clust)
estimates store m5_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m5_nclust'
estimates store m5_logit_ame

* ── Logit Model 6: Full Model (Sender A + Receiver B Characteristics) ───────
display as result _newline ">>> Logit Model 6: Full Model (Text + Treatment + Sender A + Receiver B traits)"
logit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages ///
         z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         $TREAT_CONTROLS ///
         $SENDER_CONTROLS ///
         $RECEIVER_CONTROLS i.session, ///
         vce(cluster group_id)
local m6_nclust = e(N_clust)
estimates store m6_logit
quietly margins, dydx(*) post
ereturn scalar N_clust = `m6_nclust'
estimates store m6_logit_ame

* -----------------------------------------------------------------------------
* 6. PROBIT REGRESSIONS (Full Specification)
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " 6. PROBIT REGRESSIONS (vce(cluster group_id)) & MARGINAL EFFECTS"
display as result "========================================================"

probit persuasion_ij topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
            ln_words number_of_messages ///
            z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
            $TREAT_CONTROLS ///
            $SENDER_CONTROLS ///
            $RECEIVER_CONTROLS i.session, ///
            vce(cluster group_id)
estimates store m6_probit
quietly margins, dydx(*) post
estimates store m6_probit_ame

* -----------------------------------------------------------------------------
* 7. DISPLAY SUMMARY COMPARISON TABLES
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " 7. SUMMARY TABLE: LOGISTIC REGRESSIONS (Models 1 to 6)"
display as result "========================================================"

estimates table m1_logit m2_logit m3_logit m4_logit m5_logit m6_logit, ///
    b(%9.4f) se(%9.4f) p(%9.4f) stats(N r2_p chi2)

display as result _newline(2) "--- AVERAGE MARGINAL EFFECTS (AME): Logit Models 1 to 6 ---"
estimates table m1_logit_ame m2_logit_ame m3_logit_ame m4_logit_ame m5_logit_ame m6_logit_ame, ///
    b(%9.4f) se(%9.4f) p(%9.4f)

* -----------------------------------------------------------------------------
* 8. EXPORT LATEX / BEAMER TABLES (LOGISTIC MODELS)
* -----------------------------------------------------------------------------
display as result _newline(2) "========================================================"
display as result " 8. EXPORTING LATEX & BEAMER TABLES (LOGIT MODELS)"
display as result "========================================================"

* Auto-install estout package if not present
capture which esttab
if _rc != 0 {
    display as text "Installing estout from SSC..."
    ssc install estout, replace
}

* Label variables clearly for LaTeX
label variable topic_coalition_proposal "Coalition Proposal"
label variable topic_commitment         "Commitment"
label variable topic_payoff_reasoning   "Payoff Reasoning"
label variable ln_words                 "$\ln(\text{Words} + 1)$"
label variable number_of_messages      "No. of Messages"
label variable z_sentiment              "Sentiment (std)"
label variable z_emot_tone              "Emotional Tone (std)"
label variable z_authentic              "Authenticity (std)"
label variable z_analytic               "Analytical Thinking (std)"
label variable z_clout                  "Clout (std)"
label variable treat_public             "Public Treatment"
label variable treat_slacker            "Slacker Treatment"

* ── Table 1: Full 6-Model Logit Table (Coefficients & Pseudo R2) ────────────
esttab m1_logit m2_logit m3_logit m4_logit m5_logit m6_logit using ///
    `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_6models.tex"', ///
    replace booktabs label b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    nogaps compress fragment nomtitles nodepvars ///
    prehead("\renewcommand{\arraystretch}{0.85}" "\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}" "\begin{tabular}{lcccccc}" "\toprule") ///
    posthead("\midrule") ///
    prefoot("\midrule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    keep(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         treat_public treat_slacker) ///
    order(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
          ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
          treat_public treat_slacker) ///
    stats(N r2_p ll N_clust, fmt(%9.0fc %9.3f %9.3f %9.0fc) ///
          labels("Observations" "Pseudo \$R^2\$" "Log pseudolikelihood" "Clusters (Groups)")) ///
    indicate("Session Fixed Effects = 2.session" "Sender Traits = MACH_A" "Receiver Traits = MACH_B")

copy `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_6models.tex"' ///
     `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\tab_persuasion_logit_6models.tex"', replace
display as text " → Saved: tab_persuasion_logit_6models.tex (also copied to MPPT_Slide/)"

* ── Table 2: Compact 3-Model Beamer Slide Table (Logit Models 1, 4, 6) ───────
esttab m1_logit m4_logit m6_logit using ///
    `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_beamer_3models.tex"', ///
    replace booktabs label b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    nogaps compress fragment nomtitles nodepvars ///
    prehead("\renewcommand{\arraystretch}{0.85}" "\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}" "\begin{tabular}{lccc}" "\toprule") ///
    posthead("\midrule") ///
    prefoot("\midrule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    keep(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         treat_public treat_slacker) ///
    order(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
          ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
          treat_public treat_slacker) ///
    stats(N r2_p ll N_clust, fmt(%9.0fc %9.3f %9.3f %9.0fc) ///
          labels("Observations" "Pseudo \$R^2\$" "Log pseudolikelihood" "Clusters")) ///
    indicate("Session Fixed Effects = 2.session" "Sender Traits = MACH_A" "Receiver Traits = MACH_B")

copy `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_beamer_3models.tex"' ///
     `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\tab_persuasion_logit_beamer_3models.tex"', replace
display as text " → Saved: tab_persuasion_logit_beamer_3models.tex (also copied to MPPT_Slide/)"

* ── Table 3: Full 6-Model AME Table (Average Marginal Effects) ────────────
esttab m1_logit_ame m2_logit_ame m3_logit_ame m4_logit_ame m5_logit_ame m6_logit_ame using ///
    `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_ame_6models.tex"', ///
    replace booktabs label b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    nogaps compress fragment nomtitles nodepvars ///
    prehead("\renewcommand{\arraystretch}{0.85}" "\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}" "\begin{tabular}{lcccccc}" "\toprule") ///
    posthead("\midrule") ///
    prefoot("\midrule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    keep(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         treat_public treat_slacker) ///
    order(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
          ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
          treat_public treat_slacker) ///
    stats(N N_clust, fmt(%9.0fc %9.0fc) labels("Observations" "Clusters (Groups)")) ///
    indicate("Session Fixed Effects = 2.session" "Sender Traits = MACH_A" "Receiver Traits = MACH_B")

copy `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_ame_6models.tex"' ///
     `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\tab_persuasion_logit_ame_6models.tex"', replace
display as text " → Saved: tab_persuasion_logit_ame_6models.tex (also copied to MPPT_Slide/)"

* ── Table 4: Compact 3-Model Beamer Slide Table (Average Marginal Effects) ──
esttab m1_logit_ame m4_logit_ame m6_logit_ame using ///
    `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_ame_beamer_3models.tex"', ///
    replace booktabs label b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    nogaps compress fragment nomtitles nodepvars ///
    prehead("\renewcommand{\arraystretch}{0.85}" "\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}" "\begin{tabular}{lccc}" "\toprule") ///
    posthead("\midrule") ///
    prefoot("\midrule") ///
    postfoot("\bottomrule" "\end{tabular}") ///
    keep(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
         ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
         treat_public treat_slacker) ///
    order(topic_coalition_proposal topic_commitment topic_payoff_reasoning ///
          ln_words number_of_messages z_sentiment z_emot_tone z_authentic z_analytic z_clout ///
          treat_public treat_slacker) ///
    stats(N N_clust, fmt(%9.0fc %9.0fc) labels("Observations" "Clusters")) ///
    indicate("Session Fixed Effects = 2.session" "Sender Traits = MACH_A" "Receiver Traits = MACH_B")

copy `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\tab_persuasion_logit_ame_beamer_3models.tex"' ///
     `"C:\Users\Donat\communication_coalition_formation\text_analysis--stata\MPPT_Slide\tab_persuasion_logit_ame_beamer_3models.tex"', replace
display as text " → Saved: tab_persuasion_logit_ame_beamer_3models.tex (also copied to MPPT_Slide/)"

display as result _newline(2) "========================================================"
display as result " Logistic regressions and LaTeX export completed successfully."
display as result "========================================================"

display as result _newline(2) "========================================================"
display as result " Logistic regressions and LaTeX export completed successfully."
display as result "========================================================"



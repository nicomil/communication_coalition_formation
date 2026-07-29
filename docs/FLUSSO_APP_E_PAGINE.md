# Flusso app e pagine

## Sequenza

`bargaining_tdl_intro` → `bargaining_tdl_main` → `bargaining_tdl_survey`

## 1. Intro e assegnazione

- `Welcome`: raccoglie Prolific PID e assegna un trattamento.
- `InstructionsPart1`: testo specifico private/public. Per
  `private_no_dwl` usa temporaneamente la copia delle istruzioni Private TDL,
  come richiesto dallo sperimentatore.
- `ControlQuestionsAttempt1...5`: tre esempi; Example 2 vale 12/0/0 solo nel
  braccio No-DWL e 0/0/0 nei bracci TDL.
- `Goodbye`: solo CQ failure/timeout; lo slot RCT viene restituito.

Chi supera le CQ conferma lo slot ed entra nella waiting room del proprio
trattamento.

## 2. Gioco principale

- `GroupingAfterControlQuestions`: triadi omogenee by-arrival.
- `Chat`
- `Signals`: un messaggio finale per partner e, subito sotto, rating
  obbligatorio 1–5 (`Not very convincing` → `Highly convincing`).
- `ExperimentTerminated`: solo esclusi.
- `DataMappingWaitPage`
- `Decision`: `Support Left`, `Support Right`, `Support no one`.
- `ResultsWaitPage`: calcola payoff secondo il trattamento.
- `Results`: solo attivi.
- `InactivityGoodbyeMain`: inattivi/dropout.

I rating non vengono mostrati agli altri partecipanti e restano nulli sui
timeout.

## 3. Survey

- `SurveyIntro`
- `SurveyQuestions`: age, gender, field of studies e altre demografiche.
- `SurveySD3Machiavellianism`: 9 item.
- `SurveySD3Narcissism`: 9 item.
- `SurveySD3Psychopathy`: 9 item.
- `SurveyScaleIntro`
- `SurveyPage4...SurveyPage10`
- `SurveyFeedback`
- `SurveyTerminated`: solo esclusi/inattivi.
- `FinalResults`

Ogni schermata SD3 usa la scala obbligatoria:

1. Disagree strongly
2. Disagree
3. Neither agree nor disagree
4. Agree
5. Agree strongly

## Pagamento

Part 1 è sempre pagata. Non esiste più il sorteggio Part 1/Dictator.
Restano show-up fee configurabile, domanda 11–20 e premio differito `$2`.

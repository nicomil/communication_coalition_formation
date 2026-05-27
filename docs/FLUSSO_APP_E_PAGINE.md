# Guida flusso esperimento (stato attuale)

Questo documento descrive il flusso realmente attivo nel progetto.

## Sequenza app

`bargaining_tdl_intro` → `bargaining_tdl_main` → `bargaining_tdl_part3` → `bargaining_tdl_survey`

## 1) `bargaining_tdl_intro`

- `Welcome`
- `InstructionsPart1`
- `ControlQuestionsAttempt1...5`
- `Goodbye` (solo se fail o timeout control questions; termina esperimento)

Chi passa va a `bargaining_tdl_main`.

## 2) `bargaining_tdl_main`

- `GroupingAfterControlQuestions` (gruppi da 3, by arrival)
- `Chat`
- `Signals`
- `ExperimentTerminated` (solo esclusi)
- `DataMappingWaitPage`
- `Decision`
- `ResultsWaitPage`
- `Results` (solo attivi)
- `InactivityGoodbyeMain` (solo inattivi/dropout)

Note operative:
- Dropout gestito senza bloccare il gruppo.
- Partecipante inattivo riceve payoff Part 1 a zero.
- Sorteggio parte pagata (`Part1` vs `Part3`) resta attivo.

## 3) `bargaining_tdl_part3`

Stato attivo:
- `InstructionsPart3`
- `ThankYouPart3` (solo esclusi/inattivi)
- `ResultsPart3`

La vecchia logica estesa con decisione/control questions non e' nel `page_sequence` attuale.

## 4) `bargaining_tdl_survey`

- `SurveyIntro`
- `SurveyQuestions`
- `SurveyScaleIntro`
- `SurveyPage4...SurveyPage10`
- `SurveyFeedback` (chiarezza istruzioni + commento generale)
- `SurveyTerminated` (solo esclusi/inattivi)
- `FinalResults`

## Regole di transizione chiave

- **Fail/timeout intro CQ**: `Goodbye` e uscita immediata.
- **Timeout/inattivita' in main**: gruppo continua; inattivo marcato e payoff Part 1 azzerato.
- **Timeout survey timed pages**: esclusione con `SurveyTerminated`.

## Riferimenti

- Config sessione: `settings.py`
- Logica dropout/payoff: `bargaining_tdl_main/__init__.py`
- Survey finale: `bargaining_tdl_survey/__init__.py`

# Timeouts and redirects (source of truth)

Questo documento descrive i timeout di pagina nello stato attuale del progetto e cosa succede allo scadere.

## Regole globali

- In test, se `use_test_timers=True`, i timeout pagina sono forzati a `60s`.
- In produzione, valgono i timeout per app indicati sotto.
- A timeout, oTree invia `timeout_submission` (se presente) e prosegue nel flusso.

## `bargaining_tdl_intro`

| Pagina | Timeout prod | A timeout |
|---|---:|---|
| `ControlQuestionsAttempt1...5` | 300s | esclusione inattivita', `Goodbye`, uscita esperimento |

## `bargaining_tdl_main`

| Pagina | Timeout prod | A timeout |
|---|---:|---|
| `Chat` | 600s | submit pagina, passa a `Signals` |
| `Signals` | 300s | segnali fallback automatici, player non idoneo a payoff Part 1 |
| `Decision` | 300s | scelta fallback automatica, player non idoneo a payoff Part 1 |
| `Results` | 180s | auto-advance pagina successiva, partecipante resta attivo |

Note dropout:
- disconnect con finestra reconnect (`90s`)
- se reconnect fallisce, gruppo continua senza blocco
- partecipante dropout riceve payoff Part 1 a zero

## `bargaining_tdl_part3`

| Pagina | Timeout prod | A timeout |
|---|---:|---|
| `InstructionsPart3` | 600s | esclusione inattivita', uscita su flow di terminazione |

## `bargaining_tdl_survey`

| Pagina | Timeout prod | A timeout |
|---|---:|---|
| `SurveyQuestions` | 180s | esclusione inattivita' |
| `SurveyPage4...SurveyPage9` | 180s | esclusione inattivita' |
| `SurveyPage10` | 300s | esclusione inattivita' |
| `SurveyFeedback` | 180s | esclusione inattivita' |

Routing finale:
- se escluso: `SurveyTerminated` -> fine
- se attivo: `FinalResults` -> redirect completion URL (Prolific)

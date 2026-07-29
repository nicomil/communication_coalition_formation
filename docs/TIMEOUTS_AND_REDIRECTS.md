# Timeout e redirect

Con `use_test_timers=True`, i timer applicabili diventano 60 secondi.

## Intro

| Pagina | Produzione | Esito timeout |
|---|---:|---|
| `ControlQuestionsAttempt1...5` | 300s | esclusione, CQ failure, restituzione slot RCT |

## Main

| Pagina | Produzione | Esito timeout |
|---|---:|---|
| `Chat` | 600s | passa ai messaggi finali |
| `Signals` | 300s | segnali fallback; rating nulli; non idoneo Part 1 |
| `Decision` | 300s | scelta fallback; non idoneo Part 1 |
| `Results` | 180s | auto-advance, resta attivo |

La finestra di riconnessione chat è 90 secondi. Dopo un dropout il gruppo
continua e il partecipante inattivo riceve payoff Part 1 pari a zero.

## Survey

| Pagina | Produzione | Esito timeout |
|---|---:|---|
| `SurveyQuestions` | 180s | esclusione |
| tre pagine `SurveySD3...` | 180s | esclusione |
| `SurveyPage4...SurveyPage9` | 180s | esclusione |
| `SurveyPage10` | 300s | esclusione |
| `SurveyFeedback` | 180s | esclusione |

Escluso: `SurveyTerminated`. Attivo: `FinalResults`, poi redirect al
`completionlink` Prolific configurato.

# Architettura attiva - Bargaining TDL

## Overview

Esperimento oTree con 4 app attive in sequenza:

`bargaining_tdl_intro` → `bargaining_tdl_main` → `bargaining_tdl_part3` → `bargaining_tdl_survey`

La vecchia app `bargaining_tdl_part2` e' stata rimossa dal flusso operativo.

## Moduli principali

- `bargaining_tdl_common`: helper timeout, validator CQ, mapping ruoli/colori, logging.
- `bargaining_tdl_intro`: onboarding + control questions iniziali.
- `bargaining_tdl_main`: triadi, chat/signals, decisione Part 1, dropout handling, payoff Part 1.
- `bargaining_tdl_part3`: modulo individuale post-main.
- `bargaining_tdl_survey`: survey finale, feedback sperimentale, risultati finali + redirect Prolific.

## Flusso dati

### `participant.vars` chiave

- `part1_payoff`
- `part1_payoff_eligible`
- `selected_part_for_payment`
- `inactive_excluded`
- `inactive_excluded_reason`
- `group_dropped`
- `prolific_id`
- `prolific_study_id`
- `prolific_session_id`

### Invarianti runtime

- Gruppo non si blocca su dropout in main.
- Partecipante inattivo/dropout riceve payoff Part 1 = 0.
- Gli altri membri proseguono con fallback automatici.

## Timeout e UX timer

- Timeout per pagina definiti nei moduli app.
- Override test timer centralizzato in `bargaining_tdl_common/helpers.py`.
- UI timer gestita in template globali/survey timer partial.

## Survey e risultati

- Survey include pagina feedback istruzioni (`1-5`) + commento aperto.
- `FinalResults` mostra payoff e gestisce redirect Prolific.

## Export dati

- Export oTree completo (`all_apps_wide`) usato come sorgente audit.
- Pipeline `process_all_apps.py` produce:
  - dataset `core` (analisi)
  - dataset `full` (audit)
- Data dictionary in `docs/EXPORT_DATA_DICTIONARY.md`.

## Testing

- Test bot per `bargaining_tdl_survey`.
- Test unit/integration principali in `bargaining_tdl_main`.
- Comando smoke consigliato: `otree test bargaining_tdl 9 --export`.


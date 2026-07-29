# Export data dictionary

## Dataset core

`process_all_apps.py` legge `all_apps_wide` e produce le seguenti colonne
stabili, più ogni campo survey con prefisso `survey_`.

### Identità e RCT

| Colonna | Significato |
|---|---|
| `playerid` | ID nella sessione |
| `participant_code` | codice anonimo oTree |
| `treatment` | `private`, `public`, `private_no_dwl` |
| `allocation_slot` | slot della schedule RCT |
| `allocation_block` | blocco permutato |
| `allocation_attempt` | 1 originale; >1 rimpiazzo |
| `assignment_timestamp` | epoch assegnazione |
| `assignment_status` | `assigned`, `passed`, `failed` |
| `is_replacement` | indicatore rimpiazzo |
| `allocation_failure_reason` | CQ failure/timeout, se presente |
| `prolific_id` | PID Prolific |
| `prolific_study_id` | study ID |
| `prolific_session_id` | session ID |

### Main

| Colonna | Significato |
|---|---|
| `groupid` | triade main |
| `left_player`, `right_player` | mapping partner |
| `part1_signal_left`, `part1_signal_right` | messaggi finali |
| `signal_left_convincingness` | rating 1–5 del messaggio al partner sinistro |
| `signal_right_convincingness` | rating 1–5 del messaggio al partner destro |
| `part1_finaldecision` | `Left`, `Right`, `NoOne` |
| `part1_payoff` | payoff Part 1 |
| `group_outcome` | `mutual_12`, `mutual_23`, `mutual_31`, `no_dwl_star_1/2/3`, `disagreement` |
| `part1_payoff_eligible` | eleggibilità Part 1 |
| `inactive`, `inactive_reason`, `group_dropped` | diagnostica inattività |

I due rating sono nulli quando `Signals` scade per timeout.

### Survey

Tutti i campi `bargaining_tdl_survey.1.player.*` diventano
`survey_<nome_campo>`. I nuovi campi sono:

- `survey_sd3_mach_01` … `survey_sd3_mach_09`;
- `survey_sd3_narc_01` … `survey_sd3_narc_09`;
- `survey_sd3_psych_01` … `survey_sd3_psych_09`;
- `survey_time_survey_sd3_mach`;
- `survey_time_survey_sd3_narc`;
- `survey_time_survey_sd3_psych`.

Gli item valgono 1–5:

1. Disagree strongly
2. Disagree
3. Neither agree nor disagree
4. Agree
5. Agree strongly

## Export audit RCT

`bargaining_tdl_intro` espone due custom export.

### RCT Assignments

Una riga per ogni tentativo di assegnazione, inclusi soggetti espulsi alle CQ:

`session_code`, `participant_code`, `prolific_id`, `slot_number`,
`block_number`, `treatment`, `attempt_number`, `is_replacement`, `status`,
`assigned_at`, `resolved_at`, `resolution_reason`.

### RCT Slots

Una riga per ogni slot pre-generato:

`session_code`, `randomization_seed`, `slot_number`, `block_number`,
`position_in_block`, `treatment`, `status`, `assigned_participant_code`,
`replacement_count`, `assigned_at`, `returned_at`, `filled_at`.

Conservare insieme `all_apps_wide`, `RCT Assignments` e `RCT Slots`: sono il
pacchetto minimo per audit ITT e ricostruzione della randomizzazione.

## Comando

```bash
python process_all_apps.py \
  input_all_apps_wide.csv \
  output_core.csv \
  output_full.csv \
  output_dictionary.md
```

Il dizionario generato dal quarto argomento riporta fill ratio per l'export
specifico. Non sovrascrivere questo file di schema con un export storico.

# Validità dati Prolific

Regole per inclusione/esclusione record nel pilot e nello studio principale.

## Identificatore principale

| Campo | Obbligatorio per analisi | Ruolo |
|-------|-------------------------|--------|
| `participant.prolific_id` | **Sì** | Chiave partecipante Prolific |
| `participant.prolific_study_id` | No | Audit opzionale |
| `participant.prolific_session_id` | No | Audit opzionale |

Config app: `require_prolific_id=True` in `SESSION_CONFIG_DEFAULTS` (produzione).

## Inclusione (record validi)

Includere se **tutte** vere:

1. Partecipante ha completato almeno Welcome con `prolific_id` non vuoto (o `participant.label` da URL).
2. Sessione non marcata come test interno (`local-*` solo per dev).
3. Non escluso per inattività se policy studio lo richiede (`inactive_excluded=False` per pagamento Part 1).

## Esclusione (record non validi per analisi principale)

Escludere se **una** vera:

1. `prolific_id` vuoto e `require_prolific_id` era attivo.
2. `prolific_id` inizia con `local-` (solo test locale).
3. Duplicato sospetto: stesso `prolific_id` in più submission nella stessa sessione (verificare manualmente su Prolific).
4. `inactive_excluded=True` per timeout/inattività (se policy = no pagamento).

## Query export (indicativo)

Dopo `python process_all_apps.py`, filtrare CSV:

- **Validi**: colonna `participant.prolific_id` non vuota e non prefisso `local-`.
- **Da revisione**: `prolific_id` vuoto ma `participant.visited=1`.

## Prolific lato piattaforma

- Approval/rejection: **Manual review** nel pilot.
- Non usare Study/Session ID come criterio di pagamento; solo PID + completamento task.

## Note sicurezza

`STUDY_ID` e `SESSION_ID` non sono segreti; non devono essere requisiti di accesso all’app.

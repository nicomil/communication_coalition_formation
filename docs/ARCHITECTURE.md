# Architettura attiva — Bargaining TDL

## Flusso

Esperimento oTree in tre app:

`bargaining_tdl_intro` → `bargaining_tdl_main` → `bargaining_tdl_survey`

- `bargaining_tdl_common`: registro trattamenti, helper timeout, CQ e mapping.
- `bargaining_tdl_intro`: PID, assegnazione RCT, istruzioni specifiche, CQ.
- `bargaining_tdl_main`: triadi omogenee, comunicazione, messaggi finali,
  decisione e payoff Part 1.
- `bargaining_tdl_survey`: demografia, tre scale SD3, survey esistente,
  domanda 11–20, feedback e risultati.

Il precedente modulo Dictator è stato rimosso. Part 1 è sempre pagata.

## Trattamenti

| Codice | Comunicazione | Payoff |
|---|---|---|
| `private` | privata | Total Deadweight Loss |
| `public` | pubblica | Total Deadweight Loss |
| `private_no_dwl` | privata | No-Deadweight Loss |

Un solo studio e un solo link Prolific alimentano tutti i bracci.

## Randomizzazione RCT

Alla nascita della sessione viene creata una schedule in blocchi permutati di
9: tre slot per trattamento, con ordine casuale crittograficamente seminato.
Il seed è salvato in `session.randomization_seed`.

L'assegnazione avviene solo dopo un Welcome valido. Lo slot è provvisorio fino
al superamento delle CQ:

1. CQ superata → slot `filled`;
2. CQ fallita o timeout → slot restituito;
3. il primo nuovo partecipante riceve prima lo slot restituito, nello stesso
   trattamento;
4. ogni tentativo resta nell'export audit RCT.

PostgreSQL usa row lock per serializzare claim concorrenti. Per avere
rimpiazzi disponibili, creare la sessione oTree con buffer e fermare il
reclutamento sulla quota di partecipanti che hanno superato le CQ.

## Invarianti del gioco

- Gruppi da tre, omogenei per trattamento, formati by-arrival dopo le CQ.
- Scelte finali ammesse: `Left`, `Right`, `NoOne`.
- Supporto reciproco: payoff `(6, 6, 0)`.
- Nessun supporto reciproco nei bracci TDL: `(0, 0, 0)`.
- Nel braccio No-DWL, due giocatori che supportano il terzo mentre il terzo
  sceglie `NoOne`: il terzo riceve 12, gli altri 0.
- Timeout/dropout in main: gruppo continua; partecipante inattivo non è
  idoneo al payoff Part 1.

## Pagamento

Totale mostrato: show-up fee configurabile (default `$3`) + payoff Part 1
sempre + premio della domanda 11–20. Il premio differito `$2` resta invariato.

## Export

- `all_apps_wide`: record completo oTree.
- `RCT Assignments`: ogni assegnazione, incluse CQ failure e rimpiazzi.
- `RCT Slots`: schedule, seed e stato finale degli slot.
- `process_all_apps.py`: dataset `core`, copia `full`, dizionario automatico.

Vedi `docs/EXPORT_DATA_DICTIONARY.md`.

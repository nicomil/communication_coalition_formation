# Prolific codes — data collection schedule

Questo documento riassume i codici Prolific da utilizzare per la raccolta dati.
Ogni riga corrisponde a uno studio/trattamento e contiene tre codici distinti:

I codici sono riportati come **link Prolific completi**, nel formato richiesto da
oTree per il redirect finale:

`https://app.prolific.com/submissions/complete?cc=CODICE`

- **Completion code**: esperimento completato con successo;
- **Dropout CQs code**: partecipante escluso perché ha sbagliato le control questions;
- **Dropout Timeout code**: partecipante escluso perché inattivo fino al timeout.

## Mappatura dei trattamenti

| Nome operativo | Trattamento nel codice | Descrizione |
|---|---|---|
| Baseline | `private` | Comunicazione privata con total deadweight loss |
| Public | `public` | Comunicazione pubblica con total deadweight loss |
| Slacker | `private_no_dwl` | Comunicazione privata senza deadweight loss |

## Codici per giorno e fascia oraria

Gli orari sono riportati in **Italian Time**. L'orario US Eastern è indicato tra parentesi.

### Day 1 — Monday

| Fascia italiana | Fascia US Eastern | Trattamento | Completion code | Completion URL | Dropout CQs code | Dropout CQs URL | Dropout Timeout code | Dropout Timeout URL |
|---|---|---|---|---|---|---|---|---|
| 15:30–17:30 | 09:30–11:30 | Baseline | `C19QG34V` | `https://app.prolific.com/submissions/complete?cc=C19QG34V` | `CYZ535HK` | `https://app.prolific.com/submissions/complete?cc=CYZ535HK` | `C1NX1SC7` | `https://app.prolific.com/submissions/complete?cc=C1NX1SC7` |
| 17:45–19:00 | 11:45–13:00 | Public | `C1NLKVJO` | `https://app.prolific.com/submissions/complete?cc=C1NLKVJO` | `C1GZP9YZ` | `https://app.prolific.com/submissions/complete?cc=C1GZP9YZ` | `C12QTGB5` | `https://app.prolific.com/submissions/complete?cc=C12QTGB5` |
| 19:15–20:30 | 13:15–14:30 | Slacker | `CS0SK0FT` | `https://app.prolific.com/submissions/complete?cc=CS0SK0FT` | `CBPGAP2T` | `https://app.prolific.com/submissions/complete?cc=CBPGAP2T` | `CVCH885O` | `https://app.prolific.com/submissions/complete?cc=CVCH885O` |

### Day 2 — Tuesday

| Fascia italiana | Fascia US Eastern | Trattamento | Completion code | Completion URL | Dropout CQs code | Dropout CQs URL | Dropout Timeout code | Dropout Timeout URL |
|---|---|---|---|---|---|---|---|---|
| 15:30–17:30 | 09:30–11:30 | Public | `C187VMJZ` | `https://app.prolific.com/submissions/complete?cc=C187VMJZ` | `C178PR0K` | `https://app.prolific.com/submissions/complete?cc=C178PR0K` | `COYX7OAP` | `https://app.prolific.com/submissions/complete?cc=COYX7OAP` |
| 17:45–19:00 | 11:45–13:00 | Slacker | `C1LRIGON` | `https://app.prolific.com/submissions/complete?cc=C1LRIGON` | `C1A5YEEH` | `https://app.prolific.com/submissions/complete?cc=C1A5YEEH` | `C16OVXXD` | `https://app.prolific.com/submissions/complete?cc=C16OVXXD` |
| 19:15–20:30 | 13:15–14:30 | Baseline | `C1OO523E` | `https://app.prolific.com/submissions/complete?cc=C1OO523E` | `CJA3HCA8` | `https://app.prolific.com/submissions/complete?cc=CJA3HCA8` | `C1B3RJS2` | `https://app.prolific.com/submissions/complete?cc=C1B3RJS2` |

### Day 3 — Wednesday

| Fascia italiana | Fascia US Eastern | Trattamento | Completion code | Completion URL | Dropout CQs code | Dropout CQs URL | Dropout Timeout code | Dropout Timeout URL |
|---|---|---|---|---|---|---|---|---|
| 15:30–17:30 | 09:30–11:30 | Slacker | `CTS7WY83` | `https://app.prolific.com/submissions/complete?cc=CTS7WY83` | `C18TF8C6` | `https://app.prolific.com/submissions/complete?cc=C18TF8C6` | `CQJD948X` | `https://app.prolific.com/submissions/complete?cc=CQJD948X` |
| 17:45–19:00 | 11:45–13:00 | Baseline | `C6CWP51H` | `https://app.prolific.com/submissions/complete?cc=C6CWP51H` | `CRGEJSNX` | `https://app.prolific.com/submissions/complete?cc=CRGEJSNX` | `CW12WXEV` | `https://app.prolific.com/submissions/complete?cc=CW12WXEV` |
| 19:15–20:30 | 13:15–14:30 | Public | `CMV2DGMZ` | `https://app.prolific.com/submissions/complete?cc=CMV2DGMZ` | `CG5BL66Z` | `https://app.prolific.com/submissions/complete?cc=CG5BL66Z` | `C18NC41T` | `https://app.prolific.com/submissions/complete?cc=C18NC41T` |

## Controllo rapido

- Ogni giorno contiene una sessione Baseline, una Public e una Slacker.
- Ogni trattamento ha un codice distinto per ciascuno dei tre esiti.
- I codici sono specifici per giorno e fascia oraria: non devono essere riutilizzati in un altro slot.

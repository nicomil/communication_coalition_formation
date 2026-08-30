# Audit merge all_apps_wide + ChatMessages

## Conteggi

- `wide_rows`: **162**
- `aggregated_rows`: **162**
- `long_rows`: **324**
- `expected_long_rows`: **324**
- `groups_with_messages`: **24**
- `dyads_with_messages`: **66**
- `wide_participants`: **162**

## Stato parsing dei messaggi

- `ok`: **311**

## Controlli

- Output aggregato con una riga per partecipante: **PASS**
- Output left/right con due righe per partecipante: **PASS**
- Colonne originali all_apps_wide preservate: **194** colonne di base

## Triple check

- Copertura messaggi nell’aggregato: **PASS**
- Copertura messaggi nel file left/right: **PASS**
- Conservazione valori originali: **PASS**
- JSON transcript valido: **PASS**

## Messaggi non abbinati

Nessun messaggio non abbinato rilevato.

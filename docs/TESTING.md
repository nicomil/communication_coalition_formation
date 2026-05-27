# Guida ai test - stato attuale

## Flusso testato

Esperimento attivo:
1. `bargaining_tdl_intro`
2. `bargaining_tdl_main`
3. `bargaining_tdl_part3`
4. `bargaining_tdl_survey`

## Comandi principali

```bash
otree test bargaining_tdl 9
otree test bargaining_tdl 12
otree test bargaining_tdl 9 --export
```

Numero partecipanti consigliato: multiplo di 3.

## Test singola app

```bash
otree test bargaining_tdl_intro 3
otree test bargaining_tdl_main 3
otree test bargaining_tdl_part3 3
otree test bargaining_tdl_survey 3
```

## Cosa verificare

- nessun errore bot
- gruppi da 3 formati correttamente in main
- payoff Part 1 coerenti con decisioni e fallback inattivita'
- partecipanti inattivi con `part1_payoff_eligible=False` e payoff Part 1 a zero
- survey completata fino a `FinalResults` per attivi
- redirect completion Prolific funzionante

## Checklist pre deploy

- [ ] `otree test bargaining_tdl 9` passa
- [ ] `otree test bargaining_tdl 12` passa
- [ ] test export (`--export`) passa
- [ ] verificata gestione dropout in main
- [ ] verificata pagina feedback survey e salvataggio campi


# Guida ai test

## Suite

```bash
# Flusso completo: tre casi payoff su tutti i bracci
otree test bargaining_tdl 18

# Bracci isolati
otree test bargaining_tdl_private 9
otree test bargaining_tdl_public 9
otree test bargaining_tdl_private_no_dwl 9

# Allocatore RCT con database in memoria
OTREE_IN_MEMORY=1 python -m unittest test_rct_allocator.py

# Unità payoff, schedule, dropout ed export
python -m unittest \
  bargaining_tdl_intro.tests.RandomizedScheduleTests \
  bargaining_tdl_main.tests.PayoffLogicTests \
  bargaining_tdl_main.test_dropout_sync \
  test_process_all_apps.py
```

Numero partecipanti: multiplo di 3; usare multipli di 9 per verificare blocchi
RCT completi.

## Casi end-to-end

- `mutual_12`: supporto reciproco, payoff 6/6/0.
- `disagreement`: nessun accordo, payoff 0/0/0.
- `no_dwl_star`: due supportano il terzo che sceglie `NoOne`; 12/0/0 solo
  nel trattamento `private_no_dwl`.

## Checklist pre-go-live

- [ ] suite sopra tutta verde;
- [ ] tre trattamenti presenti 3:3:3 in ogni blocco completo;
- [ ] CQ failure restituisce lo stesso slot al primo nuovo partecipante;
- [ ] triadi omogenee per trattamento;
- [ ] rating messaggi obbligatori e non mostrati ai partner;
- [ ] 27 item SD3 obbligatori e collocati dopo le demografiche;
- [ ] export `all_apps_wide`, `RCT Assignments`, `RCT Slots` scaricabili;
- [ ] ingresso unico `/room/prolific` e redirect finale provati in anonimo;
- [ ] wording No-DWL definitivo approvato prima del go-live.

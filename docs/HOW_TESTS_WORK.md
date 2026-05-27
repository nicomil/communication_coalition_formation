# Come funzionano i test automatici

## Flusso coperto

I bot percorrono il flusso reale:

`bargaining_tdl_intro` → `bargaining_tdl_main` → `bargaining_tdl_part3` → `bargaining_tdl_survey`

## Principi

- i bot non saltano pagine
- i bot compilano i form come un partecipante reale
- i test verificano invarianti di payoff e stato

## Cosa viene verificato

### Main

- gruppi da 3 su `group_by_arrival_time`
- mapping segnali tra partner
- payoff coerenti con scelte
- comportamento robusto con inattivita'/dropout

### Survey

- completamento sequenza fino a risultati finali
- salvataggio campi survey e feedback finale

## Comandi

```bash
otree test bargaining_tdl 9
otree test bargaining_tdl 12
otree test bargaining_tdl 9 --export
```

## Limiti

- bot non simulano psicologia/strategie reali
- bot non sono test UX visuale (per quello usare `browser_bots`)


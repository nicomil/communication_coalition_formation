# Come funzionano i test automatici

I bot percorrono il flusso reale:

`intro` → `main` → `survey`

Tre casi coprono supporto reciproco, disaccordo e payoff No-DWL 12/0/0. I bot
compilano anche i due rating di convincimento e tutti i 27 item SD3.

I test unitari enumerano tutte le 27 combinazioni di decisione per entrambi i
regimi payoff. I test d'integrazione RCT usano un database oTree in memoria e
verificano blocchi 3:3:3, audit, CQ failure e rimpiazzo nello stesso braccio.

Comandi e checklist sono in `docs/TESTING.md`.

Limiti:

- i bot non simulano strategie umane;
- la concorrenza reale dei row lock va provata su staging PostgreSQL;
- UX e responsive richiedono smoke manuale/browser.

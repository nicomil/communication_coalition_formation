# Legacy cleanup log

Pulizia applicata per allineare il repository al flusso sperimentale attivo.

## Rimosso

- app legacy `bargaining_tdl_part2` (non presente in `app_sequence` attiva)
- documentazione di piano legacy:
  - `docs/plan_part2_mpl.md`
  - `docs/plan_part2_payoff_function.md`
  - `docs/plan_part2_extensions.md`

## Aggiornato

- `bargaining_tdl_common/__init__.py`: rimossi export/import di helper Part2
- `bargaining_tdl_common/validators.py`: rimossa logica `part2`
- `bargaining_tdl_common/utils.py`: docstring allineata a flow attivo
- `update_cards.py`: rimossa directory `bargaining_tdl_part2`
- `scripts/test_many_participants.py`: rimossi riferimenti ai case Part2

## Documentazione allineata al flusso attuale

- `docs/FLUSSO_APP_E_PAGINE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/HOW_TESTS_WORK.md`
- `docs/FILES_FOR_DEPLOYMENT.md`
- `docs/DEBUG_GROUP_IDS.md`

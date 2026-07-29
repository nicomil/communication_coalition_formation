# Debug: Group e ID in group

Ogni app oTree ha una numerazione locale dei gruppi.

| Fase | Significato |
|---|---|
| `bargaining_tdl_intro` | contenitore tecnico individuale; il trattamento è in `assigned_treatment` |
| `bargaining_tdl_main` | triade di gioco omogenea per trattamento |
| `bargaining_tdl_survey` | contenitore tecnico individuale |

La triade viene formata solo in
`GroupingAfterControlQuestions`, by-arrival e separando i tre pool di
trattamento. Per analisi usare:

- `bargaining_tdl_main.1.group.id_in_subsession` come ID triade;
- `bargaining_tdl_intro.1.player.allocation_slot` come slot RCT;
- `bargaining_tdl_intro.1.player.assigned_treatment` come braccio.

Un cambio di `Group` tra app è normale: non è un identificatore globale.

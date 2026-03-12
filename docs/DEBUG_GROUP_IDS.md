# Debug info: significato di "Group" e "ID in group"

Nel pannello **Debug info** (solo in sviluppo), le voci **Group** e **ID in group** si riferiscono **sempre all’app corrente**. Ogni app ha i propri gruppi e numerazione; il numero di gruppo non è un identificativo globale della triade nell’esperimento.

## Perché il numero di gruppo cambia tra le fasi

### 1. Dopo General Instructions (intro) – es. Group 7 e Group 8

- **App:** `bargaining_tdl_intro`
- **Meccanismo:** La wait page `GroupingAfterWelcome` usa `group_by_arrival_time`: oTree forma triadi in ordine di arrivo e assegna a ciascuna un **group id** nell’app intro (1, 2, 3, …).
- Se P1 e P2 formano una triade con un terzo → **Group 7** (settima triade formata).
- Se P6 forma un’altra triade → **Group 8** (ottava triade).
- Quindi **Group 7** e **Group 8** sono gli id di gruppo **nell’app intro**, non nella main.

### 2. “Poi sono diventati tutti Group 8” / scelta segnali → Group 11

- **App:** passaggio da `bargaining_tdl_intro` a `bargaining_tdl_main`.
- **Meccanismo:** A ogni triade che completa `GroupingAfterWelcome`, il codice aggiorna la matrice dei gruppi dell’app **main** con `set_group_matrix`: prima le triadi già formate in intro (in ordine), poi i restanti partecipanti in gruppi da 3. Gli id di gruppo nella **main** sono 1, 2, 3, … in base a questa matrice.
- Il numero che vedi (8, 11, …) è l’**id del gruppo nell’app in cui ti trovi** (intro vs main). Se ad esempio nella main la vostra triade è l’11ª riga della matrice, in **main** vedrete **Group 11**.
- “Tutti Group 8” significa che in quel momento state tutti nella stessa triade e quella triade, nella main, ha id 8. Il “cambio” da 7/8 a 8 (o a 11) non è un bug: è il passaggio dalla numerazione **intro** alla numerazione **main**.

### 3. Part 2 – “tutti Group 6” pur essendo fase individuale

- **App:** `bargaining_tdl_part2`
- **Meccanismo:** In part2 è impostato `PLAYERS_PER_GROUP = None` (fase individuale, nessun gruppo di gioco). oTree crea comunque gruppi tecnici (es. un gruppo per partecipante o una struttura interna); l’id mostrato è quello **del gruppo nell’app part2**.
- Quindi **Group 6** in part2 non indica la vostra triade della Part 1: indica solo l’id del gruppo assegnato dal sistema in **part2**. Per la Part 2 il valore “Group” nel debug non ha significato per la logica dell’esperimento; può essere nascosto o interpretato come “N/A (fase individuale)”.

## Allineamento con il meccanismo dell’esperimento

- **Intro:** Group / ID in group = triade formata per arrivo; coerente con `group_by_arrival_time`.
- **Main:** Group / ID in group = triade nella main, dopo il sync dalla intro; coerente con la matrice impostata da `GroupingAfterWelcome` (e con eventuale `SyncWithMainWaitPage` se presente).
- **Part 2:** Group / ID in group = solo id tecnico oTree; **non** rappresenta la triade della Part 1. In part2 le debug info sono state adattate (rimozione o “N/A”) per evitare confusione.

## Riepilogo

| Fase              | App        | Significato di “Group” nel debug                         |
|-------------------|------------|----------------------------------------------------------|
| Dopo General Instr.| intro      | Id della triade in intro (ordine di arrivo)              |
| Scelta segnali / Main | main   | Id della triade nella main (stessa triade, numerazione main) |
| Part 2 (MPL)      | part2      | Nessun significato di gioco; fase individuale (N/A)     |

Il fatto che il numero cambi (7 → 8 → 11 → 6) è quindi atteso: ogni app ha la propria numerazione; l’importante è che **nella main** P1, P2 e P6 restino nella **stessa triade** (stesso Group nella main), così che Decision e Results usino la stessa composizione del gruppo.

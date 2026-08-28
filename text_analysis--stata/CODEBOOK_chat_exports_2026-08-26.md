# Codebook — export oTree con chat (2026-08-26)

## 1. File coperti

- `all_apps_wide_2026-08-26_chat_aggregated_final.csv`: **3,090 righe**, **128 colonne**; una riga per partecipante del raw.
- `all_apps_wide_2026-08-26_chat_by_partner_final.csv`: **6,180 righe**, **132 colonne**; due righe per partecipante (`chat_side=left/right`).

Entrambi i file contengono le 104 colonne oTree richieste e 16 variabili derivate comuni. Il primo aggiunge 8 variabili chat di gruppo; il secondo 12 variabili chat diadiche.

## 2. Unità, chiavi e relazione fra i file

| File | Unità di osservazione | Chiave raccomandata |
|---|---|---|
| `all_apps_wide_2026-08-26_chat_aggregated_final.csv` | partecipante | `session.code` + `participant.code` |
| `all_apps_wide_2026-08-26_chat_by_partner_final.csv` | partecipante × partner topologico | `session.code` + `participant.code` + `chat_side` |

- `chat_group_key = session.code | participant.part1_group_id` identifica la triade della Parte 1.
- `participant.part1_group_id` è preferibile a `group.id_in_subsession` perché resta stabile anche dopo eventuali regrouping.
- `chat_side` è il lato **topologico** del partner. L’ordine visto a schermo è registrato separatamente nelle variabili `id_player_visualized_*`.
- Nel by-partner ogni messaggio della diade compare nel transcript di entrambi i membri; non sommare i transcript sulle righe senza prima deduplicare la diade.

## 3. Snapshot del campione sperimentale

| Treatment | Partecipanti | Triadi osservate | Triadi valide | Messaggi |
|---|---:|---:|---:|---:|
| Private | 360 | 120 | 113 | 1,570 |
| Public | 354 | 118 | 115 | 2,009 |
| Slacker | 336 | 112 | 109 | 1,529 |
| **Totale** | **1050** | **350** | **337** | **5,108** |

Le righe con treatment vuoto appartengono ad altre parti/sessioni presenti nel raw e non alle 350 triadi dei tre treatment.

### Definizione di triade valida

Una triade è valida se contiene gli ID 1, 2 e 3, `group.group_dropped` non è vero e nessun membro ha `participant.inactive_excluded` vero, `decision_inactive=99` o `signal_inactive=99`. `group_valid` non è materializzato in questi CSV, ma si ricostruisce con questa regola.

## 4. Codifiche sostantive

### Treatment

- `private`: Baseline, comunicazione privata.
- `public`: comunicazione pubblica/osservabile.
- `private_no_dwl`: **Slacker**, comunicazione privata senza deadweight loss.

### Outcome

- `mutual_12`, `mutual_23`, `mutual_31`: minimal winning coalition (**MWC**) tra la coppia indicata.
- `no_dwl_star_1`, `no_dwl_star_2`, `no_dwl_star_3`: **SlackerPayoff**; applicabile al treatment Slacker.
- `disagreement`: mancato coordinamento.
- `pending`: outcome non finalizzato/non pertinente nelle righe esterne alle partite analizzate.
- `grp_coordinate=1` quando almeno un giocatore ottiene payoff positivo: comprende sia MWC sia SlackerPayoff.

### Segnali

- `split_you`: intenzione di supportare il destinatario del segnale.
- `split_other`: intenzione di supportare il terzo giocatore.
- `support_none`: intenzione di non supportare nessuno.

## 5. Transcript JSON

`chat_transcript_group` e `chat_transcript` sono array JSON su una sola cella CSV, ordinati per timestamp. Ogni elemento contiene:

| Campo JSON | Significato |
|---|---|
| `timestamp` | tempo Unix del messaggio |
| `from_id`, `from_color` | mittente nella triade |
| `to_id`, `to_color` | destinatario nella triade |
| `nickname` | nickname registrato da oTree |
| `participant_code` | codice del mittente, usato per risolverne l’identità |
| `body` | testo originale del messaggio |
| `channel` | canale oTree della diade |
| `parse_status` | `ok` per i messaggi validati |

Il merge 2026-08-26 identifica il mittente tramite `participant_code`, verifica che il suo `id_in_group` appartenga alla coppia codificata nel canale e usa `participant.part1_group_id` per il gruppo. Tutti i 5.108 messaggi hanno superato questi controlli.

## 6. Valori mancanti e precauzioni

- La stringa vuota rappresenta un dato mancante/non applicabile.
- `[]` è un transcript valido senza messaggi; non è un valore mancante.
- `NoOne` è una scelta sostantiva, non un missing.
- `0` può essere un valore reale o un default oTree: interpretarlo insieme allo stato della riga e ai flag d’inattività.
- I timestamp delle chat sono secondi Unix; le variabili `time_*` sono durate in secondi.
- Le variabili group-level si ripetono su tre partecipanti e, nel by-partner, su sei righe per triade: collassare/deduplicare prima di calcolare statistiche di gruppo.

## 7. Dizionario completo delle variabili

| # | Variabile | Presenza | Origine | Tipo | Copertura non vuota | Valori/codifica | Definizione |
|---:|---|---|---|---|---|---|---|
| 1 | `participant.id_in_session` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | — | Numero progressivo del partecipante nella sessione oTree. |
| 2 | `participant.code` | entrambi | oTree raw | identificatore/testo | aggregated 3090/3090; by-partner 6180/6180 | — | Codice pseudonimo univoco del partecipante; chiave del mittente nel file chat. |
| 3 | `participant.label` | entrambi | oTree raw | identificatore/testo | aggregated 1577/3090; by-partner 3154/6180 | — | Etichetta opzionale assegnata al partecipante in oTree. |
| 4 | `participant._index_in_pages` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | — | Indice interno oTree della pagina raggiunta dal partecipante. |
| 5 | `participant.payoff` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0.0; 3.0; 6.0 | Payoff complessivo oTree del partecipante, espresso nella valuta configurata. |
| 6 | `participant.inactive_excluded` | entrambi | oTree raw | booleano | aggregated 206/3090; by-partner 412/6180 | 1 | Indicatore che il partecipante è stato escluso per inattività. |
| 7 | `participant.inactive_excluded_reason` | entrambi | oTree raw | categorico/testo | aggregated 206/3090; by-partner 412/6180 | — | Motivo testuale/codificato dell’esclusione per inattività. |
| 8 | `participant.group_dropped` | entrambi | oTree raw | booleano | aggregated 1050/3090; by-partner 2100/6180 | 0; 1 | Indicatore participant-level che il gruppo è stato marcato come caduto/interrotto. |
| 9 | `participant.part1_payoff_eligible` | entrambi | oTree raw | booleano | aggregated 1050/3090; by-partner 2100/6180 | 0; 1 | Indicatore participant-level di eleggibilità al payoff della Parte 1. |
| 10 | `participant.group_outcome` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | disagreement; mutual_12; mutual_23; mutual_31; no_dwl_star_1; no_dwl_star_2; no_dwl_star_3 | Copia participant-level dell’esito del gruppo della Parte 1. |
| 11 | `participant.part1_group_id` | entrambi | oTree raw | numerico | aggregated 1050/3090; by-partner 2100/6180 | — | ID immutabile del gruppo della Parte 1. È l’ID da usare per collegare le chat; può differire dall’ID corrente oTree dopo un regrouping. |
| 12 | `session.code` | entrambi | oTree raw | identificatore/testo | aggregated 3090/3090; by-partner 6180/6180 | — | Codice univoco della sessione oTree. |
| 13 | `bargaining_tdl_intro.1.player.time_welcome` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi sulla pagina Welcome dell’introduzione. |
| 14 | `bargaining_tdl_intro.1.player.time_instructions_part1` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi sulle istruzioni della Parte 1. |
| 15 | `bargaining_tdl_intro.1.player.time_control_questions` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi sulle domande di controllo. |
| 16 | `bargaining_tdl_main.1.player.id_in_group` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | — | Posizione del giocatore nella triade: 1, 2 o 3. |
| 17 | `bargaining_tdl_main.1.player.payoff` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0.0; 3.0; 6.0 | Payoff oTree del player nell’app principale. |
| 18 | `bargaining_tdl_main.1.player.player_color` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | Orange; Purple; Yellow | Colore associato alla posizione: 1=Yellow, 2=Orange, 3=Purple. |
| 19 | `bargaining_tdl_main.1.player.treatment` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | private=Baseline; public=chat pubblica; private_no_dwl=Slacker | Trattamento sperimentale: private, public o private_no_dwl (Slacker). Vuoto per righe del raw non appartenenti a queste partite. |
| 20 | `bargaining_tdl_main.1.player.part1_calculated_payoff` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0.0; 3.0; 6.0 | Payoff teorico calcolato nella Parte 1 prima di un’eventuale esclusione per inattività. |
| 21 | `bargaining_tdl_main.1.player.signal_left` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | split_you; split_other; support_none | Intenzione inviata al partner topologico sinistro. |
| 22 | `bargaining_tdl_main.1.player.signal_right` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | split_you; split_other; support_none | Intenzione inviata al partner topologico destro. |
| 23 | `bargaining_tdl_main.1.player.first_intention_selected` | entrambi | oTree raw | categorico/testo | aggregated 1042/3090; by-partner 2084/6180 | left; right | Lato della prima intenzione selezionata nella pagina Signals: left o right. |
| 24 | `bargaining_tdl_main.1.player.guess_left_confidence` | entrambi | oTree raw | numerico | aggregated 1045/3090; by-partner 2090/6180 | 1; 2; 3; 4; 5; 6; 7; 8 | Fiducia nella previsione sulla scelta del partner sinistro, scala 1–8. |
| 25 | `bargaining_tdl_main.1.player.guess_right_confidence` | entrambi | oTree raw | numerico | aggregated 1045/3090; by-partner 2090/6180 | 1; 2; 3; 4; 5; 6; 7; 8 | Fiducia nella previsione sulla scelta del partner destro, scala 1–8. |
| 26 | `bargaining_tdl_main.1.player.time_welcome` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi sulla pagina Welcome dell’app principale. |
| 27 | `bargaining_tdl_main.1.player.time_chat` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi sulla fase di chat. |
| 28 | `bargaining_tdl_main.1.player.time_signals` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi sulla fase delle intenzioni/segnali. |
| 29 | `bargaining_tdl_main.1.player.decision_choice` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | Left; Right; NoOne | Decisione finale dal punto di vista del focal player: Left, Right o NoOne. |
| 30 | `bargaining_tdl_main.1.player.decision_option_1` | entrambi | oTree raw | categorico/testo | aggregated 1042/3090; by-partner 2084/6180 | Left; NoOne; Right | Opzione mostrata nella prima posizione visuale nella pagina Decision. |
| 31 | `bargaining_tdl_main.1.player.decision_option_2` | entrambi | oTree raw | categorico/testo | aggregated 1042/3090; by-partner 2084/6180 | Left; NoOne; Right | Opzione mostrata nella seconda posizione visuale nella pagina Decision. |
| 32 | `bargaining_tdl_main.1.player.decision_option_3` | entrambi | oTree raw | categorico/testo | aggregated 1042/3090; by-partner 2084/6180 | Left; NoOne; Right | Opzione mostrata nella terza posizione visuale nella pagina Decision. |
| 33 | `bargaining_tdl_main.1.player.received_signal_left` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | split_you; split_other; support_none | Intenzione ricevuta dal partner topologico sinistro. |
| 34 | `bargaining_tdl_main.1.player.received_signal_right` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | split_you; split_other; support_none | Intenzione ricevuta dal partner topologico destro. |
| 35 | `bargaining_tdl_main.1.player.id_player_on_the_left` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | — | participant.code del partner nella coordinata topologica sinistra. |
| 36 | `bargaining_tdl_main.1.player.id_player_on_the_right` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | — | participant.code del partner nella coordinata topologica destra. |
| 37 | `bargaining_tdl_main.1.player.id_player_visualized_on_the_left` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | — | participant.code effettivamente visualizzato nella colonna sinistra, dopo la randomizzazione dell’ordine. |
| 38 | `bargaining_tdl_main.1.player.id_player_visualized_on_the_right` | entrambi | oTree raw | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | — | participant.code effettivamente visualizzato nella colonna destra, dopo la randomizzazione dell’ordine. |
| 39 | `bargaining_tdl_main.1.player.time_decision` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi sulla pagina Decision. |
| 40 | `bargaining_tdl_main.1.player.time_post_decision_confidence` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi sulla pagina di previsione/confidenza post-decisione. |
| 41 | `bargaining_tdl_main.1.player.chat_interrupted` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore che la chat del focal player è stata interrotta. |
| 42 | `bargaining_tdl_main.1.player.part1_payoff_eligible` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore player-level di eleggibilità al payoff della Parte 1. |
| 43 | `bargaining_tdl_main.1.player.decision_inactive` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0=nessun timeout; 99=timeout/inattività | Stato d’inattività sulla decisione: 99 indica timeout senza scelta; 0 indica nessun timeout. |
| 44 | `bargaining_tdl_main.1.player.signal_inactive` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0=nessun timeout; 99=timeout/inattività | Stato d’inattività sui segnali: 99 indica timeout senza scelta; 0 indica nessun timeout. |
| 45 | `bargaining_tdl_main.1.player.received_signal_left_inactive` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0=nessun timeout; 99=timeout/inattività | Stato d’inattività (0/99) del mittente del segnale ricevuto da sinistra. |
| 46 | `bargaining_tdl_main.1.player.received_signal_right_inactive` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | 0=nessun timeout; 99=timeout/inattività | Stato d’inattività (0/99) del mittente del segnale ricevuto da destra. |
| 47 | `bargaining_tdl_main.1.player.guess_left_choice` | entrambi | oTree raw | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | Left; Right; NoOne (POV del partner) | Previsione della decisione del partner sinistro, espressa dal punto di vista di quel partner. |
| 48 | `bargaining_tdl_main.1.player.guess_right_choice` | entrambi | oTree raw | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | Left; Right; NoOne (POV del partner) | Previsione della decisione del partner destro, espressa dal punto di vista di quel partner. |
| 49 | `bargaining_tdl_main.1.group.id_in_subsession` | entrambi | oTree raw | numerico | aggregated 3090/3090; by-partner 6180/6180 | — | ID corrente del gruppo nell’app principale; per le chat preferire participant.part1_group_id. |
| 50 | `bargaining_tdl_main.1.group.grp_coordinate` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | 1 se l’esito produce payoff positivo/coordinamento (mutual oppure star in Slacker); 0 altrimenti. |
| 51 | `bargaining_tdl_main.1.group.group_outcome` | entrambi | oTree raw | categorico/testo | aggregated 3090/3090; by-partner 6180/6180 | mutual_12/23/31; no_dwl_star_1/2/3; disagreement; pending | Esito della triade: mutual_12/23/31, no_dwl_star_1/2/3, disagreement o pending. |
| 52 | `bargaining_tdl_main.1.group.chat_left_p1` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore che il giocatore 1 ha lasciato/interrotto la chat. |
| 53 | `bargaining_tdl_main.1.group.chat_left_p2` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore che il giocatore 2 ha lasciato/interrotto la chat. |
| 54 | `bargaining_tdl_main.1.group.chat_left_p3` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore che il giocatore 3 ha lasciato/interrotto la chat. |
| 55 | `bargaining_tdl_main.1.group.group_dropped` | entrambi | oTree raw | booleano | aggregated 3090/3090; by-partner 6180/6180 | 0; 1 | Indicatore group-level che la triade è stata interrotta/caduta. |
| 56 | `bargaining_tdl_survey.1.player.gender` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 0=Male; 1=Female; 2=Other | Genere: 0=Male, 1=Female, 2=Other. |
| 57 | `bargaining_tdl_survey.1.player.birth_year` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Anno di nascita (YYYY; intervallo previsto 1924–2008). |
| 58 | `bargaining_tdl_survey.1.player.field_of_study` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1 Education; 2 Arts/humanities; 3 Social sciences; 4 Business/law; 5 Natural sciences; 6 ICT; 7 Engineering; 8 Agriculture; 9 Health; 10 Services; 11 Journalism/information | Campo di studio, codifica ISCED personalizzata riportata nella sezione Codifiche. |
| 59 | `bargaining_tdl_survey.1.player.university_years` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Anni equivalenti full-time di istruzione universitaria/terziaria, 0–20. |
| 60 | `bargaining_tdl_survey.1.player.main_situation` | entrambi | oTree raw | categorico/testo | aggregated 1036/3090; by-partner 2072/6180 | education; housework; paid_work; retired; sick_disabled; unemployed | Situazione principale: paid_work, education, unemployed, sick_disabled, retired o housework. |
| 61 | `bargaining_tdl_survey.1.player.job_type` | entrambi | oTree raw | categorico/testo | aggregated 1036/3090; by-partner 2072/6180 | employee; employer; not_employed; self_employed | Tipo di occupazione: employee, self_employed, employer o not_employed. |
| 62 | `bargaining_tdl_survey.1.player.sd3_mach_01` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “It’s not wise to tell your secrets.” |
| 63 | `bargaining_tdl_survey.1.player.sd3_mach_02` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “I like to use clever manipulation to get my way.” |
| 64 | `bargaining_tdl_survey.1.player.sd3_mach_03` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “Whatever it takes, you must get the important people on your side.” |
| 65 | `bargaining_tdl_survey.1.player.sd3_mach_04` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “Avoid direct conflict with others because they may be useful in the future.” |
| 66 | `bargaining_tdl_survey.1.player.sd3_mach_05` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “It’s wise to keep track of information that you can use against people later.” |
| 67 | `bargaining_tdl_survey.1.player.sd3_mach_06` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “You should wait for the right time to get back at people.” |
| 68 | `bargaining_tdl_survey.1.player.sd3_mach_07` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “There are things you should hide from other people to preserve your reputation.” |
| 69 | `bargaining_tdl_survey.1.player.sd3_mach_08` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “Make sure your plans benefit yourself, not others.” |
| 70 | `bargaining_tdl_survey.1.player.sd3_mach_09` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Machiavellismo, scala di accordo 1–5. Item: “Most people can be manipulated.” |
| 71 | `bargaining_tdl_survey.1.player.sd3_narc_01` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “People see me as a natural leader.” |
| 72 | `bargaining_tdl_survey.1.player.sd3_narc_02` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I hate being the center of attention.” |
| 73 | `bargaining_tdl_survey.1.player.sd3_narc_03` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “Many group activities tend to be dull without me.” |
| 74 | `bargaining_tdl_survey.1.player.sd3_narc_04` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I know that I am special because everyone keeps telling me so.” |
| 75 | `bargaining_tdl_survey.1.player.sd3_narc_05` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I like to get acquainted with important people.” |
| 76 | `bargaining_tdl_survey.1.player.sd3_narc_06` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I feel embarrassed if someone compliments me.” |
| 77 | `bargaining_tdl_survey.1.player.sd3_narc_07` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I have been compared to famous people.” |
| 78 | `bargaining_tdl_survey.1.player.sd3_narc_08` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I am an average person.” |
| 79 | `bargaining_tdl_survey.1.player.sd3_narc_09` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Narcisismo, scala di accordo 1–5. Item: “I insist on getting the respect I deserve.” |
| 80 | `bargaining_tdl_survey.1.player.sd3_psych_01` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “I like to get revenge on authorities.” |
| 81 | `bargaining_tdl_survey.1.player.sd3_psych_02` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “I avoid dangerous situations.” |
| 82 | `bargaining_tdl_survey.1.player.sd3_psych_03` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “Payback needs to be quick and nasty.” |
| 83 | `bargaining_tdl_survey.1.player.sd3_psych_04` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “People often say I’m out of control.” |
| 84 | `bargaining_tdl_survey.1.player.sd3_psych_05` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “It’s true that I can be mean to others.” |
| 85 | `bargaining_tdl_survey.1.player.sd3_psych_06` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “People who mess with me always regret it.” |
| 86 | `bargaining_tdl_survey.1.player.sd3_psych_07` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “I have never gotten into trouble with the law.” |
| 87 | `bargaining_tdl_survey.1.player.sd3_psych_08` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “I enjoy having sex with people I hardly know.” |
| 88 | `bargaining_tdl_survey.1.player.sd3_psych_09` | entrambi | oTree raw | numerico | aggregated 1035/3090; by-partner 2070/6180 | 1=Disagree strongly … 5=Agree strongly | Short Dark Triad — Psicopatia, scala di accordo 1–5. Item: “I’ll say anything to get what I want.” |
| 89 | `bargaining_tdl_survey.1.player.willingness_future` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Disponibilità a rinunciare a un beneficio presente per uno futuro, scala 0–10. |
| 90 | `bargaining_tdl_survey.1.player.willingness_risk` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Disponibilità generale ad assumere rischi, scala 0–10. |
| 91 | `bargaining_tdl_survey.1.player.reciprocity_positive` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Reciprocità positiva auto-riferita, scala 0–10. |
| 92 | `bargaining_tdl_survey.1.player.reciprocity_negative` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Reciprocità negativa/vendetta auto-riferita, scala 0–10. |
| 93 | `bargaining_tdl_survey.1.player.willingness_donate` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Disponibilità a donare senza contropartita, scala 0–10. |
| 94 | `bargaining_tdl_survey.1.player.trust_general` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Fiducia generale nelle buone intenzioni altrui, scala 0–10. |
| 95 | `bargaining_tdl_survey.1.player.beauty_contest_guess` | entrambi | oTree raw | numerico | aggregated 1036/3090; by-partner 2072/6180 | — | Richiesta nel gioco 11–20/beauty contest, da 1.10 a 2.00. |
| 96 | `bargaining_tdl_survey.1.player.instructions_clarity` | entrambi | oTree raw | numerico | aggregated 1034/3090; by-partner 2068/6180 | 1; 2; 3; 4; 5 | Chiarezza percepita delle istruzioni, scala 1–5. |
| 97 | `bargaining_tdl_survey.1.player.general_comment` | entrambi | oTree raw | testo libero | aggregated 1034/3090; by-partner 2068/6180 | — | Commento libero del partecipante sull’esperimento. |
| 98 | `bargaining_tdl_survey.1.player.time_survey_questions` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi nella sezione/pagina survey “survey questions”. |
| 99 | `bargaining_tdl_survey.1.player.time_survey_sd3_mach` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | 1=Disagree strongly … 5=Agree strongly | Secondi trascorsi nella sezione/pagina survey “survey sd3 mach”. |
| 100 | `bargaining_tdl_survey.1.player.time_survey_sd3_narc` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | 1=Disagree strongly … 5=Agree strongly | Secondi trascorsi nella sezione/pagina survey “survey sd3 narc”. |
| 101 | `bargaining_tdl_survey.1.player.time_survey_sd3_psych` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | 1=Disagree strongly … 5=Agree strongly | Secondi trascorsi nella sezione/pagina survey “survey sd3 psych”. |
| 102 | `bargaining_tdl_survey.1.player.time_survey_page4` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi nella sezione/pagina survey “survey page4”. |
| 103 | `bargaining_tdl_survey.1.player.time_survey_page10` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi nella sezione/pagina survey “survey page10”. |
| 104 | `bargaining_tdl_survey.1.player.time_survey_feedback` | entrambi | oTree raw | numero (secondi) | aggregated 3090/3090; by-partner 6180/6180 | — | Secondi trascorsi nella sezione/pagina survey “survey feedback”. |
| 105 | `focal_player_id` | entrambi | derivata dal merge | numerico | aggregated 1082/3090; by-partner 2164/6180 | 1; 2; 3 | ID 1–3 del partecipante focal, derivato da player.id_in_group. |
| 106 | `focal_player_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1082/3090; by-partner 2164/6180 | Yellow; Orange; Purple | Colore del focal player derivato dall’ID. |
| 107 | `decision_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | 1; 2; 3; NoOne | ID del destinatario della decisione finale; NoOne se non supporta nessuno. |
| 108 | `decision_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | NoOne; Orange; Purple; Yellow | Colore del destinatario della decisione; NoOne se applicabile. |
| 109 | `guess_left_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | 1; 2; 3; NoOne | ID del giocatore che, secondo il focal, sarà scelto dal partner sinistro. |
| 110 | `guess_left_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a guess_left_target_id. |
| 111 | `guess_right_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | 1; 2; 3; NoOne | ID del giocatore che, secondo il focal, sarà scelto dal partner destro. |
| 112 | `guess_right_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1045/3090; by-partner 2090/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a guess_right_target_id. |
| 113 | `signal_left_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | 1; 2; 3; NoOne | ID del destinatario implicato nell’intenzione inviata al partner sinistro. |
| 114 | `signal_left_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a signal_left_target_id. |
| 115 | `signal_right_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | 1; 2; 3; NoOne | ID del destinatario implicato nell’intenzione inviata al partner destro. |
| 116 | `signal_right_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a signal_right_target_id. |
| 117 | `received_signal_left_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | 1; 2; 3; NoOne | ID del destinatario implicato nel segnale ricevuto da sinistra. |
| 118 | `received_signal_left_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a received_signal_left_target_id. |
| 119 | `received_signal_right_target_id` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | 1; 2; 3; NoOne | ID del destinatario implicato nel segnale ricevuto da destra. |
| 120 | `received_signal_right_target_color` | entrambi | derivata dal merge | categorico/testo | aggregated 1050/3090; by-partner 2100/6180 | NoOne; Orange; Purple; Yellow | Colore corrispondente a received_signal_right_target_id. |
| 121 | `chat_group_key` | entrambi | derivata dal merge | identificatore/testo | aggregated 3090/3090; by-partner 6180/6180 | — | Chiave derivata session.code\|participant.part1_group_id. |
| 122 | `chat_group_status` | aggregated | derivata dal merge | categorico/testo | aggregated 3090/3090 | matched; no_messages | Stato dell’abbinamento chat nel file participant-level: matched, no_messages o no_group. |
| 123 | `chat_message_count_group` | aggregated | derivata dal merge | numerico | aggregated 3090/3090 | — | Numero totale di messaggi nella triade. |
| 124 | `chat_message_count_sent` | aggregated | derivata dal merge | numerico | aggregated 3090/3090 | — | Numero di messaggi inviati dal focal player nella triade. |
| 125 | `chat_message_count_received` | aggregated | derivata dal merge | numerico | aggregated 3090/3090 | — | Numero di messaggi della triade indirizzati al focal player. |
| 126 | `chat_first_timestamp` | entrambi | derivata dal merge | timestamp Unix | aggregated 1044/3090; by-partner 1768/6180 | — | Timestamp Unix del primo messaggio nell’unità di conversazione. |
| 127 | `chat_last_timestamp` | entrambi | derivata dal merge | timestamp Unix | aggregated 1044/3090; by-partner 1768/6180 | — | Timestamp Unix dell’ultimo messaggio nell’unità di conversazione. |
| 128 | `chat_transcript_group` | aggregated | derivata dal merge | JSON | aggregated 3090/3090 | — | Array JSON ordinato cronologicamente con tutti i messaggi della triade. |
| 129 | `chat_side` | by-partner | derivata dal merge | categorico/testo | by-partner 6180/6180 | left; right | Partner topologico della riga: left o right; non è necessariamente la posizione visualizzata. |
| 130 | `partner_id` | by-partner | derivata dal merge | numerico | by-partner 2164/6180 | 1; 2; 3 | ID 1–3 del partner associato alla riga. |
| 131 | `partner_color` | by-partner | derivata dal merge | categorico/testo | by-partner 2164/6180 | Yellow; Orange; Purple | Colore del partner associato alla riga. |
| 132 | `chat_status` | by-partner | derivata dal merge | categorico/testo | by-partner 6180/6180 | matched; no_messages | Stato dell’abbinamento della chat diadica: matched, no_messages o no_group. |
| 133 | `chat_channel` | by-partner | derivata dal merge | identificatore/testo | by-partner 1768/6180 | — | Nome del canale oTree della diade. |
| 134 | `chat_message_count` | by-partner | derivata dal merge | numerico | by-partner 6180/6180 | — | Numero totale di messaggi nella conversazione tra focal e partner. |
| 135 | `chat_message_count_focal_sent` | by-partner | derivata dal merge | numerico | by-partner 6180/6180 | — | Numero di messaggi della diade inviati dal focal player. |
| 136 | `chat_message_count_partner_sent` | by-partner | derivata dal merge | numerico | by-partner 6180/6180 | — | Numero di messaggi della diade inviati dal partner. |
| 137 | `chat_transcript` | by-partner | derivata dal merge | JSON | by-partner 6180/6180 | — | Array JSON ordinato cronologicamente con tutti i messaggi della diade. |

## 8. Controlli di integrità eseguiti

- Colonne documentate: **137** (unione esatta dei due header).
- Colonne aggregated documentate: **128/128**.
- Colonne by-partner documentate: **132/132**.
- Rapporto righe by-partner/aggregated: **6180/3090 = 2.0**, coerente con due partner per partecipante.
- I conteggi chat e la copertura dei 5.108 messaggi sono già validati dallo script di merge e dall’audit associato.

## 9. Provenienza

- Script di produzione: `merge_otree_chat_selected.py`.
- Audit: `all_apps_wide_2026-08-26_chat_audit_final.json`.
- Sorgenti: `text_analysis/all_apps_wide_2026-08-26.csv` e `text_analysis/ChatMessages-2026-08-26.csv`.

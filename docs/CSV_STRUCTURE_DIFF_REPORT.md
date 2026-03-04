# Report Differenze Strutturali CSV

## Analisi Comparativa: OTREE vs SPERIMENTATORE

**File OTREE:** `all_apps_wide-2025-12-12_OTREE.csv`  
**File SPERIMENTATORE:** `all_apps_wide-2025-12-12_SPERIMENTATORE_NEW.csv`

---

## 📊 Statistiche Generali

- **Colonne OTREE:** 139
- **Colonne SPERIMENTATORE:** 114
- **Colonne comuni:** 112
- **Colonne solo in OTREE:** 27
- **Colonne solo in SPERIMENTATORE:** 2
- **Separatore OTREE:** virgola (`,`)
- **Separatore SPERIMENTATORE:** punto e virgola (`;`)

---

## 🔧 DIFFERENZE STRUTTURALI FONDAMENTALI

### Separatore
- **OTREE:** Usa la virgola (`,`) come separatore standard CSV
- **SPERIMENTATORE:** Usa il punto e virgola (`;`) come separatore
- **Impatto:** Richiede parsing diverso per leggere i file

---

## ❌ COLONNE RIMOSSE (presenti solo in OTREE)

### 1. Colonne MTurk e Metadata Participant (6 colonne)
- `participant._is_bot`
- `participant.label`
- `participant.mturk_worker_id`
- `participant.mturk_assignment_id`
- `session.mturk_HITId`
- `session.mturk_HITGroupId`

**Motivazione:** Colonne relative a MTurk e metadata non necessarie per l'analisi

### 2. Colonne Session Metadata (2 colonne)
- `session.comment`
- `session.label`

**Motivazione:** Metadata di sessione non utilizzati nell'analisi

### 3. Colonne Example Earnings - Intro (9 colonne)
- `bargaining_tdl_intro.1.player.example1_earnings_you`
- `bargaining_tdl_intro.1.player.example1_earnings_left`
- `bargaining_tdl_intro.1.player.example1_earnings_right`
- `bargaining_tdl_intro.1.player.example2_earnings_you`
- `bargaining_tdl_intro.1.player.example2_earnings_left`
- `bargaining_tdl_intro.1.player.example2_earnings_right`
- `bargaining_tdl_intro.1.player.example3_earnings_you`
- `bargaining_tdl_intro.1.player.example3_earnings_left`
- `bargaining_tdl_intro.1.player.example3_earnings_right`

**Motivazione:** Dati degli esempi introduttivi, probabilmente non necessari per l'analisi principale

### 4. Colonne Example Earnings - Part3 (6 colonne)
- `bargaining_tdl_part3.1.player.example1_earnings_you`
- `bargaining_tdl_part3.1.player.example1_earnings_left`
- `bargaining_tdl_part3.1.player.example1_earnings_right`
- `bargaining_tdl_part3.1.player.example2_earnings_you`
- `bargaining_tdl_part3.1.player.example2_earnings_left`
- `bargaining_tdl_part3.1.player.example2_earnings_right`

**Motivazione:** Dati degli esempi di Part3, probabilmente non necessari per l'analisi principale

### 5. Altre Colonne Rimosse (4 colonne)
- `bargaining_tdl_intro.1.player.payoff_determination`
- `bargaining_tdl_part2.1.player.control_question_1`
- `bargaining_tdl_part2.1.player.control_question_2`
- `bargaining_tdl_part2.1.player.role`

**Motivazione:** 
- `payoff_determination`: Testo descrittivo, probabilmente ridondante
- `control_question_1/2`: Risposte alle domande di controllo, non necessarie per analisi principale
- `role` in Part2: Probabilmente ridondante o derivabile da altri campi

**Totale colonne rimosse: 27**

---

## ✅ COLONNE AGGIUNTE (presenti solo in SPERIMENTATORE)

### Colonne Identificazione Player (2 colonne)
- `id.player_on_the_left` (posizione 36)
- `id.player_on_the_right` (posizione 37)

**Motivazione:** Colonne aggiunte per identificare facilmente i player a sinistra e a destra nel gruppo, probabilmente per semplificare l'analisi dei dati

**Totale colonne aggiunte: 2**

---

## ✅ COLONNE MANTENUTE (importante)

### Colonne EL/ER in Part2
**IMPORTANTE:** A differenza di analisi precedenti, le colonne `EL*` e `ER*` sono **PRESENTI in entrambi i file**:
- Tutte le 12 colonne `EL*_switch_value` e `ER*_switch_value` sono presenti
- Tutte le 12 colonne `EL*_choices` e `ER*_choices` sono presenti
- **Nessuna rinominazione** a `mpl_question_N` è stata effettuata

**Colonne EL/ER presenti:**
- `bargaining_tdl_part2.1.player.EL1_switch_value` ... `EL31_switch_value` (6 colonne)
- `bargaining_tdl_part2.1.player.ER1_switch_value` ... `ER31_switch_value` (6 colonne)
- `bargaining_tdl_part2.1.player.EL1_choices` ... `EL31_choices` (6 colonne)
- `bargaining_tdl_part2.1.player.ER1_choices` ... `ER31_choices` (6 colonne)

---

## 🔄 MODIFICHE ALL'ORDINE DELLE COLONNE

### Ordine session.config

**OTREE:**
1. `session.config.participation_fee` (pos 19)
2. `session.config.name` (pos 20)
3. `session.config.control_questions_max_attempts` (pos 21) ✅ *presente in entrambi*
4. `session.config.real_world_currency_per_point` (pos 22)

**SPERIMENTATORE:**
1. `session.config.participation_fee` (pos 11)
2. `session.config.name` (pos 12)
3. `session.config.control_questions_max_attempts` (pos 13) ✅ *presente*
4. `session.config.real_world_currency_per_point` (pos 14)

**Nota:** L'ordine è identico, ma le posizioni assolute sono diverse a causa della rimozione di colonne all'inizio del file.

### Posizione Colonne Aggiunte

Le colonne `id.player_on_the_left` e `id.player_on_the_right` sono state inserite nella sezione `bargaining_tdl_main`, tra:
- `bargaining_tdl_main.1.player.received_history_left` (pos 35)
- `id.player_on_the_right` (pos 36)
- `id.player_on_the_left` (pos 37)
- `bargaining_tdl_main.1.player.received_history_right` (pos 38)

---

## 📋 RIEPILOGO DELLE MODIFICHE

### 1. **Cambio Separatore**
   - **Da:** Virgola (`,`)
   - **A:** Punto e virgola (`;`)
   - **Impatto:** Richiede parsing diverso

### 2. **Rimozione Colonne MTurk e Metadata**
   - 6 colonne rimosse relative a MTurk e metadata participant/session
   - **Impatto:** File più pulito, senza informazioni non necessarie per l'analisi

### 3. **Rimozione Colonne Example Earnings**
   - 15 colonne rimosse (9 da intro + 6 da part3)
   - **Impatto:** File più snello, focus sui dati principali

### 4. **Rimozione Colonne di Controllo e Redondanti**
   - 4 colonne rimosse (payoff_determination, control_question_1/2, role in part2)
   - **Impatto:** Eliminazione di dati ridondanti o non essenziali

### 5. **Aggiunta Colonne Identificazione**
   - 2 colonne aggiunte per identificare player left/right
   - **Impatto:** Facilità nell'analisi dei dati di gruppo

### 6. **Mantenimento Colonne EL/ER**
   - **IMPORTANTE:** Nessuna modifica alle colonne EL/ER
   - **Impatto:** Compatibilità mantenuta con il codice esistente

---

## 🎯 RACCOMANDAZIONI

### Per allineare OTREE al formato SPERIMENTATORE:

1. **Cambiare separatore:**
   - Convertire da virgola (`,`) a punto e virgola (`;`)

2. **Rimuovere colonne:**
   - Tutte le colonne MTurk (`participant.mturk_*`, `session.mturk_*`)
   - Metadata participant (`participant.label`, `participant._is_bot`)
   - Metadata session (`session.comment`, `session.label`)
   - Tutte le colonne `example*_earnings_*` da intro e part3
   - `bargaining_tdl_intro.1.player.payoff_determination`
   - `bargaining_tdl_part2.1.player.control_question_1`
   - `bargaining_tdl_part2.1.player.control_question_2`
   - `bargaining_tdl_part2.1.player.role`

3. **Aggiungere colonne:**
   - `id.player_on_the_left` (dopo `bargaining_tdl_main.1.player.received_history_left`)
   - `id.player_on_the_right` (dopo `id.player_on_the_left`)

### Per allineare SPERIMENTATORE al formato OTREE:

1. **Cambiare separatore:**
   - Convertire da punto e virgola (`;`) a virgola (`,`)

2. **Aggiungere colonne:**
   - Tutte le colonne MTurk e metadata rimosse
   - Tutte le colonne `example*_earnings_*`
   - `bargaining_tdl_intro.1.player.payoff_determination`
   - `bargaining_tdl_part2.1.player.control_question_1`
   - `bargaining_tdl_part2.1.player.control_question_2`
   - `bargaining_tdl_part2.1.player.role`

3. **Rimuovere colonne:**
   - `id.player_on_the_left`
   - `id.player_on_the_right`

---

## ⚠️ NOTE IMPORTANTI

- **Separatore diverso:** Il file SPERIMENTATORE usa `;` invece di `,`. Questo può causare problemi con tool standard che si aspettano CSV con virgola.
- **Colonne EL/ER mantenute:** A differenza di analisi precedenti, le colonne EL/ER sono state **mantenute** in entrambi i file. Questo è positivo per la compatibilità con il codice.
- **File più snello:** Il file SPERIMENTATORE ha 25 colonne in meno, concentrandosi solo sui dati essenziali per l'analisi.
- **Colonne aggiunte utili:** Le colonne `id.player_on_the_left` e `id.player_on_the_right` possono semplificare l'analisi dei dati di gruppo.
- **Ordine colonne:** L'ordine relativo delle colonne `session.config` è identico, ma le posizioni assolute cambiano per la rimozione di colonne all'inizio.

---

## 🔍 CONFRONTO CON ANALISI PRECEDENTE

**Differenze rispetto all'analisi del file `all_apps_wide-2025-12-03_SPERIMENTATORE_NEW.csv`:**

1. **Colonne EL/ER:** Nel file precedente erano state rimosse e sostituite con `mpl_question_N`. In questo nuovo file sono **mantenute**.
2. **Separatore:** Il file precedente usava virgola, questo nuovo file usa punto e virgola.
3. **Colonne rimosse:** Questo file rimuove principalmente colonne di metadata e example earnings, non le colonne EL/ER.
4. **Colonne aggiunte:** Questo file aggiunge solo 2 colonne (`id.player_on_the_*`), non 24 colonne `mpl_question_N`.

**Conclusione:** Questo è un file diverso con una strategia di pulizia diversa, più conservativa rispetto alle colonne EL/ER.

---

*Report aggiornato il: 2025-12-12*

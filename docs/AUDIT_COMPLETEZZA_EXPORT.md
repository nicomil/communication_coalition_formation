# Audit di completezza dell'export e dataset uniti

Documento di riscontro sulla richiesta dello sperimentatore: verificare che nel
dataset del pilota ci sia *tutto* ciò che l'esperimento raccoglie, e costruire i
due dataset uniti scelte + chat.

Dati esaminati: `all_apps_wide_2026-08-18.csv` (162 partecipanti, 194 colonne) e
`ChatMessages-2026-08-18.csv` (311 messaggi).

## 1. Come è stato fatto l'audit

Lo script `scripts/audit_export_completeness.py` non si fida di un confronto a
occhio. Legge i sorgenti delle tre app della sequenza attiva
(`bargaining_tdl_intro`, `bargaining_tdl_main`, `bargaining_tdl_survey`) con
l'analizzatore sintattico di Python, ne estrae **ogni** campo dichiarato nei
modelli `Player`, `Group` e `Subsession`, aggiunge le colonne che oTree genera
da sé e le liste `PARTICIPANT_FIELDS` / `SESSION_FIELDS` di `settings.py`, e
confronta l'inventario risultante con le colonne effettivamente presenti nel
CSV. Individua inoltre le variabili di stato scritte a runtime in
`participant.vars` che non sono dichiarate fra i campi esportabili — cioè
esattamente il tipo di buco che ci interessava.

Si esegue così:

```bash
python scripts/audit_export_completeness.py \
    --wide docs/all_apps_wide_2026-08-18.csv \
    --chat docs/ChatMessages-2026-08-18.csv
```

Restituisce codice di uscita diverso da zero se trova campi mancanti, quindi può
essere usato come controllo prima di ogni sessione.

## 2. Esito

### 2.1 Campi dichiarati e assenti dal CSV

Uno solo: **`participant.part1_group_id`**, l'identificativo della triade.
Era il buco segnalato, ed è stato chiuso (vedi §3).

Tutti gli altri campi dichiarati nei modelli hanno la loro colonna. In
particolare risultano presenti e popolati tutti i campi comportamentali che
servono all'analisi: segnali inviati e ricevuti, scelta finale, belief
elicitation, payoff, i 27 item SD3, le misure di preferenze e i tempi per
pagina.

### 2.2 Variabili scritte a runtime ma non esportabili

Nessuna, al netto di quelle che lo sperimentatore ha indicato di ignorare
(`intro_cq_errors`, `failed_control_questions`, `timeout_excluded`,
`chat_advanced_reason`) e di quelle che sono copie di comodo di colonne già
presenti.

Chiarimento su `chat_advanced_reason`, di cui era stato chiesto il contenuto:
registra il motivo per cui si è chiusa la pagina di chat, con quattro valori
possibili — `normal` (timer scaduto regolarmente), `timeout`, `partners_left`,
`group_dropped`. È diagnostica di sistema e ridondante rispetto a
`group_dropped` e `decision_inactive`, che sono già esportati. Confermato che
non serve.

### 2.3 `part1_payoff` era già presente sotto altro nome

Verificato sul dataset: `participant.vars['part1_payoff']` viene scritto dopo
l'eventuale azzeramento per i non eleggibili, quindi coincide esattamente con
la colonna `bargaining_tdl_main.1.player.payoff` — zero differenze su tutte le
righe. In più il dataset contiene già
`bargaining_tdl_main.1.player.part1_calculated_payoff`, che è il payoff
**prima** dell'azzeramento.

Abbiamo quindi entrambe le grandezze che servono a Efficiency: il payoff
teorico prodotto dal profilo di scelte e quello effettivamente pagato. Nessun
intervento necessario.

### 2.4 Dati che non escono da `all_apps_wide` e vanno scaricati a parte

Non sono buchi, ma export separati da non dimenticare a fine sessione:

| Cosa | Dove | Contenuto |
|---|---|---|
| `TreatmentSlot` | export custom "RCT slots" | 10 campi: slot, blocco, posizione nel blocco, trattamento, stato, codice assegnato, tempi, conteggio sostituzioni |
| `TreatmentAssignment` | export custom "RCT assignments" | 9 campi: tentativo, esito, motivo di risoluzione |
| Messaggi di chat | export `ChatMessages` | il testo delle conversazioni |
| Tempi di pagina | export `PageTimes` | ridondante: i tempi sono già nei campi `time_*` di ciascun player |

Gli ExtraModel non compaiono **mai** in `all_apps_wide`: è un comportamento
strutturale di oTree, non un difetto di configurazione.

### 2.5 Colonne presenti ma completamente vuote

Diciotto colonne non contengono alcun valore. Tre gruppi, con implicazioni
molto diverse:

**a) Innocue.** Le quattro colonne MTurk (lo studio non gira su MTurk),
`session.label`, `session.comment` e i tre `player.role` — oTree emette sempre
quest'ultima colonna anche quando i ruoli non sono definiti, come qui.

**b) Codice morto nell'app intro.** `draft_history_left`, `draft_history_right`,
`signal_left`, `signal_right`, `first_intention_selected` appartengono alle
pagine `ChatAndSignals` e `SimulatedChat`, che **non sono nella
`page_sequence`** dell'app intro. Sono resti di una versione precedente del
disegno: nessun dato perduto, ma vanno tolte dai dataset di analisi per non
generare confusione (i segnali veri sono quelli di `bargaining_tdl_main`).

**c) Gli identificativi Prolific: nessun problema.**
`participant.prolific_study_id` e `participant.prolific_session_id` sono sempre
vuoti, ma sono costanti per sessione e ricostruibili a posteriori. L'unico campo
che conta davvero — il PROLIFIC_PID, che serve a pagare le persone — viene
raccolto correttamente.

La verifica, sulle tre sessioni pilota vere:

| Controllo | Esito |
|---|---|
| Partecipanti che hanno aperto il link (`visited = 1`) | 72 |
| Di questi, con un PROLIFIC_PID valido in `participant.label` | 72 su 72 |
| Visitatori senza PID | 0 |
| Raggruppati con PID | 54 su 54 |
| Arrivati al questionario finale con PID | 53 su 53 |

I 18 partecipanti senza `participant.label` hanno `visited = 0`: sono slot mai
aperti, per i quali non esiste alcun PID da raccogliere. Il link su Prolific
passa quindi già `?participant_label={{%PROLIFIC_PID%}}`, e il meccanismo
funziona con copertura piena.

**Quale colonna usare per i pagamenti.** `participant.label` e
`participant.prolific_id` coincidono in tutti i 72 casi in cui entrambe sono
valorizzate, senza una sola discordanza. Non sono però equivalenti:
`prolific_id` è il campo del modulo nella pagina Welcome e accetta anche testo
digitato a mano, quindi nel dataset compaiono valori come `test` o `shshaga` —
tutti provenienti dalle sessioni di collaudo interne, dove nessuno arrivava da
Prolific e il ripiego manuale ha fatto il suo lavoro. `participant.label` è
invece scritto da oTree a partire dall'URL e non è modificabile dal
partecipante.

Per la riconciliazione dei pagamenti va quindi usato **`participant.label`**,
tenendo `prolific_id` come controprova. Un filtro sul formato (24 caratteri
esadecimali) separa in modo netto i partecipanti reali da quelli di collaudo.

### 2.6 Chat

| Controllo | Esito |
|---|---|
| Messaggi totali | 311 |
| Messaggi riconducibili a un partecipante del dataset | 311 su 311 |
| Canali malformati | 0 |
| Messaggi vuoti | 0 |
| Gruppi con almeno un messaggio | 24 |

## 3. Interventi sul codice

| File | Modifica | Perché |
|---|---|---|
| `settings.py` | `participation_fee` 1.50 → 1.00 | richiesta dello sperimentatore |
| `bargaining_tdl_intro/__init__.py`, `bargaining_tdl_survey/__init__.py` | allineati i valori di ripiego della fee | coerenza se la config non fosse letta |
| `bargaining_tdl_main/__init__.py` | scrive `participant.vars['part1_group_id'] = group.id` alla formazione della triade | prima veniva scritto solo al calcolo dei payoff: i gruppi interrotti a metà restavano senza identificativo |
| `settings.py` | `part1_group_id` aggiunto a `PARTICIPANT_FIELDS` | lo rende una colonna dell'export |
| `requirements.txt` | `otree>=6,<7` → `otree==6.0.15` | senza pin, una reinstallazione delle dipendenze può cambiare versione a metà raccolta |

Nessuna modifica allo schema del database e nessun cambiamento alla logica di
gioco. Regressione verificata con `otree test bargaining_tdl 9` più export:
la colonna compare, le triadi sono corrette, la fee è 1.00.

Il commento `# oTree-may-overwrite-this-file` è stato rimosso da
`requirements.txt`, altrimenti oTree sovrascriverebbe il pin.

### 3.1 Il pin non richiede alcun `resetdb`

La versione in produzione è stata identificata **senza avviare un dyno**, per
impronta dei file statici: fra la 6.0.14 e la 6.0.15 alcuni asset cambiano, e
quelli serviti dall'app corrispondono entrambi alla 6.0.15.

```bash
curl -s https://<app>.herokuapp.com/static/otree/css/table.css | shasum -a 256
curl -s https://<app>.herokuapp.com/static/robots.txt          | shasum -a 256
```

Produzione gira quindi già su **6.0.15**: il pin fissa esattamente ciò che è
installato e non cambia nulla al prossimo deploy.

Due precisazioni, verificate nel sorgente di oTree, che ridimensionano il
rischio paventato in prima battuta:

- il controllo che fa uscire oTree con *"oTree has been updated. Please delete
  your database"* vive in `load_in_memory_db()`, che viene invocata solo quando
  `OTREE_IN_MEMORY` è attiva. Quella variabile viene impostata da oTree stesso
  soltanto per `devserver` e per i test con i bot
  (`otree/main.py:107`). In produzione gira `prodserver1of2` su PostgreSQL,
  quindi **quel blocco non può scattare**: riguarda solo il database SQLite di
  sviluppo;
- fra 6.0.14 e 6.0.15 i moduli che definiscono lo schema — `database.py`,
  `models/`, `models_concrete.py` — sono **byte per byte identici**. Anche se
  la produzione fosse rimasta indietro, il passaggio non comporterebbe alcuna
  migrazione.

In sintesi: nessun `resetdb`, né ora né al deploy.

## 4. I dataset uniti

Lo script `scripts/merge_chat_and_choices.py` unisce i due export e costruisce
le variabili di analisi.

```bash
python scripts/merge_chat_and_choices.py \
    --wide docs/all_apps_wide_2026-08-18.csv \
    --chat docs/ChatMessages-2026-08-18.csv \
    --outdir docs/merged
```

### 4.1 Come vengono ricostruite le triadi

Il punto delicato. `group.id_in_subsession` **non** identifica il gruppo:
`group_by_arrival_time` lascia chi non viene mai raggruppato in un gruppo
residuale, che nel pilota conteneva dodici persone per sessione. Contarlo come
triade produrrebbe gruppi da dodici membri.

La ricostruzione avviene in due passaggi:

1. si tengono i soli partecipanti effettivamente raggruppati, riconoscibili da
   `main.player.treatment` valorizzato — campo scritto solo alla formazione
   della triade, e quindi presente anche nei gruppi che poi si interrompono;
2. su questo sottoinsieme si raggruppa per sessione e `id_in_subsession`, e a
   ciascun gruppo si assegna un identificativo unico preso da
   `part1_group_id` oppure, per i dati raccolti prima della correzione, dal
   prefisso numerico del canale di chat, che contiene lo stesso numero.

Il risultato è un `group_uid` stabile e confrontabile fra sessioni. Sul pilota:
**25 triadi**, di cui 20 valide, e 87 partecipanti mai raggruppati che restano
nel dataset con `group_uid` vuoto — nessuna riga esclusa, come richiesto.

Per la direzione dei messaggi il mittente si legge da `participant_code`, che è
un dato esatto. Il campo `nickname` (`LeftPartner` / `RightPartner`) non viene
usato: è relativo a chi legge, non a chi scrive, e lo stesso messaggio porta
etichette diverse per i due interlocutori.

### 4.2 File prodotti

| File | Unità di osservazione | Righe (pilota) |
|---|---|---|
| `..._messages_long.csv` | il singolo messaggio | 311 |
| `..._chat_by_partner.csv` | coppia ordinata i→j, sei per triade | 237 (25×6 + 87) |
| `..._chat_aggregated.csv` | il partecipante | 162 |

Le colonne MTurk sono rimosse da tutti e tre.

`messages_long` è il file da dare in pasto alla pipeline NLP: porta testo,
mittente, destinatario, gruppo, trattamento e indici progressivi di
conversazione, ed è l'unità su cui girano TopicGPT e le misure testuali prima
di essere aggregate a diade e a gruppo.

### 4.3 Variabili costruite

**Nel file per coppia ordinata i→j**

| Variabile | Definizione |
|---|---|
| `signal_ij` | segnale finale inviato da i a j (`split_you` / `split_other` / `support_none`) |
| `signal_ij_declared_target_id` | chi il segnale dichiara di voler sostenere |
| `S_ij` | 1 se i ha inviato a j "I intend to support you" |
| `A_ji` | 1 se j ha effettivamente scelto di sostenere i |
| `persuasion_ij` | `S_ij × A_ji` |
| `C_ij` | 1 se l'azione dichiarata a j coincide con la scelta finale di i |
| `dyad_*`, `sent_*`, `recv_*` | numero di messaggi, parole, caratteri, primo e ultimo istante, durata — per la coppia, per i soli messaggi inviati da i, per quelli ricevuti |
| `dyad_transcript_text` | trascrizione leggibile della coppia |
| `sent_transcript_text` | solo i turni di i verso j, cioè l'unità direzionale rilevante per la persuasione |

**Nel file per partecipante**

| Variabile | Definizione |
|---|---|
| `strategic_deception` | 1 se i promette sostegno a entrambi e poi sceglie `NoOne` |
| `cc_i` | media di `C_ij` e `C_ik`; vale 1, 0.5 o 0 |
| `n_partners_persuaded` | quanti dei due partner ha persuaso |
| `n_partners_supporting_me` | quanti lo hanno sostenuto, a prescindere dal segnale |
| `group_total_payoff`, `group_mean_payoff` | base per Efficiency |
| `chat_group_*`, `chat_sent_*`, `chat_recv_*` | volume di conversazione a livello di gruppo, inviato e ricevuto |
| `group_transcript_text` | conversazione dell'intera triade |

**Flag di validità, presenti in entrambi i file**

| Variabile | Definizione |
|---|---|
| `focal_timeout_flag` | 1 se il singolo ha fatto scadere un timer o è stato escluso per inattività |
| `group_dropped_flag` | 1 se la triade si è interrotta |
| `group_any_timeout` | 1 se almeno un membro ha il flag di timeout |
| `group_complete` | 1 se la triade ha tutti e tre i membri |
| `group_valid` | 1 solo se completa, non interrotta e senza timeout |

Come stabilito, le analisi principali girano su `group_valid == 1`; il campione
completo resta disponibile per i controlli di robustezza.

## 5. Verifica dei risultati

I test in `scripts/test_merge_chat_and_choices.py` (`python
scripts/test_merge_chat_and_choices.py`, 13 test) girano su dati sintetici e
non richiedono database.

Il controllo più stringente è una proprietà, non un esempio: per **tutti i 27
profili di scelta possibili**, in entrambe le regole di payoff, le variabili
costruite dal merge devono risultare coerenti con la funzione di payoff del
gioco (`bargaining_tdl_common/utils.py`). Se la mappatura fra `decision_choice`
— che è relativa alla topologia circolare — e i giocatori assoluti fosse
sbagliata anche solo per una rotazione, il test fallirebbe.

Sui dati reali del pilota lo stesso confronto è stato ripetuto a posteriori:
per **24 triadi su 24** con profilo di scelte completo, i payoff e l'etichetta
di esito ricalcolati dal profilo coincidono con quelli esportati da oTree. La
venticinquesima è un gruppo interrotto senza scelta finale.

Altri riscontri sui dati reali:

- `A_ji` coerente con la scelta del partner in tutte le 150 coppie ordinate;
- `cc_i` pari alla media delle due `C_ij` per tutti i 74 partecipanti con
  entrambe definite;
- somma dei messaggi inviati dai tre membri uguale al totale del gruppo, per
  tutte le 25 triadi, e 311 messaggi su 311 conservati.

Distribuzioni ottenute sul pilota, utili come ordine di grandezza (campione
troppo piccolo per qualunque inferenza):

- `persuasion_ij` = 1 in 47 coppie ordinate su 150;
- `cc_i`: 45 partecipanti a 1, 16 a 0.5, 13 a 0;
- `strategic_deception` = 1 in 3 casi su 74.

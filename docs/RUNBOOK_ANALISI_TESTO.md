# Runbook: dall'export di oTree ai dati per Stata

Procedura completa per trasformare i dati grezzi di una sessione nei due
dataset di analisi arricchiti con topic e misure del linguaggio. Ogni passo è
un comando; nessuno richiede di modificare file.

Chi vuole capire *come* sono costruite le misure trova la spiegazione in
`@docs/PIPELINE_NLP.md`; questo documento dice solo cosa digitare e in che
ordine.

---

## Passo 0 — Preparare l'ambiente (una volta sola)

Dalla cartella del progetto:

```bash
pip install -r scripts/nlp/requirements.txt
```

Solo se servono i topic, va anche clonato il repository di TopicGPT. I file di
prompt fanno parte del metodo e non sono dentro il pacchetto pubblicato, quindi
il repository serve comunque:

```bash
git clone https://github.com/chtmp223/topicGPT.git ~/src/topicGPT
pip install ~/src/topicGPT
```

Per configurare le chiavi API, una volta sola: vedi `@docs/CHIAVI_API.md`.

---

## Passo 1 — Scaricare gli export da oTree

Dall'interfaccia di amministrazione, sezione **Data**, servono due file:

| Export | Nome tipico |
|---|---|
| All apps — wide | `all_apps_wide_<data>.csv` |
| Chat messages | `ChatMessages_<data>.csv` |

Vanno scaricati anche i due export custom della randomizzazione (**RCT slots** e
**RCT assignments**): non servono a questa procedura, ma non sono ricostruibili
a posteriori e vanno conservati insieme agli altri.

Metti i due file in una cartella qualsiasi; negli esempi che seguono sono in
`docs/`.

---

## Passo 2 — Unire scelte e chat

```bash
python scripts/merge_chat_and_choices.py \
    --wide docs/all_apps_wide_2026-08-18.csv \
    --chat docs/ChatMessages-2026-08-18.csv \
    --outdir docs/merged
```

Produce tre file in `docs/merged/`, il cui prefisso è il nome del file wide:

- `..._messages_long.csv` — un messaggio per riga
- `..._chat_by_partner.csv` — una riga per coppia ordinata i→j
- `..._chat_aggregated.csv` — una riga per partecipante

Qui sono già costruite le variabili dell'esperimento: persuasione, coerenza
segnale-scelta, inganno strategico, payoff di gruppo e i flag di validità delle
triadi.

**Cosa controllare nel riepilogo a schermo.** Il comando stampa quanti
partecipanti ha letto, quante triadi ha ricostruito e quanti messaggi ha
risolto. I messaggi risolti devono essere **tutti** quelli in input: se il
numero è inferiore, in coda compaiono le righe di avviso che spiegano quali non
sono stati ricondotti a un partecipante.

---

## Passo 3 — Analisi del testo

Il prefisso da passare a `--stem` è il nome del file wide senza estensione.

### Solo misure automatiche — nessuna chiave necessaria

```bash
python scripts/run_nlp_pipeline.py \
    --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18
```

Calcola volume, sentiment, pensiero analitico, Clout, Authenticity e tono
emotivo ai quattro livelli di aggregazione. Richiede pochi secondi.

### Aggiungendo la rubrica di validazione

```bash
python scripts/run_nlp_pipeline.py \
    --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18 \
    --llm --llm-replicates 2
```

Serve una chiave, indifferentemente OpenAI o Anthropic: la pipeline sceglie da
sola in base a quello che trova e lo dichiara a schermo. `--llm-replicates 2`
fa valutare ogni testo due volte, così la dispersione fra le due valutazioni
finisce nel dataset come stima dell'errore di misura.

### Aggiungendo i topic

```bash
python scripts/run_nlp_pipeline.py \
    --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18 \
    --topics --topicgpt-repo ~/src/topicGPT
```

### Tutto insieme

```bash
python scripts/run_nlp_pipeline.py \
    --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18 \
    --llm --llm-replicates 2 \
    --topics --topicgpt-repo ~/src/topicGPT
```

---

## Passo 4 — Cosa portare in Stata

In `docs/merged/nlp/`:

| File | Unità di osservazione |
|---|---|
| `..._chat_by_partner_nlp.csv` | coppia ordinata i→j, sei per triade |
| `..._chat_aggregated_nlp.csv` | il partecipante |

Sono i due file del passo 2 con in più le colonne del testo. Le misure hanno un
prefisso che dice a quale conversazione si riferiscono:

- `nlp_sent_*` — i messaggi che il soggetto ha **inviato** (nel file per coppia:
  a quel partner; nel file per partecipante: a tutto il gruppo)
- `nlp_recv_*` — quelli **ricevuti**
- `nlp_dyad_*` — l'intera conversazione della coppia
- `nlp_group_*` — l'intera conversazione della triade

La distinzione fra inviato e ricevuto non è cosmetica: nella persuasione conta
il linguaggio di chi parla, quindi le regressioni sulla persuasione vanno fatte
sulle colonne `nlp_sent_*`.

Gli altri file in quella cartella (`..._messages_nlp.csv`,
`..._features_<livello>.csv`) servono ai controlli e alle analisi a livelli
diversi; non servono per Stata.

---

## Prima di analizzare: tre filtri

**`group_valid == 1`** — esclude le triadi interrotte e quelle in cui almeno un
membro ha fatto scadere un timer, come stabilito. Il campione completo resta
disponibile per i controlli di robustezza. La colonna si chiama così in
entrambi i file.

**`low_language_flag == 0`** — esclude il testo che non è lingua. Serve perché
le stringhe di tastiera risultano paradossalmente *massimamente analitiche*:
quell'indice sottrae le parole funzionali, e un testo che non ne contiene non
subisce alcuna sottrazione. Sul pilota i gruppi di sole stringhe di prova
avevano punteggio mediano 93 contro 43 dei gruppi veri.

Attenzione: il flag ha il prefisso del blocco a cui si riferisce, quindi va
usato quello coerente con le misure che si stanno analizzando —
`nlp_sent_low_language_flag` per le misure di chi invia,
`nlp_dyad_low_language_flag` per la coppia, `nlp_group_low_language_flag` per
la triade. Su unità molto corte la soglia non scatta, quindi al livello diadico
va letto insieme a `nlp_sent_wc`.

**`nlp_sent_wc > 0`** (o il `wc` del blocco che stai usando) — le unità senza
testo hanno gli indici vuoti per costruzione, non a zero: senza questo filtro
finirebbero nelle medie come valori mancanti anziché come assenza di
conversazione.

---

## Se qualcosa non torna

**«File mancante: ..._messages_long.csv»** — il passo 2 non è stato eseguito, o
`--stem` non corrisponde al nome dei file. Il prefisso è quello del file wide
senza estensione.

**«Manca la chiave OPENAI_API_KEY»** — vedi `@docs/CHIAVI_API.md`. Con
`--topicgpt-api ollama` i topic girano in locale senza alcuna chiave.

**«Il pacchetto topicgpt_python non è installato»** — passo 0, seconda parte.

**Voglio vedere cosa verrebbe inviato, senza spendere.** `--llm-dry-run` mostra
la richiesta della rubrica; `--topicgpt-dry-run` scrive solo il file di input
di TopicGPT. Nessuno dei due contatta alcun servizio.

**Voglio controllare che le chiavi funzionino.**
`python scripts/setup_api_keys.py --check`

---

## Verifica della procedura

```bash
python scripts/test_merge_chat_and_choices.py
python scripts/test_nlp_pipeline.py
```

Girano senza rete e senza credenziali. Se entrambi finiscono con `OK`, gli
strumenti sono a posto e un eventuale problema sta nei dati in ingresso.

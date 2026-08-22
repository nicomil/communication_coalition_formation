# Pipeline NLP: topic e misure testuali

Estrae dalle chat dell'esperimento i topic (TopicGPT) e le misure di linguaggio
richieste — volume, tono emotivo, sentiment, pensiero analitico, Clout,
Authenticity — a livello di **coppia** e di **gruppo**, e le innesta sui
dataset delle scelte, pronte per Stata.

Tutto il codice sta in `scripts/nlp/`; il punto di ingresso è
`scripts/run_nlp_pipeline.py`.

## 1. Tre stadi indipendenti

| Stadio | Opzione | Serve una credenziale? | Stato |
|---|---|---|---|
| Misure testuali deterministiche | (sempre attivo) | no | eseguito sul pilota |
| Rubrica valutata da Claude | `--llm` | sì, Anthropic | pronto, non ancora eseguito |
| TopicGPT | `--topics` | sì, del backend scelto | pronto, non ancora eseguito |

Lo stadio 1 gira con la sola libreria standard di Python. Gli altri due sono
scritti, testati sulle parti che non toccano la rete, e attendono solo le chiavi
API: l'obiettivo posto dallo sperimentatore — «preparare tutto il codice in modo
da testarlo ora e sul dataset finale» — è quindi soddisfatto.

```bash
# Stadio 1, subito eseguibile
python scripts/run_nlp_pipeline.py \
    --merged-dir docs/merged --stem all_apps_wide_2026-08-18

# Con la rubrica LLM (due valutazioni indipendenti per unità)
python scripts/run_nlp_pipeline.py --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18 --llm --llm-replicates 2

# Con i topic
python scripts/run_nlp_pipeline.py --merged-dir docs/merged \
    --stem all_apps_wide_2026-08-18 \
    --topics --topicgpt-repo ~/src/topicGPT --topicgpt-model gpt-4o
```

Entrambi gli stadi a pagamento hanno una modalità di ispezione a costo zero
(`--llm-dry-run`, `--topicgpt-dry-run`) che mostra esattamente cosa verrebbe
inviato.

## 2. Le misure in stile LIWC-22, senza LIWC-22

Il punto che rende la cosa possibile: **Analytic, Clout e Authenticity non
dipendono da dizionari di contenuto proprietari**. Si reggono sulle *function
words* — articoli, preposizioni, pronomi, ausiliari, congiunzioni, negazioni —
che in inglese sono classi chiuse e di dominio pubblico. Quello che LIWC vende è
il software e la taratura, non la lingua inglese.

Va però detto con precisione cosa è replica e cosa è approssimazione.

**Analytic è una replica.** Il Categorical-Dynamic Index è pubblicato per esteso
in Pennebaker, Chung, Frazee, Lavergne & Beaver (2014), *PLOS ONE*:

```
CDI = 30 + article + prep − ppron − ipron − auxverb − conj − adverb − negate
```

con ogni termine in percentuale sul totale delle parole. È implementato alla
lettera in `scripts/nlp/text_metrics.py` e verificato da un test che ne ricalcola
il valore a mano.

**Clout e Authenticity sono indici in stile LIWC, non punteggi LIWC.** I
costrutti sono pubblicati — Clout su Kacewicz, Pennebaker, Davis, Jeon &
Graesser (2014), Authenticity sull'indice di menzogna di Newman, Pennebaker,
Berry & Richards (2003) — ma i pesi esatti di LIWC-22 non lo sono. Qui sono
composti a pesi uguali, con i segni presi dalla letteratura:

- Clout ↑ con `we`, `you` e riferimenti sociali; ↓ con `I`, negazioni, volgarità;
- Authenticity ↑ con `I` e parole di differenziazione (*but*, *except*, *without*);
  ↓ con emozione negativa e verbi di movimento.

Nel dataset sono nominati `clout_raw` / `clout_z` / `clout_100`, mai `LIWC
Clout`. Nella pre-registrazione, che è rimasta generica, vanno dichiarati come
*LIWC-style measures computed from published formulas*.

**La validazione convergente.** Lo stadio 2 fa valutare le stesse trascrizioni a
Claude con una rubrica esplicita (`scripts/nlp/llm_rubric.py`), su scala 0-100
per gli stessi quattro costrutti. Le due strade sono metodologicamente
indipendenti — una conta function words, l'altra legge il testo — quindi la
correlazione fra `clout_100` e `llm_clout` è un'evidenza di validità
convergente. Se le due misure divergono, va riportato: è un risultato, non un
guasto.

Con `--llm-replicates 2` ogni trascrizione è valutata più volte in chiamate
indipendenti, e la dispersione fra repliche finisce nel dataset come
`llm_*_sd`: una stima esplicita dell'errore di misura, che una singola chiamata
non offrirebbe.

**Sentiment.** VADER, open source e validato, è la misura principale
(`sentiment_compound`). Se la libreria non è installata il codice ripiega su
conteggi da dizionario e lo dichiara nella colonna `sentiment_backend`, così la
provenienza resta tracciata riga per riga.

## 3. Due decisioni metodologiche che cambiano i numeri

**Gli indici si calcolano sui conteggi sommati, non come media di percentuali
per messaggio.** I turni di chat sono cortissimi. Una percentuale calcolata su
cinque parole assume pochi valori distinti ed è dominata dal rumore, e la media
di quelle percentuali non è la percentuale del testo complessivo. La pipeline
quindi estrae *conteggi* a livello di messaggio e calcola gli *indici* solo
sull'unità di analisi vera. Un test verifica che il CDI di un gruppo coincida
con quello del testo unito dei suoi messaggi.

**Il tono emotivo usa la differenza fra percentuali, non il rapporto interno
alle parole emotive.** La formulazione a rapporto — `(pos − neg) / (pos + neg)`
— salta a ±100 non appena il testo contiene una sola parola emotiva, cosa che su
messaggi di chat accade quasi sempre. Nella prima versione il valore mediano di
gruppo era esattamente 100: degenerazione, non segnale. La misura usata è
`pct_posemo − pct_negemo`, che resta graduata; il rapporto resta disponibile
come `tone_balance`, da leggere solo dove `has_emotion_words` vale 1.

**Il testo che non è lingua va riconosciuto, non creduto.** L'esecuzione sul
pilota ha fatto emergere un artefatto che vale la pena conoscere: le stringhe di
tastiera digitate durante i test interni (`shshahah`) risultano *massimamente*
analitiche. La ragione è meccanica — il CDI parte da 30 e sottrae le percentuali
di function words; un testo che non contiene articoli, pronomi né ausiliari non
subisce alcuna sottrazione. Sul pilota i gruppi di sole stringhe di prova
avevano `analytic_100` mediano 93, contro 43 dei gruppi con conversazione vera.

La pipeline calcola quindi `pct_funcwords` (densità di function words: intorno
al 40-60% nell'inglese conversazionale, zero nel rumore da tastiera) e alza
`low_language_flag` sotto il 15% con almeno cinque parole. È un indicatore da
usare come filtro in analisi, non un'esclusione automatica. Attenzione al
livello: su unità molto corte — molte coppie ordinate lo sono — la soglia di
cinque parole non scatta, quindi al livello diadico il flag va letto insieme a
`wc`.

**La standardizzazione è sul campione.** LIWC restituisce le misure su scala
0-100 perché le standardizza su un corpus di riferimento proprietario. Qui la
standardizzazione avviene sul campione in analisi: i valori sono confrontabili
*fra unità dello stesso studio* — cioè fra trattamenti, che è l'uso previsto —
ma non con punteggi LIWC pubblicati altrove.

## 4. TopicGPT

Lo sperimentatore ha chiesto di usare rigorosamente il codice del paper.
`scripts/nlp/topicgpt_runner.py` **non riscrive l'algoritmo**: prepara l'input
nel formato atteso, invoca le funzioni ufficiali nell'ordine previsto —
generazione dei topic di primo livello, raffinamento, assegnazione, correzione —
e ricompone l'output sulle chiavi dell'esperimento.

**Installare dal repository, non da PyPI.** Due ragioni concrete: i file di
prompt (`prompt/generation_1.txt`, `seed_1.md`, …) fanno parte del metodo e
**non sono dentro il pacchetto pubblicato**; e la release 0.2.7 su PyPI importa
vLLM al primo livello, dipendenza che su macOS senza GPU non si installa, mentre
il ramo `main` l'ha già resa un extra opzionale.

```bash
git clone https://github.com/chtmp223/topicGPT.git
pip install ./topicGPT          # senza l'extra [vllm]
```

**Unità di analisi.** Un turno di chat di poche parole non è un documento. Il
default è la **coppia ordinata** — tutto ciò che i ha scritto a j — che è anche
l'unità in cui si gioca la persuasione. I topic ottenuti si aggregano poi a
partecipante e a gruppo prendendo l'unione dei topic delle unità componenti,
così le domande «i topic differiscono fra trattamenti?» hanno una risposta a
entrambi i livelli richiesti.

**Backend.** TopicGPT parla con OpenAI, Azure, Vertex, Gemini, Ollama o vLLM. Il
paper usa OpenAI ed è la scelta più fedele; serve una `OPENAI_API_KEY`. Per
usare Claude ci sono due strade che non richiedono di modificare il codice degli
autori: il backend `vertex`, che nel repository costruisce un client
`AnthropicVertex`, oppure il backend `openai` puntato a un gateway compatibile
con `OPENAI_BASE_URL`.

## 5. Cosa esce

Tutto sotto `docs/merged/nlp/`.

**I due dataset finali**, cioè quelli del merge arricchiti:

- `..._chat_by_partner_nlp.csv` — una riga per coppia ordinata, con tre blocchi
  di misure: `nlp_sent_*` (i messaggi che il focale ha mandato al partner),
  `nlp_recv_*` (quelli ricevuti), `nlp_dyad_*` (l'intera conversazione della
  coppia). La distinzione conta: nella persuasione è chi parla che agisce.
- `..._chat_aggregated_nlp.csv` — una riga per partecipante, con `nlp_sent_*`
  (tutto ciò che ha scritto nel gruppo) e `nlp_group_*` (la conversazione della
  triade).

**File intermedi**, per i controlli e per l'analisi a livelli diversi:
`..._messages_nlp.csv` (un messaggio per riga) e `..._features_<livello>.csv`
per i quattro livelli di aggregazione.

Colonne principali per ogni blocco: `n_messages`, `wc`,
`mean_words_per_message`, `type_token_ratio`, `duration_seconds`,
`median_gap_seconds`, `analytic_cdi` / `analytic_z` / `analytic_100`, e le
analoghe terne per `clout`, `authenticity`, `tone`, più
`sentiment_compound_mean` e le percentuali di categoria (`pct_i`, `pct_we`,
`pct_you`, `pct_negate`, `pct_posemo`, `pct_negemo`, `pct_commitment`,
`pct_exclusive`, `pct_social`). Con gli stadi 2 e 3 attivi si aggiungono
`llm_analytic`, `llm_clout`, `llm_authenticity`, `llm_tone` con i rispettivi
`_sd`, i due flag `llm_contains_support_commitment` /
`llm_contains_support_request`, e `nlp_*_topics` / `nlp_*_topic_primary` /
`nlp_*_n_topics`.

## 6. Esecuzione sul pilota

Stadio 1 eseguito su tutti i 311 messaggi:

| Livello | Unità |
|---|---|
| coppia ordinata (i→j) | 118 |
| coppia | 66 |
| partecipante nel gruppo | 66 |
| gruppo | 24 |

Controlli di conservazione: 1.952 parole e 311 messaggi si ritrovano identici a
tutti e quattro i livelli. Le distribuzioni non sono degeneri — per esempio a
livello di gruppo `analytic_cdi` va da −30 a +49 con 21 valori distinti su 24
unità — e gli z-score hanno media 0 e deviazione 1 per costruzione.

**Sul contenuto del pilota**: 241 messaggi su 311 contengono linguaggio inglese
riconoscibile, distribuiti su 20 gruppi; il resto sono stringhe di prova
digitate durante i test interni. C'è quindi materiale reale e strategico — «*If
you want to do that, we can support each other. Unfortunately one person must be
left out…*» — abbastanza per verificare che la pipeline funzioni end-to-end, non
abbastanza per un'ontologia di topic stabile. È esattamente lo scopo previsto:
rodare ora, produrre risultati sul dataset finale.

## 7. Costi e volumi

Sul pilota la rubrica LLM richiede 118 chiamate a livello di coppia ordinata e
24 a livello di gruppo: costo trascurabile. Sul dataset finale (~1.557
partecipanti, ~519 triadi) le coppie ordinate saranno circa 3.100 e i gruppi
519; con due repliche si arriva intorno a 7.200 chiamate su testi brevi.

Due accorgimenti già implementati tengono basso il conto: il prompt di sistema,
identico per ogni chiamata, è marcato per la cache, e `--llm-batch` usa la
Batches API a metà prezzo (esito asincrono, id del batch da conservare).

## 8. Test

`python scripts/test_nlp_pipeline.py` — 40 test, senza rete né credenziali.
Coprono la tokenizzazione delle forme contratte, l'euristica sugli avverbi in
*-ly*, la formula del CDI ricalcolata a mano, la direzione attesa dei compositi,
la standardizzazione, la conservazione di parole e messaggi attraverso i livelli
di aggregazione, l'asimmetria delle coppie ordinate, l'innesto sui dataset, il
parsing del formato di risposta di TopicGPT, l'aggregazione dei topic, e la
sintesi dei giudizi della rubrica con repliche e con errori.

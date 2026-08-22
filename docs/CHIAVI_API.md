# Configurare le chiavi API

La pipeline di analisi del testo usa due servizi esterni. Questa guida spiega
come inserire le chiavi una volta sola. Funziona identica su macOS, Windows e
Linux, e non richiede di modificare impostazioni di sistema.

| Chiave | A cosa serve | Obbligatoria? |
|---|---|---|
| `OPENAI_API_KEY` | TopicGPT **e**, se vuoi, la rubrica di validazione | Solo per estrarre i topic con OpenAI |
| `ANTHROPIC_API_KEY` | La rubrica di validazione, in alternativa a OpenAI | **No, facoltativa** |

Le misure testuali di base — volume, sentiment, pensiero analitico, Clout,
Authenticity — **non richiedono alcuna chiave** e girano già così com'è.

**Una sola chiave basta.** La rubrica di validazione non è legata a un
fornitore: se hai già `OPENAI_API_KEY` per TopicGPT, quella stessa chiave copre
anche la rubrica e non serve altro. La pipeline sceglie da sola il fornitore in
base a ciò che trova, e lo dichiara a schermo prima di partire:

```
Rubrica LLM...
  fornitore: OpenAI
```

Per forzare una scelta diversa: `--llm-provider openai|anthropic|ollama`.

## La procedura

Dalla cartella del progetto, un solo comando:

```bash
python scripts/setup_api_keys.py
```

Il programma chiede le chiavi una per una. Mentre le incolli il testo **non
compare a schermo**: è normale, non è il terminale bloccato. Premi invio dopo
ognuna; invio a vuoto salta quella chiave e lascia invariata quella già
presente.

Al termine lo script fa tre cose da solo:

1. salva le chiavi in `.secrets.env` nella cartella del progetto;
2. verifica che git stia davvero ignorando quel file, e se non lo fa si offre
   di sistemare `.gitignore` prima di scrivere qualsiasi cosa;
3. contatta i due servizi per confermare che le chiavi funzionino davvero,
   così un errore di copia-incolla salta fuori subito e non tre giorni dopo.

Esempio di esito corretto:

```
Salvato in /.../.secrets.env
Permessi ristretti al solo proprietario (600).

Verifica delle chiavi:
  OK   OpenAI: chiave valida, 87 modelli disponibili
  OK   Anthropic: chiave valida, 12 modelli disponibili
```

Se una chiave è sbagliata, lo dice senza ambiguità:

```
  FAIL OpenAI: chiave rifiutata (HTTP 401)
```

Fatto questo, non serve altro: la pipeline carica le chiavi da sola a ogni
esecuzione.

## Comandi di controllo

```bash
python scripts/setup_api_keys.py --status   # cosa è configurato, senza toccare nulla
python scripts/setup_api_keys.py --check    # ricontrolla che le chiavi funzionino
```

`--status` non stampa mai le chiavi, solo se ci sono.

## Se qualcosa non torna

**«Manca la chiave OPENAI_API_KEY».** Le chiavi non sono state ancora
configurate, oppure il comando è stato lanciato da una cartella diversa da
quella del progetto. Esegui `python scripts/setup_api_keys.py --status` per
vedere dove il programma sta cercando il file.

**Preferisci gestire le chiavi per conto tuo.** Una variabile d'ambiente già
impostata ha sempre la precedenza sul file: chi ha già un proprio metodo non
viene scavalcato.

**Vuoi togliere le chiavi.** Cancella `.secrets.env`. Non c'è nient'altro da
ripulire, perché nessuna impostazione di sistema viene toccata.

## Due avvertenze

**Il file `.secrets.env` non va mai messo sotto controllo di versione.** Il
repository di questo progetto è pubblico. Lo script lo verifica prima di
scrivere e si rifiuta di procedere se `.gitignore` non lo copre, ma vale la pena
saperlo: non aggiungerlo mai a mano a un commit, e non incollare le chiavi in
chat o via email.

**Il costo.** TopicGPT interroga il modello una volta per documento, in due
fasi. Sul dataset finale sono circa 3.100 documenti, quindi nell'ordine delle
6.500 chiamate su testi brevi. Sono cifre contenute, ma non nulle: conviene
impostare un tetto di spesa sul cruscotto di OpenAI prima di lanciare.

## Una alternativa gratuita, se serve

TopicGPT non richiede per forza un servizio a pagamento: accetta anche modelli
eseguiti in locale, che non usano alcuna chiave.

```bash
ollama pull llama3
python scripts/run_nlp_pipeline.py --merged-dir docs/merged --stem <nome> \
    --topics --topicgpt-api ollama --topicgpt-model llama3 \
    --topicgpt-repo ~/src/topicGPT
```

Va detto il rovescio della medaglia: TopicGPT vive della qualità delle etichette
che il modello produce, e il paper usa GPT-4. Con un modello locale di piccola
taglia la pipeline gira lo stesso, ma i topic risultano più poveri e meno
stabili. È la strada giusta per un collaudo, non per i risultati da pubblicare.

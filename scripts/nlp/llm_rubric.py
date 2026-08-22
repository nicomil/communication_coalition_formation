"""
Seconda misura, indipendente, dei costrutti in stile LIWC: una rubrica valutata
da Claude.

Serve a validare le misure dizionario-based di `text_metrics`. Le due strade
sono metodologicamente diverse — una conta function words, l'altra legge il
testo — quindi una correlazione alta fra loro è un'evidenza di validità
convergente; una correlazione bassa è un segnale da riportare, non da
nascondere.

Perché si valuta il testo aggregato e non il singolo messaggio
--------------------------------------------------------------
Vale lo stesso argomento delle misure automatiche: un turno di chat di cinque
parole non contiene abbastanza segnale per una scala 0-100. La rubrica gira
quindi sulle trascrizioni già aggregate — coppia ordinata, coppia, gruppo — che
sono anche le unità richieste dall'analisi.

Affidabilità
------------
Con `--replicates 2` la stessa trascrizione viene valutata più volte in
chiamate indipendenti: la dispersione fra repliche è la stima test-retest
dell'errore di misura, e finisce nel dataset come `*_sd`. Si possono anche
indicare più modelli giudici (`--judges`), ottenendo un accordo fra valutatori
diversi anziché fra repliche dello stesso.

Costo
-----
Per grandi volumi conviene `--batch`, che usa la Batches API a metà prezzo. Sul
pilota (25 gruppi, 311 messaggi) le chiamate sono poche centinaia e la modalità
sincrona basta.
"""

from __future__ import annotations

import functools
import json
import os
import statistics
import time
from dataclasses import dataclass

DEFAULT_MODEL = 'claude-opus-5'

SYSTEM_PROMPT = """You are a research assistant coding transcripts for a \
behavioural economics experiment. Three participants play a coalition-formation \
game and exchange short private chat messages before deciding whom to support.

You rate a transcript on four constructs, each on a 0-100 scale. Use the full \
range: 50 is the midpoint for an unremarkable transcript of this kind, not a \
default answer. Rate only what the text shows; never infer from what you \
imagine happened outside the transcript.

ANALYTICAL THINKING (analytic)
Formal, logical, hierarchical reasoning versus narrative, here-and-now, \
informal language. High: reasoning about payoffs, conditions, consequences, \
structured argument. Low: greetings, reactions, unstructured chatter.

CLOUT (clout)
The confidence and social status the writer projects. High: speaks with \
authority, focuses on the other person and on the group, makes offers and \
proposals, appears to lead the exchange. Low: tentative, self-focused, \
anxious, deferential, hedging.

AUTHENTICITY (authenticity)
How spontaneous and personally honest the language reads. High: unguarded, \
self-disclosing, admits uncertainty or self-interest openly. Low: guarded, \
strategic, distanced, impression-managing, evasive.

EMOTIONAL TONE (tone)
Emotional valence. Above 50: positive, warm, friendly. Below 50: negative, \
hostile, anxious. Exactly 50: neutral or no emotional content.

Also record whether the transcript contains an explicit commitment to support \
someone, and whether it contains an explicit request for support.

If the transcript is empty or contains no usable language, return 50 for every \
scale and set insufficient_text to true."""

USER_TEMPLATE = """Transcript ({unit}), {n_messages} message(s), \
treatment "{treatment}":

<transcript>
{transcript}
</transcript>

Rate the language of {target} in this transcript."""


@functools.lru_cache(maxsize=1)
def rubric_model():
    """Schema di output della rubrica.

    Costruito su richiesta perché pydantic serve solo a questo stadio: le
    misure deterministiche di `text_metrics` devono restare eseguibili senza
    alcuna dipendenza esterna.
    """
    try:
        from pydantic import BaseModel, Field
    except ImportError as exc:  # pragma: no cover - dipende dall'ambiente
        raise RuntimeError(
            'La rubrica LLM richiede pydantic e anthropic.\n'
            '  pip install -r scripts/nlp/requirements.txt'
        ) from exc

    class RubricScores(BaseModel):
        """Punteggi della rubrica per una singola trascrizione."""

        analytic: int = Field(ge=0, le=100, description='Analytical thinking, 0-100')
        clout: int = Field(ge=0, le=100, description='Confidence and social status, 0-100')
        authenticity: int = Field(ge=0, le=100, description='Spontaneous honesty, 0-100')
        tone: int = Field(ge=0, le=100, description='Emotional tone, 50 = neutral')
        contains_support_commitment: bool = Field(
            description='The text explicitly promises support to someone'
        )
        contains_support_request: bool = Field(
            description='The text explicitly asks someone for support'
        )
        insufficient_text: bool = Field(
            description='True when the transcript carries too little language to rate'
        )
        rationale: str = Field(
            description='One sentence, at most 25 words, justifying the ratings'
        )

    return RubricScores


SCALE_FIELDS = ('analytic', 'clout', 'authenticity', 'tone')
FLAG_FIELDS = (
    'contains_support_commitment', 'contains_support_request', 'insufficient_text',
)


@dataclass
class RubricUnit:
    """Una trascrizione da valutare, con la sua chiave di ricongiungimento."""

    key: tuple
    unit: str
    transcript: str
    n_messages: int
    treatment: str
    target: str


def build_units(features_rows, level: str, transcript_lookup) -> list[RubricUnit]:
    """Costruisce le unità da valutare a partire dalle righe aggregate."""
    from .aggregate import LEVEL_KEYS

    keys = LEVEL_KEYS[level]
    targets = {
        'dyad_directed': 'the sender',
        'dyad': 'both participants',
        'sender_group': 'the sender',
        'group': 'all three participants',
    }
    units = []
    for row in features_rows:
        key = tuple(str(row.get(k, '')) for k in keys)
        transcript = transcript_lookup.get(key, '')
        if not transcript.strip():
            continue
        units.append(
            RubricUnit(
                key=key,
                unit=level,
                transcript=transcript,
                n_messages=int(row.get('n_messages', 0) or 0),
                treatment=row.get('treatment', ''),
                target=targets.get(level, 'the participants'),
            )
        )
    return units


def _user_message(unit: RubricUnit) -> str:
    return USER_TEMPLATE.format(
        unit=unit.unit,
        n_messages=unit.n_messages,
        treatment=unit.treatment or 'unknown',
        transcript=unit.transcript,
        target=unit.target,
    )


def _request_params(unit: RubricUnit, model: str) -> dict:
    return dict(
        model=model,
        max_tokens=8000,
        # Il prompt di sistema è identico per ogni chiamata: metterlo in cache
        # abbatte il costo dell'input su corpus grandi.
        system=[{
            'type': 'text',
            'text': SYSTEM_PROMPT,
            'cache_control': {'type': 'ephemeral'},
        }],
        thinking={'type': 'adaptive'},
        output_config={'effort': 'medium'},
        messages=[{'role': 'user', 'content': _user_message(unit)}],
    )


def _empty_scores() -> dict:
    scores = {field: None for field in SCALE_FIELDS}
    scores.update({field: None for field in FLAG_FIELDS})
    scores['rationale'] = ''
    return scores


def score_unit(client, unit: RubricUnit, model: str = DEFAULT_MODEL) -> dict:
    """Valuta una trascrizione. Restituisce i punteggi o l'errore incontrato."""
    import anthropic

    try:
        response = client.messages.parse(
            output_format=rubric_model(),
            **_request_params(unit, model),
        )
    except anthropic.NotFoundError as exc:
        raise RuntimeError(f'modello non disponibile: {model}') from exc
    except anthropic.RateLimitError as exc:
        retry_after = int(exc.response.headers.get('retry-after', '30'))
        time.sleep(retry_after)
        return score_unit(client, unit, model)
    except anthropic.APIStatusError as exc:
        if exc.status_code >= 500:
            time.sleep(5)
            return score_unit(client, unit, model)
        return dict(_empty_scores(), error=f'api_status_{exc.status_code}')
    except anthropic.APIConnectionError:
        time.sleep(5)
        return score_unit(client, unit, model)

    if response.stop_reason == 'refusal':
        category = getattr(response.stop_details, 'category', None)
        return dict(_empty_scores(), error=f'refusal:{category}')

    parsed = response.parsed_output
    result = {field: getattr(parsed, field) for field in SCALE_FIELDS}
    result.update({field: int(getattr(parsed, field)) for field in FLAG_FIELDS})
    result['rationale'] = parsed.rationale
    result['error'] = ''
    result['model'] = model
    return result


def score_units(units, models=(DEFAULT_MODEL,), replicates=1, progress=None):
    """Valuta tutte le unità, con repliche e/o più giudici.

    Restituisce una riga per unità: media fra tutte le valutazioni, deviazione
    standard come stima dell'errore di misura, e i punteggi grezzi di ciascuna
    valutazione per gli usi di controllo.
    """
    import anthropic

    client = anthropic.Anthropic()
    rows = []
    total = len(units) * len(models) * replicates
    done = 0

    for unit in units:
        judgements = []
        for model in models:
            for _ in range(replicates):
                judgements.append(score_unit(client, unit, model))
                done += 1
                if progress:
                    progress(done, total)

        rows.append(_summarize(unit, judgements))
    return rows


def _summarize(unit: RubricUnit, judgements) -> dict:
    from .aggregate import LEVEL_KEYS

    row = dict(zip(LEVEL_KEYS[unit.unit], unit.key))
    valid = [j for j in judgements if not j.get('error')]

    for field in SCALE_FIELDS:
        values = [j[field] for j in valid if j.get(field) is not None]
        row[f'llm_{field}'] = round(statistics.mean(values), 3) if values else ''
        row[f'llm_{field}_sd'] = (
            round(statistics.stdev(values), 3) if len(values) > 1 else ''
        )
    for field in FLAG_FIELDS:
        values = [j[field] for j in valid if j.get(field) is not None]
        # Maggioranza fra le valutazioni; a parità si sceglie 0.
        row[f'llm_{field}'] = int(sum(values) * 2 > len(values)) if values else ''

    row['llm_n_judgements'] = len(valid)
    row['llm_n_errors'] = len(judgements) - len(valid)
    row['llm_errors'] = ';'.join(sorted({j['error'] for j in judgements if j.get('error')}))
    row['llm_rationale'] = valid[0]['rationale'] if valid else ''
    row['llm_models'] = ','.join(sorted({j.get('model', '') for j in valid if j.get('model')}))
    return row


# --- Modalità batch, per il dataset finale ---------------------------------


def submit_batch(units, model: str = DEFAULT_MODEL, replicates: int = 1):
    """Invia le valutazioni alla Batches API (metà prezzo, esito asincrono).

    Restituisce l'id del batch: va conservato, perché i risultati si ritirano
    con `collect_batch` anche in una sessione successiva.
    """
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    requests = []
    for index, unit in enumerate(units):
        for replicate in range(replicates):
            params = _request_params(unit, model)
            params['output_config'] = dict(
                params['output_config'],
                format={
                    'type': 'json_schema',
                    'schema': rubric_model().model_json_schema(),
                },
            )
            requests.append(
                Request(
                    custom_id=f'{index}-{replicate}',
                    params=MessageCreateParamsNonStreaming(**params),
                )
            )

    batch = client.messages.batches.create(requests=requests)
    return batch.id


def collect_batch(batch_id: str, units, poll_seconds: int = 60, progress=None):
    """Attende la fine del batch e ricompone le righe nell'ordine delle unità."""
    import anthropic

    client = anthropic.Anthropic()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == 'ended':
            break
        if progress:
            progress(batch.request_counts.processing)
        time.sleep(poll_seconds)

    # I risultati arrivano in ordine arbitrario: si indicizza per custom_id.
    by_unit = {index: [] for index in range(len(units))}
    for result in client.messages.batches.results(batch_id):
        index = int(result.custom_id.split('-')[0])
        if result.result.type != 'succeeded':
            by_unit[index].append(dict(_empty_scores(), error=result.result.type))
            continue
        message = result.result.message
        if message.stop_reason == 'refusal':
            by_unit[index].append(dict(_empty_scores(), error='refusal'))
            continue
        text = next((b.text for b in message.content if b.type == 'text'), '')
        try:
            payload = rubric_model().model_validate_json(text)
        except Exception:  # noqa: BLE001 - risposta non conforme allo schema
            by_unit[index].append(dict(_empty_scores(), error='unparseable'))
            continue
        row = {field: getattr(payload, field) for field in SCALE_FIELDS}
        row.update({field: int(getattr(payload, field)) for field in FLAG_FIELDS})
        row['rationale'] = payload.rationale
        row['error'] = ''
        row['model'] = message.model
        by_unit[index].append(row)

    return [_summarize(unit, by_unit[i]) for i, unit in enumerate(units)]


def has_credentials() -> bool:
    """True se esiste una credenziale utilizzabile per l'API."""
    if os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_AUTH_TOKEN'):
        return True
    config = os.path.expanduser('~/.config/anthropic')
    return os.path.isdir(config) and bool(os.listdir(config))


def dry_run_payload(units, model: str = DEFAULT_MODEL) -> str:
    """Anteprima della prima richiesta, per ispezione senza spendere token."""
    if not units:
        return '(nessuna unità da valutare)'
    params = _request_params(units[0], model)
    preview = dict(
        model=params['model'],
        effort=params['output_config']['effort'],
        system=params['system'][0]['text'][:400] + '...',
        user=params['messages'][0]['content'],
    )
    try:
        preview['output_format'] = rubric_model().model_json_schema()
    except RuntimeError as exc:
        # L'anteprima deve restare utile anche senza le dipendenze opzionali.
        preview['output_format'] = f'(schema non disponibile: {exc})'
    return json.dumps(preview, indent=2, ensure_ascii=False)

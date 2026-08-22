"""
Esegue la pipeline NLP sui messaggi dell'esperimento e arricchisce i dataset.

Tre stadi indipendenti, attivabili separatamente:

1. **Misure testuali** (sempre attivo, nessuna credenziale richiesta) —
   volume, sentiment e gli indici in stile LIWC-22 (analytic, clout,
   authenticity, tone), calcolati a livello di coppia ordinata, coppia,
   partecipante e gruppo.
2. **Rubrica LLM** (``--llm``) — seconda misura degli stessi costrutti
   valutata da Claude, per validazione convergente. Richiede una credenziale
   Anthropic.
3. **TopicGPT** (``--topics``) — codice ufficiale di Pham et al. (2024).
   Richiede il repository clonato e la credenziale del backend scelto.

L'output finale sono i due dataset dell'esperimento arricchiti, pronti per
Stata, più i file di feature intermedi per i controlli.

Esempi
------
    # Solo misure automatiche, subito eseguibile
    python scripts/run_nlp_pipeline.py \
        --merged-dir docs/merged --stem all_apps_wide_2026-08-18

    # Con la rubrica LLM
    python scripts/run_nlp_pipeline.py --merged-dir docs/merged \
        --stem all_apps_wide_2026-08-18 --llm --llm-replicates 2

    # Con i topic
    python scripts/run_nlp_pipeline.py --merged-dir docs/merged \
        --stem all_apps_wide_2026-08-18 \
        --topics --topicgpt-repo ~/src/topicGPT --topicgpt-model gpt-4o
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.nlp import aggregate as agg  # noqa: E402
from scripts.nlp import llm_rubric, secrets, topicgpt_runner  # noqa: E402

# Le chiavi API si configurano una volta con scripts/setup_api_keys.py e da lì
# in poi vengono caricate da sole: chi esegue la pipeline non deve ricordarsene.
_LOADED_KEYS = secrets.load_secrets()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def build_transcripts(messages, level: str) -> dict:
    """Trascrizioni leggibili per livello, usate dalla rubrica LLM."""
    from collections import defaultdict

    keys = agg.LEVEL_KEYS[level]
    buckets = defaultdict(list)
    for message in messages:
        buckets[tuple(str(message.get(k, '')) for k in keys)].append(message)

    transcripts = {}
    for key, bucket in buckets.items():
        bucket.sort(key=lambda m: float(m.get('timestamp') or 0))
        transcripts[key] = '\n'.join(
            f"{m.get('sender_color', '?')} -> {m.get('receiver_color', '?')}: "
            f"{m.get('body', '')}"
            for m in bucket
        )
    return transcripts


def _merge_llm(rows, level_rows, level):
    """Innesta le colonne della rubrica nelle righe aggregate del livello."""
    keys = agg.LEVEL_KEYS[level]
    index = {tuple(str(r.get(k, '')) for k in keys): r for r in level_rows}
    for row in rows:
        target = index.get(tuple(str(row.get(k, '')) for k in keys))
        if target is None:
            continue
        for column, value in row.items():
            if column.startswith('llm_'):
                target[column] = value


def run_llm_stage(features, transcripts_by_level, args) -> None:
    if args.llm_dry_run:
        provider = args.llm_provider or 'anthropic'
    else:
        provider = llm_rubric.resolve_provider(args.llm_provider)
        print(f'  fornitore: {llm_rubric.PROVIDERS[provider]["label"]}')

    models = [m.strip() for m in (args.llm_models or '').split(',') if m.strip()]
    if not models:
        models = [llm_rubric.default_model_for(provider)]
    for level in args.llm_levels:
        units = llm_rubric.build_units(
            features[level], level, transcripts_by_level[level]
        )
        if not units:
            print(f'  {level}: nessuna trascrizione da valutare')
            continue

        if args.llm_dry_run:
            print(f'  {level}: {len(units)} unità; anteprima della prima richiesta')
            print(llm_rubric.dry_run_payload(units, models[0]))
            continue

        total_calls = len(units) * len(models) * args.llm_replicates
        print(f'  {level}: {len(units)} unità, {total_calls} chiamate')

        if args.llm_batch and provider != 'anthropic':
            raise SystemExit(
                "--llm-batch e' disponibile solo con il fornitore anthropic; "
                'con gli altri backend usa la modalita\' sincrona.'
            )

        if args.llm_batch:
            batch_id = llm_rubric.submit_batch(
                units, models[0], args.llm_replicates
            )
            print(f'    batch inviato: {batch_id}')
            scored = llm_rubric.collect_batch(batch_id, units)
        else:
            def progress(done, total, level=level):
                if done % 25 == 0 or done == total:
                    print(f'    {level}: {done}/{total}', flush=True)

            scored = llm_rubric.score_units(
                units, models=models, replicates=args.llm_replicates,
                progress=progress, provider=provider,
            )

        _merge_llm(scored, features[level], level)
        errors = sum(int(r.get('llm_n_errors', 0) or 0) for r in scored)
        if errors:
            print(f'    ATTENZIONE: {errors} valutazioni fallite', file=sys.stderr)


def run_topics_stage(messages, args):
    """Esegue TopicGPT e restituisce le assegnazioni ai vari livelli."""
    repo = Path(args.topicgpt_repo).expanduser()
    # I backend locali (ollama, vllm) non usano chiavi: si controlla solo dove serve.
    if not args.topicgpt_dry_run and args.topicgpt_api == 'openai':
        secrets.require_key('OPENAI_API_KEY')

    documents = topicgpt_runner.build_documents(messages, args.topicgpt_unit)
    print(f'  documenti costruiti: {len(documents)} ({args.topicgpt_unit})')

    if args.topicgpt_dry_run:
        outdir = Path(args.outdir) / 'topicgpt'
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / 'topicgpt_input.jsonl'
        topicgpt_runner.write_jsonl(path, documents)
        print(f'  input scritto in {path} (nessuna chiamata effettuata)')
        return None, None, None

    try:
        corrected = topicgpt_runner.run_topicgpt(
            documents=documents,
            outdir=Path(args.outdir) / 'topicgpt',
            repo_path=repo,
            api=args.topicgpt_api,
            model=args.topicgpt_model,
            refine=not args.topicgpt_no_refine,
            verbose=args.verbose,
        )
    except topicgpt_runner.TopicGPTUnavailable as exc:
        # Manca un prerequisito: è una cosa da sistemare, non un errore del
        # programma. Si mostra l'istruzione, non la traccia dello stack.
        raise SystemExit(f'\n{exc}\n') from None
    assignments = topicgpt_runner.parse_assignments(corrected)
    print(f'  topic assegnati a {len(assignments)} documenti')

    unit = args.topicgpt_unit
    by_directed = (
        topicgpt_runner.topics_by_key(assignments, unit)
        if unit == 'dyad_directed' else None
    )
    by_sender = (
        topicgpt_runner.rollup_topics(assignments, unit, 'sender_group')
        if unit in ('dyad_directed', 'sender_group') else None
    )
    by_group = topicgpt_runner.rollup_topics(assignments, unit, 'group')
    return by_directed, by_sender, by_group


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merged-dir', required=True, type=Path,
                        help='Cartella prodotta da merge_chat_and_choices.py')
    parser.add_argument('--stem', required=True,
                        help='Prefisso dei file (es. all_apps_wide_2026-08-18)')
    parser.add_argument('--outdir', type=Path, default=None,
                        help='Cartella di output (default: <merged-dir>/nlp)')
    parser.add_argument('--verbose', action='store_true')

    parser.add_argument('--llm', action='store_true',
                        help='Esegue la rubrica valutata da Claude')
    parser.add_argument('--llm-provider', default=None,
                        choices=list(llm_rubric.PROVIDERS),
                        help='Fornitore della rubrica. Se omesso, sceglie in base '
                             'alle credenziali disponibili')
    parser.add_argument('--llm-models', default=None,
                        help='Modelli giudice, separati da virgola. Se omesso, usa '
                             'il modello predefinito del fornitore')
    parser.add_argument('--llm-replicates', type=int, default=1,
                        help='Valutazioni indipendenti per unità (affidabilità)')
    parser.add_argument('--llm-levels', nargs='+', default=['dyad_directed', 'group'],
                        choices=list(agg.LEVELS))
    parser.add_argument('--llm-batch', action='store_true',
                        help='Usa la Batches API (metà prezzo, esito asincrono)')
    parser.add_argument('--llm-dry-run', action='store_true',
                        help='Mostra la richiesta senza chiamare l API')

    parser.add_argument('--topics', action='store_true',
                        help='Esegue TopicGPT (codice ufficiale del paper)')
    parser.add_argument('--topicgpt-repo', default='./topicGPT',
                        help='Repository clonato di TopicGPT (per i prompt)')
    parser.add_argument('--topicgpt-api', default='openai',
                        choices=['openai', 'azure', 'vertex', 'gemini', 'ollama', 'vllm'])
    parser.add_argument('--topicgpt-model', default='gpt-4o')
    parser.add_argument('--topicgpt-unit', default='dyad_directed',
                        choices=list(topicgpt_runner.UNIT_KEYS))
    parser.add_argument('--topicgpt-no-refine', action='store_true',
                        help='Salta la fase di raffinamento dei topic')
    parser.add_argument('--topicgpt-dry-run', action='store_true',
                        help='Scrive solo il file di input, senza chiamate')

    args = parser.parse_args(argv)
    outdir = args.outdir or (args.merged_dir / 'nlp')
    outdir.mkdir(parents=True, exist_ok=True)
    args.outdir = outdir

    messages_path = args.merged_dir / f'{args.stem}_messages_long.csv'
    by_partner_path = args.merged_dir / f'{args.stem}_chat_by_partner.csv'
    aggregated_path = args.merged_dir / f'{args.stem}_chat_aggregated.csv'
    for path in (messages_path, by_partner_path, aggregated_path):
        if not path.is_file():
            raise SystemExit(f'File mancante: {path}\nEsegui prima merge_chat_and_choices.py')

    messages = agg.read_messages(messages_path)
    print(f'Messaggi letti: {len(messages)}')

    print('Misure testuali...')
    enriched = agg.analyze_messages(messages)
    features = agg.aggregate_all(enriched)
    for level, rows in features.items():
        print(f'  {level}: {len(rows)} unità')

    transcripts_by_level = {
        level: build_transcripts(messages, level) for level in agg.LEVELS
    }

    if args.llm:
        print('Rubrica LLM...')
        run_llm_stage(features, transcripts_by_level, args)

    topics_directed = topics_sender = topics_group = None
    if args.topics:
        print('TopicGPT...')
        topics_directed, topics_sender, topics_group = run_topics_stage(messages, args)

    agg.write_csv(outdir / f'{args.stem}_messages_nlp.csv', enriched)
    for level, rows in features.items():
        agg.write_csv(outdir / f'{args.stem}_features_{level}.csv', rows)

    by_partner = read_csv(by_partner_path)
    aggregated = read_csv(aggregated_path)
    agg.merge_into_by_partner(by_partner, features, topics_directed)
    agg.merge_into_aggregated(aggregated, features, topics_sender, topics_group)

    out_partner = outdir / f'{args.stem}_chat_by_partner_nlp.csv'
    out_aggregated = outdir / f'{args.stem}_chat_aggregated_nlp.csv'
    agg.write_csv(out_partner, by_partner)
    agg.write_csv(out_aggregated, aggregated)

    print()
    print('Dataset arricchiti:')
    print(f'  {out_partner}')
    print(f'  {out_aggregated}')
    print('Feature intermedie:')
    print(f'  {outdir}/{args.stem}_features_*.csv')
    return 0


if __name__ == '__main__':
    sys.exit(main())

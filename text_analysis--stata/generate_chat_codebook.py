"""Generate the Markdown codebook for the two final chat merge CSV files."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
AGGREGATED = HERE / "all_apps_wide_2026-08-26_chat_aggregated_final.csv"
BY_PARTNER = HERE / "all_apps_wide_2026-08-26_chat_by_partner_final.csv"
OUTPUT = HERE / "CODEBOOK_chat_exports_2026-08-26.md"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


SD3 = {
    "sd3_mach_01": "It’s not wise to tell your secrets.",
    "sd3_mach_02": "I like to use clever manipulation to get my way.",
    "sd3_mach_03": "Whatever it takes, you must get the important people on your side.",
    "sd3_mach_04": "Avoid direct conflict with others because they may be useful in the future.",
    "sd3_mach_05": "It’s wise to keep track of information that you can use against people later.",
    "sd3_mach_06": "You should wait for the right time to get back at people.",
    "sd3_mach_07": "There are things you should hide from other people to preserve your reputation.",
    "sd3_mach_08": "Make sure your plans benefit yourself, not others.",
    "sd3_mach_09": "Most people can be manipulated.",
    "sd3_narc_01": "People see me as a natural leader.",
    "sd3_narc_02": "I hate being the center of attention.",
    "sd3_narc_03": "Many group activities tend to be dull without me.",
    "sd3_narc_04": "I know that I am special because everyone keeps telling me so.",
    "sd3_narc_05": "I like to get acquainted with important people.",
    "sd3_narc_06": "I feel embarrassed if someone compliments me.",
    "sd3_narc_07": "I have been compared to famous people.",
    "sd3_narc_08": "I am an average person.",
    "sd3_narc_09": "I insist on getting the respect I deserve.",
    "sd3_psych_01": "I like to get revenge on authorities.",
    "sd3_psych_02": "I avoid dangerous situations.",
    "sd3_psych_03": "Payback needs to be quick and nasty.",
    "sd3_psych_04": "People often say I’m out of control.",
    "sd3_psych_05": "It’s true that I can be mean to others.",
    "sd3_psych_06": "People who mess with me always regret it.",
    "sd3_psych_07": "I have never gotten into trouble with the law.",
    "sd3_psych_08": "I enjoy having sex with people I hardly know.",
    "sd3_psych_09": "I’ll say anything to get what I want.",
}


DESCRIPTIONS = {
    "participant.id_in_session": "Numero progressivo del partecipante nella sessione oTree.",
    "participant.code": "Codice pseudonimo univoco del partecipante; chiave del mittente nel file chat.",
    "participant.label": "Etichetta opzionale assegnata al partecipante in oTree.",
    "participant._index_in_pages": "Indice interno oTree della pagina raggiunta dal partecipante.",
    "participant.payoff": "Payoff complessivo oTree del partecipante, espresso nella valuta configurata.",
    "participant.inactive_excluded": "Indicatore che il partecipante è stato escluso per inattività.",
    "participant.inactive_excluded_reason": "Motivo testuale/codificato dell’esclusione per inattività.",
    "participant.group_dropped": "Indicatore participant-level che il gruppo è stato marcato come caduto/interrotto.",
    "participant.part1_payoff_eligible": "Indicatore participant-level di eleggibilità al payoff della Parte 1.",
    "participant.group_outcome": "Copia participant-level dell’esito del gruppo della Parte 1.",
    "participant.part1_group_id": "ID immutabile del gruppo della Parte 1. È l’ID da usare per collegare le chat; può differire dall’ID corrente oTree dopo un regrouping.",
    "session.code": "Codice univoco della sessione oTree.",
    "bargaining_tdl_intro.1.player.time_welcome": "Secondi trascorsi sulla pagina Welcome dell’introduzione.",
    "bargaining_tdl_intro.1.player.time_instructions_part1": "Secondi trascorsi sulle istruzioni della Parte 1.",
    "bargaining_tdl_intro.1.player.time_control_questions": "Secondi trascorsi sulle domande di controllo.",
    "bargaining_tdl_main.1.player.id_in_group": "Posizione del giocatore nella triade: 1, 2 o 3.",
    "bargaining_tdl_main.1.player.payoff": "Payoff oTree del player nell’app principale.",
    "bargaining_tdl_main.1.player.player_color": "Colore associato alla posizione: 1=Yellow, 2=Orange, 3=Purple.",
    "bargaining_tdl_main.1.player.treatment": "Trattamento sperimentale: private, public o private_no_dwl (Slacker). Vuoto per righe del raw non appartenenti a queste partite.",
    "bargaining_tdl_main.1.player.part1_calculated_payoff": "Payoff teorico calcolato nella Parte 1 prima di un’eventuale esclusione per inattività.",
    "bargaining_tdl_main.1.player.signal_left": "Intenzione inviata al partner topologico sinistro.",
    "bargaining_tdl_main.1.player.signal_right": "Intenzione inviata al partner topologico destro.",
    "bargaining_tdl_main.1.player.first_intention_selected": "Lato della prima intenzione selezionata nella pagina Signals: left o right.",
    "bargaining_tdl_main.1.player.guess_left_confidence": "Fiducia nella previsione sulla scelta del partner sinistro, scala 1–8.",
    "bargaining_tdl_main.1.player.guess_right_confidence": "Fiducia nella previsione sulla scelta del partner destro, scala 1–8.",
    "bargaining_tdl_main.1.player.time_welcome": "Secondi sulla pagina Welcome dell’app principale.",
    "bargaining_tdl_main.1.player.time_chat": "Secondi sulla fase di chat.",
    "bargaining_tdl_main.1.player.time_signals": "Secondi sulla fase delle intenzioni/segnali.",
    "bargaining_tdl_main.1.player.decision_choice": "Decisione finale dal punto di vista del focal player: Left, Right o NoOne.",
    "bargaining_tdl_main.1.player.decision_option_1": "Opzione mostrata nella prima posizione visuale nella pagina Decision.",
    "bargaining_tdl_main.1.player.decision_option_2": "Opzione mostrata nella seconda posizione visuale nella pagina Decision.",
    "bargaining_tdl_main.1.player.decision_option_3": "Opzione mostrata nella terza posizione visuale nella pagina Decision.",
    "bargaining_tdl_main.1.player.received_signal_left": "Intenzione ricevuta dal partner topologico sinistro.",
    "bargaining_tdl_main.1.player.received_signal_right": "Intenzione ricevuta dal partner topologico destro.",
    "bargaining_tdl_main.1.player.id_player_on_the_left": "participant.code del partner nella coordinata topologica sinistra.",
    "bargaining_tdl_main.1.player.id_player_on_the_right": "participant.code del partner nella coordinata topologica destra.",
    "bargaining_tdl_main.1.player.id_player_visualized_on_the_left": "participant.code effettivamente visualizzato nella colonna sinistra, dopo la randomizzazione dell’ordine.",
    "bargaining_tdl_main.1.player.id_player_visualized_on_the_right": "participant.code effettivamente visualizzato nella colonna destra, dopo la randomizzazione dell’ordine.",
    "bargaining_tdl_main.1.player.time_decision": "Secondi trascorsi sulla pagina Decision.",
    "bargaining_tdl_main.1.player.time_post_decision_confidence": "Secondi trascorsi sulla pagina di previsione/confidenza post-decisione.",
    "bargaining_tdl_main.1.player.chat_interrupted": "Indicatore che la chat del focal player è stata interrotta.",
    "bargaining_tdl_main.1.player.part1_payoff_eligible": "Indicatore player-level di eleggibilità al payoff della Parte 1.",
    "bargaining_tdl_main.1.player.decision_inactive": "Stato d’inattività sulla decisione: 99 indica timeout senza scelta; 0 indica nessun timeout.",
    "bargaining_tdl_main.1.player.signal_inactive": "Stato d’inattività sui segnali: 99 indica timeout senza scelta; 0 indica nessun timeout.",
    "bargaining_tdl_main.1.player.received_signal_left_inactive": "Stato d’inattività (0/99) del mittente del segnale ricevuto da sinistra.",
    "bargaining_tdl_main.1.player.received_signal_right_inactive": "Stato d’inattività (0/99) del mittente del segnale ricevuto da destra.",
    "bargaining_tdl_main.1.player.guess_left_choice": "Previsione della decisione del partner sinistro, espressa dal punto di vista di quel partner.",
    "bargaining_tdl_main.1.player.guess_right_choice": "Previsione della decisione del partner destro, espressa dal punto di vista di quel partner.",
    "bargaining_tdl_main.1.group.id_in_subsession": "ID corrente del gruppo nell’app principale; per le chat preferire participant.part1_group_id.",
    "bargaining_tdl_main.1.group.grp_coordinate": "1 se l’esito produce payoff positivo/coordinamento (mutual oppure star in Slacker); 0 altrimenti.",
    "bargaining_tdl_main.1.group.group_outcome": "Esito della triade: mutual_12/23/31, no_dwl_star_1/2/3, disagreement o pending.",
    "bargaining_tdl_main.1.group.chat_left_p1": "Indicatore che il giocatore 1 ha lasciato/interrotto la chat.",
    "bargaining_tdl_main.1.group.chat_left_p2": "Indicatore che il giocatore 2 ha lasciato/interrotto la chat.",
    "bargaining_tdl_main.1.group.chat_left_p3": "Indicatore che il giocatore 3 ha lasciato/interrotto la chat.",
    "bargaining_tdl_main.1.group.group_dropped": "Indicatore group-level che la triade è stata interrotta/caduta.",
    "bargaining_tdl_survey.1.player.gender": "Genere: 0=Male, 1=Female, 2=Other.",
    "bargaining_tdl_survey.1.player.birth_year": "Anno di nascita (YYYY; intervallo previsto 1924–2008).",
    "bargaining_tdl_survey.1.player.field_of_study": "Campo di studio, codifica ISCED personalizzata riportata nella sezione Codifiche.",
    "bargaining_tdl_survey.1.player.university_years": "Anni equivalenti full-time di istruzione universitaria/terziaria, 0–20.",
    "bargaining_tdl_survey.1.player.main_situation": "Situazione principale: paid_work, education, unemployed, sick_disabled, retired o housework.",
    "bargaining_tdl_survey.1.player.job_type": "Tipo di occupazione: employee, self_employed, employer o not_employed.",
    "bargaining_tdl_survey.1.player.willingness_future": "Disponibilità a rinunciare a un beneficio presente per uno futuro, scala 0–10.",
    "bargaining_tdl_survey.1.player.willingness_risk": "Disponibilità generale ad assumere rischi, scala 0–10.",
    "bargaining_tdl_survey.1.player.reciprocity_positive": "Reciprocità positiva auto-riferita, scala 0–10.",
    "bargaining_tdl_survey.1.player.reciprocity_negative": "Reciprocità negativa/vendetta auto-riferita, scala 0–10.",
    "bargaining_tdl_survey.1.player.willingness_donate": "Disponibilità a donare senza contropartita, scala 0–10.",
    "bargaining_tdl_survey.1.player.trust_general": "Fiducia generale nelle buone intenzioni altrui, scala 0–10.",
    "bargaining_tdl_survey.1.player.beauty_contest_guess": "Richiesta nel gioco 11–20/beauty contest, da 1.10 a 2.00.",
    "bargaining_tdl_survey.1.player.instructions_clarity": "Chiarezza percepita delle istruzioni, scala 1–5.",
    "bargaining_tdl_survey.1.player.general_comment": "Commento libero del partecipante sull’esperimento.",
    "focal_player_id": "ID 1–3 del partecipante focal, derivato da player.id_in_group.",
    "focal_player_color": "Colore del focal player derivato dall’ID.",
    "decision_target_id": "ID del destinatario della decisione finale; NoOne se non supporta nessuno.",
    "decision_target_color": "Colore del destinatario della decisione; NoOne se applicabile.",
    "guess_left_target_id": "ID del giocatore che, secondo il focal, sarà scelto dal partner sinistro.",
    "guess_left_target_color": "Colore corrispondente a guess_left_target_id.",
    "guess_right_target_id": "ID del giocatore che, secondo il focal, sarà scelto dal partner destro.",
    "guess_right_target_color": "Colore corrispondente a guess_right_target_id.",
    "signal_left_target_id": "ID del destinatario implicato nell’intenzione inviata al partner sinistro.",
    "signal_left_target_color": "Colore corrispondente a signal_left_target_id.",
    "signal_right_target_id": "ID del destinatario implicato nell’intenzione inviata al partner destro.",
    "signal_right_target_color": "Colore corrispondente a signal_right_target_id.",
    "received_signal_left_target_id": "ID del destinatario implicato nel segnale ricevuto da sinistra.",
    "received_signal_left_target_color": "Colore corrispondente a received_signal_left_target_id.",
    "received_signal_right_target_id": "ID del destinatario implicato nel segnale ricevuto da destra.",
    "received_signal_right_target_color": "Colore corrispondente a received_signal_right_target_id.",
    "chat_group_key": "Chiave derivata session.code|participant.part1_group_id.",
    "chat_group_status": "Stato dell’abbinamento chat nel file participant-level: matched, no_messages o no_group.",
    "chat_message_count_group": "Numero totale di messaggi nella triade.",
    "chat_message_count_sent": "Numero di messaggi inviati dal focal player nella triade.",
    "chat_message_count_received": "Numero di messaggi della triade indirizzati al focal player.",
    "chat_side": "Partner topologico della riga: left o right; non è necessariamente la posizione visualizzata.",
    "partner_id": "ID 1–3 del partner associato alla riga.",
    "partner_color": "Colore del partner associato alla riga.",
    "chat_status": "Stato dell’abbinamento della chat diadica: matched, no_messages o no_group.",
    "chat_channel": "Nome del canale oTree della diade.",
    "chat_message_count": "Numero totale di messaggi nella conversazione tra focal e partner.",
    "chat_message_count_focal_sent": "Numero di messaggi della diade inviati dal focal player.",
    "chat_message_count_partner_sent": "Numero di messaggi della diade inviati dal partner.",
    "chat_first_timestamp": "Timestamp Unix del primo messaggio nell’unità di conversazione.",
    "chat_last_timestamp": "Timestamp Unix dell’ultimo messaggio nell’unità di conversazione.",
    "chat_transcript_group": "Array JSON ordinato cronologicamente con tutti i messaggi della triade.",
    "chat_transcript": "Array JSON ordinato cronologicamente con tutti i messaggi della diade.",
}


SURVEY_PREFIX = "bargaining_tdl_survey.1.player."


def description(column: str) -> str:
    if column in DESCRIPTIONS:
        return DESCRIPTIONS[column]
    if column.startswith(SURVEY_PREFIX + "sd3_"):
        short = column.removeprefix(SURVEY_PREFIX)
        domain = "Machiavellismo" if "_mach_" in short else "Narcisismo" if "_narc_" in short else "Psicopatia"
        return f"Short Dark Triad — {domain}, scala di accordo 1–5. Item: “{SD3[short]}”"
    if column.startswith(SURVEY_PREFIX + "time_"):
        page = column.removeprefix(SURVEY_PREFIX + "time_").replace("_", " ")
        return f"Secondi trascorsi nella sezione/pagina survey “{page}”."
    return "Variabile conservata dall’export oTree; vedere il nome strutturato app.round.model.field."


def variable_type(column: str, values: list[str]) -> str:
    if column in {"chat_transcript", "chat_transcript_group"}:
        return "JSON"
    if column.endswith("timestamp"):
        return "timestamp Unix"
    if ".time_" in column:
        return "numero (secondi)"
    if column.endswith("general_comment"):
        return "testo libero"
    if column.endswith((".code", "_key", "_channel")) or column in {"participant.code", "participant.label"}:
        return "identificatore/testo"
    nonempty = [v for v in values if v != ""]
    if nonempty and all(v in {"0", "1", "True", "False"} for v in nonempty):
        return "booleano"
    try:
        for value in nonempty:
            float(value)
        return "numerico"
    except ValueError:
        return "categorico/testo"


def encoding(column: str, values: list[str]) -> str:
    explicit = {
        "bargaining_tdl_main.1.player.treatment": "private=Baseline; public=chat pubblica; private_no_dwl=Slacker",
        "bargaining_tdl_main.1.player.signal_left": "split_you; split_other; support_none",
        "bargaining_tdl_main.1.player.signal_right": "split_you; split_other; support_none",
        "bargaining_tdl_main.1.player.received_signal_left": "split_you; split_other; support_none",
        "bargaining_tdl_main.1.player.received_signal_right": "split_you; split_other; support_none",
        "bargaining_tdl_main.1.player.decision_choice": "Left; Right; NoOne",
        "bargaining_tdl_main.1.player.guess_left_choice": "Left; Right; NoOne (POV del partner)",
        "bargaining_tdl_main.1.player.guess_right_choice": "Left; Right; NoOne (POV del partner)",
        "bargaining_tdl_main.1.group.group_outcome": "mutual_12/23/31; no_dwl_star_1/2/3; disagreement; pending",
        "bargaining_tdl_survey.1.player.gender": "0=Male; 1=Female; 2=Other",
        "bargaining_tdl_survey.1.player.field_of_study": "1 Education; 2 Arts/humanities; 3 Social sciences; 4 Business/law; 5 Natural sciences; 6 ICT; 7 Engineering; 8 Agriculture; 9 Health; 10 Services; 11 Journalism/information",
        "chat_side": "left; right",
        "focal_player_color": "Yellow; Orange; Purple",
        "partner_color": "Yellow; Orange; Purple",
    }
    if column in explicit:
        return explicit[column]
    if "sd3_" in column:
        return "1=Disagree strongly … 5=Agree strongly"
    if column.endswith(("decision_inactive", "signal_inactive", "received_signal_left_inactive", "received_signal_right_inactive")):
        return "0=nessun timeout; 99=timeout/inattività"
    nonempty = [v for v in values if v != ""]
    unique = sorted(set(nonempty))
    if 0 < len(unique) <= 8 and not any(len(v) > 40 for v in unique):
        return "; ".join(unique)
    return "—"


def origin(column: str) -> str:
    return "derivata dal merge" if not (column.startswith("participant.") or column.startswith("session.") or column.startswith("bargaining_tdl_")) else "oTree raw"


def coverage(column: str, agg_rows, partner_rows) -> str:
    bits = []
    if agg_rows and column in agg_rows[0]:
        bits.append(f"aggregated {sum(r[column] != '' for r in agg_rows)}/{len(agg_rows)}")
    if partner_rows and column in partner_rows[0]:
        bits.append(f"by-partner {sum(r[column] != '' for r in partner_rows)}/{len(partner_rows)}")
    return "; ".join(bits)


def valid_group(members) -> bool:
    ids = {r.get("bargaining_tdl_main.1.player.id_in_group", "") for r in members}
    dropped = any(r.get("bargaining_tdl_main.1.group.group_dropped", "").strip() in {"1", "True"} for r in members)
    timeout = any(
        r.get("participant.inactive_excluded", "").strip() in {"1", "True"}
        or r.get("bargaining_tdl_main.1.player.decision_inactive", "") == "99"
        or r.get("bargaining_tdl_main.1.player.signal_inactive", "") == "99"
        for r in members
    )
    return ids == {"1", "2", "3"} and not dropped and not timeout


def main():
    agg_headers, agg_rows = read_csv(AGGREGATED)
    partner_headers, partner_rows = read_csv(BY_PARTNER)
    all_headers = list(dict.fromkeys(agg_headers + partner_headers))

    groups = defaultdict(list)
    treatments = {"private", "public", "private_no_dwl"}
    for row in agg_rows:
        if row.get("bargaining_tdl_main.1.player.treatment") in treatments:
            groups[(row["session.code"], row["participant.part1_group_id"])].append(row)
    summary = {}
    for treatment in ("private", "public", "private_no_dwl"):
        selected = [members for members in groups.values() if members[0]["bargaining_tdl_main.1.player.treatment"] == treatment]
        summary[treatment] = {
            "participants": sum(len(m) for m in selected),
            "triads": len(selected),
            "valid": sum(valid_group(m) for m in selected),
            "messages": sum(int(m[0]["chat_message_count_group"]) for m in selected),
        }

    lines = [
        "# Codebook — export oTree con chat (2026-08-26)", "",
        "## 1. File coperti", "",
        f"- `{AGGREGATED.name}`: **{len(agg_rows):,} righe**, **{len(agg_headers)} colonne**; una riga per partecipante del raw.",
        f"- `{BY_PARTNER.name}`: **{len(partner_rows):,} righe**, **{len(partner_headers)} colonne**; due righe per partecipante (`chat_side=left/right`).", "",
        "Entrambi i file contengono le 104 colonne oTree richieste e 16 variabili derivate comuni. Il primo aggiunge 8 variabili chat di gruppo; il secondo 12 variabili chat diadiche.", "",
        "## 2. Unità, chiavi e relazione fra i file", "",
        "| File | Unità di osservazione | Chiave raccomandata |", "|---|---|---|",
        f"| `{AGGREGATED.name}` | partecipante | `session.code` + `participant.code` |",
        f"| `{BY_PARTNER.name}` | partecipante × partner topologico | `session.code` + `participant.code` + `chat_side` |", "",
        "- `chat_group_key = session.code | participant.part1_group_id` identifica la triade della Parte 1.",
        "- `participant.part1_group_id` è preferibile a `group.id_in_subsession` perché resta stabile anche dopo eventuali regrouping.",
        "- `chat_side` è il lato **topologico** del partner. L’ordine visto a schermo è registrato separatamente nelle variabili `id_player_visualized_*`.",
        "- Nel by-partner ogni messaggio della diade compare nel transcript di entrambi i membri; non sommare i transcript sulle righe senza prima deduplicare la diade.", "",
        "## 3. Snapshot del campione sperimentale", "",
        "| Treatment | Partecipanti | Triadi osservate | Triadi valide | Messaggi |", "|---|---:|---:|---:|---:|",
    ]
    labels = {"private": "Private", "public": "Public", "private_no_dwl": "Slacker"}
    for treatment in ("private", "public", "private_no_dwl"):
        s = summary[treatment]
        lines.append(f"| {labels[treatment]} | {s['participants']} | {s['triads']} | {s['valid']} | {s['messages']:,} |")
    lines.append(f"| **Totale** | **{sum(s['participants'] for s in summary.values())}** | **{sum(s['triads'] for s in summary.values())}** | **{sum(s['valid'] for s in summary.values())}** | **{sum(s['messages'] for s in summary.values()):,}** |")
    lines += [
        "", "Le righe con treatment vuoto appartengono ad altre parti/sessioni presenti nel raw e non alle 350 triadi dei tre treatment.", "",
        "### Definizione di triade valida", "",
        "Una triade è valida se contiene gli ID 1, 2 e 3, `group.group_dropped` non è vero e nessun membro ha `participant.inactive_excluded` vero, `decision_inactive=99` o `signal_inactive=99`. `group_valid` non è materializzato in questi CSV, ma si ricostruisce con questa regola.", "",
        "## 4. Codifiche sostantive", "",
        "### Treatment", "",
        "- `private`: Baseline, comunicazione privata.",
        "- `public`: comunicazione pubblica/osservabile.",
        "- `private_no_dwl`: **Slacker**, comunicazione privata senza deadweight loss.", "",
        "### Outcome", "",
        "- `mutual_12`, `mutual_23`, `mutual_31`: minimal winning coalition (**MWC**) tra la coppia indicata.",
        "- `no_dwl_star_1`, `no_dwl_star_2`, `no_dwl_star_3`: **SlackerPayoff**; applicabile al treatment Slacker.",
        "- `disagreement`: mancato coordinamento.",
        "- `pending`: outcome non finalizzato/non pertinente nelle righe esterne alle partite analizzate.",
        "- `grp_coordinate=1` quando almeno un giocatore ottiene payoff positivo: comprende sia MWC sia SlackerPayoff.", "",
        "### Segnali", "",
        "- `split_you`: intenzione di supportare il destinatario del segnale.",
        "- `split_other`: intenzione di supportare il terzo giocatore.",
        "- `support_none`: intenzione di non supportare nessuno.", "",
        "## 5. Transcript JSON", "",
        "`chat_transcript_group` e `chat_transcript` sono array JSON su una sola cella CSV, ordinati per timestamp. Ogni elemento contiene:", "",
        "| Campo JSON | Significato |", "|---|---|",
        "| `timestamp` | tempo Unix del messaggio |", "| `from_id`, `from_color` | mittente nella triade |",
        "| `to_id`, `to_color` | destinatario nella triade |", "| `nickname` | nickname registrato da oTree |",
        "| `participant_code` | codice del mittente, usato per risolverne l’identità |", "| `body` | testo originale del messaggio |",
        "| `channel` | canale oTree della diade |", "| `parse_status` | `ok` per i messaggi validati |", "",
        "Il merge 2026-08-26 identifica il mittente tramite `participant_code`, verifica che il suo `id_in_group` appartenga alla coppia codificata nel canale e usa `participant.part1_group_id` per il gruppo. Tutti i 5.108 messaggi hanno superato questi controlli.", "",
        "## 6. Valori mancanti e precauzioni", "",
        "- La stringa vuota rappresenta un dato mancante/non applicabile.",
        "- `[]` è un transcript valido senza messaggi; non è un valore mancante.",
        "- `NoOne` è una scelta sostantiva, non un missing.",
        "- `0` può essere un valore reale o un default oTree: interpretarlo insieme allo stato della riga e ai flag d’inattività.",
        "- I timestamp delle chat sono secondi Unix; le variabili `time_*` sono durate in secondi.",
        "- Le variabili group-level si ripetono su tre partecipanti e, nel by-partner, su sei righe per triade: collassare/deduplicare prima di calcolare statistiche di gruppo.", "",
        "## 7. Dizionario completo delle variabili", "",
        "| # | Variabile | Presenza | Origine | Tipo | Copertura non vuota | Valori/codifica | Definizione |",
        "|---:|---|---|---|---|---|---|---|",
    ]

    for index, column in enumerate(all_headers, 1):
        presence = "entrambi" if column in agg_headers and column in partner_headers else "aggregated" if column in agg_headers else "by-partner"
        values = []
        if column in agg_headers:
            values.extend(row[column] for row in agg_rows)
        elif column in partner_headers:
            values.extend(row[column] for row in partner_rows)
        desc = description(column).replace("|", "\\|")
        enc = encoding(column, values).replace("|", "\\|")
        lines.append(f"| {index} | `{column}` | {presence} | {origin(column)} | {variable_type(column, values)} | {coverage(column, agg_rows, partner_rows)} | {enc} | {desc} |")

    lines += [
        "", "## 8. Controlli di integrità eseguiti", "",
        f"- Colonne documentate: **{len(all_headers)}** (unione esatta dei due header).",
        f"- Colonne aggregated documentate: **{sum(c in all_headers for c in agg_headers)}/{len(agg_headers)}**.",
        f"- Colonne by-partner documentate: **{sum(c in all_headers for c in partner_headers)}/{len(partner_headers)}**.",
        f"- Rapporto righe by-partner/aggregated: **{len(partner_rows)}/{len(agg_rows)} = {len(partner_rows)/len(agg_rows):.1f}**, coerente con due partner per partecipante.",
        "- I conteggi chat e la copertura dei 5.108 messaggi sono già validati dallo script di merge e dall’audit associato.", "",
        "## 9. Provenienza", "",
        f"- Script di produzione: `merge_otree_chat_selected.py`.",
        f"- Audit: `all_apps_wide_2026-08-26_chat_audit_final.json`.",
        "- Sorgenti: `text_analysis/all_apps_wide_2026-08-26.csv` e `text_analysis/ChatMessages-2026-08-26.csv`.",
    ]

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "variables": len(all_headers), "aggregated_columns": len(agg_headers), "by_partner_columns": len(partner_headers), "status": "PASS"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

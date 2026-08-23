from os import environ
from pathlib import Path


def _load_dotenv():
    """Carica .env in dev (funziona con `otree devserver` e altri comandi oTree)."""
    env_path = Path(__file__).resolve().parent / '.env'
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

_BARGAINING_APP_SEQUENCE = [
    'bargaining_tdl_intro', 'bargaining_tdl_main', 'bargaining_tdl_survey',
]
# --- CODICI PROLIFIC — PILOT (solo test) ---
# Restano solo per le config di collaudo in fondo a SESSION_CONFIGS: non sono i
# codici della raccolta dati.
PUBLIC_COMPLETION  = "https://app.prolific.com/submissions/complete?cc=CTKDYE8E"
PUBLIC_DROPOUT_CQ  = "https://app.prolific.com/submissions/complete?cc=C7WZD8AX"
PUBLIC_DROPOUT_INE = "https://app.prolific.com/submissions/complete?cc=CHWGZZMH"

PRIVATE_COMPLETION  = "https://app.prolific.com/submissions/complete?cc=C1G2IEC2"
PRIVATE_DROPOUT_CQ  = "https://app.prolific.com/submissions/complete?cc=C13STBXG"
PRIVATE_DROPOUT_INE = "https://app.prolific.com/submissions/complete?cc=CSXVWB27"

NO_DWL_COMPLETION  = "https://app.prolific.com/submissions/complete?cc=CU9DDEAQ"
NO_DWL_DROPOUT_CQ  = "https://app.prolific.com/submissions/complete?cc=CMPNPYY3"
NO_DWL_DROPOUT_INE = "https://app.prolific.com/submissions/complete?cc=CFORQW3N"

# --- CODICI PROLIFIC — RACCOLTA DATI ---
# Fonte: docs/PROLIFIC_CODES_COLLECTION_SCHEDULE.md e
# "docs/Schedule sessions - Sheet2.csv".
#
# I codici sono specifici per giorno e fascia oraria e non vanno riutilizzati in
# un altro slot. Per questo ogni slot ha la propria session config: chi apre la
# sessione sceglie lo slot dall'elenco, non i codici, e sbagliarli richiede di
# scegliere la riga sbagliata.
#
# bargaining_tdl_common/test_prolific_codes.py rilegge i due documenti e
# fallisce se questo blocco diverge da loro.

PROLIFIC_COMPLETE_URL = "https://app.prolific.com/submissions/complete?cc={}"


def _prolific_link(code):
    return PROLIFIC_COMPLETE_URL.format(code)


TREATMENT_LABELS = {
    'private': 'Baseline',
    'public': 'Public',
    'private_no_dwl': 'Slacker',
}

# completion = esperimento completato
# dropout_cq = escluso per control questions sbagliate
# dropout_timeout = escluso per inattivita' fino al timeout
COLLECTION_SLOTS = [
    dict(key='baseline_d1', day=1, weekday='Mon', slot='15:30-17:30',
         study='Study BaselineD1', treatment='private', participants=174,
         completion='C19QG34V', dropout_cq='CYZ535HK', dropout_timeout='C1NX1SC7'),
    dict(key='public_d1', day=1, weekday='Mon', slot='17:45-19:00',
         study='Study PublicD1', treatment='public', participants=174,
         completion='C1NLKVJO', dropout_cq='C1GZP9YZ', dropout_timeout='C12QTGB5'),
    dict(key='slacker_d1', day=1, weekday='Mon', slot='19:15-20:30',
         study='Study SlackerD1', treatment='private_no_dwl', participants=171,
         completion='CS0SK0FT', dropout_cq='CBPGAP2T', dropout_timeout='CVCH885O'),

    dict(key='public_d2', day=2, weekday='Tue', slot='15:30-17:30',
         study='Study PublicD2', treatment='public', participants=174,
         completion='C187VMJZ', dropout_cq='C178PR0K', dropout_timeout='COYX7OAP'),
    dict(key='slacker_d2', day=2, weekday='Tue', slot='17:45-19:00',
         study='Study SlackerD2', treatment='private_no_dwl', participants=174,
         completion='C1LRIGON', dropout_cq='C1A5YEEH', dropout_timeout='C16OVXXD'),
    dict(key='baseline_d2', day=2, weekday='Tue', slot='19:15-20:30',
         study='Study BaselineD2', treatment='private', participants=171,
         completion='C1OO523E', dropout_cq='CJA3HCA8', dropout_timeout='C1B3RJS2'),

    dict(key='slacker_d3', day=3, weekday='Wed', slot='15:30-17:30',
         study='Study SlackerD3', treatment='private_no_dwl', participants=174,
         completion='CTS7WY83', dropout_cq='C18TF8C6', dropout_timeout='CQJD948X'),
    dict(key='baseline_d3', day=3, weekday='Wed', slot='17:45-19:00',
         study='Study BaselineD3', treatment='private', participants=174,
         completion='C6CWP51H', dropout_cq='CRGEJSNX', dropout_timeout='CW12WXEV'),
    dict(key='public_d3', day=3, weekday='Wed', slot='19:15-20:30',
         study='Study PublicD3', treatment='public', participants=171,
         completion='CMV2DGMZ', dropout_cq='CG5BL66Z', dropout_timeout='C18NC41T'),
]


def _collection_config(slot):
    """Una session config per slot, con i suoi tre codici gia' dentro."""
    label = TREATMENT_LABELS[slot['treatment']]
    return dict(
        name=f"bargaining_tdl_{slot['key']}",
        display_name=(
            f"Day {slot['day']} ({slot['weekday']}) {slot['slot']} — "
            f"{label} — {slot['study']}"
        ),
        app_sequence=_BARGAINING_APP_SEQUENCE,
        # Numero previsto per lo slot: precompila il campo alla creazione della
        # sessione.
        num_demo_participants=slot['participants'],
        completionlink=_prolific_link(slot['completion']),
        dropoutlink_cq=_prolific_link(slot['dropout_cq']),
        dropoutlink_inactive=_prolific_link(slot['dropout_timeout']),
        active_treatments=[slot['treatment']],
    )


# Raccolta dati: una config per slot, nell'ordine del calendario. Sono le
# prime dell'elenco perche' sono quelle da usare.
SESSION_CONFIGS = [_collection_config(slot) for slot in COLLECTION_SLOTS] + [
    # --- Solo collaudo: codici del pilot, non della raccolta dati. ---
    # Il trattamento qui e' misto o i codici sono vecchi: aprirle per una
    # sessione vera manderebbe i partecipanti al codice sbagliato.
    dict(
        name='bargaining_tdl',
        display_name="[TEST] Bargaining Game — 3-arm RCT (codici pilot)",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=18,
        completionlink=PUBLIC_COMPLETION,
        active_treatments=['private', 'public', 'private_no_dwl'],
    ),
    dict(
        name='bargaining_tdl_public',
        display_name="[TEST] Public TDL only (codici pilot)",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=PUBLIC_COMPLETION,
        dropoutlink_cq=PUBLIC_DROPOUT_CQ,
        dropoutlink_inactive=PUBLIC_DROPOUT_INE,
        active_treatments=['public'],
    ),
    dict(
        name='bargaining_tdl_private',
        display_name="[TEST] Private TDL only (codici pilot)",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=PRIVATE_COMPLETION,
        dropoutlink_cq=PRIVATE_DROPOUT_CQ,
        dropoutlink_inactive=PRIVATE_DROPOUT_INE,
        active_treatments=['private'],
    ),
    dict(
        name='bargaining_tdl_private_no_dwl',
        display_name="[TEST] Private No-DWL only (codici pilot)",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=NO_DWL_COMPLETION,
        dropoutlink_cq=NO_DWL_DROPOUT_CQ,
        dropoutlink_inactive=NO_DWL_DROPOUT_INE,
        active_treatments=['private_no_dwl'],
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=1.00, doc="",
    control_questions_max_attempts=5,  # Numero massimo di tentativi per le control questions
    skip_intro_control_questions=False,  # Temporarily disable intro control questions
    use_test_timers=False,  # Set all page timers to 60s for testing
    require_prolific_id=True,  # False solo in dev locale; produzione: sempre True
)

PARTICIPANT_FIELDS = [
    'prolific_id',
    'prolific_study_id',
    'prolific_session_id',
    'inactive_excluded',
    'inactive_excluded_reason',
    'group_dropped',
    'part1_payoff_eligible',
    'treatment',
    'allocation_slot',
    'allocation_block',
    'allocation_attempt',
    'assignment_timestamp',
    'assignment_status',
    'is_replacement',
    'allocation_failure_reason',
    'group_outcome',
    'part1_group_id',
]
SESSION_FIELDS = [
    'randomization_seed',
    'randomization_schedule',
    'randomization_block_size',
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = [
    dict(
        name='prolific',
        display_name='Prolific participants',
        welcome_page='_welcome_pages/ProlificRoomWelcome.html',
    ),
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


# SECRET_KEY: usa variabile d'ambiente in produzione, altrimenti usa un placeholder per sviluppo
SECRET_KEY = environ.get('SECRET_KEY', '{{ secret_key }}')

INSTALLED_APPS = ['otree']

# Compat patch: oTree 5.x expects ExceptionMiddleware._lookup_exception_handler,
# removed in newer Starlette. Reintroduce it using Starlette helper.
try:
    import otree.patch as _otree_patch
    from starlette._exception_handler import _lookup_exception_handler as _st_lookup_exception_handler

    if not hasattr(_otree_patch.ExceptionMiddleware, '_lookup_exception_handler'):
        def _lookup_exception_handler_compat(self, exc):
            handlers = getattr(self, '_exception_handlers', {})
            return _st_lookup_exception_handler(handlers, exc)

        _otree_patch.ExceptionMiddleware._lookup_exception_handler = _lookup_exception_handler_compat
except Exception:
    pass

# # Patch oTree bot: response.url può essere un oggetto URL (Starlette/httpx), unquote() richiede str
# try:
#     from urllib.parse import unquote, urlsplit
#     import otree.bots.bot as _bot
#     _fget = _bot.ParticipantBot.response.fget
# 
#     def _response_setter(self, response):
#         url = response.url
#         if not isinstance(url, str):
#             url = str(url)
#         self.url = unquote(url)
#         self.path = urlsplit(self.url).path
#         self._response = response
#         self.html = response.content.decode('utf-8')
# 
#     _bot.ParticipantBot.response = property(_fget, _response_setter)
# except Exception:
#     pass
# 
# # Patch oTree chat history: SQLAlchemy recente non accetta .values('nickname', ...)
# try:
#     from otree.channels import consumers as _consumers  # type: ignore
#     from otree.models_concrete import ChatMessage as _ChatMessage  # type: ignore
# 
#     def _wschat_get_history(self, channel):
#         rows = list(_ChatMessage.objects_filter(channel=channel).order_by('timestamp'))
#         return [
#             {
#                 'nickname': row.nickname,
#                 'body': row.body,
#                 'participant_id': row.participant_id,
#             }
#             for row in rows
#         ]
# 
#     _consumers.WSChat._get_history = _wschat_get_history
# except Exception:
#     pass

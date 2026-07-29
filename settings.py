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
_BARGAINING_COMPLETIONLINK = environ.get(
    'PROLIFIC_COMPLETION_URL',
    'https://app.prolific.com/submissions/complete?cc=C1HQEIID',
)

SESSION_CONFIGS = [
    # Produzione RCT: tre trattamenti, randomizzati in blocchi permutati 3:3:3.
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game — 3-arm RCT",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=18,
        completionlink=_BARGAINING_COMPLETIONLINK,
        active_treatments=['private', 'public', 'private_no_dwl'],
    ),
    # Trattamenti isolati per test e pilot.
    dict(
        name='bargaining_tdl_public',
        display_name="Bargaining Game — Public TDL only",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=_BARGAINING_COMPLETIONLINK,
        active_treatments=['public'],
    ),
    dict(
        name='bargaining_tdl_private',
        display_name="Bargaining Game — Private TDL only",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=_BARGAINING_COMPLETIONLINK,
        active_treatments=['private'],
    ),
    dict(
        name='bargaining_tdl_private_no_dwl',
        display_name="Bargaining Game — Private No-DWL only",
        app_sequence=_BARGAINING_APP_SEQUENCE,
        num_demo_participants=9,
        completionlink=_BARGAINING_COMPLETIONLINK,
        active_treatments=['private_no_dwl'],
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=3.00, doc="",
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

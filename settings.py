from os import environ


SESSION_CONFIGS = [
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game (TDL + Async)",
        app_sequence=['bargaining_tdl_intro', 'bargaining_tdl_main', 'bargaining_tdl_part3', 'bargaining_tdl_survey'],
        num_demo_participants=9,
        completionlink=environ.get(
            'PROLIFIC_COMPLETION_URL',
            'https://app.prolific.com/submissions/complete?cc=C1HQEIID',
        ),
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    control_questions_max_attempts=5,  # Numero massimo di tentativi per le control questions
    skip_intro_control_questions=False,  # Temporarily disable intro control questions
    use_test_timers=False,  # Set all page timers to 60s for testing
    require_prolific_id=True,  # Allow bypass of Prolific ID during local testing
)

PARTICIPANT_FIELDS = [
    'prolific_id',
    'prolific_study_id',
    'prolific_session_id',
    'inactive_excluded',
    'inactive_excluded_reason',
    'group_dropped',
    'part1_payoff_eligible',
]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = [
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

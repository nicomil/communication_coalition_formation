from os import environ


SESSION_CONFIGS = [
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        app_sequence=['guess_two_thirds', 'payment_info'],
        num_demo_participants=3,
    ),
    dict(
        name='survey', app_sequence=['survey', 'payment_info'], num_demo_participants=1
    ),
    # dict(
    #    name='phase_one_bargaining',
    #    display_name="Phase 1 Bargaining Game",
    #    app_sequence=['phase_one_bargaining'],
    #    num_demo_participants=3,
    # ),
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game (TDL + Async)",
        app_sequence=['bargaining_tdl_intro', 'bargaining_tdl_main', 'bargaining_tdl_part2', 'bargaining_tdl_part3'],
        num_demo_participants=6,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
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

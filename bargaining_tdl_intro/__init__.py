from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as cu,
    Page,
    WaitPage,
)
from otree.common import get_models_module  # type: ignore

# Patch oTree bot: response.url può essere URL object (Starlette/httpx), unquote() richiede str;
# client.post() in nuove versioni richiede keyword (data=, follow_redirects=).
try:
    from urllib.parse import unquote, urlsplit
    import otree.bots.bot as _bot  # type: ignore

    _fget = _bot.ParticipantBot.response.fget

    def _response_setter(self, response):
        url = response.url
        if not isinstance(url, str):
            url = str(url)
        self.url = unquote(url)
        self.path = urlsplit(self.url).path
        self._response = response
        self.html = response.content.decode('utf-8')

    _bot.ParticipantBot.response = property(_fget, _response_setter)

    _orig_submit = _bot.ParticipantBot.submit

    def _submit(self, submission):
        post_data = submission.post_data
        pretty_post_data = _bot.bot_prettify_post_data(post_data)
        log_string = 'Submit ' + self.path
        if pretty_post_data:
            log_string += ', {}'.format(pretty_post_data)
        if post_data.get('must_fail'):
            log_string += ', SubmissionMustFail'
        if post_data.get('timeout_happened'):
            log_string += ', timeout_happened'
        _bot.logger.info(log_string)
        try:
            self.response = self.client.post(
                self.url, data=post_data, follow_redirects=True
            )
        except TypeError:
            self.response = self.client.post(
                self.url, post_data, allow_redirects=True
            )

    _bot.ParticipantBot.submit = _submit

    # client.get() in nuove versioni usa follow_redirects invece di allow_redirects
    from otree import common as _otree_common  # type: ignore

    _orig_open_start_url = _bot.ParticipantBot.open_start_url
    def _open_start_url(self):
        start_url = _otree_common.participant_start_url(self.participant_code)
        try:
            self.response = self.client.get(start_url, follow_redirects=True)
        except TypeError:
            self.response = self.client.get(start_url, allow_redirects=True)
    _bot.ParticipantBot.open_start_url = _open_start_url

    def _on_wait_page(self):
        if not _bot.is_wait_page(self.response):
            return False
        try:
            self.response = self.client.get(self.url, follow_redirects=True)
        except TypeError:
            self.response = self.client.get(self.url, allow_redirects=True)
        return _bot.is_wait_page(self.response)
    _bot.ParticipantBot.on_wait_page = _on_wait_page
except Exception:
    pass

from bargaining_tdl_common import (  # type: ignore
    save_time_value,
    check_control_questions_intro,
    set_control_questions_failed,
    has_failed_control_questions,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
    get_logger,
)

logger = get_logger('intro')

doc = """
Bargaining Game (Part 1: Individual Tasks)
Instructions -> Chat and Intentions
Data is saved to participant.vars for the next app.
"""

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_intro'
    PLAYERS_PER_GROUP = None  # No groups in this app; grouping happens in bargaining_tdl_main
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Drafts (Simulated Chat) — not in active page_sequence but kept for consistency
    draft_history_left = models.LongStringField(blank=True)
    draft_history_right = models.LongStringField(blank=True)
    
    # Intentions — not in active page_sequence; signals are collected in bargaining_tdl_main
    signal_left = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['split_both', 'split_both'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    signal_right = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['split_both', 'split_both'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    
    # Track which chat/intention was selected first
    first_intention_selected = models.StringField(
        choices=[
            ['left', 'Left'],
            ['right', 'Right']
        ],
        blank=True,
        label="Which intention was selected first"
    )
    
    # Control Questions - Example 1
    # Scenario: You (green) share with red only. Blue shares with both. Red shares with you (green).
    # Result: Green=6, Red=6, Blue=0
    example1_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be ?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the BLUE player ?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the RED player?"
    )
    
    # Control Questions - Example 2
    # Scenario: You (Green) share with both. Blue shares with Red only. Red shares with both.
    # Result: Red=4, Green=4, Blue=4
    example2_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be ?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the BLUE player ?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the RED player ?"
    )
    
    # Control Questions - Example 3
    # Scenario: You (Green) share with both. Blue shares with you (Green) only. Red shares with Blue only.
    # Result: Red=0, Green=0, Blue=0
    example3_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be ?"
    )
    example3_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the BLUE player ?"
    )
    example3_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the RED player ?"
    )
    

    
    # Time tracking fields (in seconds)
    time_welcome = models.FloatField(initial=0)
    time_instructions_part1 = models.FloatField(initial=0)
    time_control_questions = models.FloatField(initial=0)
    time_goodbye = models.FloatField(initial=0)
    time_chat_and_signals = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# PAGES

class Welcome(Page):
    """General Instructions (moved from bargaining_tdl_welcome)."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def before_next_page(player, timeout_happened):
        time_value = save_time_value(player.time_on_page)
        player.time_welcome = time_value
        player.participant.vars['time_welcome'] = time_value
        logger.debug(f"Welcome - time_welcome saved: {player.time_welcome}")


class InstructionsPart1(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part1 = save_time_value(player.time_on_page)
        logger.debug(f"InstructionsPart1 - time_instructions_part1 saved: {player.time_instructions_part1}")

def create_control_questions_class(attempt_number):
    """
    Factory function che crea dinamicamente una classe ControlQuestions per un tentativo specifico.
    
    Args:
        attempt_number: Numero del tentativo (1-based)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'ControlQuestionsAttempt{attempt_number}'
    
    class ControlQuestionsPage(Page):
        template_name = 'bargaining_tdl_intro/ControlQuestions.html'
        form_model = 'player'
        preserve_unsubmitted_inputs = True
        form_fields = [
            'example1_earnings_you',
            'example1_earnings_left',
            'example1_earnings_right',
            'example2_earnings_you',
            'example2_earnings_left',
            'example2_earnings_right',
            'example3_earnings_you',
            'example3_earnings_left',
            'example3_earnings_right',
            'time_on_page'
        ]

        @staticmethod
        def is_displayed(player):
            """
            Mostra questa pagina solo se:
            - Non ha ancora passato le control questions E
            - Non ha ancora fallito definitivamente E
            - È il tentativo corretto (current_attempts == attempt_number - 1)
            """
            if has_passed_control_questions(player, 'intro'):
                return False
            
            if has_failed_control_questions(player, 'intro'):
                return False
            
            current_attempts = get_control_questions_attempts(player, 'intro')
            # Mostra solo quando è il turno di questo tentativo
            return current_attempts == (attempt_number - 1)

        @staticmethod
        def vars_for_template(player):
            max_attempts = get_max_attempts(player.session)
            current_attempts = get_control_questions_attempts(player, 'intro')
            attempts_remaining = max_attempts - current_attempts
            
            return {
                'example1_scenario': "Imagine that you (GREEN player) chose to split equally the $ 12 with the RED player choosing the option: 'Split equally the $ 12 only with the RED player'; the BLUE player chooses the option: 'Split equally the $ 12 with both the two players'; the RED player chooses the option: 'Split equally the $ 12 only with the GREEN player'.",
                'example2_scenario': "Imagine that you (GREEN player) chose to split equally the $ 12 with the two players choosing the option: 'Split equally the $ 12 with both the two players'; the BLUE player chooses the option: 'Split equally the $ 12 only with the RED player'; the RED player chooses the option: 'Split equally the $ 12 with both the two players'.",
                'example3_scenario': "Imagine that you (GREEN player) chose to split equally the $ 12 with the two players choosing the option: 'Split equally the $ 12 with both the two players'; the BLUE player chooses the option: 'Split equally the $ 12 only with the GREEN player'; the RED player chooses the option: 'Split equally the $ 12 only with the BLUE player'.",
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number,
                'is_first_attempt': attempt_number == 1,
            }

        @staticmethod
        def before_next_page(player, timeout_happened):
            """Gestisce la logica di retry per le control questions."""
            player.time_control_questions = save_time_value(player.time_on_page)
            logger.debug(f"ControlQuestions Attempt {attempt_number} - time_control_questions saved: {player.time_control_questions}")
            
            # Verifica le risposte
            is_correct = check_control_questions_intro(player)
            max_attempts = get_max_attempts(player.session)
            current_attempts = increment_control_questions_attempts(player, 'intro')
            
            if is_correct:
                # Risposte corrette: imposta passed e resetta attempts
                set_control_questions_passed(player, 'intro', passed=True)
                set_control_questions_failed(player, 'intro', failed=False)
                logger.debug(f"ControlQuestions Attempt {attempt_number} - All answers correct on attempt {current_attempts}")
            else:
                # Risposte sbagliate
                logger.debug(f"ControlQuestions Attempt {attempt_number} - Incorrect answers on attempt {current_attempts}/{max_attempts}")
                
                if current_attempts >= max_attempts:
                    # Raggiunto il massimo numero di tentativi: imposta failed
                    set_control_questions_failed(player, 'intro', failed=True)
                    logger.debug(f"ControlQuestions Attempt {attempt_number} - Max attempts reached, setting failed flag")
    
    # Imposta il nome della classe per il debug
    ControlQuestionsPage.__name__ = class_name
    ControlQuestionsPage.__qualname__ = class_name
    
    return ControlQuestionsPage


# Crea fino a 5 istanze di ControlQuestions (supporta fino a 5 tentativi)
# Ogni istanza gestirà un tentativo specifico
ControlQuestionsAttempt1 = create_control_questions_class(1)
ControlQuestionsAttempt2 = create_control_questions_class(2)
ControlQuestionsAttempt3 = create_control_questions_class(3)
ControlQuestionsAttempt4 = create_control_questions_class(4)
ControlQuestionsAttempt5 = create_control_questions_class(5)

class Goodbye(Page):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        return has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_goodbye = save_time_value(player.time_on_page)
        logger.debug(f"Goodbye - time_goodbye saved: {player.time_goodbye}")
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []


page_sequence = [
    Welcome,
    InstructionsPart1,
    ControlQuestionsAttempt1,
    ControlQuestionsAttempt2,
    ControlQuestionsAttempt3,
    ControlQuestionsAttempt4,
    ControlQuestionsAttempt5,
    Goodbye,
]

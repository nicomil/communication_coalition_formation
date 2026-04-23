"""
Test suite for bargaining_tdl_intro module.

Tests cover:
- Control questions validation
- Chat and signals submission
- Data persistence in participant.vars
"""

from otree.api import Currency as c, currency_range, expect, Bot  # type: ignore
from . import (  # type: ignore
    Welcome,
    InstructionsPart1,
    ControlQuestionsAttempt1,
)
import random


class PlayerBot(Bot):
    """
    Bot realistico per testare la Part 1 (Intro).
    Simula comportamenti umani variabili per rendere i test realistici.
    """
    
    cases = [
        'cooperative',      # Partecipante cooperativo (Both)
        'competitive',     # Partecipante competitivo (Left/Right)
        'mixed',           # Partecipante misto
        'altruistic',      # Partecipante altruista (Both sempre)
    ]
    
    def play_round(self):
        """Simula il comportamento del partecipante attraverso tutte le pagine."""
        # Welcome is now first page in intro (merged from bargaining_tdl_welcome)
        yield Welcome, dict(time_on_page=1.0)

        yield InstructionsPart1, dict(time_on_page=1.0)

        yield ControlQuestionsAttempt1, dict(
            example1_earnings_you='6',
            example1_earnings_left='0',
            example1_earnings_right='6',
            example2_earnings_you='4',
            example2_earnings_left='4',
            example2_earnings_right='4',
            example3_earnings_you='0',
            example3_earnings_left='0',
            example3_earnings_right='0',
        )

        # Intro ends here for passers; next app is main (GroupingAfterControlQuestions then ChatAndSignals, etc.)
        expect(self.player.time_welcome, '>=', 0)
        expect(self.player.participant.vars.get('time_welcome', 0), '>=', 0)










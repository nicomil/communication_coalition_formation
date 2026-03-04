"""
Test suite for bargaining_tdl_intro module.

Tests cover:
- Control questions validation
- Chat and signals submission
- Data persistence in participant.vars
"""

from otree.api import Currency as c, currency_range, expect, Bot
from . import *
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
        
        # Welcome page (no form)
        yield Welcome
        
        # Instructions page (no form)
        yield InstructionsPart1
        
        # Control Questions - risposte sempre corrette per permettere il test completo
        # Usa ControlQuestionsAttempt1 (primo tentativo)
        # Le altre pagine (Attempt2-5) non verranno mostrate perché is_displayed ritorna False
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
            payoff_determination='I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'
        )
        
        # ChatAndSignals - comportamento varia in base al case
        case = self.case
        
        # Genera chat history realistiche (simulate)
        chat_left = f"Hi, I'm participant {self.player.id}. Let's work together!"
        chat_right = f"Hello from participant {self.player.id}. I hope we can coordinate."
        
        if case == 'cooperative':
            # Sempre Both per entrambi
            signal_left = "I wish to split the $ 12 equally with both you and player on the right"
            signal_right = "I wish to split the $ 12 equally with both you and player on the left"
        elif case == 'competitive':
            # Strategia competitiva: cerca di formare coalizioni
            signal_left = "I wish to split the $ 12 equally with you only, player on the left."
            signal_right = "I wish to split the $ 12 equally with the other player only, the one on the left."
        elif case == 'mixed':
            # Strategia mista
            signal_left = "I wish to split the $ 12 equally with you only, player on the left."
            signal_right = "I wish to split the $ 12 equally with both you and player on the left"
        else:  # altruistic
            # Sempre Both
            signal_left = "I wish to split the $ 12 equally with both you and player on the right"
            signal_right = "I wish to split the $ 12 equally with both you and player on the left"
        
        yield ChatAndSignals, dict(
            signal_left=signal_left,
            signal_right=signal_right,
            draft_history_left=chat_left,
            draft_history_right=chat_right
        )
        
        # Verifica che i dati siano stati salvati in participant.vars
        expect(self.player.participant.vars.get('signal_left'), signal_left)
        expect(self.player.participant.vars.get('signal_right'), signal_right)
        expect(self.player.participant.vars.get('failed_control_questions'), False)










from otree.api import Currency as c, currency_range, expect, Bot  # type: ignore
from . import (  # type: ignore
    InstructionsPart3,
    ResultsPart3,
)


class PlayerBot(Bot):
    """
    Bot realistico per testare la Part 3 (Three-Person Dictator Game).
    Simula decisioni individuali realistiche.
    """
    
    cases = [
        'share_one',       # Condivide con un solo receiver
        'share_both',      # Condivide con entrambi i receivers
        'selfish',         # Strategia egoista (share_one)
        'cooperative',     # Strategia cooperativa (share_both)
    ]
    
    def play_round(self):
        """Simula il comportamento del partecipante nella Part 3."""
        
        # InstructionsPart3 now includes the decision field.
        case = self.case
        if case in ['share_one', 'selfish']:
            decision = 'share_one'
        else:
            decision = 'share_both'
        
        yield InstructionsPart3, dict(decision=decision, time_on_page=1.0)
        
        # Verifica che la decisione sia stata salvata
        expect(self.player.decision, decision)
        
        # Results page
        yield ResultsPart3, dict(time_on_page=1.0)












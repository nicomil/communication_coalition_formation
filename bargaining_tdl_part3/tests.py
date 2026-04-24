from otree.api import Currency as c, currency_range, expect, Bot  # type: ignore
from . import (  # type: ignore
    InstructionsPart3,
    SummaryPart3,
    ControlQuestionsPart3Attempt1,
    DecisionPart3,
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
        
        # Instructions page (no form)
        yield InstructionsPart3
        
        # Summary page (no form)
        yield SummaryPart3
        
        # Control Questions - risposte sempre corrette
        # Usa ControlQuestionsPart3Attempt1 (primo tentativo)
        # Le altre pagine (Attempt2-5) non verranno mostrate perché is_displayed ritorna False
        yield ControlQuestionsPart3Attempt1, dict(
            example1_earnings_you='4',
            example1_earnings_left='4',
            example1_earnings_right='4',
            example2_earnings_you='6',
            example2_earnings_left='0',
            example2_earnings_right='6',
        )
        
        # Verifica che le control questions siano corrette
        expect(self.player.all_control_questions_correct, True)
        
        # Decision - la scelta varia in base al case
        case = self.case
        
        if case == 'share_one':
            decision = 'share_one'
        elif case == 'share_both':
            decision = 'share_both'
        elif case == 'selfish':
            decision = 'share_one'
        else:  # cooperative
            decision = 'share_both'
        
        yield DecisionPart3, dict(decision=decision)
        
        # Verifica che la decisione sia stata salvata
        expect(self.player.decision, decision)
        
        # Results page
        yield ResultsPart3
        
        # Verifica che il payoff di Part 2 sia stato calcolato
        # (viene calcolato in vars_for_template di ResultsPart3)
        part2_payoff_data = self.player.participant.vars.get('part2_payoff_data')
        expect(part2_payoff_data, '!=', None)
        
        # Verifica che i dati del payoff siano presenti
        expect(part2_payoff_data.get('payoff'), '!=', None)












from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    """
    Bot realistico per testare la Part 3 (Three-Person Dictator Game).
    Simula decisioni individuali realistiche.
    """
    
    cases = [
        'share_left',      # Condivide solo con left
        'share_right',     # Condivide solo con right
        'share_both',      # Condivide con entrambi
        'selfish',         # Strategia egoista (share_left o share_right)
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
            example2_earnings_you='0',
            example2_earnings_left='6',
            example2_earnings_right='6',
            payoff_question='I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'
        )
        
        # Verifica che le control questions siano corrette
        expect(self.player.all_control_questions_correct, True)
        
        # Decision - la scelta varia in base al case
        case = self.case
        
        if case == 'share_left':
            decision = 'share_left'
        elif case == 'share_right':
            decision = 'share_right'
        elif case == 'share_both':
            decision = 'share_both'
        elif case == 'selfish':
            # Strategia egoista: sceglie share_left o share_right
            decision = 'share_left'  # o 'share_right', a scelta
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
        expect(part2_payoff_data.get('selected_question'), '!=', None)
        expect(part2_payoff_data.get('payoff'), '!=', None)












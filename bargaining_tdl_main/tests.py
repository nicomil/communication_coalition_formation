from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    """
    Bot realistico per testare la Part 1 Main (Decision).
    I bot devono essere raggruppati in gruppi di 3 per testare correttamente.
    """
    
    cases = [
        'all_both',        # Tutti scelgono Both -> payoff 4 per tutti
        'match_12',        # P1->Right, P2->Left -> P1 e P2 vincono (6), P3 perde (0)
        'match_23',        # P2->Right, P3->Left -> P2 e P3 vincono (6), P1 perde (0)
        'match_31',        # P3->Right, P1->Left -> P3 e P1 vincono (6), P2 perde (0)
        'disagreement',    # Nessun match -> tutti 0
        'mixed_strategy',  # Strategia mista per testare vari scenari
    ]
    
    def play_round(self):
        """Simula il comportamento del partecipante nel gioco principale."""
        
        # GroupingWaitPage - oTree gestisce automaticamente il raggruppamento
        # I bot vengono raggruppati in gruppi di 3 automaticamente
        
        # Decision - la scelta varia in base al case e alla posizione nel gruppo
        case = self.case
        id_in_group = self.player.id_in_group
        
        if case == 'all_both':
            decision = 'Both'
        elif case == 'match_12':
            # P1->Right, P2->Left, P3->Both (non partecipa al match)
            if id_in_group == 1:
                decision = 'Right'
            elif id_in_group == 2:
                decision = 'Left'
            else:  # id_in_group == 3
                decision = 'Both'
        elif case == 'match_23':
            # P2->Right, P3->Left, P1->Both
            if id_in_group == 1:
                decision = 'Both'
            elif id_in_group == 2:
                decision = 'Right'
            else:  # id_in_group == 3
                decision = 'Left'
        elif case == 'match_31':
            # P3->Right, P1->Left, P2->Both
            if id_in_group == 1:
                decision = 'Left'
            elif id_in_group == 2:
                decision = 'Both'
            else:  # id_in_group == 3
                decision = 'Right'
        elif case == 'disagreement':
            # Tutti scelgono Left (nessun match)
            decision = 'Left'
        else:  # mixed_strategy
            # Strategia variabile per testare diversi scenari
            if id_in_group == 1:
                decision = 'Right'
            elif id_in_group == 2:
                decision = 'Left'
            else:
                decision = 'Both'
        
        yield Decision, dict(decision_choice=decision)
        
        # ResultsWaitPage - oTree gestisce automaticamente l'attesa
        # Il calcolo del payoff viene fatto in after_all_players_arrive
        
        yield Results
        
        # Verifica che il payoff sia stato calcolato correttamente
        expect(self.player.payoff, '!=', None)
        
        # Verifica payoff specifici in base al case
        if case == 'all_both':
            expect(self.player.payoff, C.PAYOFF_SPLIT)  # 4
        elif case == 'match_12':
            if id_in_group in [1, 2]:
                expect(self.player.payoff, C.PAYOFF_MAX)  # 6
            else:
                expect(self.player.payoff, C.PAYOFF_DISAGREEMENT)  # 0
        elif case == 'match_23':
            if id_in_group in [2, 3]:
                expect(self.player.payoff, C.PAYOFF_MAX)  # 6
            else:
                expect(self.player.payoff, C.PAYOFF_DISAGREEMENT)  # 0
        elif case == 'match_31':
            if id_in_group in [3, 1]:
                expect(self.player.payoff, C.PAYOFF_MAX)  # 6
            else:
                expect(self.player.payoff, C.PAYOFF_DISAGREEMENT)  # 0
        elif case == 'disagreement':
            expect(self.player.payoff, C.PAYOFF_DISAGREEMENT)  # 0
        
        # Verifica che il payoff sia stato salvato in participant.vars
        expect(self.player.participant.vars.get('part1_payoff'), self.player.payoff)





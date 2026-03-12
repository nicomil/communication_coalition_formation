from otree.api import Currency as c, currency_range, expect, Bot
from . import *
from bargaining_tdl_common import set_control_questions_failed


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
        # Nota: 'experiment_terminated' non può essere testato insieme agli altri casi
        # perché richiede che tutti i partecipanti falliscano le control questions
    ]
    
    def play_round(self):
        """Simula il comportamento del partecipante nel gioco principale."""
        
        case = self.case
        
        # Test per ExperimentTerminated page (quando failed_control_questions=True)
        if case == 'experiment_terminated':
            # Imposta il flag per simulare il fallimento delle control questions
            set_control_questions_failed(self.player, 'intro', failed=True)
            
            # ExperimentTerminated page - dovrebbe essere mostrata
            yield ExperimentTerminated, dict(time_on_page=1.0)
            
            # Verifica che il time tracking sia stato salvato
            expect(self.player.time_experiment_terminated, '>=', 0)
            
            # L'esperimento dovrebbe terminare qui (app_after_this_page ritorna [])
            # Non ci dovrebbero essere altre pagine dopo questa
            return
        
        # GroupingAfterControlQuestions is a WaitPage - handled automatically by oTree
        # Chat - save draft messages to participant.vars
        chat_left = "Hi, let's work together!"
        chat_right = "Hello, I hope we can coordinate."
        yield Chat, dict(
            draft_history_left=chat_left,
            draft_history_right=chat_right,
            time_on_page=1.0,
        )
        # Signals - save intentions to participant.vars for DataMappingWaitPage mapping
        signal_left = "I wish to split the $ 12 equally with both you and player on the right"
        signal_right = "I wish to split the $ 12 equally with both you and player on the left"
        yield Signals, dict(
            signal_left=signal_left,
            signal_right=signal_right,
            time_on_page=1.0,
        )
        
        # DataMappingWaitPage is a wait page - bots handle it automatically (no yield)
        
        # Decision - la scelta varia in base al case e alla posizione nel gruppo
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
        
        yield Decision, dict(decision_choice=decision, time_on_page=1.5)
        
        # ResultsWaitPage - oTree gestisce automaticamente l'attesa
        # Il calcolo del payoff viene fatto in after_all_players_arrive
        
        yield Results, dict(time_on_page=2.0)
        
        # Verifica che i time tracking fields siano stati salvati
        expect(self.player.time_decision, '>=', 0)
        expect(self.player.time_results, '>=', 0)
        
        # Verifica che i campi received_* siano stati popolati dopo il mapping
        # (questi vengono popolati in after_all_players_arrive della DataMappingWaitPage)
        # I dati provengono da participant.vars salvati nella fase intro
        expect(self.player.received_history_left, '!=', None)
        expect(self.player.received_history_right, '!=', None)
        expect(self.player.received_signal_left, '!=', None)
        expect(self.player.received_signal_right, '!=', None)
        
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





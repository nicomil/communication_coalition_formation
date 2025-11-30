from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    """
    Bot realistico per testare la Part 2 (MPL Questions).
    Simula risposte realistiche alle 12 domande MPL.
    """
    
    cases = [
        'risk_averse',     # Switching points bassi (preferisce Option 1)
        'risk_neutral',    # Switching points medi
        'risk_loving',     # Switching points alti (preferisce Option 2)
        'mixed',           # Switching points variabili
    ]
    
    def play_round(self):
        """Simula il comportamento del partecipante nelle MPL questions."""
        
        # Instructions page (no form)
        yield InstructionsPart2
        
        # PaymentInstruction page (no form)
        yield PaymentInstructionPart2
        
        # Control Questions - risposte sempre corrette
        yield ControlQuestionsPart2, dict(
            control_question_1='5',
            control_question_2='5'
        )
        
        # Le 12 MPL Questions
        case = self.case
        
        # Determina switching points in base al case
        if case == 'risk_averse':
            # Switching points bassi (0-30) - preferisce Option 1
            base_switch = random.randint(0, 30)
        elif case == 'risk_neutral':
            # Switching points medi (40-60)
            base_switch = random.randint(40, 60)
        elif case == 'risk_loving':
            # Switching points alti (70-100) - preferisce Option 2
            base_switch = random.randint(70, 100)
        else:  # mixed
            # Switching points variabili
            base_switch = random.randint(0, 100)
        
        # Rispondi alle 12 domande MPL
        # Genera tutti i switching points prima (per coerenza)
        switch_values = []
        for question_num in range(1, 13):
            # Aggiungi variazione casuale al switching point base
            variation = random.randint(-10, 10)
            switch_value = max(0, min(100, base_switch + variation))
            switch_values.append(switch_value)
        
        # Submit tutte le 12 domande
        question_classes = [
            MPLQuestion1, MPLQuestion2, MPLQuestion3, MPLQuestion4,
            MPLQuestion5, MPLQuestion6, MPLQuestion7, MPLQuestion8,
            MPLQuestion9, MPLQuestion10, MPLQuestion11, MPLQuestion12
        ]
        
        for i, question_class in enumerate(question_classes):
            question_num = i + 1
            switch_value = switch_values[i]
            
            # Genera choices JSON (simula le scelte dell'utente)
            choices_json = f'{{"switch_value": {switch_value}}}'
            
            # Submit la risposta per questa domanda
            field_switch = f'mpl_question_{question_num}_switch_value'
            field_choices = f'mpl_question_{question_num}_choices'
            
            yield question_class, {field_switch: switch_value, field_choices: choices_json}
        
        # Results page
        yield ResultsPart2
        
        # Verifica che tutte le 12 risposte siano state salvate
        for i in range(1, 13):
            switch_value = getattr(self.player, f'mpl_question_{i}_switch_value', None)
            expect(switch_value, '!=', None)


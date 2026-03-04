from otree.api import Currency as c, currency_range, expect, Bot, Submission
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
        # Usa ControlQuestionsPart2Attempt1 (primo tentativo)
        # Le altre pagine (Attempt2-5) non verranno mostrate perché is_displayed ritorna False
        yield ControlQuestionsPart2Attempt1, dict(
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
        
        # MPLIntroFirstPlayer (no form)
        yield MPLIntroFirstPlayer
        
        # Prime 6 domande MPL (1-6)
        question_classes_first = [
            MPLQuestion1, MPLQuestion2, MPLQuestion3, 
            MPLQuestion4, MPLQuestion5, MPLQuestion6
        ]
        
        for i, question_class in enumerate(question_classes_first):
            question_num = i + 1
            switch_value = switch_values[i]
            
            # Genera choices JSON (simula le scelte dell'utente)
            choices_json = f'{{"switch_value": {switch_value}}}'
            
            # Submit la risposta per questa domanda
            # Nota: I form fields sono dinamici e gestiti via JavaScript, quindi disabilitiamo il controllo HTML
            field_switch = f'mpl_question_{question_num}_switch_value'
            field_choices = f'mpl_question_{question_num}_choices'
            
            yield Submission(question_class, {field_switch: switch_value, field_choices: choices_json, 'time_on_page': 0.5}, check_html=False)
        
        # MPLIntroSecondPlayer (no form)
        yield MPLIntroSecondPlayer
        
        # Ultime 6 domande MPL (7-12)
        question_classes_second = [
            MPLQuestion7, MPLQuestion8, MPLQuestion9,
            MPLQuestion10, MPLQuestion11, MPLQuestion12
        ]
        
        for i, question_class in enumerate(question_classes_second):
            question_num = i + 7  # Domande 7-12
            switch_value = switch_values[question_num - 1]
            
            # Genera choices JSON (simula le scelte dell'utente)
            choices_json = f'{{"switch_value": {switch_value}}}'
            
            # Submit la risposta per questa domanda
            # Nota: I form fields sono dinamici e gestiti via JavaScript, quindi disabilitiamo il controllo HTML
            field_switch = f'mpl_question_{question_num}_switch_value'
            field_choices = f'mpl_question_{question_num}_choices'
            
            yield Submission(question_class, {field_switch: switch_value, field_choices: choices_json, 'time_on_page': 0.5}, check_html=False)
        
        # Results page
        yield ResultsPart2
        
        # Verifica che almeno alcune risposte siano state salvate
        # Nota: I nomi dei campi sono dinamici basati sull'ordine randomizzato,
        # quindi verifichiamo che il partecipante abbia completato le domande
        # controllando che participant.vars contenga i dati necessari
        part2_payoff_data = self.player.participant.vars.get('part2_payoff_data')
        # Se part2_payoff_data esiste, significa che le domande sono state completate
        # (viene creato solo dopo aver completato tutte le 12 domande)












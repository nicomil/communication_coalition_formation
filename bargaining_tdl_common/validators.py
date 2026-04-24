"""
Control questions validators and helpers for bargaining_tdl modules.
"""


def get_max_attempts(session):
    """
    Ottiene il numero massimo di tentativi per le control questions dalla configurazione della sessione.
    
    Args:
        session: oTree Session instance
    
    Returns:
        int: Numero massimo di tentativi (default: 2)
    """
    return session.config.get('control_questions_max_attempts', 5)


def get_control_questions_attempts(player, part_name):
    """
    Ottiene il numero di tentativi effettuati per le control questions di una specifica parte.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
    
    Returns:
        int: Numero di tentativi effettuati (default: 0)
    """
    key = f'control_questions_attempts_{part_name}'
    return player.participant.vars.get(key, 0)


def increment_control_questions_attempts(player, part_name):
    """
    Incrementa il contatore dei tentativi per le control questions di una specifica parte.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
    
    Returns:
        int: Nuovo numero di tentativi
    """
    key = f'control_questions_attempts_{part_name}'
    current = player.participant.vars.get(key, 0)
    new_value = current + 1
    player.participant.vars[key] = new_value
    return new_value


def reset_control_questions_attempts(player, part_name):
    """
    Resetta il contatore dei tentativi per le control questions di una specifica parte.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
    """
    key = f'control_questions_attempts_{part_name}'
    player.participant.vars[key] = 0


def has_passed_control_questions(player, part_name):
    """
    Verifica se il partecipante ha passato le control questions (risposte corrette).
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
    
    Returns:
        bool: True se ha passato, False altrimenti
    """
    key = f'control_questions_passed_{part_name}'
    return player.participant.vars.get(key, False)


def set_control_questions_passed(player, part_name, passed=True):
    """
    Imposta il flag di passaggio delle control questions per una specifica parte.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
        passed: Whether the control questions were passed (default: True)
    """
    key = f'control_questions_passed_{part_name}'
    player.participant.vars[key] = passed
    if passed:
        # Se ha passato, resetta anche i tentativi
        reset_control_questions_attempts(player, part_name)


def set_control_questions_failed(player, part_name, failed=True):
    """
    Set the control questions failed flag for a specific part.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
        failed: Whether the control questions were failed (default: True)
    """
    if part_name == 'intro':
        player.participant.vars['failed_control_questions'] = failed
    elif part_name == 'part2':
        player.participant.vars['failed_control_questions_part2'] = failed
    elif part_name == 'part3':
        player.participant.vars['failed_control_questions_part3'] = failed


def has_failed_control_questions(player, part_name):
    """
    Check if the participant has failed control questions for a specific part.
    
    Args:
        player: oTree Player instance
        part_name: Name of the part ('intro', 'part2', 'part3')
    
    Returns:
        bool: True if control questions were failed, False otherwise
    """
    if part_name == 'intro':
        return player.participant.vars.get('failed_control_questions', False)
    elif part_name == 'part2':
        return player.participant.vars.get('failed_control_questions_part2', False)
    elif part_name == 'part3':
        return player.participant.vars.get('failed_control_questions_part3', False)
    return False


def check_control_questions_intro(player):
    """
    Verifica se tutte le risposte alle control questions di intro sono corrette.
    
    Args:
        player: Player instance from bargaining_tdl_intro
    
    Returns:
        bool: True se tutte le risposte sono corrette, False altrimenti
    """
    # Verifica che tutti i campi siano stati compilati
    if (not player.example1_earnings_you or 
        not player.example1_earnings_left or 
        not player.example1_earnings_right or
        not player.example2_earnings_you or 
        not player.example2_earnings_left or 
        not player.example2_earnings_right or
        not player.example3_earnings_you or 
        not player.example3_earnings_left or 
        not player.example3_earnings_right):
        return False
    
    correct = (
        player.example1_earnings_you == "6" and
        player.example1_earnings_left == "0" and
        player.example1_earnings_right == "6" and
        player.example2_earnings_you == "4" and
        player.example2_earnings_left == "4" and
        player.example2_earnings_right == "4" and
        player.example3_earnings_you == "0" and
        player.example3_earnings_left == "0" and
        player.example3_earnings_right == "0"
    )
    return correct


def check_control_questions_part2(player):
    """
    Verifica se entrambe le risposte alle control questions di part2 sono corrette.
    
    Args:
        player: Player instance from bargaining_tdl_part2
    
    Returns:
        bool: True se entrambe le risposte sono corrette, False altrimenti
    """
    if not player.control_question_1 or not player.control_question_2:
        return False
    
    # Entrambe le risposte corrette devono essere "5" ($5)
    correct = (
        player.control_question_1 == "5" and
        player.control_question_2 == "5"
    )
    return correct


def check_control_questions_part3(player):
    """
    Verifica se tutte le risposte alle control questions di part3 sono corrette.
    
    Args:
        player: Player instance from bargaining_tdl_part3
    
    Returns:
        bool: True se tutte le risposte sono corrette, False altrimenti
    """
    # Verifica che tutti i campi siano stati compilati
    if (not player.example1_earnings_you or 
        not player.example1_earnings_left or 
        not player.example1_earnings_right or
        not player.example2_earnings_you or 
        not player.example2_earnings_left or 
        not player.example2_earnings_right):
        return False
    
    # Example 1: tutte le risposte devono essere '4'
    # Example 2: you='6', e poi (left='0', right='6') OPPURE (left='6', right='0')
    example2_correct = (
        player.example2_earnings_you == '6' and
        (
            (player.example2_earnings_left == '0' and player.example2_earnings_right == '6') or
            (player.example2_earnings_left == '6' and player.example2_earnings_right == '0')
        )
    )

    correct = (
        player.example1_earnings_you == '4' and
        player.example1_earnings_left == '4' and
        player.example1_earnings_right == '4' and
        example2_correct
    )
    return correct


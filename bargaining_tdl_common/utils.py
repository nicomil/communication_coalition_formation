"""
Utility functions for cross-module operations in bargaining_tdl.
"""


def get_main_group_player(player):
    """
    Recupera il player dal gruppo di main (bargaining_tdl_main).
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    In oTree, per accedere ai dati di un'app precedente, dobbiamo:
    1. Ottenere la sessione corrente
    2. Cercare il subsession dell'app main
    3. Trovare il player corrispondente (stesso participant)
    
    Args:
        player: Player instance da qualsiasi app
    
    Returns:
        Player instance da bargaining_tdl_main, o None se non trovato
    """
    try:
        from importlib import import_module
        
        # Importiamo l'app main
        main_app = import_module('bargaining_tdl_main')
        MainPlayer = main_app.Player
        MainSubsession = main_app.Subsession
        
        # Otteniamo la sessione corrente
        session = player.session
        
        # Cerchiamo il subsession dell'app main
        # In oTree, ogni app ha un subsession per round
        # Cerchiamo tutti i subsessions e controlliamo se sono di tipo MainSubsession
        main_subsession = None
        for subsession in session.get_subsessions():
            # Controlliamo se questo subsession è un'istanza di MainSubsession
            if isinstance(subsession, MainSubsession):
                main_subsession = subsession
                break
        
        if main_subsession is None:
            return None
        
        # Cerchiamo il player corrispondente (stesso participant)
        for main_player in main_subsession.get_players():
            if main_player.participant == player.participant:
                return main_player
        
        return None
    except Exception as e:
        # In caso di errore, ritorniamo None
        # Questo può succedere durante i test o se l'app main non è ancora stata eseguita
        import traceback
        print(f"ERROR in get_main_group_player: {e}")
        traceback.print_exc()
        return None


def get_participant_role_in_group(player):
    """
    Determina il ruolo del player nel gruppo (A, B, o C).
    Basato sulla posizione nel gruppo (id 1, 2, o 3).
    
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    Mapping:
    - P1 (id_in_group=1) → A
    - P2 (id_in_group=2) → B  
    - P3 (id_in_group=3) → C
    
    Args:
        player: Player instance da qualsiasi app
    
    Returns:
        str: 'A', 'B', o 'C', o None se non determinabile
    """
    main_player = get_main_group_player(player)
    if main_player is None:
        return None
    
    # Il ruolo è determinato da id_in_group nel gruppo di main
    id_in_group = main_player.id_in_group
    if id_in_group == 1:
        return 'A'
    elif id_in_group == 2:
        return 'B'
    elif id_in_group == 3:
        return 'C'
    return None


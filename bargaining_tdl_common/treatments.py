"""
Framework dei trattamenti per l'esperimento bargaining_tdl.

Registry generico dei trattamenti (varianti sperimentali). Ogni trattamento è un
insieme di flag comportamentali letti dalle varie app. Aggiungere un esperimento
futuro = aggiungere una voce qui + il comportamento che essa controlla.

Stato attuale: l'unica differenza comportamentale è la visibilità della chat nella
Decision finale di Part 1:
  - 'private': vedi solo le conversazioni di cui hai fatto parte (baseline attuale)
  - 'public' : vedi anche la conversazione tra gli altri due partecipanti

NB: la divisione equa 2,2,2 è GLOBALE (non è una differenza tra trattamenti).
"""

# Registry dei trattamenti disponibili.
TREATMENTS = {
    'private': {
        'label': 'Private communication (baseline)',
        'reveal_third_party_chat': False,
    },
    'public': {
        'label': 'Public communication',
        'reveal_third_party_chat': True,
    },
}

DEFAULT_TREATMENT = 'private'
DEFAULT_ACTIVE_TREATMENTS = ['private', 'public']


def get_active_treatments(session):
    """
    Trattamenti attivi per questa sessione (settings.py: `active_treatments`).

    Permette di testare un singolo trattamento in isolamento: basta una session
    config con `active_treatments=['public']`. Vengono mantenuti solo i
    trattamenti registrati, preservando l'ordine dichiarato.
    """
    active = session.config.get('active_treatments', DEFAULT_ACTIVE_TREATMENTS)
    valid = [t for t in active if t in TREATMENTS]
    return valid or [DEFAULT_TREATMENT]


def get_treatment(player):
    """Trattamento assegnato al partecipante (fallback: baseline)."""
    return player.participant.vars.get('treatment') or DEFAULT_TREATMENT


def treatment_flag(player, key, default=None):
    """Legge un flag comportamentale per il trattamento del partecipante."""
    return TREATMENTS.get(get_treatment(player), {}).get(key, default)


def assign_treatment(player, players_per_block=3):
    """
    Assegna il trattamento al PRIMO accesso, a BLOCCHI di `players_per_block`
    per ORDINE DI ARRIVO: i primi N partecipanti che iniziano vanno al primo
    trattamento attivo, i successivi N al secondo, e così via (rotazione di
    blocchi). Con un solo trattamento attivo tutti ricevono quello (test isolato).

    È idempotente: non riassegna se il trattamento è già impostato (es. refresh).
    """
    p = player.participant
    existing = p.vars.get('treatment')
    if existing in TREATMENTS:
        return existing

    active = get_active_treatments(player.session)
    counter = player.session.vars.get('treatment_counter', 0)
    block = counter // max(1, players_per_block)
    treatment = active[block % len(active)]

    player.session.vars['treatment_counter'] = counter + 1
    p.vars['treatment'] = treatment
    return treatment

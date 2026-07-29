"""
Registry dei trattamenti per l'esperimento bargaining_tdl.

I trattamenti combinano due dimensioni indipendenti:
- protocollo di comunicazione: private/public;
- regola di payoff: total deadweight loss/no deadweight loss.

I codici storici ``private`` e ``public`` restano invariati per mantenere
compatibili gli export già raccolti.
"""

TREATMENTS = {
    'private': {
        'label': 'Private communication — Total Deadweight Loss',
        'communication_mode': 'private',
        'payoff_rule': 'tdl',
        'reveal_third_party_chat': False,
        'no_deadweight_loss': False,
    },
    'public': {
        'label': 'Public communication — Total Deadweight Loss',
        'communication_mode': 'public',
        'payoff_rule': 'tdl',
        'reveal_third_party_chat': True,
        'no_deadweight_loss': False,
    },
    'private_no_dwl': {
        'label': 'Private communication — No-Deadweight Loss',
        'communication_mode': 'private',
        'payoff_rule': 'no_dwl',
        'reveal_third_party_chat': False,
        'no_deadweight_loss': True,
    },
}

DEFAULT_TREATMENT = 'private'
DEFAULT_ACTIVE_TREATMENTS = ['private', 'public', 'private_no_dwl']


def get_active_treatments(session):
    """Restituisce i trattamenti validi attivi nella sessione."""
    active = session.config.get('active_treatments', DEFAULT_ACTIVE_TREATMENTS)
    valid = [treatment for treatment in active if treatment in TREATMENTS]
    return valid or [DEFAULT_TREATMENT]


def get_treatment(player):
    """Restituisce il trattamento assegnato, con fallback alla baseline."""
    stored = player.participant.vars.get('treatment')
    return stored if stored in TREATMENTS else DEFAULT_TREATMENT


def get_treatment_config(player):
    """Restituisce configurazione completa del trattamento del partecipante."""
    return TREATMENTS[get_treatment(player)]


def treatment_flag(player, key, default=None):
    """Legge un attributo comportamentale del trattamento."""
    return get_treatment_config(player).get(key, default)

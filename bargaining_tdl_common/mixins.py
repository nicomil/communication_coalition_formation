"""
Mixins and base classes for bargaining_tdl modules.
"""

from otree.api import Page
from .helpers import save_time_value
from .logger import get_logger

logger = get_logger('mixins')


class TimeTrackedPage(Page):
    """
    Base class for pages that automatically track time spent on page.
    
    This mixin automatically saves the time spent on the page to a Player model field.
    The field name must be explicitly set in the subclass using the `time_field_name`
    class attribute.
    
    Usage:
        class MyPage(TimeTrackedPage):
            time_field_name = 'time_my_page'  # REQUIRED: Nome del campo nel Player model
            
            @staticmethod
            def before_next_page(player, timeout_happened):
                super().before_next_page(player, timeout_happened)
                # ... altre operazioni ...
    
    Note:
        - time_field_name DEVE essere definito nella sottoclasse
        - Il campo deve esistere nel Player model
        - Se time_field_name non è definito, viene loggato un warning ma non viene sollevato errore
    """
    
    # Subclass MUST override this with the field name in Player model
    time_field_name = None
    
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """
        Salva automaticamente il tempo speso sulla pagina.
        
        Il campo viene determinato dall'attributo time_field_name della classe.
        Se time_field_name non è definito, viene loggato un warning.
        """
        # Ottieni la classe dalla pagina stessa
        # oTree passa la classe come attributo della pagina
        page_class = getattr(player, '_page_class', None)
        
        if page_class is None:
            # Fallback: cerca nella gerarchia delle classi
            # Questo è un workaround per oTree
            for cls in type(player).__mro__:
                if hasattr(cls, 'time_field_name') and issubclass(cls, TimeTrackedPage):
                    page_class = cls
                    break
        
        if page_class and hasattr(page_class, 'time_field_name'):
            time_field_name = page_class.time_field_name
            if time_field_name:
                time_value = save_time_value(player.time_on_page)
                setattr(player, time_field_name, time_value)
                logger.debug(f"Time saved to {time_field_name}: {time_value} seconds")
                return
        
        # Se non trovato, logga warning
        logger.warning(
            f"TimeTrackedPage: time_field_name not set for page. "
            f"Player: {player.id}, Participant: {player.participant.id}"
        )


"""
Mixins and base classes for bargaining_tdl modules.
"""

from otree.api import Page
from .helpers import save_time_value


class TimeTrackedPage(Page):
    """
    Base class for pages that track time spent on page.
    
    Usage:
        class MyPage(TimeTrackedPage):
            time_field_name = 'time_my_page'  # Nome del campo nel Player model
            
            def before_next_page(player, timeout_happened):
                super().before_next_page(player, timeout_happened)
                # ... altre operazioni ...
    """
    
    # Subclass should override this with the field name in Player model
    time_field_name = None
    
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """
        Salva automaticamente il tempo speso sulla pagina.
        
        Il campo time_field_name deve essere definito nella sottoclasse.
        """
        if TimeTrackedPage.time_field_name:
            time_value = save_time_value(player.time_on_page)
            setattr(player, TimeTrackedPage.time_field_name, time_value)
            print(f"{TimeTrackedPage.__name__} - time saved: {time_value}")
        else:
            # Se time_field_name non è definito, usa il nome della classe
            # come fallback (richiede che il campo esista nel Player model)
            time_value = save_time_value(player.time_on_page)
            # Nota: questo è un fallback, meglio definire time_field_name esplicitamente


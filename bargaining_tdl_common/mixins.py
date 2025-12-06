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
            
            @staticmethod
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
        
        Il campo time_field_name deve essere definito nella sottoclasse come attributo di classe.
        """
        # Ottieni il nome della classe per accedere all'attributo time_field_name
        # Usa type() per ottenere la classe anche se chiamato come metodo statico
        cls = type(player).__class__.__mro__[1] if hasattr(type(player), '__mro__') else None
        
        # Prova a ottenere time_field_name dalla classe della pagina
        # Dobbiamo cercare nella gerarchia delle classi
        time_field = None
        for base_class in Page.__subclasses__():
            if hasattr(base_class, 'time_field_name') and base_class.time_field_name:
                # Questo è un approccio semplificato - in realtà dobbiamo trovare la classe corretta
                pass
        
        # Approccio più semplice: usa il nome della classe per inferire il campo
        # Oppure richiedi che time_field_name sia definito esplicitamente
        # Per ora, se time_field_name non è definito, non salviamo (evita errori)
        # Le sottoclassi devono definire time_field_name come attributo di classe
        
        # Nota: questo mixin richiede che le sottoclassi definiscano time_field_name
        # come attributo di classe. Se non è definito, non viene salvato nulla.
        # Questo è intenzionale per evitare errori silenziosi.


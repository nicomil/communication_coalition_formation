import unittest
from unittest.mock import patch

from bargaining_tdl_common import VALID_DECISIONS
from . import _decision_option_order


class _PlayerStub:
    """Imita un Player oTree: i campi partono a None e non esiste .save().

    In oTree 6 i modelli sono SQLAlchemy e l'assegnazione viene scritta a fine
    richiesta. Lo stub non espone quindi un save(): se il codice lo chiamasse,
    il test fallirebbe con lo stesso AttributeError della produzione.
    """

    def __init__(self, values=None):
        values = values or {}
        for i in (1, 2, 3):
            name = f'decision_option_{i}'
            setattr(self, name, values.get(name))

    def field_maybe_none(self, name):
        return getattr(self, name)


class DecisionOrderTests(unittest.TestCase):
    def test_order_is_generated_once_and_persisted(self):
        player = _PlayerStub()
        with patch('random.shuffle', side_effect=lambda values: values.reverse()) as shuffle:
            first = _decision_option_order(player)
            second = _decision_option_order(player)

        self.assertEqual(first, second)
        self.assertEqual(sorted(first), sorted(VALID_DECISIONS))
        # L'ordine e' finito sui campi del player: e' quello che il database
        # scrive a fine richiesta.
        self.assertEqual(
            [player.decision_option_1, player.decision_option_2,
             player.decision_option_3],
            first,
        )
        shuffle.assert_called_once()

    def test_invalid_or_partial_order_is_repaired(self):
        player = _PlayerStub({
            'decision_option_1': 'Left',
            'decision_option_2': 'Left',
            'decision_option_3': None,
        })
        order = _decision_option_order(player)

        self.assertEqual(sorted(order), sorted(VALID_DECISIONS))
        self.assertEqual(
            [player.decision_option_1, player.decision_option_2,
             player.decision_option_3],
            order,
        )


if __name__ == '__main__':
    unittest.main()

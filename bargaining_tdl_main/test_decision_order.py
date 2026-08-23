import unittest
from unittest.mock import patch

from bargaining_tdl_common import VALID_DECISIONS
from . import _decision_option_order


class _PlayerStub:
    def __init__(self, values=None):
        values = values or {}
        self.decision_option_1 = values.get('decision_option_1', '')
        self.decision_option_2 = values.get('decision_option_2', '')
        self.decision_option_3 = values.get('decision_option_3', '')
        self.save_calls = 0

    def field_maybe_none(self, name):
        return getattr(self, name)

    def save(self):
        self.save_calls += 1


class DecisionOrderTests(unittest.TestCase):
    def test_order_is_generated_once_and_persisted(self):
        player = _PlayerStub()
        with patch('random.shuffle', side_effect=lambda values: values.reverse()) as shuffle:
            first = _decision_option_order(player)
            second = _decision_option_order(player)

        self.assertEqual(first, second)
        self.assertEqual(sorted(first), sorted(VALID_DECISIONS))
        self.assertEqual(player.save_calls, 1)
        shuffle.assert_called_once()

    def test_invalid_or_partial_order_is_repaired(self):
        player = _PlayerStub({
            'decision_option_1': 'Left',
            'decision_option_2': 'Left',
            'decision_option_3': '',
        })
        order = _decision_option_order(player)

        self.assertEqual(sorted(order), sorted(VALID_DECISIONS))
        self.assertEqual(player.save_calls, 1)


if __name__ == '__main__':
    unittest.main()

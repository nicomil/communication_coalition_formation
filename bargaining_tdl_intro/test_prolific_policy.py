"""
Test policy Prolific ID (obbligatorio in produzione, opzionale in dev).
"""
import unittest
from unittest.mock import MagicMock

from . import Welcome, _require_prolific_id


def _player(require=True, label='', pid_url=''):
    player = MagicMock()
    player.session.config = {'require_prolific_id': require}
    player.participant.label = label
    player.prolific_pid_url = pid_url
    return player


class TestProlificPolicy(unittest.TestCase):
    def test_require_prolific_id_default_true(self):
        player = MagicMock()
        player.session.config = {}
        self.assertTrue(_require_prolific_id(player))

    def test_error_when_pid_missing_and_required(self):
        player = _player(require=True, label='', pid_url='')
        msg = Welcome.prolific_pid_url_error_message(player, '')
        self.assertIsNotNone(msg)

    def test_no_error_when_pid_in_label(self):
        player = _player(require=True, label='prolific-abc', pid_url='')
        msg = Welcome.prolific_pid_url_error_message(player, '')
        self.assertIsNone(msg)

    def test_no_error_when_not_required(self):
        player = _player(require=False, label='', pid_url='')
        msg = Welcome.prolific_pid_url_error_message(player, '')
        self.assertIsNone(msg)


if __name__ == '__main__':
    unittest.main()

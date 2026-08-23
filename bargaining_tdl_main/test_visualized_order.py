import unittest

from . import _visualized_partner_context, _ensure_visualized_order
from bargaining_tdl_common import TOPOLOGY


class _Participant:
    def __init__(self, code):
        self.code = code


class _Player:
    """Imita un Player oTree, compreso il comportamento dei campi nulli.

    I due campi partono a None come nel database, e leggerli direttamente
    solleva TypeError esattamente come fa oTree: senza questo il test passava
    mentre la produzione andava in errore 500 sulla wait page di
    raggruppamento.
    """

    def __init__(self, player_id, code, group):
        self.id_in_group = player_id
        self.participant = _Participant(code)
        self.group = group
        self._fields = {
            'id_player_visualized_on_the_left': None,
            'id_player_visualized_on_the_right': None,
        }

    def __getattr__(self, name):
        if name in ('id_player_visualized_on_the_left',
                    'id_player_visualized_on_the_right'):
            value = self._fields[name]
            if value is None:
                raise TypeError(
                    f'player.{name} is None. Accessing a null field is '
                    f'generally considered an error. Or, if this is '
                    f'intentional, use field_maybe_none()'
                )
            return value
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ('id_player_visualized_on_the_left',
                    'id_player_visualized_on_the_right'):
            self._fields[name] = value
            return
        super().__setattr__(name, value)

    def field_maybe_none(self, name):
        return self._fields[name]


class _Group:
    id = 42

    def __init__(self):
        self.players = [_Player(i, f"P{i}", self) for i in (1, 2, 3)]

    def get_players(self):
        return self.players


class VisualizedOrderTests(unittest.TestCase):
    def test_order_contains_exactly_the_two_topological_partners(self):
        group = _Group()
        for player in group.get_players():
            _ensure_visualized_order(player)
            visual_ids = {
                next(p.id_in_group for p in group.get_players()
                     if p.participant.code == player.id_player_visualized_on_the_left),
                next(p.id_in_group for p in group.get_players()
                     if p.participant.code == player.id_player_visualized_on_the_right),
            }
            self.assertEqual(visual_ids, set(TOPOLOGY[player.id_in_group].values()))
            self.assertNotEqual(
                player.id_player_visualized_on_the_left,
                player.id_player_visualized_on_the_right,
            )

    def test_order_is_stable_and_channels_follow_visual_positions(self):
        group = _Group()
        player = group.players[0]
        _ensure_visualized_order(player)
        saved_order = (
            player.id_player_visualized_on_the_left,
            player.id_player_visualized_on_the_right,
        )
        context = _visualized_partner_context(player)
        _ensure_visualized_order(player)
        self.assertEqual(saved_order, (
            player.id_player_visualized_on_the_left,
            player.id_player_visualized_on_the_right,
        ))
        self.assertTrue(context['visual_left_channel'].endswith(
            f"_{min(1, context['visual_left_id'])}_{max(1, context['visual_left_id'])}"
        ))
        self.assertTrue(context['visual_right_channel'].endswith(
            f"_{min(1, context['visual_right_id'])}_{max(1, context['visual_right_id'])}"
        ))


if __name__ == '__main__':
    unittest.main()

import unittest

from . import _visualized_partner_context, _ensure_visualized_order
from bargaining_tdl_common import (
    COLOR_MAPPING,
    TOPOLOGY,
    get_left_partner_id,
    get_right_partner_id,
)


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


def resolve_nickname(nickname, receiver_id):
    """Il colore che il destinatario vede, come fa _chat_customization.html.

    Il template JS traduce la stringa con i colori topologici di chi legge:
    'RightPartner' diventa il colore del suo partner destro, 'LeftPartner'
    quello del sinistro. Riprodurlo qui e' l'unico modo per verificare la
    catena intera senza aprire un browser.
    """
    if nickname == 'RightPartner':
        return COLOR_MAPPING[get_right_partner_id(receiver_id)]
    if nickname == 'LeftPartner':
        return COLOR_MAPPING[get_left_partner_id(receiver_id)]
    raise AssertionError(f'nickname inatteso: {nickname!r}')


class NicknameReciprocityTests(unittest.TestCase):
    """Chi legge deve vedere il colore di chi ha scritto.

    Il nickname non dice chi c'e' nella colonna: dice come il mittente appare a
    chi legge. Invertirlo non da' errore da nessuna parte — i messaggi arrivano
    lo stesso — ma vengono firmati con il colore del terzo giocatore, che e'
    l'unico partecipante che quella conversazione non puo' vedere.
    """

    def test_sender_is_labelled_with_their_own_colour(self):
        group = _Group()
        for sender in group.get_players():
            context = _visualized_partner_context(sender)
            by_code = {p.participant.code: p for p in group.get_players()}
            pairs = (
                (by_code[sender.id_player_visualized_on_the_left],
                 context['visual_left_nickname']),
                (by_code[sender.id_player_visualized_on_the_right],
                 context['visual_right_nickname']),
            )
            for receiver, nickname in pairs:
                self.assertEqual(
                    resolve_nickname(nickname, receiver.id_in_group),
                    COLOR_MAPPING[sender.id_in_group],
                    msg=(f'{COLOR_MAPPING[sender.id_in_group]} scrive a '
                         f'{COLOR_MAPPING[receiver.id_in_group]} e si annuncia '
                         f'come {nickname!r}'),
                )

    def test_the_third_player_colour_never_appears(self):
        """Il sintomo osservato: il colore di chi non e' nella conversazione."""
        group = _Group()
        for sender in group.get_players():
            context = _visualized_partner_context(sender)
            by_code = {p.participant.code: p for p in group.get_players()}
            for side in ('left', 'right'):
                receiver = by_code[
                    getattr(sender, f'id_player_visualized_on_the_{side}')
                ]
                third = next(
                    p for p in group.get_players()
                    if p.id_in_group not in (sender.id_in_group,
                                             receiver.id_in_group)
                )
                self.assertNotEqual(
                    resolve_nickname(context[f'visual_{side}_nickname'],
                                     receiver.id_in_group),
                    COLOR_MAPPING[third.id_in_group],
                )

    def test_order_on_screen_does_not_change_the_label(self):
        """La randomizzazione e' visiva: il nickname resta quello topologico."""
        group = _Group()
        for sender in group.get_players():
            context = _visualized_partner_context(sender)
            left_id = get_left_partner_id(sender.id_in_group)
            for side in ('left', 'right'):
                shown_id = next(
                    p.id_in_group for p in group.get_players()
                    if p.participant.code == getattr(
                        sender, f'id_player_visualized_on_the_{side}')
                )
                expected = 'RightPartner' if shown_id == left_id else 'LeftPartner'
                self.assertEqual(context[f'visual_{side}_nickname'], expected)


if __name__ == '__main__':
    unittest.main()

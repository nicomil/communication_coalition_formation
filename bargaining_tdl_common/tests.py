"""
Test suite for bargaining_tdl_common module.

Tests cover:
- Helper functions
- Validators
- Utils (cross-module functions)
- Logger
"""

from otree.api import Currency as c, expect, Bot
from . import *
import unittest


class TestHelpers(unittest.TestCase):
    """Test helper functions."""
    
    def test_save_time_value_valid(self):
        """Test save_time_value with valid inputs."""
        self.assertEqual(save_time_value('10.5'), 10.5)
        self.assertEqual(save_time_value(10.5), 10.5)
        self.assertEqual(save_time_value(10), 10.0)
        self.assertEqual(save_time_value('0'), 0.0)
    
    def test_save_time_value_invalid(self):
        """Test save_time_value with invalid inputs."""
        self.assertEqual(save_time_value(None), 0.0)
        self.assertEqual(save_time_value(''), 0.0)
        self.assertEqual(save_time_value('invalid'), 0.0)
        self.assertEqual(save_time_value('invalid', default=5.0), 5.0)
    
    def test_save_time_value_edge_cases(self):
        """Test save_time_value with edge cases."""
        self.assertEqual(save_time_value('-5'), 0.0)  # Negative becomes default
        self.assertEqual(save_time_value('1e6'), 0.0)  # Too large becomes default


class TestValidators(unittest.TestCase):
    """Test validator functions."""
    
    def test_set_and_get_control_questions_failed(self):
        """Test setting and getting control questions failed flag."""
        from otree.models import Participant
        
        # Mock player (in real test would use oTree test framework)
        # This is a simplified test structure
        pass  # Would need oTree test session setup


class TestLogger(unittest.TestCase):
    """Test logging system."""
    
    def test_logger_creation(self):
        """Test that logger can be created."""
        logger = get_logger('test')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'bargaining_tdl.test')
    
    def test_logger_functions(self):
        """Test logger convenience functions."""
        # These should not raise exceptions
        info("Test info message")
        warning("Test warning message")
        error("Test error message")
        debug("Test debug message")


class TestColorMapping(unittest.TestCase):
    """Test color-based player identification utilities."""

    def test_get_player_color(self):
        self.assertEqual(get_player_color(1), 'Red')
        self.assertEqual(get_player_color(2), 'Green')
        self.assertEqual(get_player_color(3), 'Blue')
        self.assertEqual(get_player_color(4), 'Unknown')

    def test_color_mapping_completeness(self):
        self.assertEqual(set(COLOR_MAPPING.keys()), {1, 2, 3})
        self.assertEqual(set(COLOR_MAPPING.values()), {'Red', 'Green', 'Blue'})

    def test_topology_consistency(self):
        from .utils import TOPOLOGY
        for pid, partners in TOPOLOGY.items():
            self.assertIn(partners['left'], {1, 2, 3})
            self.assertIn(partners['right'], {1, 2, 3})
            self.assertNotEqual(partners['left'], pid)
            self.assertNotEqual(partners['right'], pid)
            self.assertNotEqual(partners['left'], partners['right'])

    def test_role_id_roundtrip(self):
        self.assertEqual(get_id_from_role('A'), 1)
        self.assertEqual(get_id_from_role('B'), 2)
        self.assertEqual(get_id_from_role('C'), 3)
        self.assertEqual(get_id_from_role('Z'), None)
        self.assertEqual(get_role_from_id(1), 'A')
        self.assertEqual(get_role_from_id(2), 'B')
        self.assertEqual(get_role_from_id(3), 'C')
        self.assertEqual(get_role_from_id(9), None)

    def test_partner_side_helpers(self):
        self.assertEqual(get_left_partner_id(1), 3)
        self.assertEqual(get_right_partner_id(1), 2)
        self.assertEqual(get_partner_side(1, 3), 'left')
        self.assertEqual(get_partner_side(1, 2), 'right')
        self.assertEqual(get_partner_side(1, 1), None)


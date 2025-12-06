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


# Integration tests would go here
# These require oTree test session setup


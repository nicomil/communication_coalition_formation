"""
Common utilities and helpers for bargaining_tdl experiment modules.

This module provides shared functionality across:
- bargaining_tdl_intro
- bargaining_tdl_main
- bargaining_tdl_survey
"""

from .helpers import (
    save_time_value,
    TEST_TIMER_SECONDS,
    use_test_timers,
    get_page_timeout_seconds,
    timeout_submission_with_time,
)
from .validators import (
    set_control_questions_failed,
    has_failed_control_questions,
    check_control_questions_intro,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    reset_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
)
from .utils import (
    get_main_group_player,
    get_participant_role_in_group,
    COLOR_MAPPING,
    ROLE_TO_ID,
    ID_TO_ROLE,
    TOPOLOGY,
    get_player_color,
    get_role_from_id,
    get_id_from_role,
    get_left_partner_id,
    get_right_partner_id,
    get_partner_side,
    get_partner_colors,
    custom_calculate_payoff_vector,
    VALID_DECISIONS,
)
from .treatments import (
    TREATMENTS,
    DEFAULT_TREATMENT,
    DEFAULT_ACTIVE_TREATMENTS,
    get_active_treatments,
    get_treatment,
    get_treatment_config,
    treatment_flag,
)
from .mixins import TimeTrackedPage
from .logger import get_logger, logger, info, warning, error, debug

__all__ = [
    'save_time_value',
    'TEST_TIMER_SECONDS',
    'use_test_timers',
    'get_page_timeout_seconds',
    'timeout_submission_with_time',
    'set_control_questions_failed',
    'has_failed_control_questions',
    'check_control_questions_intro',
    'get_max_attempts',
    'get_control_questions_attempts',
    'increment_control_questions_attempts',
    'reset_control_questions_attempts',
    'has_passed_control_questions',
    'set_control_questions_passed',
    'get_main_group_player',
    'get_participant_role_in_group',
    'COLOR_MAPPING',
    'ROLE_TO_ID',
    'ID_TO_ROLE',
    'TOPOLOGY',
    'get_player_color',
    'get_role_from_id',
    'get_id_from_role',
    'get_left_partner_id',
    'get_right_partner_id',
    'get_partner_side',
    'get_partner_colors',
    'custom_calculate_payoff_vector',
    'VALID_DECISIONS',
    'TREATMENTS',
    'DEFAULT_TREATMENT',
    'DEFAULT_ACTIVE_TREATMENTS',
    'get_active_treatments',
    'get_treatment',
    'get_treatment_config',
    'treatment_flag',
    'TimeTrackedPage',
    'get_logger',
    'logger',
    'info',
    'warning',
    'error',
    'debug',
]

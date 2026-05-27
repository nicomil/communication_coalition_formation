# Export Data Dictionary

## Core dataset columns

- `playerid`
- `participant_code`
- `groupid`
- `inactive`
- `inactive_reason`
- `group_dropped`
- `part1_payoff_eligible`
- `left_player`
- `right_player`
- `part1_signal_left`
- `part1_signal_right`
- `part1_finaldecision`
- `part1_payoff`
- `part3_finaldecision`
- `selected_part_for_payment`
- `prolific_id`
- `prolific_study_id`
- `prolific_session_id`
- `survey_gender`
- `survey_age`
- `survey_field_of_study`
- `survey_university_years`
- `survey_job_status`
- `survey_willingness_future`
- `survey_willingness_risk`
- `survey_reciprocity_positive`
- `survey_reciprocity_negative`
- `survey_willingness_donate`
- `survey_trust_general`
- `survey_beauty_contest_guess`

## Full export diagnostics

| Column | Non-empty rows | Fill ratio | Category |
|---|---:|---:|---|
| `participant.id_in_session` | 111/111 | 1.0 | populated |
| `participant.code` | 111/111 | 1.0 | populated |
| `participant.label` | 0/111 | 0.0 | always_empty |
| `participant._is_bot` | 111/111 | 1.0 | populated |
| `participant._index_in_pages` | 111/111 | 1.0 | populated |
| `participant._max_page_index` | 111/111 | 1.0 | populated |
| `participant._current_app_name` | 48/111 | 0.4324 | populated |
| `participant._current_page_name` | 48/111 | 0.4324 | populated |
| `participant.time_started_utc` | 48/111 | 0.4324 | populated |
| `participant.visited` | 111/111 | 1.0 | populated |
| `participant.mturk_worker_id` | 0/111 | 0.0 | always_empty |
| `participant.mturk_assignment_id` | 0/111 | 0.0 | always_empty |
| `participant.payoff` | 111/111 | 1.0 | populated |
| `participant.prolific_id` | 0/111 | 0.0 | always_empty |
| `participant.prolific_study_id` | 0/111 | 0.0 | always_empty |
| `participant.prolific_session_id` | 0/111 | 0.0 | always_empty |
| `participant.inactive_excluded` | 0/111 | 0.0 | always_empty |
| `participant.inactive_excluded_reason` | 0/111 | 0.0 | always_empty |
| `participant.group_dropped` | 48/111 | 0.4324 | populated |
| `participant.part1_payoff_eligible` | 48/111 | 0.4324 | populated |
| `session.code` | 111/111 | 1.0 | populated |
| `session.label` | 0/111 | 0.0 | always_empty |
| `session.mturk_HITId` | 0/111 | 0.0 | always_empty |
| `session.mturk_HITGroupId` | 0/111 | 0.0 | always_empty |
| `session.comment` | 0/111 | 0.0 | always_empty |
| `session.is_demo` | 111/111 | 1.0 | populated |
| `session.config.name` | 111/111 | 1.0 | populated |
| `session.config.participation_fee` | 111/111 | 1.0 | populated |
| `session.config.real_world_currency_per_point` | 111/111 | 1.0 | populated |
| `session.config.control_questions_max_attempts` | 111/111 | 1.0 | populated |
| `session.config.skip_intro_control_questions` | 111/111 | 1.0 | populated |
| `session.config.use_test_timers` | 111/111 | 1.0 | populated |
| `session.config.completionlink` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.id_in_group` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.role` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.payoff` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.prolific_id` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.prolific_pid_url` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.prolific_study_id` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.prolific_session_id` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.draft_history_left` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.draft_history_right` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.signal_left` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.signal_right` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.first_intention_selected` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_intro.1.player.example1_earnings_you` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example1_earnings_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example1_earnings_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example2_earnings_you` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example2_earnings_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example2_earnings_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example3_earnings_you` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example3_earnings_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.example3_earnings_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_intro.1.player.time_welcome` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.time_instructions_part1` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.time_control_questions` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.time_goodbye` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.time_chat_and_signals` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.player.time_on_page` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.group.id_in_subsession` | 111/111 | 1.0 | populated |
| `bargaining_tdl_intro.1.subsession.round_number` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.id_in_group` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.role` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_main.1.player.payoff` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.player_color` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.part1_calculated_payoff` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.signal_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.signal_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.first_intention_selected` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.time_welcome` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_chat` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_signals` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_chat_and_signals` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.decision_choice` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.received_signal_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.received_signal_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.id_player_on_the_left` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.id_player_on_the_right` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_main.1.player.time_experiment_terminated` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_decision` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_results` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.time_on_page` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.chat_interrupted` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.participant_left_ts` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.part1_payoff_eligible` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.decision_inactive` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.signal_inactive` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.received_signal_left_inactive` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.player.received_signal_right_inactive` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.id_in_subsession` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.grp_coordinate` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.grp_triadicsplit` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.selected_part_for_payment` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.chat_left_p1` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.chat_left_p2` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.chat_left_p3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.group_dropped` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.reconnect_deadline_ts` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.interrupted_player_id` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.last_ping_p1` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.last_ping_p2` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.last_ping_p3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.submit_grace_until_p1` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.submit_grace_until_p2` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.submit_grace_until_p3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.group.part1_payoff_eligible` | 111/111 | 1.0 | populated |
| `bargaining_tdl_main.1.subsession.round_number` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.id_in_group` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.role` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.payoff` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.decision` | 48/111 | 0.4324 | populated |
| `bargaining_tdl_part3.1.player.example1_earnings_you` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.example1_earnings_left` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.example1_earnings_right` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.example2_earnings_you` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.example2_earnings_left` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.example2_earnings_right` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_part3.1.player.all_control_questions_correct` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_instructions_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_summary_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_control_questions_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_thank_you_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_decision_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_results_part3` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.time_on_page` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.player.selected_part_for_payment` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.group.id_in_subsession` | 111/111 | 1.0 | populated |
| `bargaining_tdl_part3.1.subsession.round_number` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.id_in_group` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.role` | 0/111 | 0.0 | always_empty |
| `bargaining_tdl_survey.1.player.payoff` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.gender` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.age` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.field_of_study` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.university_years` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.job_status` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.willingness_future` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.willingness_risk` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.reciprocity_positive` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.reciprocity_negative` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.willingness_donate` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.trust_general` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.beauty_contest_guess` | 3/111 | 0.027 | sparse |
| `bargaining_tdl_survey.1.player.time_on_page` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_intro` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_questions` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_scale_intro` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page4` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page5` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page6` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page7` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page8` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page9` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_survey_page10` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.player.time_final_results` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.group.id_in_subsession` | 111/111 | 1.0 | populated |
| `bargaining_tdl_survey.1.subsession.round_number` | 111/111 | 1.0 | populated |

from unittest.mock import patch

import pytest


class TestSlotCheckerService:
    def test_initialization(self, slot_checker):
        assert slot_checker.client is not None
        assert slot_checker.notifier is not None

    def test_execute_steps_success(self, slot_checker):
        steps = [("test_step", lambda: True, [])]
        assert slot_checker._execute_steps(steps) is True

    def test_execute_steps_failure(self, slot_checker):
        steps = [("test_step", lambda: False, [])]
        with pytest.raises(Exception):
            slot_checker._execute_steps(steps)

    @patch("src.services.slot_checker.TelegramNotifier.send_message")
    def test_run_with_slots(self, mock_send, slot_checker):
        slot_checker.client.check_slots.return_value = {"status": "slots_available"}
        slot_checker.run()
        mock_send.assert_called()

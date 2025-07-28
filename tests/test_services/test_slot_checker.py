from unittest.mock import MagicMock, patch

import pytest


class TestSlotCheckerService:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.check_slots.return_value = {"status": "slots_available"}
        return client

    @pytest.fixture
    def mock_notifier(self):
        return MagicMock()

    @pytest.fixture
    def slot_checker(self, mock_client, mock_notifier):
        with (
            patch(
                "request_sender.services.slot_checker.RequestClient",
                return_value=mock_client,
            ),
            patch(
                "request_sender.services.slot_checker.TelegramNotifier",
                return_value=mock_notifier,
            ),
        ):
            from request_sender.services.slot_checker import SlotCheckerService

            return SlotCheckerService()

    def test_run_with_slots(self, slot_checker, mock_client, mock_notifier):
        slot_checker.run()
        mock_notifier.send_message.assert_called_once()

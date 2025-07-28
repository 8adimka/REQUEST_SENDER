from unittest.mock import MagicMock, patch

import pytest


class TestSlotCheckerService:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        # Эмулируем разные статусы при каждом вызове
        client.check_slots.side_effect = [
            {"status": "no_slots"},
            {"status": "no_slots"},
            {"status": "slots_available"},  # Завершаем цикл на третьем вызове
        ]
        # Мокируем все необходимые методы
        client.load_initial_page.return_value = True
        client.select_province.return_value = True
        client.select_tramite.return_value = True
        client.submit_info_page.return_value = True
        client.fill_personal_data.return_value = True
        client.confirm_data.return_value = True
        client.restart_cycle.return_value = True
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
            patch("time.sleep"),  # Убираем реальные задержки
            patch("random.uniform", return_value=0),  # Фиксируем случайные задержки
            patch("random.randint", return_value=1),  # Фиксируем случайные значения
        ):
            from request_sender.services.slot_checker import SlotCheckerService

            return SlotCheckerService()

    # def test_run_with_slots(self, slot_checker, mock_client, mock_notifier):
    #     # Patch MAX_RETRIES to prevent infinite loops
    #     with patch("request_sender.services.slot_checker.MAX_RETRIES", 1):
    #         slot_checker.run()

    #     # Проверяем основные вызовы
    #     mock_client.load_initial_page.assert_called_once()
    #     mock_client.select_province.assert_called_once_with("Alicante")
    #     assert mock_client.check_slots.call_count == 3  # Проверяем количество вызовов
    #     mock_notifier.send_message.assert_called_once()

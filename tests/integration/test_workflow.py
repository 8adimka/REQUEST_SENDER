from unittest.mock import MagicMock, patch

import pytest


class TestSlotCheckerWorkflow:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        # Мокируем полный цикл работы
        client.load_initial_page.return_value = True
        client.select_province.return_value = True
        client.select_tramite.return_value = True
        client.submit_info_page.return_value = True
        client.fill_personal_data.return_value = True
        client.confirm_data.return_value = True
        client.check_slots.side_effect = [
            {"status": "no_slots"},
            {"status": "slots_available"},  # Завершаем цикл на втором вызове
        ]
        client.restart_cycle.return_value = True
        return client

    @pytest.fixture
    def mock_notifier(self):
        return MagicMock()

    def test_successful_workflow(self, mock_client, mock_notifier):
        with (
            patch(
                "app.services.slot_checker.RequestClient",
                return_value=mock_client,
            ),
            patch(
                "app.services.slot_checker.TelegramNotifier",
                return_value=mock_notifier,
            ),
            patch("time.sleep"),  # Убираем реальные задержки
            patch("random.uniform", return_value=0),  # Фиксируем задержки
            patch("logging.info"),  # Отключаем логирование
        ):
            from app.services.slot_checker import SlotCheckerService

            checker = SlotCheckerService()
            checker.run()  # Должен завершиться после второго check_slots

            # Проверяем ключевые вызовы
            mock_client.load_initial_page.assert_called_once()
            assert mock_client.select_province.call_count == 2
            mock_client.select_province.assert_any_call("Alicante")
            assert mock_client.check_slots.call_count >= 2
            mock_notifier.send_message.assert_called_once()

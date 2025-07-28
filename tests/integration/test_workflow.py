from unittest.mock import patch


class TestIntegrationWorkflow:
    @patch("src.client.request_client.RequestClient")
    @patch("src.telegram.notifier.TelegramNotifier")
    def test_full_workflow(self, mock_notifier, mock_client):
        # Настройка моков
        mock_client_instance = mock_client.return_value
        mock_client_instance.load_initial_page.return_value = True
        mock_client_instance.select_province.return_value = True
        mock_client_instance.check_slots.return_value = {"status": "no_slots"}

        # Запуск основного потока
        from request_sender.main import main

        main()

        # Проверки вызовов
        mock_client_instance.load_initial_page.assert_called_once()
        mock_client_instance.select_province.assert_called_once_with("Alicante")

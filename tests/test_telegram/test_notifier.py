from unittest.mock import patch


class TestTelegramNotifier:
    @patch("requests.post")
    def test_send_message_success(self, mock_post, telegram_notifier):
        mock_post.return_value.status_code = 200
        telegram_notifier.send_message("Test message")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_message_failure(self, mock_post, telegram_notifier):
        mock_post.side_effect = Exception("Connection error")
        telegram_notifier.send_message("Test message")
        mock_post.assert_called_once()

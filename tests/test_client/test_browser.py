from unittest.mock import MagicMock, patch

import pytest


class TestBrowserOperations:
    @pytest.fixture
    def mock_driver(self):
        return MagicMock()

    @pytest.fixture
    def request_client(self, mock_driver):
        with patch("undetected_chromedriver.Chrome", return_value=mock_driver):
            from request_sender.client.request_client import RequestClient

            return RequestClient()

    def test_driver_initialization(self, request_client, mock_driver):
        assert request_client.driver is not None
        assert request_client.driver == mock_driver

    def test_load_initial_page(self, request_client, mock_driver):
        mock_driver.get.return_value = None
        mock_driver.page_source = "<html>Test page</html>"
        assert request_client.load_initial_page() is True
        mock_driver.get.assert_called_once()

    def test_restart_browser(self, request_client, mock_driver):
        mock_driver.quit.return_value = None
        assert request_client.restart_browser() is True
        mock_driver.quit.assert_called_once()

    def test_random_delay(self, request_client):
        with patch("time.sleep") as mock_sleep:
            request_client._random_delay()
            mock_sleep.assert_called_once()

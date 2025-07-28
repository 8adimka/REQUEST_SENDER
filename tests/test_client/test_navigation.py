from unittest.mock import MagicMock, patch

import pytest


class TestNavigation:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        driver.find_element.return_value = MagicMock()
        return driver

    @pytest.fixture
    def request_client(self, mock_driver):
        with patch("undetected_chromedriver.Chrome", return_value=mock_driver):
            from request_sender.client.request_client import RequestClient

            return RequestClient()

    def test_select_province(self, request_client, mock_driver):
        mock_driver.page_source = ""
        assert request_client.select_province("Alicante") is True

    def test_check_slots_available(self, request_client, mock_driver):
        mock_driver.page_source = "disponibilidad de citas"
        result = request_client.check_slots()
        assert result["status"] == "slots_available"

    def test_check_slots_unavailable(self, request_client, mock_driver):
        mock_driver.page_source = "no hay citas disponibles"
        result = request_client.check_slots()
        assert result["status"] == "no_slots"

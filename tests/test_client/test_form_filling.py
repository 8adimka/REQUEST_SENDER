from unittest.mock import MagicMock, patch

import pytest


class TestFormFilling:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        driver.find_element.return_value = MagicMock()
        return driver

    @pytest.fixture
    def request_client(self, mock_driver):
        with patch("undetected_chromedriver.Chrome", return_value=mock_driver):
            with patch(
                "request_sender.settings.PERSONAL_DATA",
                {
                    "txtIdCitado": "TEST123",
                    "txtDesCitado": "Test User",
                    "txtAnnoCitado": "1990",
                    "txtPaisNac": "Spain",
                },
            ):
                from request_sender.client.request_client import RequestClient

                client = RequestClient()
            return client

    def test_fill_personal_data(self, request_client, mock_driver):
        with patch("selenium.webdriver.support.wait.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = MagicMock()
            assert request_client.fill_personal_data() is True

    def test_select_dropdown_failure(self, request_client, mock_driver):
        mock_driver.find_element.side_effect = Exception("Element not found")
        assert request_client._select_dropdown("id", "test_id", "Option") is False

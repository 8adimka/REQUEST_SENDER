from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.common.by import By


class TestFormFilling:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        mock_element = MagicMock()
        mock_element.tag_name = "select"
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True

        def select_by_visible_text(text):
            if text == "RUSIA":
                return None
            raise Exception(f"Could not locate element with visible text: {text}")

        mock_select = MagicMock()
        mock_select.select_by_visible_text.side_effect = select_by_visible_text
        driver.find_element.return_value = mock_element

        with patch("selenium.webdriver.support.ui.Select", return_value=mock_select):
            yield driver

    @pytest.fixture
    def request_client(self, mock_driver):
        with patch("undetected_chromedriver.Chrome", return_value=mock_driver):
            with patch(
                "request_sender.settings.PERSONAL_DATA",
                {
                    "txtIdCitado": "TEST123",
                    "txtDesCitado": "Test User",
                    "txtAnnoCitado": "1990",
                    "txtPaisNac": "RUSIA",
                },
            ):
                from request_sender.client.request_client import RequestClient

                client = RequestClient()
            return client

    def test_fill_personal_data(self, request_client, mock_driver):
        mock_driver.current_url = (
            "https://icp.administracionelectronica.gob.es/icpco/acEntrada"
        )
        assert request_client.fill_personal_data() is True
        mock_driver.find_element.assert_any_call(By.ID, "txtIdCitado")
        mock_driver.find_element.assert_any_call(By.ID, "txtDesCitado")
        mock_driver.find_element.assert_any_call(By.ID, "txtAnnoCitado")
        mock_driver.find_element.assert_any_call(By.ID, "txtPaisNac")

    def test_select_dropdown_failure(self, request_client, mock_driver):
        mock_driver.find_element.side_effect = Exception("Element not found")
        assert request_client._select_dropdown("id", "test_id", "Option") is False

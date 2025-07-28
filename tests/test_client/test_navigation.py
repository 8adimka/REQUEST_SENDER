from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.common.by import By


class TestNavigation:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        mock_element = MagicMock()
        mock_element.tag_name = "select"
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True

        def select_by_visible_text(text):
            if text == "Alicante (AL)":
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
            from request_sender.client.request_client import RequestClient

            return RequestClient()

    def test_select_province(self, request_client, mock_driver):
        mock_driver.current_url = (
            "https://icp.administracionelectronica.gob.es/icpco/index"
        )
        assert request_client.select_province("Alicante (AL)") is True
        mock_driver.find_element.assert_any_call(By.NAME, "form")
        mock_driver.find_element.assert_any_call(By.ID, "btnAceptar")

    def test_check_slots_available(self, request_client, mock_driver):
        mock_driver.page_source = "disponibilidad de citas"
        result = request_client.check_slots()
        assert result["status"] == "slots_available"

    def test_check_slots_unavailable(self, request_client, mock_driver):
        mock_driver.page_source = "no hay citas disponibles"
        result = request_client.check_slots()
        assert result["status"] == "no_slots"

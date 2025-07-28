from unittest.mock import MagicMock, patch

from selenium.webdriver.common.by import By


class TestFormFilling:
    @patch("selenium.webdriver.support.wait.WebDriverWait")
    @patch("selenium.webdriver.support.select.Select")
    def test_fill_personal_data(
        self, mock_select, mock_webdriver_wait, request_client, mock_driver
    ):
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element

        # Mock WebDriverWait chain
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_webdriver_wait.return_value.__enter__.return_value = mock_wait_instance

        # Mock Select chain
        mock_select_instance = MagicMock()
        mock_select_instance.select_by_visible_text.return_value = None
        mock_select.return_value = mock_select_instance

        request_client.PERSONAL_DATA = {
            "txtIdCitado": "TEST123",
            "txtDesCitado": "Test User",
            "txtAnnoCitado": "1990",
            "txtPaisNac": "Spain",
        }

        assert request_client.fill_personal_data() is True

    def test_select_dropdown_failure(self, request_client, mock_driver):
        mock_driver.find_element.side_effect = Exception("Element not found")
        assert request_client._select_dropdown(By.ID, "test_id", "Option") is False

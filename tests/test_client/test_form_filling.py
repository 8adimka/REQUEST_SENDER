from unittest.mock import MagicMock, patch

import pytest


class TestFormFilling:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        mock_element = MagicMock()
        mock_element.tag_name = "select"
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True

        # Мок для ActionChains
        mock_actions = MagicMock()
        mock_actions.move_to_element_with_offset.return_value = mock_actions
        mock_actions.perform.return_value = None

        # Настройка select_by_visible_text для успешного выбора "RUSIA"
        def select_by_visible_text(text):
            if text != "RUSIA":
                raise Exception(f"Could not locate element with visible text: {text}")
            return None  # Успешный выбор для "RUSIA"

        mock_select = MagicMock()
        mock_select.select_by_visible_text.side_effect = select_by_visible_text
        driver.find_element.return_value = mock_element

        with patch("selenium.webdriver.support.ui.Select", return_value=mock_select):
            with patch(
                "selenium.webdriver.common.action_chains.ActionChains",
                return_value=mock_actions,
            ):
                yield driver

    @pytest.fixture
    def request_client(self, mock_driver):
        with patch("undetected_chromedriver.Chrome", return_value=mock_driver):
            from app.client.request_client import RequestClient

            client = RequestClient()
            return client

    def test_select_dropdown_failure(self, request_client, mock_driver):
        mock_driver.find_element.side_effect = Exception("Element not found")
        assert request_client._select_dropdown("id", "test_id", "Option") is False

    def test_fill_personal_data_failure(self, request_client, mock_driver):
        mock_driver.current_url = "invalid_url"
        assert request_client.fill_personal_data() is False

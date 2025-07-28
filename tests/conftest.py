from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from request_sender.client.request_client import RequestClient
from request_sender.services.slot_checker import SlotCheckerService
from request_sender.telegram.notifier import TelegramNotifier


@pytest.fixture
def mock_driver():
    driver = MagicMock(spec=WebDriver)
    driver.current_url = "https://test.url"
    driver.page_source = "<html>Test page</html>"
    return driver


@pytest.fixture
def request_client(mock_driver):
    with patch("undetected_chromedriver.Chrome") as mock_chrome:
        mock_chrome.return_value = mock_driver
        client = RequestClient()
        client.driver = mock_driver
        yield client
        client.close()


@pytest.fixture
def slot_checker(request_client):
    return SlotCheckerService()


@pytest.fixture
def telegram_notifier():
    return TelegramNotifier(token="test_token", chat_id=12345)

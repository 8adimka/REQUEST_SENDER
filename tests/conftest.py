from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from request_sender.telegram.notifier import TelegramNotifier


@pytest.fixture
def mock_driver():
    driver = MagicMock(spec=WebDriver)
    driver.current_url = "https://test.url"
    driver.page_source = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <select name="form" id="provinceSelect">
                <option value="1">Alicante</option>
            </select>
            <input type="text" id="txtIdCitado">
            <input type="text" id="txtDesCitado">
            <input type="text" id="txtAnnoCitado">
            <select id="txtPaisNac">
                <option value="Spain">Spain</option>
            </select>
            <button id="btnAceptar"></button>
            <button id="btnEnviar"></button>
        </body>
    </html>
    """

    # Mock find_element to return proper elements
    def mock_find_element(by, value):
        element = MagicMock()
        if value == "provinceSelect":
            element.tag_name = "select"
            element.get_attribute.return_value = "form"
        elif value in ["txtIdCitado", "txtDesCitado", "txtAnnoCitado"]:
            element.tag_name = "input"
            element.clear.return_value = None
            element.send_keys.return_value = None
        elif value == "txtPaisNac":
            element.tag_name = "select"
            element.get_attribute.return_value = "txtPaisNac"
        elif value in ["btnAceptar", "btnEnviar"]:
            element.tag_name = "button"
            element.click.return_value = None
        return element

    driver.find_element.side_effect = mock_find_element

    # Mock for context manager support
    driver.find_element.return_value.__enter__.return_value = (
        driver.find_element.return_value
    )

    # Mock page navigation
    driver.get.return_value = None

    return driver


@pytest.fixture
def request_client(mock_driver):
    """
    Обратите внимание: patch делаем до импорта RequestClient!
    Пути к patch должны строго совпадать с импортами в request_client.py
    """
    with (
        patch("undetected_chromedriver.Chrome", return_value=mock_driver),
        patch("request_sender.client.request_client.WebDriverWait") as mock_wait,
        patch("selenium.webdriver.support.ui.Select") as mock_select,
        patch(
            "request_sender.settings.PERSONAL_DATA",
            {
                "txtIdCitado": "TEST123",
                "txtDesCitado": "Test User",
                "txtAnnoCitado": "1990",
                "txtPaisNac": "Spain",
            },
        ),
    ):
        # Сделаем mock для WebDriverWait, чтобы он возвращал правильные элементы
        def mock_wait_until(condition):
            if (
                hasattr(condition, "__name__")
                and condition.__name__ == "presence_of_element_located"
            ):
                locator = condition.locator
                if locator[1] == "txtPaisNac":
                    element = MagicMock()
                    element.tag_name = "select"
                    return element
            return mock_driver.find_element(*locator)

        mock_wait.return_value.until.side_effect = mock_wait_until

        # Настроим mock для Select
        def mock_select_constructor(element):
            select = MagicMock()
            if not hasattr(element, "tag_name") or element.tag_name != "select":
                raise Exception(
                    f"Select only works on <select> elements, not on {element}"
                )
            select.select_by_visible_text.return_value = None
            return select

        mock_select.side_effect = mock_select_constructor

        from request_sender.client.request_client import RequestClient

        client = RequestClient()
        yield client
        client.close()


@pytest.fixture
def telegram_notifier():
    return TelegramNotifier(token="test_token", chat_id=12345)

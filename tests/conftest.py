from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from app.telegram.notifier import TelegramNotifier


@pytest.fixture
def mock_driver():
    driver = MagicMock(spec=WebDriver)
    driver.current_url = "https://test.url"
    driver.page_source = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <select name="form" id="provinceSelect">
                <option value="1">Alicante (AL)</option>
            </select>
            <input type="text" id="txtIdCitado">
            <input type="text" id="txtDesCitado">
            <input type="text" id="txtAnnoCitado">
            <select id="txtPaisNac">
                <option value="RUSIA">RUSIA</option>
            </select>
            <button id="btnAceptar"></button>
            <button id="btnEnviar"></button>
        </body>
    </html>
    """

    def mock_find_element(by, value):
        print(f"Finding element: by={by}, value={value}")
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
    driver.find_element.return_value.__enter__.return_value = (
        driver.find_element.return_value
    )
    driver.get.return_value = None

    return driver


@pytest.fixture
def request_client(mock_driver):
    with (
        patch("undetected_chromedriver.Chrome", return_value=mock_driver),
        patch("app.client.request_client.WebDriverWait") as mock_wait,
        patch("selenium.webdriver.support.ui.Select") as mock_select,
        patch("selenium.webdriver.common.action_chains.ActionChains") as mock_actions,
    ):

        def mock_wait_until(condition):
            print(
                f"WebDriverWait condition: {condition.__name__}, Locator: {condition.locator}"
            )
            if (
                hasattr(condition, "__name__")
                and condition.__name__ == "presence_of_element_located"
            ):
                locator = condition.locator
                if locator[1] in ["txtPaisNac", "form"]:
                    element = MagicMock()
                    element.tag_name = "select"
                    return element
                return mock_driver.find_element(*locator)
            elif (
                hasattr(condition, "__name__")
                and condition.__name__ == "element_to_be_clickable"
            ):
                locator = condition.locator
                if locator[1] in ["btnAceptar", "btnEnviar"]:
                    element = MagicMock()
                    element.tag_name = "button"
                    element.click.return_value = None
                    return element
            return mock_driver.find_element(*locator)

        mock_wait.return_value.until.side_effect = mock_wait_until

        def mock_select_constructor(element):
            print(f"Creating Select for element with tag: {element.tag_name}")
            select = MagicMock()
            if not hasattr(element, "tag_name") or element.tag_name != "select":
                raise Exception(
                    f"Select only works on <select> elements, not on {element}"
                )

            def select_by_visible_text(text):
                print(f"Selecting: {text}")
                if text not in ["RUSIA", "Alicante (AL)"]:
                    raise Exception(
                        f"Could not locate element with visible text: {text}"
                    )
                return None

            select.select_by_visible_text.side_effect = select_by_visible_text
            return select

        mock_select.side_effect = mock_select_constructor

        mock_actions.return_value.move_to_element_with_offset.return_value = (
            mock_actions.return_value
        )
        mock_actions.return_value.perform.return_value = None

        from app.client.request_client import RequestClient

        client = RequestClient()
        yield client
        client.close()


@pytest.fixture
def telegram_notifier():
    return TelegramNotifier(token="test_token", chat_id=12345)

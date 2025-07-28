from selenium.webdriver.remote.webdriver import WebDriver


class TestBrowserOperations:
    def test_driver_initialization(self, request_client, mock_driver):
        assert request_client.driver is not None
        assert isinstance(request_client.driver, WebDriver)

    def test_load_initial_page(self, request_client, mock_driver):
        mock_driver.get.return_value = None
        assert request_client.load_initial_page() is True
        mock_driver.get.assert_called_once()

    def test_restart_browser(self, request_client, mock_driver):
        mock_driver.quit.return_value = None
        assert request_client.restart_browser() is True
        mock_driver.quit.assert_called_once()

    def test_random_delay(self, request_client):
        delay = request_client._random_delay()
        assert 1.5 <= delay <= 4.0

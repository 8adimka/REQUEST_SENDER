from unittest.mock import MagicMock


class TestNavigation:
    def test_select_province(self, request_client, mock_driver):
        mock_driver.find_element.return_value = MagicMock()
        assert request_client.select_province("Alicante") is True

    def test_check_slots_available(self, request_client, mock_driver):
        mock_driver.page_source = "disponibilidad de citas"
        result = request_client.check_slots()
        assert result["status"] == "slots_available"

    def test_check_slots_unavailable(self, request_client, mock_driver):
        mock_driver.page_source = "no hay citas disponibles"
        result = request_client.check_slots()
        assert result["status"] == "no_slots"

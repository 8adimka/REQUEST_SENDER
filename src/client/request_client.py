import logging
import random
import time
from typing import Dict, Optional

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from src.settings import (
    BOOKING_DATA,
    MAX_DELAY,
    MIN_DELAY,
    PERSONAL_DATA,
    WAIT_TIMEOUT,
)


class RequestClient:
    def __init__(self):
        self.driver: Optional[WebDriver] = None
        self.base_url = "https://icp.administracionelectronica.gob.es"
        self.current_url = ""
        self._init_driver()

    def _random_delay(self) -> None:
        """Задержка между действиями для имитации поведения человека"""
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    def _init_driver(self) -> None:
        """Инициализация драйвера браузера с настройками"""
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(
            f"--window-size={random.randint(1200, 1400)},{random.randint(800, 1000)}"
        )
        options.add_argument(
            f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 115)}.0.0.0 Safari/537.36"
        )

        self.driver = uc.Chrome(
            options=options, headless=False, use_subprocess=True, version_main=136
        )

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {},
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-ES', 'es'],
                });
                """
            },
        )

    def _check_too_many_attempts(self) -> bool:
        """Проверка на сообщение о слишком многих попытках"""
        if not self.driver:
            return False

        try:
            page_text = self.driver.page_source.lower()
            if "too many requests" in page_text:
                return True

            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            return any("too many requests" in h1.text.lower() for h1 in h1_elements)
        except Exception:
            return False

    def _human_like_mouse_movement(self, element) -> None:
        """Имитация человеческого движения мыши к элементу"""
        if not self.driver:
            return

        try:
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(
                element, random.randint(-5, 5), random.randint(-5, 5)
            )
            actions.perform()
            time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            logging.debug(f"Mouse movement error: {str(e)}")

    def _human_like_typing(self, element, text: str) -> None:
        """Имитация человеческого ввода текста"""
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
                if random.random() > 0.9:  # 10% chance to make a "mistake"
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.1, 0.3))
                    element.send_keys(char)
        except Exception:
            element.send_keys(text)

    def _handle_blocked_page(self) -> bool:
        """Обработка заблокированной страницы"""
        if not self.driver:
            return False

        try:
            if "The requested URL was rejected" in self.driver.page_source:
                logging.warning("Обнаружена блокировка! Перезапускаем браузер...")
                self.restart_browser()
                return False
            return True
        except Exception:
            return False

    def _handle_initial_error(self) -> bool:
        """Обработка начальной ошибки на странице"""
        if not self.driver:
            return False

        try:
            if "infogenerica" in self.driver.current_url:
                accept_btn = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.ID, "btnSubmit"))
                )
                self._human_like_mouse_movement(accept_btn)
                accept_btn.click()
                self._random_delay()
                return True
            return False
        except Exception:
            return False

    def _is_booking_page(self) -> bool:
        """Проверка, что текущая страница - страница бронирования"""
        if not self.driver:
            return False

        try:
            required_texts = [
                "CITA PREVIA EXTRANJERÍA",
                "POLICIA- EXPEDICIÓN/RENOVACIÓN DE DOCUMENTOS DE SOLICITANTES DE ASILO",
                "Identidad del usuario de cita",
            ]
            page_source = self.driver.page_source
            return all(text in page_source for text in required_texts)
        except Exception:
            return False

    def _fill_booking_form(self) -> bool:
        """Заполнение формы бронирования"""
        if not self.driver:
            return False

        try:
            if not self._click_element(By.ID, "btnSiguiente"):
                return False

            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "txtTelefonoCitado"))
            )

            fields_mapping = [
                ("txtTelefonoCitado", "phone"),
                ("emailUNO", "email"),
                ("emailDOS", "email"),
                ("txtObservaciones", "motivo"),
            ]

            for field_id, data_key in fields_mapping:
                elem = self.driver.find_element(By.ID, field_id)
                elem.clear()
                self._human_like_typing(elem, BOOKING_DATA[data_key])

            return self._click_element(By.ID, "btnSiguiente")
        except Exception as e:
            logging.error(f"Ошибка заполнения формы бронирования: {str(e)}")
            return False

    def load_initial_page(self) -> bool:
        """Загрузка начальной страницы"""
        if not self.driver:
            return False

        try:
            self.driver.get(f"{self.base_url}/icpco/acOpcDirect")
            self._random_delay()

            if not self._handle_blocked_page():
                return False

            if not self._handle_initial_error():
                if (
                    "index" not in self.driver.current_url
                    and "acOpcDirect" not in self.driver.current_url
                ):
                    return False

            return True
        except Exception as e:
            logging.error(f"Ошибка загрузки страницы: {str(e)}")
            return False

    def _click_element(self, by: str, value: str) -> bool:
        """Клик по элементу с обработкой ошибок"""
        if not self.driver:
            return False

        try:
            element = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((by, value))
            )
            self._human_like_mouse_movement(element)
            element.click()
            self._random_delay()
            return True
        except Exception as e:
            logging.error(f"Ошибка клика по элементу {by}={value}: {str(e)}")
            return False

    def _select_dropdown(self, by: str, value: str, option_text: str) -> bool:
        """Выбор значения в выпадающем списке"""
        if not self.driver:
            return False

        try:
            select = Select(
                WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((by, value))
                )
            )
            self._human_like_mouse_movement(select)
            select.select_by_visible_text(option_text)
            self._random_delay()
            return True
        except Exception as e:
            logging.error(f"Ошибка выбора в dropdown {option_text}: {str(e)}")
            return False

    def restart_cycle(self) -> bool:
        """Перезапуск цикла проверки"""
        if not self.driver:
            return False

        try:
            if "acCitar" in self.driver.current_url:
                return self._click_element(By.ID, "btnSalir")
            elif "infogenerica" in self.driver.current_url:
                return self._handle_initial_error()
            else:
                self.driver.get(f"{self.base_url}/icpco/acOpcDirect")
                self._random_delay()
                return self._handle_blocked_page()
        except Exception:
            return False

    def check_slots(self) -> Dict[str, str]:
        """Проверка наличия свободных слотов"""
        if not self.driver:
            return {"status": "error"}

        try:
            if self._check_too_many_attempts():
                return {"status": "too_many_attempts"}

            if "acValidarEntrada" in self.driver.current_url:
                if not self._click_element(By.ID, "btnEnviar"):
                    return {"status": "error"}

            try:
                WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    lambda d: (
                        "no hay citas disponibles" in d.page_source.lower()
                        or "disponibilidad de citas" in d.page_source.lower()
                    )
                )

                if "no hay citas disponibles" in self.driver.page_source.lower():
                    return {"status": "no_slots"}
                return {"status": "slots_available"}

            except Exception:
                if self._check_too_many_attempts():
                    return {"status": "too_many_attempts"}

                if self._is_booking_page():
                    logging.critical("Найдены свободные места! Заполняем форму...")
                    if self._fill_booking_form():
                        return {"status": "form_filled"}
                    return {"status": "error"}

                logging.warning("Нестандартный ответ страницы, возможно есть слоты!")
                return {"status": "slots_available"}

        except Exception as e:
            logging.error(f"Ошибка проверки слотов: {str(e)}")
            return {"status": "error"}

    def select_province(self, province_name: str) -> bool:
        """Выбор провинции"""
        if not self.driver:
            return False

        try:
            if "index" not in self.driver.current_url:
                self.driver.get(f"{self.base_url}/icpco/index")
                self._random_delay()
                if not self._handle_blocked_page():
                    return False

            if self._check_too_many_attempts():
                return False

            return self._select_dropdown(
                By.NAME, "form", province_name
            ) and self._click_element(By.ID, "btnAceptar")
        except Exception as e:
            logging.error(f"Ошибка выбора провинции: {str(e)}")
            return False

    def select_tramite(self, tramite_name: str) -> bool:
        """Выбор типа процедуры"""
        if not self.driver:
            return False

        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "citar?p=" in d.current_url
            )

            if self._check_too_many_attempts():
                return False

            return self._select_dropdown(
                By.ID, "tramiteGrupo[1]", tramite_name
            ) and self._click_element(By.ID, "btnAceptar")
        except Exception as e:
            logging.error(f"Ошибка выбора trámite: {str(e)}")
            return False

    def submit_info_page(self) -> bool:
        """Отправка информационной страницы"""
        if not self.driver:
            return False

        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acInfo" in d.current_url
            )

            if self._check_too_many_attempts():
                return False

            return self._click_element(By.ID, "btnEntrar")
        except Exception as e:
            logging.error(f"Ошибка отправки информации: {str(e)}")
            return False

    def fill_personal_data(self) -> bool:
        """Заполнение персональных данных"""
        if not self.driver:
            return False

        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acEntrada" in d.current_url
            )

            if self._check_too_many_attempts():
                return False

            for field_id, value in PERSONAL_DATA.items():
                if field_id == "txtPaisNac":
                    continue

                elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, field_id))
                )
                elem.clear()
                self._human_like_typing(elem, value)
                self._random_delay()

            return self._select_dropdown(
                By.ID, "txtPaisNac", PERSONAL_DATA["txtPaisNac"]
            )
        except Exception as e:
            logging.error(f"Ошибка заполнения данных: {str(e)}")
            return False

    def confirm_data(self) -> bool:
        """Подтверждение данных"""
        if not self.driver:
            return False

        try:
            if self._check_too_many_attempts():
                return False

            if not self._click_element(By.ID, "btnEnviar"):
                return False

            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acValidarEntrada" in d.current_url
            )

            return True
        except Exception as e:
            logging.error(f"Ошибка подтверждения данных: {str(e)}")
            return False

    def restart_browser(self) -> bool:
        """Перезапуск браузера"""
        try:
            if self.driver:
                self.driver.quit()
            time.sleep(random.uniform(2, 5))
            self._init_driver()
            return True
        except Exception as e:
            logging.error(f"Ошибка перезапуска браузера: {str(e)}")
            return False

    def close(self) -> None:
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()

import logging
import random
import time

import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from settings import (
    MAX_DELAY,
    MIN_DELAY,
    PERSONAL_DATA,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    WAIT_TIMEOUT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


class RequestClient:
    def __init__(self):
        self.driver = None
        self.base_url = "https://icp.administracionelectronica.gob.es"
        self.current_url = ""
        self.random_delay = lambda: time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        self._init_driver()

    def _init_driver(self):
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
            f"--window-size={random.randint(1200,1400)},{random.randint(800,1000)}"
        )
        options.add_argument(
            f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90,115)}.0.0.0 Safari/537.36"
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

    def _check_too_many_attempts(self):
        """Проверка на сообщение 'Too Many Requests'"""
        try:
            page_text = self.driver.page_source.lower()
            if "too many requests" in page_text:
                return True

            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            if any("too many requests" in h1.text.lower() for h1 in h1_elements):
                return True

            return False
        except Exception:
            return False

    def _human_like_mouse_movement(self, element):
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(
                element, random.randint(-5, 5), random.randint(-5, 5)
            )
            actions.perform()
            time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass

    def _human_like_typing(self, element, text):
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

    def _handle_blocked_page(self):
        if "The requested URL was rejected" in self.driver.page_source:
            logging.warning("Обнаружена блокировка! Перезапускаем браузер...")
            self.restart_browser()
            return False
        return True

    def _handle_initial_error(self):
        try:
            if "infogenerica" in self.driver.current_url:
                accept_btn = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.ID, "btnSubmit"))
                )
                self._human_like_mouse_movement(accept_btn)
                accept_btn.click()
                self.random_delay()
                return True
            return False
        except Exception:
            return False

    def _is_booking_page(self):
        """Проверка, что это страница бронирования"""
        try:
            return (
                "CITA PREVIA EXTRANJERÍA" in self.driver.page_source
                and "POLICIA- EXPEDICIÓN/RENOVACIÓN DE DOCUMENTOS DE SOLICITANTES DE ASILO"
                in self.driver.page_source
                and "Identidad del usuario de cita" in self.driver.page_source
            )
        except Exception:
            return False

    def _fill_booking_form(self):
        """Заполнение формы бронирования"""
        try:
            # 1. Нажимаем кнопку Siguiente на первой странице
            if not self._click_element(By.ID, "btnSiguiente"):
                return False

            # 2. Заполняем данные на второй странице
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "txtTelefonoCitado"))
            )

            # Заполняем телефон
            phone_field = self.driver.find_element(By.ID, "txtTelefonoCitado")
            phone_field.clear()
            self._human_like_typing(phone_field, "661315361")

            # Заполняем email (первое поле)
            email1_field = self.driver.find_element(By.ID, "emailUNO")
            email1_field.clear()
            self._human_like_typing(email1_field, "m8adimka@gmail.com")

            # Заполняем email (второе поле)
            email2_field = self.driver.find_element(By.ID, "emailDOS")
            email2_field.clear()
            self._human_like_typing(email2_field, "m8adimka@gmail.com")

            # Заполняем motivo
            motivo_field = self.driver.find_element(By.ID, "txtObservaciones")
            motivo_field.clear()
            self._human_like_typing(
                motivo_field,
                "Renovación/prórroga de una tarjeta roja por su caducidad.",
            )

            # Нажимаем Siguiente
            if not self._click_element(By.ID, "btnSiguiente"):
                return False

            return True
        except Exception as e:
            logging.error(f"Ошибка заполнения формы бронирования: {str(e)}")
            return False

    def load_initial_page(self):
        try:
            self.driver.get(f"{self.base_url}/icpco/acOpcDirect")
            self.random_delay()

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

    def _click_element(self, by, value):
        try:
            element = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((by, value))
            )
            self._human_like_mouse_movement(element)
            element.click()
            self.random_delay()
            return True
        except Exception as e:
            logging.error(f"Ошибка клика: {str(e)}")
            return False

    def _select_dropdown(self, by, value, option_text):
        try:
            select = Select(
                WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((by, value))
                )
            )
            self._human_like_mouse_movement(select)
            select.select_by_visible_text(option_text)
            self.random_delay()
            return True
        except Exception as e:
            logging.error(f"Ошибка выбора в dropdown: {str(e)}")
            return False

    def restart_cycle(self):
        if "acCitar" in self.driver.current_url:
            return self._click_element(By.ID, "btnSalir")
        elif "infogenerica" in self.driver.current_url:
            return self._handle_initial_error()
        else:
            self.driver.get(f"{self.base_url}/icpco/acOpcDirect")
            self.random_delay()
            return self._handle_blocked_page()

    def check_slots(self):
        try:
            # Сначала проверяем на too many attempts
            if self._check_too_many_attempts():
                return {"status": "too_many_attempts"}

            if "acValidarEntrada" in self.driver.current_url:
                if not self._click_element(By.ID, "btnEnviar"):
                    return {"status": "error"}

            try:
                WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    lambda d: "no hay citas disponibles" in d.page_source.lower()
                    or "disponibilidad de citas" in d.page_source.lower()
                )

                if "no hay citas disponibles" in self.driver.page_source.lower():
                    return {"status": "no_slots"}
                return {"status": "slots_available"}

            except Exception:
                # Если не нашли стандартные сообщения, проверяем на too many attempts ещё раз
                if self._check_too_many_attempts():
                    return {"status": "too_many_attempts"}

                # Проверяем, не страница ли это бронирования
                if self._is_booking_page():
                    logging.critical("НАЙДЕНЫ СВОБОДНЫЕ МЕСТА! ЗАПОЛНЯЕМ ФОРМУ...")
                    if self._fill_booking_form():
                        self.send_telegram_alert(
                            "СРОЧНО: Доступны citas! Форма заполнена, требуется ручное подтверждение!"
                        )
                        return {"status": "form_filled"}
                    else:
                        self.send_telegram_alert(
                            "СРОЧНО: Доступны citas! Ошибка заполнения формы, требуется ручное вмешательство!"
                        )
                        return {"status": "error"}

                # Все остальные случаи считаем возможными слотами
                logging.warning("Нестандартный ответ страницы, возможно есть слоты!")
                self.send_telegram_alert(
                    "ВНИМАНИЕ: Нестандартный ответ страницы, проверьте вручную!"
                )
                return {"status": "slots_available"}

        except Exception as e:
            logging.error(f"Ошибка проверки слотов: {str(e)}")
            return {"status": "error"}

    def select_province(self, province_name):
        try:
            if "index" not in self.driver.current_url:
                self.driver.get(f"{self.base_url}/icpco/index")
                self.random_delay()
                if not self._handle_blocked_page():
                    return False

            if self._check_too_many_attempts():
                return "too_many_attempts"

            return self._select_dropdown(
                By.NAME, "form", province_name
            ) and self._click_element(By.ID, "btnAceptar")
        except Exception as e:
            logging.error(f"Ошибка выбора провинции: {str(e)}")
            return False

    def select_tramite(self, tramite_name):
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "citar?p=" in d.current_url
            )

            if self._check_too_many_attempts():
                return "too_many_attempts"

            return self._select_dropdown(
                By.ID, "tramiteGrupo[1]", tramite_name
            ) and self._click_element(By.ID, "btnAceptar")
        except Exception as e:
            logging.error(f"Ошибка выбора trámite: {str(e)}")
            return False

    def submit_info_page(self):
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acInfo" in d.current_url
            )

            if self._check_too_many_attempts():
                return "too_many_attempts"

            return self._click_element(By.ID, "btnEntrar")
        except Exception as e:
            logging.error(f"Ошибка отправки информации: {str(e)}")
            return False

    def fill_personal_data(self):
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acEntrada" in d.current_url
            )

            if self._check_too_many_attempts():
                return "too_many_attempts"

            for field_id, value in PERSONAL_DATA.items():
                if field_id == "txtPaisNac":
                    continue

                elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, field_id))
                )
                elem.clear()
                self._human_like_typing(elem, value)
                self.random_delay()

            if not self._select_dropdown(
                By.ID, "txtPaisNac", PERSONAL_DATA["txtPaisNac"]
            ):
                return False

            return True
        except Exception as e:
            logging.error(f"Ошибка заполнения данных: {str(e)}")
            return False

    def confirm_data(self):
        try:
            if self._check_too_many_attempts():
                return "too_many_attempts"

            if not self._click_element(By.ID, "btnEnviar"):
                return False

            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                lambda d: "acValidarEntrada" in d.current_url
            )

            return True
        except Exception as e:
            logging.error(f"Ошибка подтверждения данных: {str(e)}")
            return False

    def send_telegram_alert(self, message):
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": f"🚨 *{message}*\n\nСсылка: {self.driver.current_url}",
                    "parse_mode": "Markdown",
                },
                timeout=5,
            )
        except Exception as e:
            logging.error(f"Ошибка отправки в Telegram: {str(e)}")

    def restart_browser(self):
        try:
            if self.driver:
                self.driver.quit()
            time.sleep(random.uniform(2, 5))
            self._init_driver()
            return True
        except Exception as e:
            logging.error(f"Ошибка перезапуска браузера: {str(e)}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()

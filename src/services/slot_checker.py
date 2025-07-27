import logging
import random
import time

from src.client.request_client import RequestClient
from src.settings import MAX_RETRIES, RATE_LIMIT_DELAY
from src.telegram.notifier import TelegramNotifier


class SlotCheckerService:
    def __init__(self):
        self.client = RequestClient()
        self.notifier = TelegramNotifier()

    def run(self):
        retries = 0
        steps = [
            ("Выбор провинции", self.client.select_province, ["Alicante"]),
            (
                "Выбор trámite",
                self.client.select_tramite,
                [
                    "POLICIA- EXPEDICIÓN/RENOVACIÓN DE DOCUMENTOS DE SOLICITANTES DE ASILO"
                ],
            ),
            ("Отправка информации", self.client.submit_info_page),
            ("Заполнение данных", self.client.fill_personal_data),
            ("Подтверждение данных", self.client.confirm_data),
        ]

        while retries < MAX_RETRIES:
            try:
                logging.info(f"Попытка {retries + 1}/{MAX_RETRIES}")
                if not self.client.load_initial_page():
                    raise Exception("Не удалось загрузить начальную страницу")

                for step_name, func, args in steps:
                    logging.info(f"Выполняется: {step_name}")
                    result = func(*args)
                    if result == "too_many_attempts":
                        logging.warning("Слишком много попыток, ждем")
                        time.sleep(RATE_LIMIT_DELAY)
                        retries -= 1
                        raise Exception("Повтор после too_many_attempts")
                    elif not result:
                        raise Exception(f"Ошибка на шаге: {step_name}")

                while True:
                    check_result = self.client.check_slots()

                    if check_result["status"] == "slots_available":
                        logging.critical("Свободные слоты найдены!")
                        self.notifier.send_message("СРОЧНО: Доступны citas!")
                        time.sleep(3600)
                        return

                    elif check_result["status"] == "form_filled":
                        logging.critical("Форма бронирования заполнена!")
                        self.notifier.send_message(
                            "Форма заполнена, требуется ручное подтверждение!"
                        )
                        time.sleep(3600)
                        return

                    elif check_result["status"] == "error":
                        raise Exception("Ошибка проверки слотов")

                    else:
                        logging.info("Слоты не найдены, повторяем цикл")
                        if not self.client.restart_cycle():
                            raise Exception("Ошибка перезапуска цикла")

                        t = random.randint(20, 60)
                        logging.info(f"Ждем {t} секунд перед повтором")
                        time.sleep(t)
                        for step_name, func, args in steps:
                            result = func(*args)
                            if result == "too_many_attempts":
                                logging.warning("Слишком много попыток, ждем")
                                time.sleep(RATE_LIMIT_DELAY)
                                retries -= 1
                                raise Exception("Повтор после too_many_attempts")
                            elif not result:
                                raise Exception(
                                    f"Ошибка на повторном шаге: {step_name}"
                                )

            except Exception as e:
                logging.error(f"Ошибка: {str(e)}")
                retries += 1
                self.client.restart_browser()
                time.sleep(random.uniform(1, 3))

        logging.error(f"Превышено максимальное количество попыток ({MAX_RETRIES})")
        self.client.close()

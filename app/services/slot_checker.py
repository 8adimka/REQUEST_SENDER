import logging
import random
import time

from app.client.request_client import RequestClient
from app.settings import MAX_RETRIES, RATE_LIMIT_DELAY
from app.telegram.notifier import TelegramNotifier


class SlotCheckerService:
    def __init__(self):
        self.client = RequestClient()
        self.notifier = TelegramNotifier()

    def _execute_steps(self, steps):
        for step_name, func, args in steps:
            logging.info(f"Executing: {step_name}")
            result = func(*args)
            if result == "too_many_attempts":
                logging.warning("Too many attempts, waiting")
                time.sleep(RATE_LIMIT_DELAY)
                return "too_many_attempts"
            elif not result:
                raise Exception(f"Step failed: {step_name}")
        return True

    def run(self):
        retries = 0
        steps = [
            ("Select province", self.client.select_province, ["Alicante"]),
            (
                "Select tramite",
                self.client.select_tramite,
                [
                    "POLICIA- EXPEDICIÓN/RENOVACIÓN DE DOCUMENTOS DE SOLICITANTES DE ASILO"
                ],
            ),
            ("Submit info", self.client.submit_info_page, []),
            ("Fill data", self.client.fill_personal_data, []),
            ("Confirm data", self.client.confirm_data, []),
        ]

        while retries < MAX_RETRIES:
            try:
                logging.info(f"Attempt {retries + 1}/{MAX_RETRIES}")
                if not self.client.load_initial_page():
                    raise Exception("Failed to load initial page")

                step_result = self._execute_steps(steps)
                if step_result == "too_many_attempts":
                    retries -= 1
                    continue

                while True:
                    check_result = self.client.check_slots()

                    if check_result["status"] == "slots_available":
                        self.notifier.send_message(
                            "URGENT: Available citas!", self.client.current_url
                        )
                        time.sleep(3600)
                        return

                    elif check_result["status"] == "form_filled":
                        self.notifier.send_message(
                            "Form filled, manual confirmation required!",
                            self.client.current_url,
                        )
                        time.sleep(3600)
                        return

                    elif check_result["status"] == "error":
                        raise Exception("Slot check error")

                    else:
                        logging.info("No slots, retrying")
                        if not self.client.restart_cycle():
                            raise Exception("Cycle restart failed")

                        delay = random.randint(20, 60)
                        logging.info(f"Waiting {delay} seconds")
                        time.sleep(delay)

                        step_result = self._execute_steps(steps)
                        if step_result == "too_many_attempts":
                            retries -= 1
                            raise Exception("Retry after too_many_attempts")

            except Exception as e:
                logging.error(f"Error: {str(e)}")
                retries += 1
                self.client.restart_browser()
                time.sleep(random.uniform(1, 3))

        logging.error(f"Max attempts reached ({MAX_RETRIES})")
        self.client.close()

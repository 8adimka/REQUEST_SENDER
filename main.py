import time
import random
from request_client import RequestClient
import logging
from settings import MAX_RETRIES, RATE_LIMIT_DELAY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    retries = 0
    client = None
    
    while retries < MAX_RETRIES:
        try:
            client = RequestClient()
            logging.info(f"Попытка {retries + 1}/{MAX_RETRIES}")
            
            if not client.load_initial_page():
                raise Exception("Не удалось загрузить начальную страницу")
                
            steps = [
                ("Выбор провинции", client.select_province, ["Alicante"]),
                ("Выбор trámite", client.select_tramite, ["POLICIA- EXPEDICIÓN/RENOVACIÓN DE DOCUMENTOS DE SOLICITANTES DE ASILO"]),
                ("Отправка информации", client.submit_info_page),
                ("Заполнение данных", client.fill_personal_data),
                ("Подтверждение данных", client.confirm_data),
                ("Проверка слотов", client.check_slots)
            ]
            
            for step_name, step_func, *args in steps:
                logging.info(f"Выполняется: {step_name}")
                result = step_func(*args[0] if args else [])
                if result == "too_many_attempts":
                    logging.warning("Обнаружено слишком много попыток, ожидаем 5 минут...")
                    time.sleep(RATE_LIMIT_DELAY)
                    retries -= 1  # Не считать эту попытку
                    raise Exception("Повтор после too_many_attempts")
                elif not result:
                    raise Exception(f"Ошибка на шаге: {step_name}")
                    break
            
            while True:
                result = client.check_slots()
                
                if result["status"] == "slots_available":
                    logging.critical("НАЙДЕНЫ СВОБОДНЫЕ МЕСТА!")
                    client.send_telegram_alert("СРОЧНО: Доступны citas!")
                    time.sleep(3600)  # Даем время на ручное подтверждение
                    return
                elif result["status"] == "form_filled":
                    logging.critical("ФОРМА БРОНИРОВАНИЯ ЗАПОЛНЕНА!")
                    time.sleep(3600)  # Даем время на ручное подтверждение
                    return
                elif result["status"] == "error":
                    raise Exception("Ошибка проверки слотов")
                else:
                    logging.info("Нет доступных слотов, перезапуск цикла")
                    if not client.restart_cycle():
                        raise Exception("Ошибка перезапуска цикла")
                    
                    # Быстро проходим шаги заново
                    t = random.randint(20,60)
                    print(f"Ожидаем {t} секунд")
                    time.sleep(t)
                    for step_name, step_func, *args in steps:
                        result = step_func(*args[0] if args else [])
                        if result == "too_many_attempts":
                            logging.warning("Обнаружено слишком много попыток, ожидаем 5 минут...")
                            time.sleep(RATE_LIMIT_DELAY)
                            retries -= 1
                            raise Exception("Повтор после too_many_attempts")
                        elif not result:
                            raise Exception(f"Ошибка повторного прохождения шага {step_name}")

        except Exception as e:
            logging.error(f"Ошибка: {str(e)}")
            retries += 1
            if client:
                client.restart_browser()
            time.sleep(random.uniform(1, 3))

    logging.error(f"Достигнуто максимальное количество попыток ({MAX_RETRIES})")
    if client:
        client.close()

if __name__ == "__main__":
    main()
    
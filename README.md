# Автоматизированная проверка доступных слотов для записи

# 🇷🇺 Русская версия

## 📋 Описание

Программа автоматически проверяет доступность слотов (citas) на официальном сайте Министерства внутренних дел Испании для замены удостоверения личности (TIE, NIE, tarjeta roja) для лиц, запросивших убежище. При обнаружении свободных слотов отправляет уведомление в ваш Telegram-бот, после чего введёт ваши личные данные и закончит запись в автоматическом режиме, либо вы можете завершить запись вручную.

### Она нужна вам и придётся со всем этим разобраться если

- Вы живёте в Испании (особенно в Аликанте)
- Вы подавались на убежище и подошёл срок менять карту
- Вы не хотите платить 100 евро ситоловам, которые всё сделают за вас

## Используемый стек технологий

- Python 3 — основной язык программирования
- selenium — автоматизация действий в браузере
- undetected-chromedriver — модифицированный драйвер Chrome для обхода защиты от ботов
- requests — для отправки HTTP-запросов (например, к API)
- python-dotenv — для загрузки переменных окружения из .env файла

## Среда выполнения

- Arch Linux / Windows (проект кроссплатформенный)
- Docker (рекомендуемый способ развертывания)
- Google Chrome (работа через undetected-chromedriver)

## 🔗 Официальный сайт: [https://icp.administracionelectronica.gob.es/icpco/index](https://icp.administracionelectronica.gob.es/icpco/index)

### 🔔 Настройка Telegram-бота

1. Создайте бота через [BotFather](https://t.me/BotFather):
   - Отправьте `/newbot`
   - Укажите имя бота (например: `CitaCheckerBot`)
   - Получите токен вида `123456789:AAFm2e4f5g6h7i8j9k0l1m2n9o4p5q6r7s8`

2. Узнайте свой Chat ID:
   - Добавьте бота [userinfobot](https://t.me/userinfobot)
   - Отправьте любое сообщение этому боту
   - Он ответит с вашим Chat ID

3. Сохраните полученные:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

# Настройка программы

- Скопируйте env.example в .env

- Откройте .env в Блокноте

- Заполните свои данные

## 🔧 Настройка персональных данных

Откройте файл .env и измените:

```ini
# Ваши личные данные
PERSONAL_DATA='{
  "txtIdCitado": "Z1234567R",       # Ваш NIE/NIF
  "txtDesCitado": "IVAN PETROV",    # Ваше имя как в документе
  "txtAnnoCitado": "1985",          # Год рождения
  "txtPaisNac": "RUSIA"             # Страна рождения (испанское написание)
}'

# Данные Telegram-бота
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_chat_ID"
```

# 🚀 Запуск программы

## Docker (рекомендуемый способ)

- Запускает весь процесс в закрытом контейнере (вы его не видите), но в случае успеха - получите все данные уведомлением в telegram.
- Это избавляет вас от необходимости вручную настраивать все зависимости, но лишает вас возможности вручную доввести что-либо в браузере, в случае необходимости. Однако, основная функциональность послостью автоматизирована.

1. Убедитесь что установлен Docker и Docker Compose
2. Заполните .env файл (скопируйте из .env.example)
3. Выполните команды:

```bash
docker-compose build
docker-compose up
```

- Доступные порты:

  - 4444 - Selenium Grid
  - 5900 - VNC (для отладки)

# ⚙️ Установка и локальный запуск на Linux (Arch)

1. **Установите Python 3.11:**

   ```bash
   sudo pacman -S python311
   ```

2. Создайте виртуальное окружение в папке проекта:

```bash
python3.11 -m venv env_name

source env_name/bin/activate
```

3. Установите браузер Chrome:

```bash
sudo pacman -S google-chrome
```

4. Установите Chromedriver:

```bash
yay -S chromedriver
```

5. Проверьте совместимость версий:

```bash
google-chrome-stable --version  # Должна быть версия 135+
chromedriver --version         # Версии должны совпадать
```

6. Установите зависимости:

```bash
pip install undetected-chromedriver selenium python-dotenv requests
```

7. Настройка программы:

```bash
cp .env.example .env
nano .env  # Заполните свои данные
```

## Linux (локальный запуск)

```source env_name/bin/activate
PYTHONPATH=. python scripts/main.py
```

### Пара небольших дополнений  

в файле /request_client.py
есть строка - version_main=136
в участке ```self.driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True,
            version_main=136
        )```

- не забудьсе синхнонизировать вашу версию Google chrome и ChromeWebDriver
- Вводим команды:
  - ```chromedriver --version```

    - Узнаём версию WebDriver

  - ```google-chrome-stable --version```

    - Узнаём версию google-chrome

Желательно одинаковые, если нет то меняем - ```version_main=136``` на версию вашего google-chrome

- Для чистоты перед запуском скрипта рекомендую выполнить (не обязательно)  
```pkill -f chromedriver && pkill -f chrome && rm -rf /home/v/.config/selenium-profile```

- т.е. убить процессы браузера и почистить кэш selenium

# 🪟 Установка на Windows

## Установите Python 3.11

Скачайте установщик с официального сайта

В установщике отметьте:

- ☑ Add Python to PATH

- ☑ Install launcher for all users

## Установите Google Chrome

Скачайте с официального сайта

После установки проверьте версию:

- Откройте chrome://settings/help

- Должна быть версия 135+

## Установите Chromedriver

Скачайте соответствующую версию с официального сайта

Распакуйте chromedriver.exe в папку с программой

Установите зависимости (в CMD):

```cmd
py -3.11 -m pip install undetected-chromedriver selenium python-dotenv requests
```

## Локальный запуск Windows

```bash
py -3.11 main.py
```

## ⚠️ Важные примечания

### Для Docker-развертывания

- Убедитесь что версии Chrome в контейнере и ChromeDriver совместимы
- Для отладки можно подключиться через VNC (порт 5900)
- Логи доступны через `docker-compose logs`

Программа автоматически делает паузу 5 минут при обнаружении "Too Many Requests"

При обнаружении слотов:

- Отправляет Telegram-уведомление

- Оставляет браузер открытым для ручного завершения

- Делает паузу 1 час перед следующим циклом

- Рекомендуется запускать на сервере с постоянным подключением к интернету

# Automated Appointment Slot Checker

# 🇬🇧 English Version

## 📋 Description

The program automatically checks for available appointment slots (citas) on the official Spanish Ministry of Interior website for renewing identity documents (TIE, NIE, tarjeta roja) for asylum seekers. When free slots are found, it sends a notification to your Telegram bot, then can either automatically enter your personal data and complete the booking, or leave the browser open for manual completion.

## Technology Stack

- Python 3 - main programming language
- selenium - browser automation
- undetected-chromedriver - modified Chrome driver to bypass bot protection
- requests - for sending HTTP requests (e.g. to APIs)
- python-dotenv - for loading environment variables from .env file

## Runtime Environment

- Arch Linux / Windows (cross-platform project)
- Docker (recommended deployment method)
- Google Chrome (works through undetected-chromedriver)

## 🔗 Official website: [https://icp.administracionelectronica.gob.es/icpco/index](https://icp.administracionelectronica.gob.es/icpco/index)

### 🔔 Telegram Bot Setup

1. Create a bot via [BotFather](https://t.me/BotFather):
   - Send `/newbot`
   - Specify bot name (e.g.: `CitaCheckerBot`)
   - Get token in format `123456789:AAFm2e4f5g6h7i8j9k0l1m2n9o4p5q6r7s8`

2. Get your Chat ID:
   - Add [userinfobot](https://t.me/userinfobot)
   - Send any message to this bot
   - It will reply with your Chat ID

3. Save these values:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

# Program Configuration

- Copy env.example to .env
- Open .env in a text editor
- Fill in your details

## 🔧 Personal Data Configuration

Open .env file and modify:

```ini
# Your personal data
PERSONAL_DATA='{
  "txtIdCitado": "Z1234567R",       # Your NIE/NIF
  "txtDesCitado": "IVAN PETROV",    # Your name as in documents
  "txtAnnoCitado": "1985",          # Birth year
  "txtPaisNac": "RUSIA"             # Birth country (Spanish spelling)
}'

# Telegram bot data
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_chat_ID"
```

# 🚀 Running the Program

## Docker (Recommended Method)

1. Make sure Docker and Docker Compose are installed
2. Configure .env file (copy from .env.example)
3. Run commands:

```bash
docker-compose build
docker-compose up
```

Available ports:

- 4444 - Selenium Grid
- 5900 - VNC (for debugging)

# ⚙️ Linux (Arch) Installation

1. **Install Python 3.11:**

   ```bash
   sudo pacman -S python311
   ```

2. Create virtual environment in project folder:

```bash
python3.11 -m venv env_name
source env_name/bin/activate
```

3. Install Chrome browser:

```bash
sudo pacman -S google-chrome
```

4. Install Chromedriver:

```bash
yay -S chromedriver
```

5. Verify version compatibility:

```bash
google-chrome-stable --version  # Should be version 135+
chromedriver --version         # Versions should match
```

6. Install dependencies:

```bash
pip install undetected-chromedriver selenium python-dotenv requests
```

7. Program configuration:

```bash
cp .env.example .env
nano .env  # Fill in your details
```

## Linux (Local Run)

```bash
source env_name/bin/activate
PYTHONPATH=. python scripts/main.py
```

### Important Notes

In file /request_client.py
there's a line - version_main=136
in section ```self.driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True,
            version_main=136
        )```

- Don't forget to synchronize your Google Chrome and ChromeWebDriver versions
- Run commands:
  - ```chromedriver --version``` - Check WebDriver version
  - ```google-chrome-stable --version``` - Check Chrome version

Versions should match, if not change ```version_main=136``` to your Chrome version

- For clean runs (optional but recommended):
```pkill -f chromedriver && pkill -f chrome && rm -rf /home/v/.config/selenium-profile```

- This kills browser processes and cleans selenium cache

# 🪟 Windows Installation

## Install Python 3.11

Download installer from official site

During installation check:

- ☑ Add Python to PATH
- ☑ Install launcher for all users

## Install Google Chrome

Download from official site

After installation verify version:

- Open chrome://settings/help
- Should be version 135+

## Install Chromedriver

Download matching version from official site
Unzip chromedriver.exe to program folder
Install dependencies (in CMD):

```cmd
py -3.11 -m pip install undetected-chromedriver selenium python-dotenv requests
```

## Windows Local Run

```bash
py -3.11 main.py
```

## ⚠️ Important Notes

### For Docker Deployment

- Ensure Chrome and ChromeDriver versions in container are compatible
- Debug via VNC (port 5900)
- View logs with `docker-compose logs`

Program automatically pauses for 5 minutes when detecting "Too Many Requests"

When slots are found:

- Sends Telegram notification
- Keeps browser open for manual completion
- Pauses for 1 hour before next cycle
- Recommended to run on a server with stable internet connection

# 📜 License

MIT License - Free for personal and commercial use

Copyright (c) 2025 REQUEST_SENDER Project

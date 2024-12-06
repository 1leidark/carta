import time
import json
import os
from flask import Flask, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Путь к файлу данных
DATA_FILE = os.path.join(os.getcwd(), 'data.json')

# Список регионов
REGION_ORDER = [
    "Белгородская область", "Брянская область", "Владимирская область", "Воронежская область",
    "Ивановская область", "Калужская область", "Костромская область", "Курская область",
    "Липецкая область", "Московская область", "Орловская область", "Рязанская область",
    "Смоленская область", "Тамбовская область", "Тверская область", "Тульская область",
    "Ярославская область", "г.Москва", "Республика Карелия", "Республика Коми",
    "Архангельская область", "Вологодская область", "Калининградская область",
    "Ленинградская область", "Мурманская область", "Новгородская область", "Псковская область",
    "г.Санкт-Петербург", "Республика Адыгея", "Республика Дагестан", "Республика Ингушетия",
    "Кабардино-Балкарская Республика", "Республика Калмыкия", "Карачаево-Черкесская Республика",
    "Республика Северная Осетия - Алания", "Чеченская Республика", "Краснодарский край",
    "Ставропольский край", "Астраханская область", "Волгоградская область", "Ростовская область",
    "Республика Башкортостан", "Республика Марий Эл", "Республика Мордовия", "Республика Татарстан",
    "Удмуртская Республика", "Чувашская Республика", "Пермский край", "Кировская область",
    "Нижегородская область", "Оренбургская область", "Пензенская область", "Самарская область",
    "Саратовская область", "Ульяновская область", "Курганская область", "Свердловская область",
    "Тюменская область", "Ханты-Мансийский автономный округ-Югра", "Ямало-Ненецкий автономный округ",
    "Челябинская область", "Республика Алтай", "Республика Бурятия", "Республика Тыва",
    "Республика Хакасия", "Алтайский край", "Забайкальский край", "Красноярский край",
    "Иркутская область", "Кемеровская область", "Новосибирская область", "Омская область",
    "Томская область", "Республика Саха (Якутия)", "Камчатский край", "Приморский край",
    "Хабаровский край", "Амурская область", "Магаданская область", "Сахалинская область",
    "Еврейская автономная область", "Чукотский автономный округ", "Республика Крым"
]


# Загрузка данных из файла
def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"Файл {DATA_FILE} не существует.")
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки данных: {e}")
        return []

# Сохранение данных в файл
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Данные успешно сохранены в файл {DATA_FILE}")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

# Главная страница
@app.route('/')
def home():
    data = load_data()
    return render_template('index.html', data=data)

# Обновление данных по бензину
@app.route('/update_data', methods=['POST'])
def update_data():
    data = load_data()
    new_data = get_latest_data(data)
    if new_data:
        save_data(new_data)
    return redirect(url_for('home'))

# Обновление данных по электричеству
@app.route('/update_electric_data', methods=['POST'])
def update_electric_data():
    electric_data = fetch_electric_data()
    data = load_data()

    updated_data = []
    for existing_entry in data:
        region = existing_entry.get("region")
        if not region:
            continue

        new_electric_price = electric_data.get(region)

        if new_electric_price is not None and new_electric_price > 0:
            existing_entry["electric_price"] = new_electric_price

        updated_data.append(existing_entry)

    save_data(updated_data)
    return redirect(url_for('home'))

# Путь к ChromeDriver и бинарному файлу Chrome
chrome_driver_path = '/usr/local/bin/chromedriver'
chrome_binary_path = '/usr/bin/chromium-browser'

chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument("--window-size=800x600")  # Минимизация окна

service = Service(executable_path=chrome_driver_path)

# Функция запуска браузера с повторными попытками
def start_driver_with_retries(retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            logging.info(f"Попытка запуска ChromeDriver: {attempt + 1}/{retries}")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            WebDriverWait(driver, 20)  # Не увеличивайте тайм-ауты без необходимости
            logging.info("ChromeDriver успешно запущен")
            return driver
        except WebDriverException as e:
            logging.error(f"Ошибка запуска ChromeDriver: {e}")
            attempt += 1
            time.sleep(delay)  # Задержка перед повторной попыткой
    raise RuntimeError("Не удалось запустить ChromeDriver после нескольких попыток")

# Пример использования
try:
    driver = start_driver_with_retries(retries=3, delay=5)  # 3 попытки с задержкой в 5 секунд
    driver.get("https://www.google.com")
    WebDriverWait(driver, 10).until(EC.title_contains("Google"))  # Явное ожидание
    print("Title of the page is:", driver.title)
finally:
    if 'driver' in locals():
        driver.quit()


# Функция для получения данных с сайта (для бензина)
def get_latest_data(existing_data):
    username = 'leidark777@gmail.com'
    password = 'lei777dark'

    latest_prices = {region['id']: region for region in existing_data}

    try:
        driver.get("https://www.benzin-price.ru/account.php")
        username_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='login']"))
        )
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='ok']"))
        )
        login_button.click()

        time.sleep(5)

        for region_id in range(1, 6):  # Можете изменять диапазон в зависимости от нужд
            region_url = f'https://www.benzin-price.ru/stat_month.php?region_id={region_id}'
            driver.get(region_url)
            time.sleep(10)

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', {'cellpadding': '5', 'cellspacing': '1', 'border': '0'})

            if table:
                rows = table.find_all('tr')
                last_valid_data = None

                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) > 4:
                        ai_95_price = cells[4].get_text().strip()
                        electric_price = "N/A"

                        try:
                            ai_95_price = float(ai_95_price.replace(',', '.'))
                            if ai_95_price > 0:
                                last_valid_data = {"ai_95_price": ai_95_price, "electric_price": electric_price}
                        except ValueError:
                            continue

                if last_valid_data:
                    calc_value_3 = last_valid_data["ai_95_price"] * 8
                    existing_entry = next((entry for entry in existing_data if entry['id'] == region_id), None)
                    calc_value_4 = existing_entry['calc_value_4'] if existing_entry and 'calc_value_4' in existing_entry else 0

                    latest_prices[region_id] = {
                        "id": region_id,
                        "region": existing_data[region_id - 1]["region"],
                        "ai_95_price": last_valid_data["ai_95_price"],
                        "electric_price": existing_data[region_id - 1]["electric_price"],
                        "calc_value_3": calc_value_3,
                        "calc_value_4": calc_value_4,
                        "source": "ИСТИНА"
                    }
    except Exception as e:
        print(f"Ошибка при авторизации или соединении: {e}")
    finally:
        driver.quit()

    return list(latest_prices.values())

# Функция для получения данных по электричеству
def fetch_electric_data():
    service = webdriver.chrome.service.Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = 'https://time2save.ru/tarify-na-elektroenergiu-dla-malih-predpriyatiy-i-ip'

    try:
        driver.get(url)
        time.sleep(20)
        table = driver.find_element(By.CLASS_NAME, 'table_title')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        data = {}
        for row in rows[2:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 0:
                region = cells[0].text.strip()
                price = float(cells[-2].text.strip().replace(',', '.'))
                data[region] = round(price, 2)
        return data
    except Exception as e:
        print("Ошибка при парсинге электричества:", e)
        return {}
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)

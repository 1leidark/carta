import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

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

def fetch_electric_data():
    options = Options()
    options.add_argument('--no-sandbox')  
    options.add_argument('--disable-dev-shm-usage')  

    service = Service('/usr/local/bin/chromedriver')

    # Инициализация драйвера с настройками
    driver = webdriver.Chrome(service=service, options=options)
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

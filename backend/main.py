import pandas as pd
from bs4 import BeautifulSoup
import time as tm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc


# Загрузка кодов товаров из файла
with open('codes.txt', 'r') as f:
    codes = f.read().splitlines()

# Создание пустого DataFrame для хранения данных
df = pd.DataFrame(columns=['Код товара', 'Название товара', 'URL страницы с товаром', 'URL первой картинки', 'Цена базовая', 'Цена с учетом скидок без Ozon Карты', 'Цена по Ozon Карте', 'Продавец', 'Количество отзывов', 'Количество видео', 'Количество вопросов', 'Рейтинг товара', 'Все доступные характеристики товара', 'Информация о доставке в Москве', 'Уцененный товар'])

# Инициализация веб-драйвера
driver = uc.Chrome()

# Парсинг каждого товара
for code in codes:

#получение ссылки на товар через костыли
    #ссылка на главную страницу озон
    url = 'https://www.ozon.ru'

    # Загрузка страницы товара с помощью веб-драйвера
    driver.get(url)
    tm.sleep(2)

    find_goods = driver.find_element(By.NAME, 'text')
    find_goods.clear()
    find_goods.send_keys(code)
    tm.sleep(2)

    find_goods.send_keys(Keys.ENTER)
    tm.sleep(2)

    try:
        find_goods = driver.find_element(By.XPATH, '//*[@id="paginatorContent"]/div/div/div/a')
    except:
        continue
    find_goods.click()
    tm.sleep(2)

    # Получение HTML-кода страницы
    page_source = str(driver.page_source)

    # Создание объекта BeautifulSoup для парсинга HTML-кода
    soup = BeautifulSoup(page_source, 'html.parser')

#работа с html
    # Получение названия товара
    name_element = soup.find('h1', {'class': 'ln3'})#.find('h1')
    name = name_element.text.strip() if name_element else 'No name'

    # Получение URL страницы с товаром
    page_url = url + '/' + code

    # Получение URL первой картинки
    image_element = soup.find('img')
    image_url = image_element.get('src') if image_element else ''

    # Получение цены базовая
    base_price_element = soup.find('span', {'class': 'm7l m8l m6l lm8'})
    base_price = base_price_element.text.strip() if base_price_element is not None else ''

    # Получение цены со скидкой без Ozon Карты
    discount_price_element = soup.find('span', {'class': 'l8m ml8 n1l'})
    discount_price = discount_price_element.text.strip() if discount_price_element else ''

    # Получение цены по Ozon Карте
    ozon_card_price_element = soup.find('span', {'class': 'ml3 m1l'})
    ozon_card_price = ozon_card_price_element.text.strip() if ozon_card_price_element else ''

    # Получение продавца
    seller_element = soup.find('a', {'class': 'j4q'})
    seller = seller_element.text.strip() if seller_element else ''

    # Получение количества отзывов, видео, вопросов
    reviews_element = soup.findAll('div', {'class': 'a2429-e7'})
    reviews_count = reviews_element[0].text.strip().split()[0] if reviews_element[0] else ''
    video_count = reviews_element[1].text.strip().split()[0] if reviews_element[1] else ''
    questions_count = reviews_element[2].text.strip().split()[0] if reviews_element[2] else ''


    # Получение всех доступных характеристик товара
    characteristics_element = soup.findAll('dd', {'class': 'tj8'})
    characteristics = ', '.join([element.text.strip() for element in characteristics_element]) if characteristics_element else ''

    # Получение информации о доставке в Москве
    delivery_info_element = soup.find('div', {'class': 'k5m'})
    delivery_info = delivery_info_element.text.strip() if delivery_info_element else ''

    # Получение рейтинга
    rate_element = soup.find('div', {'class': 'r2r'})
    rate_info = rate_element.text.strip().split('/')[0].strip() if rate_element else ''

    # Получение информации об уцененном товаре
    damaged_element = soup.find('div', {'class': 'd7b1'})
    damaged_info = damaged_element.text.strip() if damaged_element else ''

    # Заполнение DataFrame
    df = pd.concat([
        df, pd.DataFrame({
            'Код товара': [code],
            'Название товара': [name],
            'URL страницы с товаром': [page_url],
            'URL первой картинки': [image_url],
            'Цена базовая': [base_price],
            'Цена с учетом скидок без Ozon Карты': [discount_price],
            'Цена по Ozon Карте': [ozon_card_price],
            'Продавец': [seller],
            'Количество отзывов': [reviews_count],
            'Количество видео': video_count,
            'Количество вопросов': questions_count,
            'Рейтинг товара': rate_info,
            'Все доступные характеристики товара': [characteristics],
            'Информация о доставке в Москве': [delivery_info],
            'Уцененный товар': [damaged_info]
        })
    ], ignore_index=True)

# Закрытие веб-драйвера
driver.close()
driver.quit()

# Сохранение DataFrame в файл
df.to_excel('products.xlsx', index=False)







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
df = pd.DataFrame(columns=['Код товара', 'Название товара', 'URL страницы с товаром', 'URL первой картинки', 'Цена базовая', 'Цена с учетом скидок без Ozon Карты', 'Цена по Ozon Карте', 'Продавец', 'Количество отзывов', 'Количество видео', 'Количество вопросов', 'Рейтинг товара', 'Все доступные характеристики товара', 'Информация о доставке в Москве'])

# Инициализация веб-драйвера
driver = uc.Chrome()

driver.implicitly_wait(10)

# Парсинг каждого товара
for code in codes:
    # try:
        print(code)
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
        # работа с html
        # Получение названия товара
        name_element = soup.find('h1')
        name = name_element.text.strip() if name_element else 'No name'
        tm.sleep(2)

        if True:
            print('video')
            find_img = driver.find_element(By.XPATH, '//*[@data-index="1"]').find_element(By.TAG_NAME, 'img')
            find_img.click()
            tm.sleep(1)
            image_element = driver.find_element(By.CSS_SELECTOR, f'//*[@alt*="{name}"]').get_attribute('src')
            print(image_element)
            image_url = ''
        # else:
        #     # Получение URL первой картинки
        #     image_element = soup.select(f'img[alt*="{name}"]')
        #     print(soup.select(f'img[alt*="{name}"]'))
        #     # image_url = image_element[1].get('src') if image_element else ''

        # Получение информации о доставке в Москве
        tm.sleep(1)
        driver.execute_script("window.scrollBy(0, 3200)")
        tm.sleep(4)
        try:
            delivery_info_element = soup.find('h2', string="Информация о доставке").parent
            delivery_info = delivery_info_element.text.strip() if delivery_info_element else ''
        except:
            delivery_info = ''

        # Получение URL страницы с товаром
        page_url = url + '/product/' + code

        # Получение цены со скидкой без Ozon Карты
        price_element = soup.find('span', string="без Ozon Карты").parent.parent.find('div').findAll('span')
        discount_price = price_element[0].text.strip() if price_element[0] else ''

        # Получение цены базовая
        base_price = price_element[1].text.strip() if price_element[1] is not None else ''

        # Получение цены по Ozon Карте
        ozon_card_price_element = soup.find('span', string="c Ozon Картой").parent.find('div').find('span')
        ozon_card_price = ozon_card_price_element.text.strip() if ozon_card_price_element else ''

        # Получение количества отзывов, видео, вопросов
        reviews_element = soup.find('div', {"data-widget": "webReviewProductScore"}).find('a').find('div')
        reviews_count = reviews_element.text.strip().split()[0] if reviews_element else ''

        video_element = soup.find('div', {"data-widget": "webVideosCount"}).find('a').find('div')
        video_count = video_element.text.strip().split()[0] if video_element else ''

        questions_element = soup.find('div', {"data-widget": "webQuestionCount"}).find('a').find('div')
        questions_count = questions_element.text.strip().split()[0] if questions_element else ''

        print(reviews_count, video_count, questions_count)

        # Получение всех доступных характеристик товара
        characteristics_element = soup.findAll('dd')
        characteristics = ', '.join([element.text.strip() for element in characteristics_element]) if characteristics_element else ''

        # Получение рейтинга
        try:
            rate_element = soup.find("span", string=" рейтинг товаров").parent.findAll('span')[0]
            print(rate_element)
            rate_info = rate_element.text.strip() if rate_element else ''
        except:
            rate_info = 0

        # Получение информации об уцененном товаре
        damaged_element = soup.find('div', {'class': 'd7b1'})
        damaged_info = damaged_element.text.strip() if damaged_element else ''

        # Получение продавца
        seller_element = soup.find( 'div', {"data-widget":"webCurrentSeller"}).select('a[href*="ozon.ru/seller"]' )
        seller = seller_element[-1].get('title').strip() if seller_element else ''

        # Заполнение DataFrame
        df = pd.concat([
            df, pd.DataFrame({
                'Код товара': [code],
                'Название товара': [name],
                'URL страницы с товаром': [page_url],
                # 'URL первой картинки': [image_url],
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
            })
        ], ignore_index=True)
    # except:
    #     continue

# Закрытие веб-драйвера
driver.close()
driver.quit()

print(df.to_string())

# Сохранение DataFrame в файл
df.to_excel('products.xlsx', index=False)







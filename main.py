from playwright.sync_api import sync_playwright
import pandas as pd
import time

def get_cars(url, filename):
    # Заранее создаем структуру таблицы, чтобы не было ошибки KeyError
    data = []
    columns = ["Название", "Цена", "Ссылка"] # Важно: имена колонок как в app.py
    
    with sync_playwright() as p:
        # Запускаем браузер (headless=False, чтобы вы видели глазами, что происходит)
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        try:
            print(f"Захожу на сайт: {url}")
            page.goto(url, timeout=60000)
            
            # Ждем 5 секунд, пока сайт загрузится полностью
            page.wait_for_timeout(5000)
            
            # --- ЛОГИКА СБОРА (Пример для Avtoelon) ---
            # Ищем блоки с объявлениями (селекторы могут меняться, пробуем универсальный)
            # Обычно это div с классом, содержащим 'row' или 'listing'
            # ВНИМАНИЕ: Тут нужно проверить актуальные селекторы на сайте
            
            # Попробуем найти все элементы с ценой (обычно они имеют класс price)
            items = page.locator(".price") 
            count = items.count()
            print(f"Найдено элементов цен: {count}")

            if count > 0:
                # Если нашли, собираем (это упрощенный пример)
                # Вам нужно будет настроить точные селекторы под дизайн сайта
                for i in range(min(count, 10)): # Берем первые 10 для теста
                    price_text = items.nth(i).inner_text()
                    # Добавляем в список (Название пока пустим как заглушку)
                    data.append({
                        "Название": "Авто " + str(i+1), 
                        "Цена": price_text, 
                        "Ссылка": url
                    })
            else:
                print("Машины не найдены. Возможно, изменился дизайн сайта.")

        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
        finally:
            browser.close()
            
    # Создаем DataFrame
    if data:
        df = pd.DataFrame(data)
    else:
        # Если пусто, создаем пустую таблицу с НУЖНЫМИ колонками
        df = pd.DataFrame(columns=columns)

    # Сохраняем
    df.to_excel(filename, index=False)
    return df

if __name__ == "__main__":
    get_cars("https://avtoelon.uz/avto/chevrolet/cobalt/", "test.xlsx")
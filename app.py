import asyncio
import sys
import streamlit as st
import pandas as pd
import re

# --- 1. ВАЖНЫЙ ФИКС ДЛЯ WINDOWS (чтобы не было NotImplementedError) ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Импортируем вашу функцию парсинга
from main import get_cars

# --- 2. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Avto Analytics", page_icon="🚗")
st.title("🚗 Анализ цен на авто в Узбекистане")

# --- 3. ФУНКЦИЯ ОЧИСТКИ ЦЕНЫ (чтобы превратить "12 000 у.е." в число 12000) ---
def clean_price_value(price_str):
    if pd.isna(price_str):
        return 0
    # Оставляем только цифры
    clean_str = re.sub(r'\D', '', str(price_str))
    if clean_str:
        return int(clean_str)
    return 0

# --- 4. БЛОК ВЫБОРА МАШИНЫ ---
car_options = {
    "Chevrolet Cobalt": "https://avtoelon.uz/avto/chevrolet/cobalt/",
    "Chevrolet Gentra / Lacetti": "https://avtoelon.uz/avto/chevrolet/lacetti-gentra/",
    "Chevrolet Spark": "https://avtoelon.uz/avto/chevrolet/spark/",
    "Chevrolet Nexia 3": "https://avtoelon.uz/avto/chevrolet/nexia-3/",
    "Chevrolet Malibu 2": "https://avtoelon.uz/avto/chevrolet/malibu/",
    "Chevrolet Tracker 2": "https://avtoelon.uz/avto/chevrolet/tracker/",
    "Chevrolet Onix": "https://avtoelon.uz/avto/chevrolet/onix/",
    "Kia K5": "https://avtoelon.uz/avto/kia/k5/",
    "BYD Song Plus": "https://avtoelon.uz/avto/byd/song-plus/",
    "Ввести свою ссылку вручную...": "custom"
}

# Выпадающий список
selected_name = st.selectbox("Какую машину будем искать?", list(car_options.keys()))

# Логика выбора ссылки
if selected_name == "Ввести свою ссылку вручную...":
    url = st.text_input("Вставьте ссылку с Avtoelon (например, на Lada Vesta):")
else:
    url = car_options[selected_name]
    st.caption(f"Ссылка для поиска: {url}")

st.divider() # Красивая разделительная линия

# --- 5. КНОПКА И ЗАПУСК ---
if st.button("🔍 Найти машины и проанализировать", type="primary"):
    if not url:
        st.error("Пожалуйста, выберите машину или вставьте ссылку.")
    else:
        with st.spinner("Робот работает... Захожу на сайт..."):
            try:
                # Запускаем парсер из main.py
                df = get_cars(url, "current_data.xlsx")
                
                if df.empty:
                    st.warning("Робот вернулся с пустыми руками. Возможно, сайт долго грузился или машин нет.")
                else:
                    st.success(f"Успешно! Найдено объявлений: {len(df)}")
                    
                    # --- АНАЛИТИКА ---
                    if 'Цена' in df.columns:
                        # Создаем чистую колонку с ценой (числами)
                        df['price_num'] = df['Цена'].apply(clean_price_value)
                        
                        # Считаем среднюю, исключая нули (где цена не указана "Договорная")
                        valid_prices = df[df['price_num'] > 100] # Фильтр от мусора
                        
                        if not valid_prices.empty:
                            avg_price = valid_prices['price_num'].mean()
                            min_price = valid_prices['price_num'].min()
                            max_price = valid_prices['price_num'].max()
                            
                            # Выводим красивые метрики в ряд
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Средняя цена", f"{int(avg_price):,} у.е.".replace(",", " "))
                            col2.metric("Самая дешевая", f"{int(min_price):,} у.е.".replace(",", " "))
                            col3.metric("Самая дорогая", f"{int(max_price):,} у.е.".replace(",", " "))
                        else:
                            st.info("Цены не указаны или указаны как 'Договорная'.")
                    
                    # Показываем таблицу
                    st.dataframe(df)
                    
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
import asyncio
import sys
import os
import subprocess

# --- ХАК ДЛЯ ОБЛАКА STREAMLIT ---
# Эта команда заставит сервер скачать браузер Chromium при первом запуске
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])

# Проверяем, установлен ли браузер, и если нет — ставим
# (Это сработает и на Windows, и на Linux в облаке)
subprocess.run(["playwright", "install", "chromium"])
# -------------------------------

# --- ФИКС ДЛЯ WINDOWS (твой старый код) ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
import streamlit as st
import pandas as pd
import re
import plotly.express as px  # <-- НОВАЯ БИБЛИОТЕКА

# --- 1. ФИКС ДЛЯ WINDOWS ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from main import get_cars

# --- 2. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Avto Analytics", page_icon="🚗", layout="wide") # layout="wide" делает сайт шире
st.title("🚗 Анализ цен на авто в Узбекистане")

# --- 3. ФУНКЦИЯ ОЧИСТКИ ---
def clean_price_value(price_str):
    if pd.isna(price_str):
        return 0
    clean_str = re.sub(r'\D', '', str(price_str))
    if clean_str:
        return int(clean_str)
    return 0

# --- 4. МЕНЮ ВЫБОРА ---
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

col1, col2 = st.columns([2, 1]) # Делим экран на две части для меню
with col1:
    selected_name = st.selectbox("Какую машину будем искать?", list(car_options.keys()))

if selected_name == "Ввести свою ссылку вручную...":
    url = st.text_input("Вставьте ссылку с Avtoelon:")
else:
    url = car_options[selected_name]

st.divider()

# --- 5. ЛОГИКА И ГРАФИКИ ---
if st.button("🔍 Найти машины и построить график", type="primary"):
    with st.spinner("Робот работает... Собираем данные..."):
        try:
            df = get_cars(url, "current_data.xlsx")
            
            if df.empty:
                st.warning("Машин не найдено. Проверьте ссылку.")
            else:
                # Очистка данных
                if 'Цена' in df.columns:
                    df['price_num'] = df['Цена'].apply(clean_price_value)
                    valid_prices = df[df['price_num'] > 100] # Убираем "Договорная" (0)

                    if not valid_prices.empty:
                        # 1. МЕТРИКИ (Цифры)
                        avg = int(valid_prices['price_num'].mean())
                        mn = int(valid_prices['price_num'].min())
                        mx = int(valid_prices['price_num'].max())
                        
                        st.success(f"Обработано объявлений: {len(valid_prices)}")
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("📉 Минимальная цена", f"{mn:,} у.е.".replace(",", " "))
                        m2.metric("💰 СРЕДНЯЯ ЦЕНА", f"{avg:,} у.е.".replace(",", " "), delta="Рыночная цена")
                        m3.metric("📈 Максимальная цена", f"{mx:,} у.е.".replace(",", " "))
                        
                        # 2. ГРАФИК (Гистограмма)
                        st.subheader("📊 Распределение цен на рынке")
                        fig = px.histogram(
                            valid_prices, 
                            x="price_num", 
                            nbins=20, 
                            title=f"Разброс цен на {selected_name}",
                            labels={"price_num": "Цена (у.е.)"},
                            color_discrete_sequence=['#3b82f6'] # Синий красивый цвет
                        )
                        # Добавляем линию средней цены на график
                        fig.add_vline(x=avg, line_dash="dash", line_color="red", annotation_text="Средняя")
                        
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.info("Цены не указаны.")
                
                # 3. ТАБЛИЦА
                with st.expander("📄 Посмотреть детальную таблицу"):
                    st.dataframe(df)

                # 4. СКАЧАТЬ
                with open("current_data.xlsx", "rb") as file:
                    st.download_button(
                        label="📥 Скачать Excel",
                        data=file,
                        file_name="avto_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f"Ошибка: {e}")
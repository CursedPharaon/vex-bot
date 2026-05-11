import os
import json
from flask import Flask, request, jsonify
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests

app = Flask(__name__)

# Токен группы ВК (получить в Управлении сообществом -> Работа с API)
VK_TOKEN = os.environ.get('VK_TOKEN')
CONFIRMATION_CODE = os.environ.get('CONFIRMATION_CODE')  # Код из настроек Callback API

# ID менеджера
MANAGER_ID = "kalashnikov3002"  # Короткое имя
MANAGER_LINK = "https://vk.com/kalashnikov3002"

# URL сообщества
COMMUNITY_LINK = "https://vk.com/vex.studio"

def get_main_keyboard():
    """Главное меню с кнопками"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("📦 Услуги", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("💬 Написать менеджеру", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🌐 ВК Сообщество", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_services_text():
    """Текст с услугами"""
    services = """📋 **Наши услуги — Vex Studio**

1️⃣ 3D логотип — 230₽
2️⃣ 2D логотип — 160₽
3️⃣ Сайт под ключ — договорная (от 300₽)
4️⃣ Автопиар — договорная
5️⃣ Веб-игра — от 400₽
6️⃣ Оформление поста (текст+логотип) — от 80₽

💬 Для заказа пишите менеджеру: @kalashnikov3002
🌐 Наш паблик: @vex.studio
"""

def send_message(user_id, message, keyboard=None):
    """Отправка сообщения пользователю"""
    url = "https://api.vk.com/method/messages.send"
    data = {
        "user_id": user_id,
        "message": message,
        "access_token": VK_TOKEN,
        "v": "5.131",
        "random_id": 0
    }
    if keyboard:
        data["keyboard"] = keyboard
    
    response = requests.post(url, data=data)
    return response.json()

@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    
    # Проверка на подтверждение сервера
    if data.get('type') == 'confirmation':
        return CONFIRMATION_CODE
    
    # Обработка сообщений
    if data.get('type') == 'message_new':
        msg = data['object']['message']
        user_id = msg['from_id']
        text = msg.get('text', '').lower()
        
        if text == 'начать' or text == 'start' or text == 'привет':
            send_message(
                user_id,
                f"👋 Привет! Я бот магазина Vex Studio\n"
                f"Выбери действие на кнопках ниже:",
                get_main_keyboard()
            )
        
        elif 'услуг' in text:
            send_message(
                user_id,
                get_services_text(),
                get_main_keyboard()
            )
        
        elif 'менеджер' in text:
            send_message(
                user_id,
                f"👨‍💼 Напиши менеджеру: {MANAGER_LINK}\nОн ответит на все вопросы!",
                get_main_keyboard()
            )
        
        elif 'сообщество' in text or 'паблик' in text or 'vex.studio' in text:
            send_message(
                user_id,
                f"🌐 Наше сообщество ВК: {COMMUNITY_LINK}\nПодписывайся, там все новости!",
                get_main_keyboard()
            )
        
        else:
            # Ответ по умолчанию с кнопками
            send_message(
                user_id,
                f"❓ Не понял команду.\n\n"
                f"📌 Доступные команды:\n"
                f"• «Услуги» — посмотреть цены\n"
                f"• «Написать менеджеру» — контакт\n"
                f"• «ВК Сообщество» — наш паблик\n"
                f"• «Привет» — начать сначала",
                get_main_keyboard()
            )
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

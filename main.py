import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Переменные из окружения (настрой на Render.com)
VK_TOKEN = os.environ.get('VK_TOKEN')
CONFIRMATION_CODE = os.environ.get('CONFIRMATION_CODE')

# ID менеджера
MANAGER_LINK = "https://vk.com/kalashnikov3002"
COMMUNITY_LINK = "https://vk.com/vex.studio"

def send_message(user_id, text):
    """Отправка сообщения пользователю"""
    url = "https://api.vk.com/method/messages.send"
    data = {
        "user_id": user_id,
        "message": text,
        "access_token": VK_TOKEN,
        "v": "5.131",
        "random_id": 0
    }
    response = requests.post(url, data=data)
    return response.json()

def get_services():
    return """📋 Услуги Vex Studio:

1️⃣ 3D логотип — 230₽
2️⃣ 2D логотип — 160₽
3️⃣ Сайт под ключ — от 300₽ (договорная)
4️⃣ Автопиар — договорная
5️⃣ Веб-игра — от 400₽
6️⃣ Оформление поста (текст+логотип) — от 80₽

Заказ: @kalashnikov3002"""

def get_help():
    return """🔍 Доступные команды:

привет — поздороваться
услуги — посмотреть цены
цены — то же самое
менеджер — контакт менеджера
контакт — то же самое
паблик — ссылка на сообщество
помощь — показать это сообщение"""

@app.route('/', methods=['GET'])
def index():
    return "Бот работает!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    
    # Подтверждение сервера (ВАЖНО!)
    if data.get('type') == 'confirmation':
        return CONFIRMATION_CODE
    
    # Обработка сообщений
    if data.get('type') == 'message_new':
        msg = data['object']['message']
        user_id = msg['from_id']
        text = msg.get('text', '').lower().strip()
        
        if text in ['привет', 'начать', 'старт', 'start', 'здарова']:
            send_message(user_id, f"👋 Привет! Я бот Vex Studio.\n\n{get_help()}")
        
        elif text in ['услуги', 'цены', 'прайс', 'услуги vex']:
            send_message(user_id, get_services())
        
        elif text in ['менеджер', 'контакт', 'поддержка', 'менедж', 'мен']:
            send_message(user_id, f"👨‍💼 Наш менеджер: {MANAGER_LINK}\nПиши по любым вопросам!")
        
        elif text in ['паблик', 'сообщество', 'вк', 'vex.studio', 'группа']:
            send_message(user_id, f"🌐 Наше сообщество: {COMMUNITY_LINK}\nПодписывайся!")
        
        elif text in ['помощь', 'хелп', 'help', 'команды', 'что умеешь']:
            send_message(user_id, get_help())
        
        elif text in ['пока', 'до свидания', 'bye']:
            send_message(user_id, "👋 Пока! Возвращайся, если понадобится дизайн!")
        
        else:
            send_message(user_id, f"❌ Не понял команду.\n\n{get_help()}")
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

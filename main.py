import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Переменные из окружения (настрой на Render.com)
VK_TOKEN = os.environ.get('VK_TOKEN')
CONFIRMATION_CODE = os.environ.get('CONFIRMATION_CODE')

# ID сообщества Vex Studio (можно получить из короткого имени)
# Если короткое имя @vex.studio, то ID можно найти в управлении сообществом
# Или использовать короткое имя напрямую: 'vex.studio'
GROUP_ID = 'vex.studio'  # Замени на ID или короткое имя твоего сообщества
GROUP_LINK = 'https://vk.com/vex.studio'

def is_subscribed(user_id):
    """
    Проверяет, подписан ли пользователь на сообщество.
    Возвращает True если подписан, False если нет.
    """
    url = 'https://api.vk.com/method/groups.isMember'
    params = {
        'access_token': VK_TOKEN,
        'group_id': GROUP_ID,
        'user_id': user_id,
        'v': '5.131'
    }
    
    try:
        response = requests.post(url, params=params)
        data = response.json()
        
        # Проверяем наличие ошибок
        if 'error' in data:
            print(f"Ошибка API: {data['error']}")
            return False
        
        # Метод возвращает 1 (подписан) или 0 (не подписан) [citation:2]
        return data.get('response', 0) == 1
    
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

def send_message(user_id, text):
    """Отправка сообщения пользователю"""
    url = 'https://api.vk.com/method/messages.send'
    data = {
        'user_id': user_id,
        'message': text,
        'access_token': VK_TOKEN,
        'v': '5.131',
        'random_id': 0
    }
    response = requests.post(url, data=data)
    return response.json()

def send_subscription_required(user_id):
    """Отправляет сообщение с требованием подписаться"""
    text = f"""❌ Для начала подпишись на сообщество: {GROUP_LINK}

Подпишись, а потом напиши любое слово — я проверю и покажу услуги!"""
    send_message(user_id, text)

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
паблик — ссылка на сообщество
помощь — показать это сообщение"""

@app.route('/', methods=['GET'])
def index():
    return "Бот работает!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    
    # Подтверждение сервера
    if data.get('type') == 'confirmation':
        return CONFIRMATION_CODE
    
    # Обработка сообщений
    if data.get('type') == 'message_new':
        msg = data['object']['message']
        user_id = msg['from_id']
        text = msg.get('text', '').lower().strip()
        
        # Игнорируем сообщения от самого себя (от бота)
        # ВАЖНО: user_id сообщества отрицательный, например -123456789
        # Нужно получать реальный ID бота, но для простоты пропускаем
        
        # Проверяем подписку
        if not is_subscribed(user_id):
            send_subscription_required(user_id)
            return 'ok', 200
        
        # Пользователь подписан — обрабатываем команды
        if text in ['привет', 'начать', 'старт', 'start']:
            send_message(user_id, f"👋 Привет! Я бот Vex Studio.\n\n{get_help()}")
        
        elif text in ['услуги', 'цены', 'прайс']:
            send_message(user_id, get_services())
        
        elif text in ['менеджер', 'контакт', 'поддержка']:
            send_message(user_id, f"👨‍💼 Наш менеджер: https://vk.com/kalashnikov3002\nПиши по любым вопросам!")
        
        elif text in ['паблик', 'сообщество', 'группа']:
            send_message(user_id, f"🌐 Наше сообщество: {GROUP_LINK}\nСпасибо, что подписался!")
        
        elif text in ['помощь', 'help', 'команды']:
            send_message(user_id, get_help())
        
        elif text in ['проверь', 'подписка']:
            # Повторная проверка подписки (полезно после подписки)
            if is_subscribed(user_id):
                send_message(user_id, "✅ Да, ты подписан! Теперь доступны команды.\n\n" + get_help())
            else:
                send_subscription_required(user_id)
        
        else:
            send_message(user_id, f"❌ Не понял команду.\n\n{get_help()}")
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

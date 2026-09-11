import datetime
import os
import requests

DAYS_OF_WEEK = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


def normalize_env_value(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def build_post_text():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ufa_now = utc_now + datetime.timedelta(hours=5)

    today = ufa_now.date()
    tomorrow = today + datetime.timedelta(days=1)

    date_today_str = today.strftime("%d.%m.%Y")
    date_tomorrow_str = tomorrow.strftime("%d.%m.%Y")

    day_today_name = DAYS_OF_WEEK[today.weekday()]
    day_tomorrow_name = DAYS_OF_WEEK[tomorrow.weekday()]

    return f"""Есть места 📞8(927)08-80-720 
🌞{date_today_str} {day_today_name}
🌞{date_tomorrow_str} {day_tomorrow_name}
🚕Набираем водителей!!!
Исянгулово-Мраково-Уфа-Мраково-Исянгулово 
✅Выдаём билеты с QR-кодом 
📌Заберём со всех попутных городов и деревень 
📌В любое удобное для Вас время 
📌Курьерские услуги 
📌Онлайн оплата
🔥Сообщества VK:
https://vk.ru/uldashsoo
https://vk.ru/taxi_mrk_ufa"""


POST_TEXT = build_post_text()


def send_telegram_message(token, chat_id, text):
    token = normalize_env_value(token)
    chat_id = normalize_env_value(chat_id)

    if not token or not chat_id:
        print("Пропущено: Переменные Telegram не настроены.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if response.status_code == 200 and isinstance(data, dict) and data.get("ok"):
            print("Успешно отправлено в Telegram")
            return True

        print("Ошибка Telegram:", data)
        return False
    except ValueError:
        print("Telegram вернул не JSON:", response.text[:500])
        return False
    except requests.RequestException as e:
        print("Критическая ошибка сети в TG:", e)
        return False


def normalize_vk_group_id(group_id):
    group_id = normalize_env_value(group_id)
    if not group_id:
        return None
    return group_id if group_id.startswith("-") else f"-{group_id}"


def publish_vk_post(token, group_id, text):
    token = normalize_env_value(token)
    group_id = normalize_env_value(group_id)

    if not token or not group_id:
        print("Пропущено: Переменные группы ВК не настроены.")
        return False

    owner_id = normalize_vk_group_id(group_id)
    params = {
        "owner_id": owner_id,
        "from_group": 1,
        "message": text,
        "access_token": token,
        "v": "5.131",
    }

    try:
        response = requests.post("https://api.vk.ru/method/wall.post", data=params, headers=HEADERS, timeout=10)
        data = response.json()

        if "response" in data:
            print(f"Успешно опубликовано в группе ВК {owner_id}!")
            return True

        if "error" in data:
            print(f"Ошибка VK API в группе {owner_id}:", data["error"])
            return False

        print(f"Неизвестный ответ VK API в группе {owner_id}:", data)
        return False
    except requests.RequestException as e:
        print(f"Ошибка сети (Группа ВК {owner_id}):", e)
        return False


def run_telegram_targets(targets):
    for target in targets:
        send_telegram_message(target.get("token"), target.get("chat_id"), POST_TEXT)


def run_vk_groups(groups):
    for group in groups:
        publish_vk_post(group.get("token"), group.get("group_id"), POST_TEXT)


TELEGRAM_TARGETS = [
    {
        "token": os.environ.get("TELEGRAM_TOKEN"),
        "chat_id": os.environ.get("TELEGRAM_CHAT_ID"),
    }
]

VK_GROUPS = [
    {
        "token": os.environ.get("VK_TOKEN"),
        "group_id": os.environ.get("VK_GROUP_ID"),
    },
    {
        "token": os.environ.get("VK_TOKEN_2"),
        "group_id": os.environ.get("VK_GROUP_ID_2"),
    },
]


run_telegram_targets(TELEGRAM_TARGETS)
run_vk_groups(VK_GROUPS)

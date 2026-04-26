import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from config import TELEGRAM_TOKEN, API_BASE_URL
from api_client import BarAPI
from character import BarmanPersonality
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector
    
PROXY_URL = "socks5://206.123.156.213:6510"

api = BarAPI(API_BASE_URL)
personality = BarmanPersonality()
user_states = {}



dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    result = await api.register(user_id)
    if result.get("status") == "ok":
        await message.answer(
            f"🍸 *Великий бармен приветствует тебя*\n\n"
            f"{personality.greet(name)}\n\n"
            f"Твой ID: `{result['id']}`\n"
            f"Баланс: 100 монет\n\n"
            f"Доступные команды:\n"
            f"/menu — посмотреть меню\n"
            f"/order <напиток> — заказать\n"
            f"/mix <ингредиенты> — смешать\n"
            f"/balance — баланс\n"
            f"/tip <сумма> — чаевые\n"
            f"/history — история заказов\n"
            f"/profile — мой профиль\n"
            f"/reset — сбросить аккаунт",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Бар закрыт. Приходи позже.")

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    user_id = message.from_user.id
    result = await api.get_menu(user_id)
    
    if result.get("status") == "ok":
        drinks = result.get("drinks", [])
        menu_text = "📋 *Меню:*\n\n"
        for drink in drinks:
            menu_text += f"🍹 *{drink['name']}* — {drink['price']} монет\n"
            menu_text += f"   Состав: {', '.join(drink['ingredients'])}\n\n"
        
        mood = personality.mood_to_text(result.get("mood_level", "normal"))
        menu_text += f"\n{mood} Баланс: {result.get('balance', 0)} монет"
        await message.answer(menu_text, parse_mode="Markdown")
    else:
        await message.answer("Не могу показать меню. Возможно, ты не зарегистрирован. Напиши /start")

@dp.message(Command("order"))
async def cmd_order(message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("🍸 *Использование:* `/order <напиток>`\n\nПример: `/order Русский`", parse_mode="Markdown")
        return
    
    drink_name = args[1].strip()
    result = await api.order(user_id, drink_name)
    
    if result.get("status") == "ok":
        response = personality.order_response(
            drink_name, 
            result["price"], 
            result["balance"]
        )
        await message.answer(f"✅ {response}")
    elif result.get("error") == "insufficient_funds":
        await message.answer(f"❌ {personality.insufficient_funds(result['price'], result['balance'])}")
    elif result.get("error") == "unknown_drink":
        await message.answer(f"❌ {personality.unknown_drink(drink_name)}")
    else:
        await message.answer("❌ Что-то пошло не так. Попробуй /reset")

@dp.message(Command("mix"))
async def cmd_mix(message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("🍸 *Использование:* `/mix ингредиент1, ингредиент2, ...`\n\nПример: `/mix водка, сок`", parse_mode="Markdown")
        return
    
    ingredients_raw = args[1].strip()
    ingredients = [i.strip().lower() for i in ingredients_raw.split(",")]
    
    result = await api.mix(user_id, ingredients)
    
    if result.get("status") == "ok":
        response = personality.mix_response(
            result["drink"],
            result["price"],
            result["balance"]
        )
        await message.answer(f"✅ {response}")
    elif result.get("error") == "unknown_recipe":
        await message.answer(f"❌ {personality.unknown_recipe()}")
    else:
        await message.answer("❌ Не получилось смешать. Проверь ингредиенты.")

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    result = await api.get_balance(user_id)
    
    if result.get("status") == "ok":
        balance = result["balance"]
        mood = personality.mood_to_text(result.get("mood_level", "normal"))
        await message.answer(f"💰 {personality.balance_response(balance)} {mood}")

@dp.message(Command("tip"))
async def cmd_tip(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer("🍸 *Использование:* `/tip <сумма>`\n\nПример: `/tip 10`", parse_mode="Markdown")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной, скряга.")
            return
    except ValueError:
        await message.answer("❌ Введи нормальное число.")
        return
    
    result = await api.tip(user_id, amount)
    
    if result.get("status") == "ok":
        await message.answer(f"💸 {personality.tip_response(amount, result['balance'])}")
    else:
        await message.answer("❌ Не получилось дать чаевые.")

@dp.message(Command("history"))
async def cmd_history(message: Message):
    user_id = message.from_user.id
    result = await api.get_history(user_id)
    
    if result.get("status") == "ok":
        orders = result.get("orders", [])
        balance = result.get("balance", 0)
        
        if orders:
            history_text = "📜 *История заказов:*\n\n"
            for i, order in enumerate(orders[-10:], 1):
                method_emoji = "🍹" if order["method"] == "order" else "🔀"
                history_text += f"{i}. {method_emoji} *{order['drink']}* — {order['price']} монет\n"
            
            await message.answer(history_text + f"\n{personality.history_summary(orders, balance)}", parse_mode="Markdown")
        else:
            await message.answer(personality.history_summary([], balance))
    else:
        await message.answer("❌ История недоступна.")

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    result = await api.get_profile(user_id)
    
    if result.get("status") == "ok":
        balance_result = await api.get_balance(user_id)
        balance = balance_result.get("balance", 0) if balance_result.get("status") == "ok" else 0
        
        await message.answer(personality.profile_response(result, balance), parse_mode="Markdown")
    else:
        await message.answer("❌ Профиль недоступен. Попробуй /reset")

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    user_id = message.from_user.id
    result = await api.reset(user_id)
    
    if result.get("status") == "ok":
        await message.answer("🔄 Баланс сброшен. Начинаем с чистого листа. Можешь не благодарить.")
    else:
        await message.answer("❌ Не получилось сбросить. Может, ты вообще не регистрировался? /start")

async def main():
    
    # Создаём прокси-коннектор
    # connector = ProxyConnector.from_url(PROXY_URL)
    # session = ClientSession(connector=connector)
    # session = AiohttpSession(proxy= PROXY_URL)
    
    # Передаем сессию напрямую в Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    
    print("🍸 Великий бармен вышел на работу")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
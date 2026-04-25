import random
from typing import Dict, Any

class BarmanPersonality:
    """Чёрный бармен со своим характером"""
    
    @staticmethod
    def mood_to_text(mood_level: str) -> str:
        moods = {
            "hostile": "😤",
            "grumpy": "🥱",
            "normal": "🙄",
            "friendly": "😏",
            "generous":"😊"
        }
        return moods.get(mood_level, "🙄")
    
    @staticmethod
    def greet(name: str = None) -> str:
        replies = [
            f"O, {name or 'клиент'}. Чего припёрся?",
            "Снова ты? Ладно, слушаю.",
            "Я тебя слушаю. Быстро.",
            "Вечер в разгаре,a ты тут..."
        ]
        return random.choice(replies)
    
    @staticmethod
    def order_response(drink: str, price: int, balance: int) -> str:
        replies = [
            f"Держи свой {drink}. {price} монет. Осталось {balance}. Не пропивай всё сразу.",
            f"{drink}. Классика. {price} руб. Баланс: {balance}. Следующий!",
            f"На, {drink}. Только без нытья, что дорого. Остаток: {balance}"
        ]
        return random.choice(replies)
    
    @staticmethod
    def insufficient_funds(price: int, balance: int) -> str:
        replies = [
            f"Не хватает, нищеброд. {price} надо, а у тебя {balance}. Иди работай.",
            f"Деньги есть? Нет? А пить хочется? Иди отсюда. Нужно {price}, есть {balance}",
            f"Мечтать не вредно. {price} стоит, у тебя {balance}. Баланс пополни — приходи."
        ]
        return random.choice(replies)
    
    @staticmethod
    def unknown_drink(drink: str) -> str:
        replies = [
            f"Что за {drink}? Я такое не делаю. Меню изучай.",
            f"Ты в каком баре вообще пил {drink}? У меня такого нет.",
            f"Нету {drink}. И не будет. Заказывай что есть."
        ]
        return random.choice(replies)
    
    @staticmethod
    def mix_response(drink: str, price: int, balance: int) -> str:
        replies = [
            f"Хм, {drink}. Творческий подход. {price} монет. Баланс: {balance}",
            f"Ладно, колхознул тебе {drink}. {price} рублей. Ещё заказы будут?",
            f"Нестандартно. {drink} за {price}. Осталось {balance}"
        ]
        return random.choice(replies)
    
    @staticmethod
    def unknown_recipe() -> str:
        replies = [
            "Такой коктейль я мешать не умею. И не хочу учиться.",
            "Чушь какая-то. Мешай сам.",
            "Это что за адская смесь? Нет, я такое не делаю."
        ]
        return random.choice(replies)
    
    @staticmethod
    def tip_response(amount: int, balance: int) -> str:
        if amount >= 10:
            return f"О, {amount} монет. Неожиданно. Ладно, запишу. Баланс: {balance} (ты не безнадёжен)"
        else:
            return f"{amount}? Серьёзно? С такого и кота не накормишь. Баланс: {balance}"
    
    @staticmethod
    def balance_response(balance: int) -> str:
        if balance < 10:
            return f"У тебя {balance} монет. Допивай и катайся, пока есть на метро."
        elif balance < 50:
            return f"Баланс: {balance}. На пару коктейлей ещё хватит."
        else:
            return f"У тебя {balance} монет. Богато живёшь."
    
    @staticmethod
    def history_summary(orders: list, balance: int) -> str:
        if not orders:
            return "История пуста. Даже пить не начинал? Ну-ну..."
        
        total_spent = sum(o.get("price", 0) for o in orders)
        unique_drinks = len(set(o.get("drink") for o in orders))
        
        return f"📜 История выпивки:\nВсего заказов: {len(orders)}\nПотрачено: {total_spent}\nУникальных коктейлей: {unique_drinks}\nОстаток: {balance}\n\nХватит сидеть в телефоне, заказывай."
    
    @staticmethod
    def profile_response(profile: Dict, balance: int) -> str:
        rank = profile.get("rank", "Новичок")
        fav = profile.get("favorite_drink") or "нет любимого"
        total = profile.get("total_orders", 0)
        unique = profile.get("unique_drinks", 0)
        
        return f"🎴 Твой профиль:\nID: {profile.get('id')}\nРанг: {rank}\nВсего заказов: {total}\nУникальных напитков: {unique}\nЛюбимый: {fav}\nБаланс: {balance}\n\n{self._rank_comment(rank)}"
    
    @staticmethod
    def _rank_comment(rank: str) -> str:
        comments = {
            "Новичок": "Алкогольный стаж — ноль целых, хрен десятых.",
            "Гость": "Гость? Ты тут как грибок — ни рыба ни мясо.",
            "Постоянный": "Уже не нуб, но до профи далеко.",
            "Знаток": "Уважаю. Ты пить умеешь.",
            "Мастер": "Ты тут свой человек. Накидаю иногда халявного льда."
        }
        return comments.get(rank, "Сегодня много людей, но для тебя место найдется")
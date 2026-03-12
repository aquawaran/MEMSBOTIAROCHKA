import random
import time
import asyncio
from typing import Dict
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Константы
LOW_BAND_CHANCE = 0.70  # 70% шанс упасть в [1.00, 1.10]
CRASH_COOLDOWN = 5  # секунды
LOW_BAND_MAX = 1.10
CRASH_MIN_X = 1.00
CRASH_MAX_X = 10.0
MIN_STAKE_CR = 100

# Эмодзи
ROCKET_EMOJI = "🚀"
BOOM_EMOJI = "💥"
CHECK_MARK_EMOJI = "✅"
CROSS_MARK_EMOJI = "❌"

# ID стикера ракеты (можно заменить на настоящий ID стикера)
ROCKET_STICKER = "🚀"  # Временно эмодзи, потом можно заменить на ID стикера

def hbold(text: str) -> str:
    return f"<b>{text}</b>"

async def send_rocket_animation(chat_id, bot, won: bool = True):
    """Отправляет один стикер ракеты"""
    try:
        # Отправляем один стикер ракеты
        await bot.send_message(chat_id, ROCKET_STICKER)
    except Exception:
        # Если стикер не работает, просто пропускаем
        pass

def generate_crash_x_simple() -> float:
    """
    70% шанс, что crash_x попадёт в [1.00, 1.10], иначе равномерно в (1.10, CRASH_MAX_X).
    Округление до 2 знаков.
    """
    if random.random() < LOW_BAND_CHANCE:
        crash_x = random.uniform(CRASH_MIN_X, LOW_BAND_MAX)
    else:
        # выбираем чуть выше 1.10, чтобы не дублировать край
        lower = LOW_BAND_MAX + 1e-9
        crash_x = random.uniform(lower, CRASH_MAX_X)
    return round(crash_x, 2)

class CrashGame:
    """Игра Краш - ракета с множителем"""
    
    def __init__(self, database):
        self.db = database
        # Состояния для каждого пользователя
        self.crash_games: Dict[int, Dict] = {}  # user_id -> {stake, chosen_x, ts}
        self.crash_cooldowns: Dict[int, float] = {}  # user_id -> last_time
    
    async def start_game(self, message: Message, stake: int, chosen_x: float) -> bool:
        """Начать игру в краш"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        now = time.time()
        
        # Проверка пользователя
        user = await self.db.get_user(user_id)
        if not user:
            await message.reply("❌ Пользователь не найден")
            return False
        
        # Проверка бана
        if user.get('banned', False):
            await message.reply("❌ Вы забанены и не можете использовать эту команду.")
            return False
        
        # Кулдаун
        last = self.crash_cooldowns.get(user_id)
        if last and now - last < CRASH_COOLDOWN:
            remaining = CRASH_COOLDOWN - (now - last)
            await message.reply(f"❌ Подождите {remaining:.1f} сек. перед новой игрой.")
            return False
        
        # Валидация коэффициента
        if not (CRASH_MIN_X <= chosen_x <= CRASH_MAX_X):
            await message.reply(f"❌ Коэффициент должен быть от {CRASH_MIN_X:.1f} до {CRASH_MAX_X:.1f}.")
            return False
        
        # Проверка баланса
        balance = user['balance']
        if stake < MIN_STAKE_CR:
            await message.reply(f"❌ Минимальная ставка: {MIN_STAKE_CR} MEM")
            return False
        
        if stake <= 0:
            await message.reply("❌ Ставка должна быть больше 0.")
            return False
        
        if stake > balance:
            await message.reply("❌ Недостаточно средств на балансе.")
            return False
        
        # Проверяем, нет ли уже активной игры
        if user_id in self.crash_games:
            await message.reply("❌ У вас уже есть активная игра в краш.")
            return False
        
        # Списание ставки
        await self.db.update_balance(user_id, -stake)
        
        # Сохраняем активную игру
        self.crash_games[user_id] = {"stake": stake, "chosen_x": chosen_x, "ts": now}
        
        # Фоновой обработчик результата
        async def _process_and_notify():
            try:
                crash_x = generate_crash_x_simple()
                won = crash_x >= chosen_x
                
                # Отправляем один стикер ракеты
                await send_rocket_animation(chat_id, message.bot, won=won)
                
                if won:
                    winnings = int(round(stake * chosen_x))
                    await self.db.update_balance(user_id, winnings)
                    
                    # Статистика для выигрыша
                    try:
                        await self.db.add_game_history(user_id, "краш", stake, "win", winnings)
                    except Exception:
                        pass
                    
                    result_text = (
                        f"<blockquote>🚀 Краш</blockquote>\n\n"
                        f"📊 Вы выбрали коэффициент: {chosen_x:.2f}\n"
                        f"💥 Ракета упала на: {crash_x:.2f}\n"
                        f"{CHECK_MARK_EMOJI} Вы долетели и выиграли: {hbold(f'{winnings} MEM')}!"
                    )
                    button_text = f"{CHECK_MARK_EMOJI} Успешно"
                    emoji = ROCKET_EMOJI
                else:
                    # Проигрыш — ставка уже списана
                    try:
                        await self.db.add_game_history(user_id, "краш", stake, "lose", 0)
                    except Exception:
                        pass
                    
                    result_text = (
                        f"<blockquote>🚀 Краш</blockquote>\n\n"
                        f"📊 Вы выбрали коэффициент: {chosen_x:.2f}\n"
                        f"💥 Ракета упала на: {crash_x:.2f}\n"
                        f"{CROSS_MARK_EMOJI} Вы не долетели и потеряли: {hbold(f'{stake} MEM')}!"
                    )
                    button_text = f"{CROSS_MARK_EMOJI} Поражение"
                    emoji = BOOM_EMOJI
                
                # Отправляем итоговый текст
                try:
                    await message.bot.send_message(chat_id, result_text, parse_mode="HTML")
                except Exception:
                    pass
                
                # Отправляем эмодзи + кнопка
                try:
                    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(button_text, callback_data="dummy")]])
                    await message.bot.send_message(chat_id, emoji, reply_markup=kb)
                except Exception:
                    pass
                
            except Exception:
                # попытка вернуть ставку при фатальной ошибке
                try:
                    await self.db.update_balance(user_id, stake)
                    await message.bot.send_message(chat_id, "❌ Произошла ошибка при обработке игры. Ставка возвращена.")
                except Exception:
                    pass
            finally:
                # Гарантированно удаляем активную игру
                try:
                    self.crash_games.pop(user_id, None)
                except Exception:
                    pass
        
        # Запускаем фоновую задачу
        try:
            asyncio.create_task(_process_and_notify())
        except Exception:
            # Возврат ставки при ошибке запуска задачи
            try:
                await self.db.update_balance(user_id, stake)
            except Exception:
                pass
            self.crash_games.pop(user_id, None)
            await message.reply("❌ Произошла ошибка. Ставка возвращена.")
            return False
        
        # Обновляем кулдаун
        self.crash_cooldowns[user_id] = now
        
        return True
    
    async def show_help(self, message: Message):
        """Показать справку по крашу"""
        help_text = """
<blockquote>🚀 ИГРА КРАШ</blockquote>

📋 Команда:
• Краш [ставка] [коэффициент] - сделать ставку

💰 Правила:
• Вы выбираете коэффициент от 1.0 до 10.0
• Ракета летит и множитель растет
• Если ракета упала выше вашего коэффициента - вы выиграли!
• Если ракета упала ниже вашего коэффициента - вы проиграли

📌 Примеры:
• краш 1000 2.5 - 1000 MEM на коэффициент 2.5x
• краш 500 1.5 - 500 MEM на коэффициент 1.5x
• краш все 3.0 - все средства на коэффициент 3.0x

⚡ Правила:
• Минимальная ставка: 100 MEM
• Кулдаун между играми: 5 секунд
• Максимальный коэффициент: 10.0x
• 70% шанс падения в диапазоне 1.00-1.10
"""
        await message.reply(help_text, parse_mode="HTML")

# Инициализация игры
def init_crash(database):
    """Инициализация игры краш"""
    return CrashGame(database)

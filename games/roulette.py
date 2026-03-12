import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List
from collections import deque
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Константы
RED = '🔴'
BLACK = '⚫'
GREEN = '🟢'
COOLDOWN_TIME = 10
ROULETTE_SPIN_DURATION = 3
GO_COOLDOWN = 3
MAX_NUMBERS_IN_BET = 50
ODD_EVEN_PAYOUT = 1.4

# Стикеры для анимации рулетки
ROULETTE_STICKER_IDS = {
    0: 'CAACAgIAAxkBAAEPX3NoxsnQquBEKy69rKwukikQcPNPBQACMXEAAsGPqEvgtLCZn60BCTYE',
    1: 'CAACAgIAAxkBAAEPX7Boxs-_mNWvtDbqR_aE0dsdt_--kgACYm0AAsV_qUvwV2I-O_92MzYE',
    2: 'CAACAgIAAxkBAAEPX2FoxsfTQRWf6Sc6EKpXeMrrmm0xnwACu3AAAmt8qUuMHj22bDK7hDYE',
    3: 'CAACAgIAAxkBAAEPX3loxsy26RdMmbvFTg7YMpEr2pqT1wACf2sAAobNqUv5NhB7HLBzLTYE',
    4: 'CAACAgIAAxkBAAEPX4toxs3-en3kMoXrWAzvBNtvkNKCvwACGWwAAgmWqEvDac6OXAABYnY2BA',
    5: 'CAACAgIAAxkBAAEPX1loxsdi70h2Sw3e_SH5Xsyw4WMiBAACaG8AAvZ0qUs10WCEkqxX3DYE',
    6: 'CAACAgIAAxkBAAEPX5Noxs6U0UpA0uoab7TNXKUM_25pNAACInAAAkkgqUum3rYhVGMOYzYE',
    7: 'CAACAgIAAxkBAAEPX65oxs-j-fVYeN0ZyC6AQ7e7__s-hQACpmUAAgxQsEvOOrqMWzDs9zYE',
    8: 'CAACAgIAAxkBAAEPX5Foxs5z3EvMHfB1w74PYOnXpkUGvQACc2kAAo0yqUsreLPxA-J-aTYE',
    9: 'CAACAgIAAxkBAAEPX5Voxs640DyPMMEyDzons_hY5xNMCgACg2YAArU-qUvBsA5QppMYBDYE',
    10: 'CAACAgIAAxkBAAEPX3VoxsxuCRfiBaXkS2AEOzCWajByVwACCGwAAn9KqEtl9f_8GfnALDYE',
    11: 'CAACAgIAAxkBAAEPX2loxsg7rrwkTVZRwtpLZeZoMQkudwAC3msAAjl-qUtgCWpsiik4pDYE',
    12: 'CAACAgIAAxkBAAEPX3toxsztP0kyrOmhMZ7laQqlhsDwmgACc3cAAqZkqEsZBYHZtb4HsDYE',
    13: 'CAACAgIAAxkBAAEPX6Foxs94kqp9NHFY_EUZIyPGwsrfPQAC9WUAAqUtsEu4A_dYVBl3EzYE',
    14: 'CAACAgIAAxkBAAEPX5loxs75MpXHlkWaZD2yTJtwQE2C4QACaHUAAm06qUubaUhHHkRQtDYE',
    15: 'CAACAgIAAxkBAAEPX4loxs3ZbPTATZPn0YAlLWootXp8HwACXnIAArg5qUueqto_IaZInTYE',
    16: 'CAACAgIAAxkBAAEPX21oxsmDjbMlpsjZsQ5MJ7PJyPN09QAC3nQAAl2LqEti203L-GHZ8TYE',
    17: 'CAACAgIAAxkBAAEPX31oxs0RH4dTn7ejukEn6K2Pui9WUwAC-XEAA8qoSzy-pE02t_7DNgQ',
    18: 'CAACAgIAAxkBAAEPX3doxsyPaBsyhOdqry3srpy-aT3R4AACu3EAApaoqUt4-NurUHdQCzYE',
    19: 'CAACAgIAAxkBAAEPX2NoxsfzMT2bszLE7hi9CyC0FIFsJQAC028AAhRvqEs4hAdYEq6-sDYE',
    20: 'CAACAgIAAxkBAAEPX4Noxs1vYPMzxVRurk3eUDLNKrkHDwACmmMAAn-tqUuIolA0hUdGuzYE',
    21: 'CAACAgIAAxkBAAEPX4Voxs2Kqe4YqaG79jI9lfpJFpLcIQACDnkAAkJhqEsh2VgC776rRTYE',
    22: 'CAACAgIAAxkBAAEPX5doxs7f3Ze62CsAAU_X_UzR-CzplU4AAqJ1AAJbeKhLntslojyJfEU2BA',
    23: 'CAACAgIAAxkBAAEPX3Foxsmjo8GZy1Kl0gSiNGCbEKLG8QACxXEAAnmNqEsZVFvH7_y5lzYE',
    24: 'CAACAgIAAxkBAAEPX1toxseCAae1XaeprwIN8dsG7E-mhgAC4nkAArFxsEu3KApsLo6nfDYE',
    25: 'CAACAgIAAxkBAAEPX4doxs23OriwoivF4EMrzhLWCLf4EgACf3MAAkiqqUt2dUbW8-Qg9DYE',
    26: 'CAACAgIAAxkBAAEPX59oxs9C6nzI4_hXW3cH3XIdYvDrEgACPmsAAv_5sUuGhpKQfUxwwDYE',
    27: 'CAACAgIAAxkBAAEPX2doxsggBKW_-miQzl10ucKIjaL_cwACPW0AApj1qEvwCGMLvBnxbTYE',
    28: 'CAACAgIAAxkBAAEPX51oxs8mzwJLOWMuaqW0Fn-PhFDxCgACu2wAAiUkqEsTMHlkQoOOyzYE',
    29: 'CAACAgIAAxkBAAEPX4Foxs1S7n223c3m_mTRIls4uy_WJAAC324AAh7VqUte0Uc3aofKwzYE',
    30: 'CAACAgIAAxkBAAEPX39oxs00YkKjlnEO0aXwM2iVbrm52wAC3G0AAjoGsEumvpK88ed0uzYE',
    31: 'CAACAgIAAxkBAAEPX2toxslck6g_E58D-HhK_gNN7kdXJAACFm8AAmRmqUvFyBdW_r3jBDYE',
    32: 'CAACAgIAAxkBAAEPX11oxseh0f7MZJbpoXTGilgQopcVrAACY3EAAlBCsUunVsFT9ROxzzYE',
    33: 'CAACAgIAAxkBAAEPX19oxse8P__VXs6N4HHcA5NO3yIBEAACUXIAAiibsUu7t8mandGQuTYE',
    34: 'CAACAgIAAxkBAAEPX41oxs4kQT9io8rPNYEaMsJ48fiAmAACaXcAAq6jsUsGQj_3FSUlEzYE',
    35: 'CAACAgIAAxkBAAEPX2VoxsgKXsC6SBhD2mLWITKDnN9FSwACvWgAAs2XqEsLYlAQNIGlDTYE',
    36: 'CAACAgIAAxkBAAEPX49oxs5OyT17P_TlkDji0TPA3kyEtgACUW8AAi9JqEuBxymhD-OS3TYE',
}

NUMBER_COLOR_MAP = {
    0: GREEN,
    1: RED,
    2: BLACK,
    3: RED,
    4: BLACK,
    5: RED,
    6: BLACK,
    7: RED,
    8: BLACK,
    9: RED,
    10: BLACK,
    11: BLACK,
    12: RED,
    13: BLACK,
    14: RED,
    15: BLACK,
    16: RED,
    17: BLACK,
    18: RED,
    19: RED,
    20: BLACK,
    21: RED,
    22: BLACK,
    23: RED,
    24: BLACK,
    25: RED,
    26: BLACK,
    27: RED,
    28: BLACK,
    29: BLACK,
    30: RED,
    31: BLACK,
    32: RED,
    33: BLACK,
    34: RED,
    35: BLACK,
    36: RED,
}

COLOR_MAPPING = {
    'к': 'красное🔴', 'ч': 'черное⚫', 'красное': 'красное🔴', 'черное': 'черное⚫',
    'кра': 'красное🔴', 'чер': 'черное⚫', '0': 'зеро🟢', 'зеро': 'зеро🟢',
    'одд': 'одд', 'евен': 'евен'
}

class RouletteGame:
    def __init__(self, db):
        self.db = db
        # Состояния для каждого пользователя
        self.user_roulette: Dict[int, 'UserRoulette'] = {}
        # Глобальные состояния
        self.result_log = deque(maxlen=10)
        self.roulette_cooldown: Dict[int, datetime] = {}
        self.last_roulette_use: Dict[int, datetime] = {}
        self.last_bet_time: Dict[int, datetime] = {}

class UserRoulette:
    def __init__(self):
        # список ставок: [{'stake': int, 'bet_type': str, 'bet_value': str}]
        self.current_bets: List[Dict] = []
        self.users_playing: bool = False
        self.users_with_bets: bool = False

def init_roulette(db):
    """Инициализация игры рулетка"""
    return RouletteGame(db)

# Утилиты для работы с суммами
def format_number(amount):
    """Форматирует сумму без копеек: округляет до целого и вставляет пробел как разделитель тысяч."""
    try:
        amt = int(round(float(amount)))
    except Exception:
        return str(amount)
    return f"{amt:,}".replace(",", " ")

def get_number_color(number):
    return NUMBER_COLOR_MAP.get(number)

def roll_roulette():
    result = random.randint(0, 36)
    return result, get_number_color(result)

def is_odd(number):
    return number % 2 != 0

def is_even(number):
    return number % 2 == 0

def is_valid_range(range_str):
    """Проверяет валидность любого диапазона от 0 до 36"""
    try:
        start, end = map(int, range_str.split('-'))
        if start > end:
            return False
        if 0 <= start <= 36 and 0 <= end <= 36:
            return True
        else:
            return False
    except ValueError:
        return False

def check_win(bet_type, bet_value, result, result_color):
    if bet_type in ('к', 'красное', 'кра'):
        return result_color == RED
    elif bet_type in ('ч', 'черное', 'чер'):
        return result_color == BLACK
    elif bet_type in ('0', 'зеро'):
        return result == 0
    elif bet_type == 'одд':
        return is_odd(result)
    elif bet_type == 'евен':
        return is_even(result)
    elif bet_type == 'число':
        return int(bet_value) == result
    elif bet_type == 'числа':
        numbers = list(map(int, bet_value.split()))
        return result in numbers
    elif bet_type == 'диапазон':
        # Поддержка любых диапазонов
        try:
            start, end = map(int, bet_value.split('-'))
            return start <= result <= end
        except ValueError:
            return False
    elif bet_type == 'диапазон1':
        return 1 <= result <= 12
    elif bet_type == 'диапазон2':
        return 13 <= result <= 24
    elif bet_type == 'диапазон3':
        return 25 <= result <= 36
    return False

def calculate_payout(bet_type, stake, bet_value=None):
    """Возвращает чистый выигрыш: то, что добавляется к балансу (ставка уже списана)."""
    if bet_type in ('к', 'ч', 'красное', 'черное', 'кра', 'чер'):
        return int(round(stake * 0.9))  # x1.9 минус ставка
    elif bet_type == 'диапазон':
        # Динамический расчет для любых диапазонов
        try:
            start, end = map(int, bet_value.split('-'))
            numbers_count = end - start + 1
            # Множитель зависит от количества чисел в диапазоне
            if numbers_count <= 6:
                return int(round(stake * 5))  # x6 минус ставка
            elif numbers_count <= 12:
                return int(round(stake * 2))  # x3 минус ставка
            elif numbers_count <= 18:
                return int(round(stake * 0.5))  # x1.5 минус ставка
            else:
                return int(round(stake * 0.2))  # x1.2 минус ставка
        except:
            return int(round(stake * 2))  # По умолчанию x3 минус ставка
    elif bet_type in ('диапазон1', 'диапазон2', 'диапазон3'):
        return int(round(stake * 3))  # x3 минус ставка
    elif bet_type in ('0', 'число', 'зеро'):
        return int(round(stake * 16))  # x17 минус ставка
    elif bet_type in ('одд', 'евен'):
        return int(round(stake * (ODD_EVEN_PAYOUT - 1)))
    elif bet_type == 'числа':
        return int(round(stake * 6))  # x7 минус ставка
    else:
        return 0

async def send_roulette_animation(message: types.Message, result_number):
    """Отправляет стикер анимации рулетки."""
    sticker_id = ROULETTE_STICKER_IDS.get(result_number)
    if sticker_id:
        sent_message = await message.reply_sticker(sticker_id)
        return sent_message.message_id  # Возвращаем ID сообщения
    else:
        await message.reply("❌Ошибка: не найден стикер для этого числа.")
        return None

async def is_roulette_allowed(roulette_game, user_id):
    """Проверяет, можно ли пользователю использовать рулетку сейчас."""
    if user_id in roulette_game.roulette_cooldown:
        time_since_last_use = datetime.now() - roulette_game.roulette_cooldown[user_id]
        if time_since_last_use < timedelta(seconds=COOLDOWN_TIME):
            remaining_time = timedelta(seconds=COOLDOWN_TIME) - time_since_last_use
            return False, f"❌Вы сможете начать новую игру в рулетку через {remaining_time.seconds} сек!"
    return True, None

def parse_stake_amount(stake_str):
    """Парсит сумму ставки с поддержкой сокращений"""
    stake_str = stake_str.lower().replace(" ", "")
    multipliers = {"к": 10**3, "м": 10**6, "г": 10**9}

    # Проверка, если просто число
    if stake_str.isdigit():
        return int(stake_str)

    # Проверяем на окончания к/м/г
    for suffix, factor in multipliers.items():
        if stake_str.endswith(suffix):
            try:
                number_part = float(stake_str[:-len(suffix)].replace(",", "."))
                return int(round(number_part * factor))
            except ValueError:
                return None
    return None

# Методы для RouletteGame
async def place_bet(self, message: types.Message, bet: int, bet_values: List[str]):
    """Обработка ставки"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Убедимся что у пользователя есть состояние рулетки
    if user_id not in self.user_roulette:
        self.user_roulette[user_id] = UserRoulette()
    roulette = self.user_roulette[user_id]
    
    # Проверка разрешений
    allowed, reason = await is_roulette_allowed(self, user_id)
    if not allowed:
        await message.reply(reason, reply_to_message_id=message.message_id)
        return
    
    # Защита от частых команд
    if user_id in self.last_roulette_use and datetime.now() - self.last_roulette_use[user_id] < timedelta(seconds=4):
        wait = timedelta(seconds=4) - (datetime.now() - self.last_roulette_use[user_id])
        await message.reply(f"❌Подождите {wait.total_seconds():.1f} секунд перед повторным использованием команды.", reply_to_message_id=message.message_id)
        return
    
    # Проверка баланса
    user = await self.db.get_user(user_id)
    if not user:
        await message.reply("❌ Пользователь не найден", reply_to_message_id=message.message_id)
        return
    
    balance = user['balance']
    
    # Обработка множественных чисел
    if len(bet_values) > 1 and all(p.isdigit() for p in bet_values):
        # множественные числа
        if len(bet_values) > MAX_NUMBERS_IN_BET:
            await message.reply(f"❌Максимальное количество отдельных чисел: {MAX_NUMBERS_IN_BET}", reply_to_message_id=message.message_id)
            return
        
        total_stake = bet * len(bet_values)
        if balance < total_stake:
            await message.reply("❌ Недостаточно средств на балансе", reply_to_message_id=message.message_id)
            return
        
        # Списываем суммарно
        await self.db.update_balance(user_id, -total_stake)
        
        for num_str in bet_values:
            num = int(num_str)
            if not (0 <= num <= 36):
                # При ошибке - возврат всех средств
                await self.db.update_balance(user_id, total_stake)
                await message.reply("❌Число должно быть от 0 до 36.", reply_to_message_id=message.message_id)
                return
            roulette.current_bets.append({'stake': bet, 'bet_type': 'число', 'bet_value': str(num)})
        
        roulette.users_with_bets = True
        self.last_bet_time[user_id] = datetime.now()
        self.last_roulette_use[user_id] = datetime.now()
        
        new_balance = await self.db.get_user_balance(user_id)
        
        await message.reply(
            f"<blockquote>🎰 Рулетка</blockquote>\n\n"
            f"💰 Ставки: {format_number(bet)} MEM на числа {', '.join(bet_values)} приняты\n"
            f"💳 Ваш баланс: {format_number(new_balance)} MEM\n\n"
            f"Напишите 'го' чтобы запустить раунд!",
            reply_to_message_id=message.message_id,
            parse_mode="HTML"
        )
        return
    
    # Обработка одиночной ставки (может быть диапазон или что-то другое)
    if not bet_values:
        await message.reply("❌Не указан тип ставки.", reply_to_message_id=message.message_id)
        return
    
    bet_token = bet_values[0].lower()  # Берем первый аргумент
    
    bet_type = None
    bet_value = None
    display_value = bet_token
    
    if bet_token in ('к', 'ч', 'одд', 'евен', 'красное', 'черное', 'кра', 'чер', '0', 'зеро'):
        if bet_token in ('к', 'красное', 'кра'):
            bet_type = 'к'
            display_value = COLOR_MAPPING.get('к', 'красное')
        elif bet_token in ('ч', 'черное', 'чер'):
            bet_type = 'ч'
            display_value = COLOR_MAPPING.get('ч', 'черное')
        elif bet_token in ('0', 'зеро'):
            bet_type = '0'
            display_value = 'зеро🟢'
        elif bet_token == 'одд':
            bet_type = 'одд'
            display_value = 'одд'
        elif bet_token == 'евен':
            bet_type = 'евен'
            display_value = 'евен'
        bet_value = bet_type
    elif "-" in bet_token:
        if not is_valid_range(bet_token):
            await message.reply("❌Неправильно введен диапазон. Допустимые: 0-36, 17-27, 9-19 и т.д.", reply_to_message_id=message.message_id)
            return
        start, end = map(int, bet_token.split('-'))
        # Проверяем стандартные дюжины для совместимости
        if start == 1 and end == 12:
            bet_type = 'диапазон1'
        elif start == 13 and end == 24:
            bet_type = 'диапазон2'
        elif start == 25 and end == 36:
            bet_type = 'диапазон3'
        else:
            bet_type = 'диапазон'  # Новый тип для любых диапазонов
        bet_value = bet_token
        display_value = bet_token  # Показываем сам диапазон
    elif bet_token.isdigit():
        num = int(bet_token)
        if not (0 <= num <= 36):
            await message.reply("❌Число должно быть от 0 до 36.", reply_to_message_id=message.message_id)
            return
        bet_type = 'число'
        bet_value = str(num)
        display_value = bet_value
    
    # Проверка и списание ставки
    if balance < bet:
        await message.reply("❌ Недостаточно средств на балансе", reply_to_message_id=message.message_id)
        return
    
    await self.db.update_balance(user_id, -bet)
    roulette.current_bets.append({'stake': bet, 'bet_type': bet_type, 'bet_value': bet_value})
    roulette.users_with_bets = True
    self.last_bet_time[user_id] = datetime.now()
    self.last_roulette_use[user_id] = datetime.now()
    
    new_balance = await self.db.get_user_balance(user_id)
    
    await message.reply(
            f"<blockquote>🎰 Рулетка</blockquote>\n\n"
            f"💰 Ставка: {bet} MEM принята на {display_value}\n"
            f"💳 Ваш баланс: {format_number(new_balance)} MEM\n\n"
            f"Напишите 'го' чтобы запустить раунд!",
            reply_to_message_id=message.message_id,
            parse_mode="HTML"
        )

async def start_round(self, message: types.Message):
    """Запуск раунда рулетки"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    if user_id not in self.user_roulette:
        self.user_roulette[user_id] = UserRoulette()
    roulette = self.user_roulette[user_id]
    
    if not roulette.current_bets:
        await message.reply("❌Нельзя писать 'го' вне участия в рулетке.", reply_to_message_id=message.message_id)
        return
    
    if roulette.users_playing:
        await message.reply("⏳Дождитесь, когда закончится ваша текущая игра!", reply_to_message_id=message.message_id)
        return
    
    # Проверка GO_COOLDOWN
    if user_id in self.last_bet_time:
        time_since_last_bet = datetime.now() - self.last_bet_time[user_id]
        if time_since_last_bet < timedelta(seconds=GO_COOLDOWN):
            remaining_time = GO_COOLDOWN - time_since_last_bet.total_seconds()
            await message.reply(f"⏱||Подождите {remaining_time:.1f} сек. перед началом игры!", reply_to_message_id=message.message_id)
            return
    
    roulette.users_playing = True
    try:
        result, result_color = roll_roulette()
        # Отправляем стикер-анимацию
        anim_msg_id = await send_roulette_animation(message, result)
        
        if anim_msg_id:
            await asyncio.sleep(ROULETTE_SPIN_DURATION)
            # Удаляем стикер
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=anim_msg_id)
            except Exception:
                pass
        
        # Добавляем в лог результатов
        self.result_log.append((result, result_color))
        
        # Считаем выплаты
        total_win = 0
        total_loss = 0
        bet_descriptions: List[str] = []
        
        # Обрабатываем ставки
        for bet in roulette.current_bets:
            b_type = bet['bet_type']
            b_value = bet['bet_value']
            stake = int(bet['stake'])
            win = check_win(b_type, b_value, result, result_color)
            if win:
                payout = calculate_payout(b_type, stake, b_value)
                await self.db.update_balance(user_id, payout)
                total_win += int(payout)
                display_label = COLOR_MAPPING.get(b_type, b_value)
                bet_descriptions.append(
                    f"✅ Ставка {format_number(stake)} MEM на {display_label} - ВЫИГРАЛ +{format_number(payout)} MEM"
                )
            else:
                total_loss += stake
                display_label = COLOR_MAPPING.get(b_type, b_value)
                bet_descriptions.append(
                    f"❌ Ставка {format_number(stake)} MEM на {display_label} - ПРОИГРАЛ -{format_number(stake)} MEM"
                )
        
        # Обновляем статистику
        try:
            if roulette.current_bets:
                await self.db.add_game_history(user_id, "рулетка", total_loss, "win" if total_win > 0 else "lose", total_win)
        except Exception:
            pass
        
        # Формируем результатный текст
        result_text = f"<blockquote>🎰 Результат рулетки: {result} {result_color}!</blockquote>\n\n"
        
        for desc in bet_descriptions:
            result_text += f"{desc}\n"
        
        result_text += f"\n💰 Общий выигрыш: +{format_number(int(total_win))} MEM"
        result_text += f"\n💸 Общий проигрыш: -{format_number(int(total_loss))} MEM"
        result_text += f"\n\n🔄 Рулетка окончена! Делайте новые ставки."
        
        await message.reply(result_text, parse_mode="HTML", reply_to_message_id=message.message_id)
        
    finally:
        # Очищаем состояние
        roulette.users_playing = False
        roulette.current_bets = []
        roulette.users_with_bets = False
        if user_id in self.last_bet_time:
            del self.last_bet_time[user_id]
        self.roulette_cooldown[user_id] = datetime.now()
        
        # Освобождаем кулдаун позже
        async def clear_cd(uid: int):
            await asyncio.sleep(COOLDOWN_TIME)
            self.roulette_cooldown.pop(uid, None)
        asyncio.create_task(clear_cd(user_id))

async def show_history(self, message: types.Message):
    """Показать историю результатов"""
    if not self.result_log:
        await message.reply("🎰 История рулетки пуста", reply_to_message_id=message.message_id)
        return
    text = "<blockquote>🎰 Последние результаты рулетки:</blockquote>\n\n"
    for number, color in self.result_log:
        text += f"{color} {number}\n"
    await message.reply(text, parse_mode="HTML", reply_to_message_id=message.message_id)

async def show_help(self, message: types.Message):
    """Показать справку по рулетке"""
    help_text = """
<blockquote>🎰 ИГРА РУЛЕТКА</blockquote>

📋 Команды:
• Рулетка [ставка] [ставка...] - сделать ставку
• рул [ставка] [ставка...] - сокращенная версия
• го - запустить раунд
• лог - показать последние результаты

💰 Типы ставок и множители:
• к/красное - красное (x1.9)
• ч/черное - черное (x1.9)
• одд - нечетные (x1.4)
• евен - четные (x1.4)
• 1-12 - первая дюжина (x3)
• 13-24 - вторая дюжина (x3)
• 25-36 - третья дюжина (x3)
• X-Y - любой диапазон (динамический x)
• 0-36 - конкретное число (x17)

📌 Примеры:
• рул 1000 к - 1000 на красное
• рул 500 7 14 21 - 500 на каждое число
• рул 2000 1-12 - 2000 на первую дюжину
• рул 1500 17-27 - 1500 на диапазон 17-27
• рул 800 9-19 - 800 на диапазон 9-19

⚡ Правила:
• Игра работает только в чатах
• Минимальная ставка: 100 MEM
• Кулдаун между раундами: 10 секунд
"""
    await message.reply(help_text, parse_mode="HTML", reply_to_message_id=message.message_id)

# Добавляем методы в класс
RouletteGame.place_bet = place_bet
RouletteGame.start_round = start_round
RouletteGame.show_history = show_history
RouletteGame.show_help = show_help

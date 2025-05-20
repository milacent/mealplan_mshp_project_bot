import asyncio
import re
from aiogram import F
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery, Message
from handlers.menu import build_menu_text
from database.db import save_user_to_db, delete_user_from_db, get_user_data, on_startup, on_shutdown
from keyboards.allergy_keyboards import allergy_inline_keyboard, ALLERGENS
from handlers.ai import get_ai_response

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_allergy_confirmation = State()
    waiting_for_allergies = State()
    waiting_for_allergies_manual = State()
    waiting_for_goal = State()
    waiting_for_timeframe = State()
    waiting_for_confirmation = State()
    waiting_for_delete_confirmation = State()
    waiting_ai_question = State()

def gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="М"), KeyboardButton(text="Ж")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def allergy_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Похудение")],
            [KeyboardButton(text="Набор массы")],
            [KeyboardButton(text="Поддержание веса")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def timeframe_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="3 месяца")],
            [KeyboardButton(text="Полгода")],
            [KeyboardButton(text="Год")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def final_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вперёд к цели")],
            [KeyboardButton(text="Мои данные"), KeyboardButton(text="Новый план")],
            [KeyboardButton(text="Задать вопрос"), KeyboardButton(text="Удалить аккаунт")]  # Добавлена новая кнопка
        ],
        resize_keyboard=True
    )

def delete_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, удалить")],
            [KeyboardButton(text="Нет, отменить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def bot_startup():
    on_startup()

async def bot_shutdown():
    on_shutdown()

@router.message(Command("start"))
async def start_handler(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    await state.update_data(user_id=user_id)
    await msg.answer(f"Привет! Добро пожаловать в нашего бота.\nТвой уникальный ID: {user_id}\n\nКак тебя зовут?")
    await state.set_state(RegistrationStates.waiting_for_name)

@router.message(Command("mydata"))
async def mydata_handler(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    loop = asyncio.get_running_loop()
    user_data = await loop.run_in_executor(None, get_user_data, user_id)
    if user_data:
        summary = (f"📋 <b>Ваши данные</b>:\n\n"
                   f"🆔 ID: {user_data['user_id']}\n"
                   f"👤 Имя: {user_data['name']}\n"
                   f"🎂 Возраст: {user_data['age']}\n"
                   f"⚧ Пол: {user_data['gender']}\n"
                   f"⚖ Вес: {user_data['weight']} кг\n"
                   f"📏 Рост: {user_data['height']} см\n"
                   f"🌿 Аллергии: {user_data['allergies']}\n"
                   f"🎯 Цель: {user_data['goal']}\n"
                   f"⏳ Срок: {user_data['timeframe']}")
        await msg.answer(summary)
    else:
        await msg.answer("Вы еще не зарегистрированы. Введите /start для регистрации.")

@router.message(Command("regenerate"))
async def regenerate_handler(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    loop = asyncio.get_running_loop()
    user_data = await loop.run_in_executor(None, get_user_data, user_id)

    if not user_data:
        await msg.reply("Вы еще не зарегистрированы. Введите /start для регистрации.")
        return

    processing_msg = await msg.reply("⏳ Составляю новый план питания...")
    menu_text = await build_menu_text(user_data)
    await processing_msg.delete()
    await msg.reply(menu_text)

@router.message(Command("delete"))
async def delete_handler(msg: types.Message, state: FSMContext):
    await msg.answer("Вы уверены, что хотите удалить свой аккаунт? Все данные будут потеряны.", reply_markup=delete_keyboard())
    await state.set_state(RegistrationStates.waiting_for_delete_confirmation)

@router.message(StateFilter(RegistrationStates.waiting_for_delete_confirmation))
async def process_delete_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Да, удалить":
        user_id = message.from_user.id
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_user_from_db, user_id)
        await message.reply("Ваш аккаунт успешно удален из базы данных.\n"
                            "Если хотите начать заново, введите /start.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif message.text == "Нет, отменить":
        await message.reply(
            "Удаление отменено.", reply_markup=final_menu_keyboard())
        await state.set_state(RegistrationStates.waiting_for_confirmation)
    else:
        await message.reply("Пожалуйста, выберите 'Да, удалить' или 'Нет, отменить'.", reply_markup=delete_keyboard())

@router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not re.match(r'^[А-Яа-яЁё\s]+', name):
        await message.reply("Пожалуйста, введите корректное имя (только русские буквы и пробелы).")
        return
    await state.update_data(name=name)
    await message.reply("Сколько тебе лет?")
    await state.set_state(RegistrationStates.waiting_for_age)

@router.message(StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 10 or int(message.text) > 100:
        await message.reply("Пожалуйста, введи корректный возраст (от 10 до 100 лет).")
        return
    await state.update_data(age=int(message.text))
    await message.reply("Какой у тебя пол?", reply_markup=gender_keyboard())
    await state.set_state(RegistrationStates.waiting_for_gender)

@router.message(StateFilter(RegistrationStates.waiting_for_gender))
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.strip().lower()
    if gender not in ["м", "ж"]:
        await message.reply("Пожалуйста, выбери пол с помощью кнопок ниже.", reply_markup=gender_keyboard())
        return
    await state.update_data(gender="Мужской" if gender == "м" else "Женский")
    await message.reply("Какой у тебя текущий вес (в кг)?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.waiting_for_weight)

@router.message(StateFilter(RegistrationStates.waiting_for_weight))
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if weight <= 25 or weight>300:
            await message.reply("Пожалуйста, введите корректный вес.")
            return
        await state.update_data(weight=weight)
        await message.reply("Какой у тебя рост (в см)?")
        await state.set_state(RegistrationStates.waiting_for_height)
    except ValueError:
        await message.reply("Пожалуйста, введите корректный вес (например, 70.5).")

@router.message(StateFilter(RegistrationStates.waiting_for_height))
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        if height <= 120 or height>240:
            await message.reply("Пожалуйста, введите корректный рост.")
            return
        await state.update_data(height=height)
        await message.reply("У тебя есть аллергии?", reply_markup=allergy_keyboard())
        await state.set_state(RegistrationStates.waiting_for_allergy_confirmation)
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

@router.message(StateFilter(RegistrationStates.waiting_for_allergy_confirmation))
async def process_allergy_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await state.update_data(selected_allergies=set())
        await message.reply(
            "Выбери из списка свои аллергии (можно несколько). Если нужного продукта нет — нажми «Ввести вручную».",
            reply_markup=allergy_inline_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_allergies)
    elif message.text.lower() == "нет":
        await state.update_data(allergies="Нет")
        await message.reply("Какова твоя цель?", reply_markup=goal_keyboard())
        await state.set_state(RegistrationStates.waiting_for_goal)
    else:
        await message.reply("Пожалуйста, выбери вариант с помощью кнопок ниже.", reply_markup=allergy_keyboard())

@router.callback_query(lambda c: c.data.startswith("allergy_"), StateFilter(RegistrationStates.waiting_for_allergies))
async def process_allergy_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = set(data.get("selected_allergies", set()))
    cb_data = callback.data

    if cb_data == "allergy_manual":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Введи свои аллергии через запятую (например, молоко, орехи):")
        await state.set_state(RegistrationStates.waiting_for_allergies_manual)
        await callback.answer()
        return

    if cb_data == "allergy_done":
        allergies_str = ", ".join(selected) if selected else "Нет"
        await state.update_data(allergies=allergies_str)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"Аллергии сохранены: {allergies_str}")
        await callback.message.answer("Какова твоя цель?", reply_markup=goal_keyboard())
        await state.set_state(RegistrationStates.waiting_for_goal)
        await callback.answer()
        return

    allergen = cb_data.replace("allergy_", "")
    if allergen in selected:
        selected.remove(allergen)
    else:
        selected.add(allergen)
    await state.update_data(selected_allergies=selected)
    await callback.message.edit_reply_markup(reply_markup=allergy_inline_keyboard(selected))
    await callback.answer()

@router.message(StateFilter(RegistrationStates.waiting_for_allergies_manual))
async def process_manual_allergies(message: types.Message, state: FSMContext):
    entered = [a.strip().lower() for a in message.text.split(",")]
    invalid = [a for a in entered if a not in ALLERGENS]
    if invalid:
        await message.reply(
            f"Некорректные или неизвестные продукты: {', '.join(invalid)}.\n"
            f"Пожалуйста, введи только из списка: {', '.join(ALLERGENS)}"
        )
        return
    allergies_str = ", ".join(entered)
    await state.update_data(allergies=allergies_str)
    await message.reply(f"Аллергии сохранены: {allergies_str}")
    await message.answer("Какова твоя цель?", reply_markup=goal_keyboard())
    await state.set_state(RegistrationStates.waiting_for_goal)

@router.message(StateFilter(RegistrationStates.waiting_for_goal))
async def process_goal(message: types.Message, state: FSMContext):
    if message.text not in ["Похудение", "Набор массы", "Поддержание веса"]:
        await message.reply("Пожалуйста, выбери цель с помощью кнопок ниже.", reply_markup=goal_keyboard())
        return
    await state.update_data(goal=message.text.strip())
    await message.reply("За какое время ты хочешь достичь цели?", reply_markup=timeframe_keyboard())
    await state.set_state(RegistrationStates.waiting_for_timeframe)


@router.message(Command("ask"))
async def handle_ai_question(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    loop = asyncio.get_running_loop()
    user_data = await loop.run_in_executor(None, get_user_data, user_id)

    await msg.reply("Напишите ваш вопрос о питании или здоровом образе жизни:")
    await state.set_state("waiting_ai_question")
    await state.update_data(user_context=user_data)

@router.message(F.text, StateFilter("waiting_ai_question"))
async def process_ai_question(msg: Message, state: FSMContext):
    data = await state.get_data()
    processing_msg = await msg.reply("🧠 Обрабатываю вопрос...")

    try:
        response = await get_ai_response(
            user_message=msg.text,
            user_context=data.get("user_context")
        )
        await msg.reply(response)

        # Отправляем клавиатуру с кнопками для дальнейших действий
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Задать вопрос")],
                [KeyboardButton(text="Назад в меню")]
            ],
            resize_keyboard=True
        )
        await msg.answer("Выберите действие:", reply_markup=keyboard)

        # Установите состояние на ожидание подтверждения
        await state.set_state(RegistrationStates.waiting_for_confirmation)

    except Exception as e:
        await msg.reply(f"Ошибка: {str(e)}")
    finally:
        await processing_msg.delete()


@router.message(StateFilter(RegistrationStates.waiting_for_timeframe))
async def process_timeframe(message: types.Message, state: FSMContext):
    if message.text not in ["3 месяца", "Полгода", "Год"]:
        await message.reply("Пожалуйста, выбери срок с помощью кнопок ниже.", reply_markup=timeframe_keyboard())
        return
    await state.update_data(timeframe=message.text.strip())
    user_data = await state.get_data()

    summary = (f"✅ Регистрация завершена!\n\n"
               f"🆔 ID: {user_data['user_id']}\n"
               f"👤 Имя: {user_data['name']}\n"
               f"🎂 Возраст: {user_data['age']}\n"
               f"⚧ Пол: {user_data['gender']}\n"
               f"⚖ Вес: {user_data['weight']} кг\n"
               f"📏 Рост: {user_data['height']} см\n"
               f"🌿 Аллергии: {user_data['allergies']}\n"
               f"🎯 Цель: {user_data['goal']}\n"
               f"⏳ Срок: {user_data['timeframe']}")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, save_user_to_db, user_data)

    await message.reply(summary)
    await message.reply(
        "Выберите дальнейшее действие:",
        reply_markup=final_menu_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_confirmation)

@router.message(StateFilter(RegistrationStates.waiting_for_confirmation))
async def send_menu(message: types.Message, state: FSMContext):
    text = message.text.lower().replace("ё", "е").strip()
    if text == "назад в меню":
        await state.clear()
        await message.reply(
            "Вы вернулись в главное меню.",
            reply_markup=final_menu_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_confirmation)

    elif text == "вперед к цели":
        user_id = message.from_user.id
        loop = asyncio.get_running_loop()
        user_data = await loop.run_in_executor(None, get_user_data, user_id)

        if not user_data:
            await message.reply("Вы еще не зарегистрированы. Введите /start для регистрации.", reply_markup=ReplyKeyboardRemove())
            return

        processing_msg = await message.reply("⏳ Составляю план питания...")
        menu_text = await build_menu_text(user_data)
        await processing_msg.delete()
        await message.reply(menu_text, reply_markup=final_menu_keyboard())
    elif text == "мои данные":
        await mydata_handler(message, state)
    elif text == "новый план":
        await regenerate_handler(message, state)
    elif text == "задать вопрос":
        await handle_ai_question(message, state)
    elif text == "удалить аккаунт":
        await delete_handler(message, state)
    elif text == "/mydata":
        await mydata_handler(message, state)
    elif text == "/regenerate":
        await regenerate_handler(message, state)
    elif text == "/delete":
        await delete_handler(message, state)
    else:
        await message.reply(
            "Пожалуйста, выберите действие с помощью кнопок ниже.",
            reply_markup=final_menu_keyboard()
        )

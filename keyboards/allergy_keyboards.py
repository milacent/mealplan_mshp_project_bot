from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Топ-8 популярных аллергенов для кнопок
POPULAR_ALLERGENS = [
    "молоко", "яйца", "пшеница", "арахис",
    "рыба", "морепродукты", "соевые продукты", "орехи"
]

# Расширенный список для проверки ручного ввода
ALLERGENS = [
    "молоко", "коровье молоко", "козье молоко", "овечье молоко", "сыры", "сливки", "творог", "йогурт", "кефир", "сметана", "масло",
    "яйца", "куриные яйца", "перепелиные яйца", "яичный белок", "яичный желток",
    "пшеница", "глютен", "рожь", "ячмень", "овёс", "манная крупа", "макароны", "хлеб", "булочки",
    "арахис",
    "древесные орехи", "грецкие орехи", "фундук", "миндаль", "кешью", "фисташки", "пекан", "орехи",
    "соевые продукты", "соя",
    "рыба",
    "ракообразные", "креветки", "омары", "крабы", "лобстеры",
    "моллюски", "устрицы", "мидии", "кальмары",
    "кунжут",
    "горчица",
    "сельдерей",
    "люпин",
    "сульфиты",
    "шоколад",
    "мёд",
    "фрукты", "овощи", "сухофрукты",
    "мясо", "говядина", "свинина", "курица", "индейка",
]

def allergy_inline_keyboard(selected=None):
    selected = selected or set()
    buttons = []
    row = []
    for i, allergen in enumerate(POPULAR_ALLERGENS, 1):
        text = f"{'✅ ' if allergen in selected else ''}{allergen}"
        row.append(InlineKeyboardButton(text=text, callback_data=f"allergy_{allergen}"))
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="Ввести вручную", callback_data="allergy_manual")])
    buttons.append([InlineKeyboardButton(text="Готово", callback_data="allergy_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

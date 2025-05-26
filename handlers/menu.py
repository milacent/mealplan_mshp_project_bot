import aiohttp
from config import SPOONACULAR_API_KEY


def calculate_target_calories(weight, height, age, gender, goal, timeframe, activity_level=1.55):
    if gender == "мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    maintenance_calories = bmr * activity_level

    if goal == "похудение":
        if "3 месяца" in timeframe:
            target = maintenance_calories * 0.8
        elif "полгода" in timeframe:
            target = maintenance_calories * 0.85
        elif "год" in timeframe:
            target = maintenance_calories * 0.9
        else:
            target = maintenance_calories * 0.85
    elif goal == "набор массы":
        if "3 месяца" in timeframe:
            target = maintenance_calories + 350
        elif "полгода" in timeframe:
            target = maintenance_calories + 300
        elif "год" in timeframe:
            target = maintenance_calories + 250
        else:
            target = maintenance_calories + 300
    else:
        target = maintenance_calories

    return int(target)

async def get_meal_nutrition(meal_id: int) -> dict:
    """Получает КБЖУ для конкретного блюда по его ID."""
    url = f"https://api.spoonacular.com/recipes/{meal_id}/information"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": "true"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                nutrition = data.get("nutrition", {}).get("nutrients", [])
                result = {
                    "calories": 0,
                    "protein": 0,
                    "fat": 0,
                    "carbohydrates": 0
                }
                for nutrient in nutrition:
                    name = nutrient["name"].lower()
                    amount = nutrient["amount"]
                    if name == "calories":
                        result["calories"] = round(amount)
                    elif name == "protein":
                        result["protein"] = round(amount, 1)
                    elif name == "fat":
                        result["fat"] = round(amount, 1)
                    elif name == "carbohydrates":
                        result["carbohydrates"] = round(amount, 1)
                return result
            else:
                return {"calories": 0, "protein": 0, "fat": 0, "carbohydrates": 0}


async def build_menu_text(user_data: dict) -> str:
    """
    Генерирует план питания на один день с КБЖУ для каждого приема пищи.

    Args:
        user_data (dict): Данные пользователя (goal, weight, height, age, gender, allergies, timeframe)

    Returns:
        str: Текстовый план питания на день
    """
    goal = user_data["goal"].lower()
    timeframe = user_data["timeframe"].lower()
    weight = user_data["weight"]
    height = user_data["height"]
    age = user_data["age"]
    gender = user_data["gender"].lower()
    allergies = user_data["allergies"] if user_data["allergies"] != "Нет" else ""

    target_calories = calculate_target_calories(weight, height, age, gender, goal, timeframe)

    url = "https://api.spoonacular.com/mealplanner/generate"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "timeFrame": "day",
        "targetCalories": target_calories,
    }
    if allergies:
        params["excludeIngredients"] = allergies

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                meals = data.get("meals", [])

                menu = f"🍽 <b>План питания на день для {goal} (~{target_calories} ккал)</b>\n"
                menu += f"Период: {timeframe}\n\n"

                total_calories = 0
                total_protein = 0
                total_fat = 0
                total_carbs = 0

                for i, meal in enumerate(meals, 1):
                    nutrition = await get_meal_nutrition(meal["id"])
                    total_calories += nutrition["calories"]
                    total_protein += nutrition["protein"]
                    total_fat += nutrition["fat"]
                    total_carbs += nutrition["carbohydrates"]

                    menu += f"  <b>Прием {i}: {meal['title']}</b>\n"
                    menu += f"  Время приготовления: {meal['readyInMinutes']} мин\n"
                    menu += f"  Ссылка на рецепт: {meal['sourceUrl']}\n"
                    menu += f"  КБЖУ: {nutrition['calories']} ккал, "
                    menu += f"Б: {nutrition['protein']} г, Ж: {nutrition['fat']} г, У: {nutrition['carbohydrates']} г\n\n"

                menu += f"<b>Итого за день</b>:\n"
                menu += f"Калории: {round(total_calories, 2)} ккал\n"
                menu += f"Белки: {round(total_protein, 2)} г\n"
                menu += f"Жиры: {round(total_fat, 2)} г\n"
                menu += f"Углеводы: {round(total_carbs, 2)} г"

                return menu
            else:
                return f"Ошибка при запросе к API: {response.status}. Попробуйте позже."

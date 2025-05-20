import asyncio
from g4f.client import AsyncClient
from g4f.Provider import DeepInfra, Liaobots
from config import DEEPINFRA_API_KEY, LIAOBOTS_AUTHCODE

SYSTEM_PROMPT = """Ты - персональный ассистент по питанию и здоровому образу жизни. 
Отвечай на вопросы, используя научно обоснованную информацию. 
Правила:
1. Отвечай только на русском
2. Будь кратким (до 500 символов)
4. Учитывай контекст пользователя"""

history = []
async def get_ai_response(user_message: str, user_context: dict = None) -> str:
    providers = [
        {
            "name": "DeepInfra",
            "provider": DeepInfra,
            "params": {
                "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                "api_key": DEEPINFRA_API_KEY
            }
        },
        {
            "name": "Liaobots",
            "provider": Liaobots,
            "params": {
                "model": "gpt-3.5-turbo",
                "authcode": LIAOBOTS_AUTHCODE
            }
        }
    ]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    if user_context:
        context_msg = (
            f"Контекст пользователя: "
            f"Цель: {user_context.get('goal')}, "
            f"Аллергии: {user_context.get('allergies')}, "
            f"Вес: {user_context.get('weight')}кг, "
            f"Рост: {user_context.get('height')}см"
        )
        messages.append({"role": "user", "content": context_msg})

    messages.append({"role": "user", "content": user_message})

    for provider in providers:
        try:
            # Создаем клиента с классом провайдера и параметрами
            if provider["name"] == "DeepInfra":
                client = AsyncClient(
                    provider=provider["provider"],
                    api_key=provider["params"]["api_key"]
                )
                model = provider["params"]["model"]

            elif provider["name"] == "Liaobots":
                client = AsyncClient(
                    provider=provider["provider"],
                    authcode=provider["params"]["authcode"]
                )
                model = provider["params"]["model"]

            else:
                client = AsyncClient(provider=provider["provider"])
                model = provider["params"].get("model", None)

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=20
            )

            result = response.choices[0].message.content

            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": result})

            return result

        except Exception as e:
            print(f"Ошибка в {provider['name']}: {str(e)}")
            continue

    return "⚠️ Все сервисы временно недоступны. Попробуйте позже."
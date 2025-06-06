# MealPlanBot – Твой Персональный Помощник по Питанию и Здоровью

MealPlanBot — это умный бот, который помогает создать индивидуальный план питания, учитывая твои цели и предпочтения. С помощью искусственного интеллекта бот поддерживает тебя на пути к здоровью, отвечая на вопросы и обновляя твой план в любое время.

## Возможности MealPlanBot

- **Умная регистрация и персонализация**  
  Пройди простую регистрацию, укажи свое имя, возраст, пол, вес, рост, аллергии, цели и срок, за который ты хочешь достичь желаемого результата, чтобы получить индивидуальный план питания.

- **Персональные планы питания**  
  Бот формирует рацион, адаптированный под твои цели и сроки достижения результата.

- **Управление данными и планом**  
  В любой момент можешь просмотреть свои данные или изменить план.

- **Интерактивный ИИ-консультант**  
  Задавай вопросы о здоровье и питании — бот учитывает твою анкету и дает персонализированные ответы.

- **Простое и дружелюбное общение**  
  Следуй подсказкам бота, чтобы легко и удобно двигаться к своей цели.

## Установка и запуск

### 1. Создай файл `.env` в корне проекта с такими переменными:
```
BOT_TOKEN=твой_токен_бота_из_Telegram
SPOONACULAR_API_KEY=твой_ключ_от_Spoonacular_API
DB_HOST=localhost
DB_PORT=5432
DB_NAME=USER_DB
DB_USER=USER
DB_PASSWORD=USER_PASSWORD
```

### 2. Установи PostgreSQL и настрой базу данных

- Установи PostgreSQL (например, версию 17)
- Добавь путь к папке `bin` PostgreSQL в системные переменные PATH
- Запусти PowerShell или терминал и активируй виртуальное окружение:
```
venv\Scripts\activate
```

- Проверь доступность psql:
```
psql --version
```

- Подключись к postgres и создай базу и пользователя:
```
psql -U postgres
-- Введи пароль: USER_PASSWORD
CREATE DATABASE USER_DB;
CREATE USER USER WITH PASSWORD 'USER_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE USER_DB TO USER;
\q
```

- Войдите в базу и дайте права на схему:
```
psql -U postgres -d USER_DB
GRANT ALL PRIVILEGES ON SCHEMA public TO USER;
\q
```

### 3. Создай и активируй виртуальное окружение

На Windows:
```
python -m venv venv
venv\Scripts\activate
```

На Linux/macOS:
```
python3 -m venv venv
source venv/bin/activate
```

### 4. Установи зависимости
```
pip install -r requirements.txt
```

### 5. Запусти бота
```
python create_bot.py
```
### 6. Использование

После запуска бот будет готов принимать команды и помогать с планом питания через Telegram.

## Дальнейшие планы развития

- Расширение функционала умной регистрации и анализа целей  
- Интеграция с дополнительными API для расширения базы рецептов и нутриентов  
- Внедрение системы напоминаний и мотивационных сообщений  
- Добавление веб-интерфейса для удобного управления планом питания  
- Многоязычная поддержка  

## Как помочь проекту

Мы рады любым предложениям и улучшениям!

- Fork репозиторий  
- Создай свою ветку с описанием новой функции или исправления  
- Сделай коммиты с понятными сообщениями  
- Запусти тесты и убедись, что всё работает  
- Отправь merge request для рассмотрения  

## Авторы и благодарности

Проект создан Копейкиной Милой, 2025 год. Спасибо всем, кто помогает развивать MealPlanBot!

## Лицензия

MIT License  
Copyright (c) 2025 Копейкина Мила

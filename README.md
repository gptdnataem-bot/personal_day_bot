# Personal Day Bot (Telegram) — MVP

Ежедневный персональный дайджест: погода, валюта, короткие новости, цитата дня. 
Бот присылает утреннее сообщение в выбранное время и по команде.

## Быстрый старт

1) Установите зависимости:
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```
2) Скопируйте `.env.example` → `.env` и заполните токены.
3) Запустите:
```bash
python -m app.main
```

## Команды бота
- `/start` — приветствие и запись пользователя
- `/settings` — город, часовой пояс, время рассылки, валюты, темы новостей
- `/daily` — прислать дайджест прямо сейчас
- `/time` — показать текущее время и расписание
- `/help` — помощь

## Технологии
- aiogram 3 (Telegram Bot API)
- APScheduler (ежедневная рассылка)
- OpenWeatherMap (погода)
- RSS (новости через feedparser)
- SQLite (настройки пользователей)

## Файлы
- `app/main.py` — точка входа
- `app/bot.py` — маршрутизация команд
- `app/scheduler.py` — планировщик
- `app/storage.py` — SQLite для настроек
- `app/modules/weather.py` — погода (OpenWeather)
- `app/modules/news.py` — короткие новости из RSS
- `app/modules/currency.py` — курсы (ECB/исходники бесплатно)
- `app/modules/quote.py` — цитата дня

> Это MVP: код рассчитан на быстрый запуск, многое упрощено. Улучшайте по мере роста.

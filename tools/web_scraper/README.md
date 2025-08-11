# 🌐 Инструмент для веб-скрапинга

Профессиональный инструмент для загрузки HTML страниц с веб-сайтов. Создан на основе вашего старого скрипта `downloader.ipynb`, но значительно улучшен и структурирован.

## ✨ Возможности

- **Загрузка HTML страниц** с настраиваемыми задержками
- **Управление сессиями** скрапинга с метаданными
- **Обработка ошибок** и автоматические повторные попытки
- **Статистика загрузок** с детальными отчётами
- **Экспорт результатов** в CSV и JSON форматах
- **Гибкая настройка** User-Agent и параметров запросов

## 🏗️ Архитектура

```
tools/web_scraper/
├── __init__.py              # Основной модуль
├── html_downloader.py       # Класс для загрузки страниц
├── scraping_manager.py      # Менеджер сессий скрапинга
├── main.py                  # Демонстрационный скрипт
└── README.md                # Документация
```

## 🚀 Быстрый старт

### Простая загрузка одной страницы:

```python
from tools.web_scraper import HTMLDownloader

# Создаём загрузчик
downloader = HTMLDownloader(
    base_url="https://example.com",
    save_path="./downloads"
)

# Загружаем страницу
if downloader.download_page(filename="example.html"):
    print("Страница загружена успешно!")

# Получаем статистику
stats = downloader.get_stats()
print(f"Успешных загрузок: {stats['successful']}")

downloader.close()
```

### Загрузка нескольких страниц:

```python
# Загружаем 10 страниц с задержками
downloaded_files = downloader.download_multiple_pages(
    num_pages=10,
    filename_pattern="page_{}.html",
    delay=True
)

print(f"Загружено файлов: {len(downloaded_files)}")
```

### Использование менеджера скрапинга:

```python
from tools.web_scraper import ScrapingManager

# Создаём менеджер
manager = ScrapingManager(
    base_url="https://example.com",
    save_path="./scraping_results"
)

# Запускаем сессию
session_result = manager.start_scraping_session(
    session_name="my_session",
    num_pages=5,
    delay_range=(2, 5)
)

# Экспортируем метаданные
manager.export_metadata_to_csv("summary.csv")
```

## ⚙️ Настройки

### HTMLDownloader параметры:

- **`base_url`** - Базовый URL для загрузки
- **`save_path`** - Путь для сохранения файлов
- **`delay_range`** - Диапазон задержек между запросами (в секундах)
- **`max_retries`** - Максимальное количество повторных попыток
- **`user_agent`** - Пользовательский User-Agent

### ScrapingManager параметры:

- **`base_url`** - Базовый URL для скрапинга
- **`save_path`** - Путь для сохранения результатов
- **`metadata_file`** - Имя файла с метаданными

## 📊 Статистика и отчёты

### Получение статистики:

```python
# Статистика загрузчика
stats = downloader.get_stats()
print(f"Процент успеха: {stats['success_rate_percent']}%")

# Общая статистика менеджера
total_stats = manager.get_total_stats()
print(f"Всего сессий: {total_stats['total_sessions']}")
```

### Экспорт данных:

```python
# Экспорт в CSV
manager.export_metadata_to_csv("scraping_summary.csv")

# Метаданные автоматически сохраняются в JSON
# Файл: scraping_results/scraping_metadata.json
```

## 🛡️ Безопасность и этика

- **Уважайте robots.txt** - проверяйте правила сайта
- **Используйте задержки** - не перегружайте серверы
- **Соблюдайте лимиты** - не делайте слишком много запросов
- **Проверяйте Terms of Service** - убедитесь, что скрапинг разрешён

## 🔧 Примеры использования

### 1. Загрузка тестов по вождению (как в вашем старом скрипте):

```python
downloader = HTMLDownloader(
    base_url="https://practicatest.com/tests/permiso-B/online",
    save_path="./driving_tests",
    delay_range=(3, 7)  # Увеличенные задержки для уважения сервера
)

# Загружаем 50 страниц
downloaded_files = downloader.download_multiple_pages(
    num_pages=50,
    filename_pattern="test_page_{}.html"
)
```

### 2. Скрапинг с параметрами:

```python
manager = ScrapingManager(
    base_url="https://api.example.com/search",
    save_path="./search_results"
)

# Список параметров для поиска
search_params = [
    {"query": "spanish", "level": "beginner"},
    {"query": "spanish", "level": "intermediate"},
    {"query": "spanish", "level": "advanced"}
]

# Загружаем страницы с параметрами
session_result = manager.scrape_with_parameters(
    session_name="spanish_search",
    parameters_list=search_params
)
```

## 🚨 Обработка ошибок

Инструмент автоматически обрабатывает:
- **Сетевые ошибки** - повторные попытки
- **HTTP ошибки** - логирование и статистика
- **Таймауты** - настраиваемые лимиты
- **Ошибки записи** - безопасное сохранение

## 📁 Структура результатов

```
scraping_results/
├── session_name_1/
│   ├── page_1.html
│   ├── page_2.html
│   └── ...
├── session_name_2/
│   ├── params_1.html
│   └── params_2.html
├── scraping_metadata.json
└── scraping_summary.csv
```

## 🎯 Замена старого скрипта

Вместо старого `downloader.ipynb` теперь используйте:

```python
# Старый способ (из downloader.ipynb):
# Простой цикл с requests.get()

# Новый способ:
from tools.web_scraper import HTMLDownloader

downloader = HTMLDownloader(
    base_url="https://practicatest.com/tests/permiso-B/online",
    save_path="./data/driving_tests"
)

downloaded_files = downloader.download_multiple_pages(
    num_pages=50,
    delay_range=(2, 5)
)
```

## 🧪 Тестирование

Запустите демонстрационный скрипт:

```bash
cd tools/web_scraper
python main.py
```

Это создаст тестовые загрузки и покажет все возможности инструмента.

## 📝 Лицензия

MIT License - используйте свободно для любых целей.

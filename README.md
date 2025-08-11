# Spanish Analyser

Модуль для анализа испанского языка с интеграцией Anki. Проект предоставляет инструменты для обработки испанских текстов, анализа частоты слов и работы с коллекциями Anki.

## Возможности

- **Обработка текста**: Очистка HTML тегов, удаление испанских артиклей, определение доминирующего языка
- **Анализ слов**: Подсчёт частоты, категоризация по частоте, выявление новых слов
- **Интеграция с Anki**: Работа с коллекциями, поиск заметок, извлечение текста из карточек
- **Экспорт данных**: Сохранение результатов в Excel с категоризацией

## Структура проекта

```
spanish_analyser/
├── src/
│   ├── spanish_analyser/
│   │   ├── __init__.py
│   │   ├── text_processor.py      # Обработка испанского текста
│   │   ├── anki_integration.py    # Интеграция с Anki
│   │   └── word_analyzer.py       # Анализ слов
│   └── main.py                    # Основной скрипт
├── tools/                         # Основные инструменты
│   ├── web_scraper/               # Инструмент 1: Универсальный веб-скрапинг
│   │   ├── html_downloader.py           # Базовый загрузчик HTML
│   │   ├── scraping_manager.py          # Менеджер скрапинга
│   │   └── driving_tests_downloader.py # Специализация для билетов
│   ├── text_analyzer/             # Инструмент 2: Текстовый анализатор
│   │   └── driving_tests_analyzer.py
│   ├── main_tools.py              # Главный скрипт управления
│   └── README.md                  # Документация инструментов
├── data/                          # Данные проекта
│   ├── downloads/                 # Загруженные HTML файлы
│   └── results/                   # Результаты анализа (Excel)
├── tests/                         # Тесты
├── requirements.txt               # Зависимости Python
├── setup.py                      # Установка модуля
└── README.md                     # Документация
```

## Требования

- Python 3.8 или выше
- Git (для подмодуля Anki)

## Установка

1. **Клонирование репозитория:**

   ```bash
   git clone --recurse-submodules <URL_вашего_репозитория>
   cd spanish_analyser
   ```

2. **Создание виртуального окружения:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # для Linux/MacOS
   # source venv/Scripts/activate  # для Windows
   ```

3. **Установка зависимостей:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Установка модуля в режиме разработки:**

   ```bash
   pip install -e .
   ```

## Использование

### Базовый анализ текста

```python
from spanish_analyser import SpanishTextProcessor

processor = SpanishTextProcessor()
cleaned_text = processor.clean_text("<p>Los colores del semáforo</p>")
print(cleaned_text)  # "colores del semáforo"
```

### Анализ слов

```python
from spanish_analyser import WordAnalyzer

analyzer = WordAnalyzer()
analyzer.add_words_from_text("hola mundo, ¿cómo estás?")
stats = analyzer.get_summary_stats()
print(f"Всего слов: {stats['всего_уникальных_слов']}")

# Загрузка известных слов из Anki
from spanish_analyser import AnkiIntegration
with AnkiIntegration() as anki:
    if anki.is_connected():
        analyzer.load_known_words_from_anki(anki)
```

### Интеграция с Anki

```python
from spanish_analyser import AnkiIntegration

with AnkiIntegration() as anki:
    if anki.is_connected():
        stats = anki.get_collection_stats()
        print(f"Заметок: {stats['total_notes']}")
```

### Запуск основного скрипта

```bash
python src/main.py
```

### Использование инструментов

```bash
# Показать статус инструментов
python tools/main_tools.py status

# Загрузить билеты (страницы 1-10)
python tools/main_tools.py download --start 1 --end 10

# Анализировать загруженные билеты
python tools/main_tools.py analyze

# Полный цикл: загрузка + анализ
python tools/main_tools.py full --start 1 --end 5
```

## Тестирование

Запуск тестов:

```bash
python -m pytest tests/
```

Запуск конкретного теста:

```bash
python -m pytest tests/test_text_processor.py -v
```

## Разработка

Для разработки установите дополнительные зависимости:

```bash
pip install -e ".[dev]"
```

## Лицензия

MIT License

## Автор

Sergey
#!/usr/bin/env python3
"""
Основной скрипт для анализа испанского языка

Этот скрипт демонстрирует использование всех модулей проекта:
- Обработка текста
- Интеграция с Anki
- Анализ слов
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from spanish_analyser import SpanishTextProcessor, AnkiIntegration, WordAnalyzer


def main():
    """Основная функция для демонстрации возможностей"""
    print("=== Анализатор испанского языка ===\n")
    
    # Инициализируем компоненты
    text_processor = SpanishTextProcessor()
    word_analyzer = WordAnalyzer()
    
    print("Загружаем данные...")
    
    # Демонстрируем обработку текста
    print("\n--- Демонстрация обработки текста ---")
    sample_texts = [
        "<p>Los colores del semáforo</p>",
        "El coche rojo",
        "Las señales de tráfico"
    ]
    
    for text in sample_texts:
        cleaned = text_processor.clean_text(text)
        print(f"Исходный: {text}")
        print(f"Очищенный: {cleaned}")
        print()
    
    # Демонстрируем анализ слов
    print("--- Демонстрация анализа слов ---")
    for text in sample_texts:
        cleaned = text_processor.clean_text(text)
        word_analyzer.add_words_from_text(cleaned)
    
    # Показываем статистику
    stats = word_analyzer.get_summary_stats()
    print(f"Всего уникальных слов: {stats['всего_уникальных_слов']}")
    print(f"Новых слов: {stats['новых_слов']}")
    
    # Показываем топ слов
    top_words = word_analyzer.get_top_words(10)
    print("\nТоп 10 слов:")
    for word, freq in top_words:
        print(f"  {word}: {freq}")
    
    # Демонстрируем интеграцию с Anki (если доступно)
    print("\n--- Проверка интеграции с Anki ---")
    try:
        with AnkiIntegration() as anki:
            if anki.is_connected():
                stats = anki.get_collection_stats()
                print(f"Подключились к Anki:")
                print(f"  Всего заметок: {stats.get('total_notes', 'N/A')}")
                print(f"  Всего карточек: {stats.get('total_cards', 'N/A')}")
                print(f"  Всего колод: {stats.get('total_decks', 'N/A')}")
                
                # Показываем колоды
                deck_names = anki.get_deck_names()
                spanish_decks = [name for name in deck_names if 'spanish' in name.lower()]
                if spanish_decks:
                    print(f"\nИспанские колоды: {len(spanish_decks)}")
                    for deck in spanish_decks[:5]:  # Показываем первые 5
                        print(f"  - {deck}")
                    
                    # Загружаем известные слова из Anki
                    print("\nЗагружаем известные слова из Anki...")
                    if word_analyzer.load_known_words_from_anki(anki):
                        print("✅ Известные слова успешно загружены из Anki")
                    else:
                        print("⚠️ Не удалось загрузить известные слова из Anki")
                else:
                    print("Испанские колоды не найдены")
            else:
                print("Не удалось подключиться к Anki")
    except Exception as e:
        print(f"Ошибка при работе с Anki: {e}")
        print("Убедитесь, что Anki установлен и запущен")
    
    # Экспортируем результаты
    print("\n--- Экспорт результатов ---")
    try:
        word_analyzer.export_to_excel("word_analysis_results.xlsx")
        print("Результаты экспортированы в word_analysis_results.xlsx")
    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
    
    print("\n=== Анализ завершён ===")


if __name__ == "__main__":
    main()

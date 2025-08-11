#!/usr/bin/env python3
"""
Основные инструменты Spanish Analyser

Этот скрипт предоставляет доступ ко всем основным инструментам проекта:
1. Web Scraper - загрузка HTML страниц с practicatest.com
2. Text Analyzer - анализ текста и создание Excel отчётов
"""

import os
import sys
import argparse
from pathlib import Path

# Добавляем пути к модулям
sys.path.insert(0, str(Path(__file__).parent / "web_scraper"))
sys.path.insert(0, str(Path(__file__).parent / "text_analyzer"))

def run_web_scraper():
    """Запускает веб-скрапер для загрузки тестов"""
    print("🌐 Запуск веб-скрапера...")
    
    try:
        from download_tests import download_available_tests
        success = download_available_tests()
        
        if success:
            print("✅ Веб-скрапер завершил работу успешно")
        else:
            print("❌ Веб-скрапер завершил работу с ошибками")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля веб-скрапера: {e}")
    except Exception as e:
        print(f"❌ Ошибка при запуске веб-скрапера: {e}")

def run_text_analyzer():
    """Запускает текстовый анализатор"""
    print("📊 Запуск текстового анализатора...")
    
    try:
        from driving_tests_analyzer import DrivingTestsAnalyzer
        
        # Создаём анализатор с правильными путями
        analyzer = DrivingTestsAnalyzer(
            downloads_path="../data/downloads",
            results_path="../data/results"
        )
        
        try:
            # Подключаемся к Anki
            print("🔗 Подключение к Anki...")
            if not analyzer.connect_to_anki():
                print("⚠️ Продолжаю без Anki...")
            
            # Анализируем HTML файлы
            print("\n📄 Начинаю анализ HTML файлов...")
            analysis_result = analyzer.analyze_html_files()
            
            print(f"\n📊 Результаты анализа:")
            print(f"   Обработано файлов: {analysis_result['files_processed']}")
            print(f"   Найдено слов: {analysis_result['words_found']}")
            print(f"   Уникальных слов: {analysis_result['unique_words']}")
            
            # Экспортируем результаты
            print(f"\n📁 Экспортирую результаты...")
            export_file = analyzer.export_results()
            
            if export_file:
                print(f"✅ Результаты экспортированы в: {export_file}")
            
            # Показываем сводку
            summary = analyzer.get_analysis_summary()
            print(f"\n📋 Сводка анализа:")
            print(f"   Время выполнения: {summary['analysis_time']}")
            print(f"   Известных слов: {summary['known_words']}")
            print(f"   Новых слов: {summary['new_words']}")
            
        finally:
            analyzer.close()
            
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля текстового анализатора: {e}")
    except Exception as e:
        print(f"❌ Ошибка при запуске текстового анализатора: {e}")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="Spanish Analyser - Основные инструменты",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main_tools.py --scraper          # Запуск только веб-скрапера
  python main_tools.py --analyzer         # Запуск только текстового анализатора
  python main_tools.py --all              # Запуск всех инструментов
  python main_tools.py                    # Интерактивный режим
        """
    )
    
    parser.add_argument(
        '--scraper', 
        action='store_true',
        help='Запустить веб-скрапер для загрузки тестов'
    )
    
    parser.add_argument(
        '--analyzer', 
        action='store_true',
        help='Запустить текстовый анализатор'
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Запустить все инструменты'
    )
    
    args = parser.parse_args()
    
    print("🚗 Spanish Analyser - Основные инструменты")
    print("=" * 50)
    
    if args.all:
        print("🔄 Запуск всех инструментов...")
        run_web_scraper()
        print("\n" + "=" * 50)
        run_text_analyzer()
        
    elif args.scraper:
        run_web_scraper()
        
    elif args.analyzer:
        run_text_analyzer()
        
    else:
        # Интерактивный режим
        while True:
            print("\n📋 Доступные инструменты:")
            print("1. 🌐 Web Scraper - загрузка тестов с practicatest.com")
            print("2. 📊 Text Analyzer - анализ текста и создание отчётов")
            print("3. 🚪 Выход")
            
            choice = input("\nВыберите инструмент (1-3): ").strip()
            
            if choice == '1':
                run_web_scraper()
            elif choice == '2':
                run_text_analyzer()
            elif choice == '3':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()

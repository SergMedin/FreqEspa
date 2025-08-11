#!/usr/bin/env python3
"""
Главный скрипт для управления инструментами

Предоставляет единый интерфейс для:
1. Загрузки веб-страниц с билетами
2. Анализа загруженных страниц
3. Управления результатами
"""

import sys
import argparse
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web_scraper import DrivingTestsDownloader
from text_analyzer import DrivingTestsAnalyzer


def download_tests(start_page: int, end_page: int, delay: bool = True):
    """Загружает билеты по вождению"""
    print(f"🚗 Загрузка билетов с {start_page} по {end_page}")
    
    downloader = DrivingTestsDownloader(
        save_path="../../data/downloads",
        delay_range=(3, 7)
    )
    
    try:
        downloaded_files = downloader.download_multiple_tests(start_page, end_page, delay)
        
        stats = downloader.get_stats()
        print(f"\n📊 Статистика загрузки:")
        print(f"   Успешных: {stats['successful']}")
        print(f"   Неудачных: {stats['failed']}")
        print(f"   Процент успеха: {stats['success_rate_percent']}%")
        print(f"   Время выполнения: {stats['elapsed_time']}")
        
        if downloaded_files:
            print(f"\n📁 Загружено файлов: {len(downloaded_files)}")
        
        return len(downloaded_files) > 0
        
    finally:
        downloader.close()


def analyze_tests():
    """Анализирует загруженные билеты"""
    print("📊 Анализ загруженных билетов")
    
    analyzer = DrivingTestsAnalyzer(
        downloads_path="../data/downloads",
        results_path="../data/results"
    )
    
    try:
        # Анализируем HTML файлы
        analysis_result = analyzer.analyze_html_files()
        
        print(f"\n📊 Результаты анализа:")
        print(f"   Обработано файлов: {analysis_result['files_processed']}")
        print(f"   Найдено слов: {analysis_result['words_found']}")
        print(f"   Уникальных слов: {analysis_result['unique_words']}")
        
        # Экспортируем результаты
        export_file = analyzer.export_results()
        
        if export_file:
            print(f"✅ Результаты экспортированы в: {export_file}")
        
        # Показываем сводку
        summary = analyzer.get_analysis_summary()
        print(f"\n📋 Сводка анализа:")
        print(f"   Время выполнения: {summary['analysis_time']}")
        print(f"   Известных слов: {summary['known_words']}")
        print(f"   Новых слов: {summary['new_words']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        return False


def show_status():
    """Показывает статус инструментов"""
    print("📋 Статус инструментов\n")
    
    # Проверяем папку загрузок
    downloads_path = Path("../data/downloads")
    if downloads_path.exists():
        html_files = list(downloads_path.glob("*.html"))
        print(f"📁 Папка загрузок: {len(html_files)} HTML файлов")
        if html_files:
            print("   Последние файлы:")
            for file in sorted(html_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                print(f"     - {file.name}")
    else:
        print("📁 Папка загрузок: не найдена")
    
    # Проверяем папку результатов
    results_path = Path("../data/results")
    if results_path.exists():
        excel_files = list(results_path.glob("*.xlsx"))
        print(f"\n📊 Папка результатов: {len(excel_files)} Excel файлов")
        if excel_files:
            print("   Последние результаты:")
            for file in sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                print(f"     - {file.name}")
    else:
        print("\n📊 Папка результатов: не найдена")


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Инструменты для работы с билетами по вождению")
    parser.add_argument("action", choices=["download", "analyze", "status", "full"], 
                       help="Действие для выполнения")
    parser.add_argument("--start", type=int, default=1, 
                       help="Начальная страница для загрузки (по умолчанию: 1)")
    parser.add_argument("--end", type=int, default=10, 
                       help="Конечная страница для загрузки (по умолчанию: 10)")
    parser.add_argument("--no-delay", action="store_true", 
                       help="Отключить задержки между запросами")
    
    args = parser.parse_args()
    
    print("🚗 Инструменты для работы с билетами по вождению\n")
    
    try:
        if args.action == "download":
            success = download_tests(args.start, args.end, not args.no_delay)
            if success:
                print("\n✅ Загрузка завершена успешно")
            else:
                print("\n❌ Загрузка завершена с ошибками")
                
        elif args.action == "analyze":
            success = analyze_tests()
            if success:
                print("\n✅ Анализ завершён успешно")
            else:
                print("\n❌ Анализ завершён с ошибками")
                
        elif args.action == "status":
            show_status()
            
        elif args.action == "full":
            print("🔄 Полный цикл: загрузка + анализ")
            
            # Загружаем билеты
            if download_tests(args.start, args.end, not args.no_delay):
                print("\n" + "="*50)
                
                # Анализируем загруженные билеты
                if analyze_tests():
                    print("\n🎉 Полный цикл завершён успешно!")
                else:
                    print("\n⚠️ Загрузка прошла успешно, но анализ завершился с ошибками")
            else:
                print("\n❌ Загрузка не удалась, анализ пропущен")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Операция прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Анализатор билетов по вождению

Специализированный инструмент для анализа HTML страниц с билетами
по вождению и формирования Excel отчётов с датой/временем
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import glob
import logging
import pandas as pd
from collections import Counter

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spanish_analyser import SpanishTextProcessor, WordAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DrivingTestsAnalyzer:
    """Специализированный анализатор для билетов по вождению"""
    
    def __init__(self, 
                 downloads_path: str = "../data/downloads",
                 results_path: str = "../data/results",
                 max_files: int = 20):
        """
        Инициализация анализатора
        
        Args:
            downloads_path: Путь к папке с загруженными HTML файлами
            results_path: Путь для сохранения результатов анализа
            max_files: Максимальное количество файлов результатов
        """
        self.downloads_path = Path(downloads_path)
        self.results_path = Path(results_path)
        self.max_files = max_files
        
        # Создаём папку для результатов
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем компоненты
        self.text_processor = SpanishTextProcessor()
        self.word_analyzer = WordAnalyzer()
        
        # Статистика анализа
        self.analysis_stats = {
            'files_processed': 0,
            'words_found': 0,
            'start_time': datetime.now()
        }
        
        logger.info(f"Анализатор инициализирован")
        logger.info(f"Папка загрузок: {self.downloads_path}")
        logger.info(f"Папка результатов: {self.results_path}")
    
    def find_html_files(self, pattern: str = "*.html") -> list:
        """
        Находит HTML файлы для анализа
        
        Args:
            pattern: Паттерн для поиска файлов
            
        Returns:
            Список путей к HTML файлам
        """
        html_files = list(self.downloads_path.glob(pattern))
        logger.info(f"Найдено {len(html_files)} HTML файлов для анализа")
        return html_files
    
    def extract_text_from_html(self, html_file: Path) -> str:
        """
        Извлекает текст из HTML файла
        
        Args:
            html_file: Путь к HTML файлу
            
        Returns:
            Извлечённый текст
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Очищаем HTML теги
            cleaned_text = self.text_processor.clean_text(html_content, remove_prefixes=False)
            
            logger.debug(f"Извлечён текст из {html_file.name}: {len(cleaned_text)} символов")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из {html_file.name}: {e}")
            return ""
    
    def analyze_html_files(self, html_files: list = None) -> dict:
        """
        Анализирует HTML файлы и извлекает слова
        
        Args:
            html_files: Список HTML файлов для анализа
            
        Returns:
            Словарь со статистикой анализа
        """
        if html_files is None:
            html_files = self.find_html_files()
        
        logger.info(f"Начинаю анализ {len(html_files)} HTML файлов")
        
        total_words = 0
        
        for html_file in html_files:
            try:
                # Извлекаем текст
                text = self.extract_text_from_html(html_file)
                if text:
                    # Добавляем слова в анализатор
                    self.word_analyzer.add_words_from_text(text)
                    
                    # Подсчитываем слова в этом файле
                    words_in_file = len(self.text_processor.extract_spanish_words(text))
                    total_words += words_in_file
                    
                    self.analysis_stats['files_processed'] += 1
                    logger.info(f"✅ Обработан {html_file.name}: найдено {words_in_file} слов")
                else:
                    logger.warning(f"⚠️ Пропущен {html_file.name}: пустой текст")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при анализе {html_file.name}: {e}")
        
        self.analysis_stats['words_found'] = total_words
        
        logger.info(f"Анализ завершён. Обработано файлов: {self.analysis_stats['files_processed']}")
        logger.info(f"Всего найдено слов: {total_words}")
        
        return {
            'files_processed': self.analysis_stats['files_processed'],
            'words_found': total_words,
            'unique_words': len(self.word_analyzer.word_frequencies)
        }
    
    def generate_filename_with_timestamp(self, prefix: str = "word_analysis") -> str:
        """
        Генерирует имя файла с временной меткой
        
        Args:
            prefix: Префикс для имени файла
            
        Returns:
            Имя файла с временной меткой
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.xlsx"
    
    def cleanup_old_files(self):
        """Удаляет старые файлы результатов, оставляя не более max_files"""
        try:
            # Находим все Excel файлы в папке результатов
            excel_files = list(self.results_path.glob("*.xlsx"))
            
            if len(excel_files) > self.max_files:
                # Сортируем по времени изменения (старые первыми)
                excel_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Удаляем самые старые файлы
                files_to_delete = excel_files[:-self.max_files]
                
                for old_file in files_to_delete:
                    old_file.unlink()
                    logger.info(f"Удалён старый файл: {old_file.name}")
                
                logger.info(f"Удалено {len(files_to_delete)} старых файлов результатов")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке старых файлов: {e}")
    
    def export_results(self, include_categories: bool = True) -> str:
        """
        Экспортирует результаты анализа в Excel
        
        Args:
            include_categories: Включать ли категории по частоте
            
        Returns:
            Путь к созданному файлу
        """
        try:
            # Генерируем имя файла с временной меткой
            filename = self.generate_filename_with_timestamp("driving_tests_analysis")
            file_path = self.results_path / filename
            
            # Экспортируем результаты
            self.word_analyzer.export_to_excel(str(file_path), include_categories)
            
            # Очищаем старые файлы
            self.cleanup_old_files()
            
            logger.info(f"Результаты экспортированы в: {filename}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте результатов: {e}")
            return ""
    
    def get_analysis_summary(self) -> dict:
        """Получает сводку по анализу"""
        # Получаем статистику от WordAnalyzer
        word_stats = self.word_analyzer.get_summary_stats()
        
        # Добавляем нашу статистику
        analysis_summary = {
            'files_processed': self.analysis_stats['files_processed'],
            'words_found': self.analysis_stats['words_found'],
            'unique_words': word_stats['всего_уникальных_слов'],
            'known_words': word_stats['известных_слов'],
            'new_words': word_stats['новых_слов'],
            'analysis_time': str(datetime.now() - self.analysis_stats['start_time'])
        }
        
        return analysis_summary
    
    def reset_analysis(self):
        """Сбрасывает результаты анализа"""
        self.word_analyzer.reset()
        self.analysis_stats = {
            'files_processed': 0,
            'words_found': 0,
            'start_time': datetime.now()
        }
        logger.info("Результаты анализа сброшены")


def main():
    """Основная функция для демонстрации"""
    print("📊 Анализатор билетов по вождению\n")
    
    # Создаём анализатор
    analyzer = DrivingTestsAnalyzer(
        downloads_path="../../data/downloads",
        results_path="../../data/results"
    )
    
    try:
        # Анализируем HTML файлы
        print("Начинаю анализ HTML файлов...")
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
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

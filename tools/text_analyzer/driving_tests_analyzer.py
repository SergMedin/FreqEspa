#!/usr/bin/env python3
"""
Анализатор билетов по вождению

Анализирует HTML файлы с билетами и создаёт Excel отчёты
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import time

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.spanish_analyser.word_analyzer import WordAnalyzer
from src.spanish_analyser.anki_integration import AnkiIntegration
from src.spanish_analyser.config import config


class DrivingTestsAnalyzer:
    """Анализатор билетов по вождению"""
    
    def __init__(self):
        """Инициализация анализатора"""
        self.word_analyzer = WordAnalyzer()
        self.anki_integration = AnkiIntegration()
        
        # Получаем настройки из конфигурации
        self.downloads_path = Path(config.get_downloads_folder())
        self.results_path = Path(config.get_results_folder())
        self.max_results_files = config.get_max_results_files()
        self.results_filename_prefix = config.get_results_filename_prefix()
        
        # Создаём папку для результатов
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем компоненты
        from src.spanish_analyser.text_processor import SpanishTextProcessor
        self.text_processor = SpanishTextProcessor()
        
        # Статистика анализа
        self.analysis_stats = {
            'files_processed': 0,
            'words_found': 0,
            'start_time': datetime.now()
        }
        
        # Настройка логирования
        logging.basicConfig(
            level=getattr(logging, config.get_logging_level()),
            format=config.get_logging_format()
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Анализатор инициализирован")
        self.logger.info(f"Папка загрузок: {self.downloads_path}")
        self.logger.info(f"Папка результатов: {self.results_path}")
    
    def connect_to_anki(self) -> bool:
        """
        Подключается к Anki и загружает известные слова
        
        Returns:
            True если подключение успешно
        """
        try:
            self.logger.info("Подключаюсь к Anki...")
            if self.anki_integration.connect():
                self.logger.info("✅ Подключение к Anki успешно")
                
                # Загружаем известные слова из испанских колод
                self.logger.info("Загружаю известные слова из колод Spanish...")
                if self.word_analyzer.load_known_words_from_anki(
                    self.anki_integration, 
                    deck_pattern="Spanish*",
                    field_names=['FrontText', 'BackText']
                ):
                    self.logger.info("✅ Известные слова загружены из Anki")
                    return True
                else:
                    self.logger.warning("⚠️ Не удалось загрузить известные слова из Anki")
                    return False
            else:
                self.logger.warning("⚠️ Не удалось подключиться к Anki")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при подключении к Anki: {e}")
            return False
    
    def find_html_files(self, pattern: str = "*.html") -> list:
        """
        Находит HTML файлы для анализа
        
        Args:
            pattern: Паттерн для поиска файлов
            
        Returns:
            Список путей к HTML файлам
        """
        html_files = list(self.downloads_path.glob(pattern))
        self.logger.info(f"Найдено {len(html_files)} HTML файлов для анализа")
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
            
            # Используем улучшенный метод извлечения текста
            cleaned_text = self._extract_text_improved(html_content)
            
            # Дополнительно извлекаем испанские слова для лучшего качества
            spanish_words = self.text_processor.extract_spanish_words(cleaned_text)
            
            # Объединяем в текст для анализа
            final_text = ' '.join(spanish_words)
            
            self.logger.debug(f"Извлечён текст из {html_file.name}: {len(final_text)} символов, {len(spanish_words)} слов")
            return final_text
            
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении текста из {html_file.name}: {e}")
            return ""
    
    def _extract_text_improved(self, html_content: str) -> str:
        """
        Улучшенное извлечение текста из HTML с поиском блоков col-md-8
        
        Args:
            html_content: HTML содержимое
            
        Returns:
            Извлечённый текст
        """
        try:
            from bs4 import BeautifulSoup
            
            # Создаём объект BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Извлекаем все блоки с классом "col-md-8" (как в оригинальном коде)
            blocks = soup.find_all('div', class_='col-md-8')
            
            if blocks:
                # Извлекаем текст из каждого блока и объединяем их
                text = "\n".join([block.get_text(separator=" ", strip=True) for block in blocks])
                self.logger.debug(f"Найдено {len(blocks)} блоков col-md-8")
            else:
                # Fallback: ищем другие элементы с текстом
                text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'])
                text = "\n".join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
                self.logger.debug(f"Fallback: найдено {len(text_elements)} текстовых элементов")
            
            return text.strip()
            
        except Exception as e:
            self.logger.warning(f"Ошибка при улучшенном извлечении текста: {e}")
            # Fallback к базовому методу
            return self.text_processor.clean_text(html_content, remove_prefixes=False)
    
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
        
        self.logger.info(f"Начинаю анализ {len(html_files)} HTML файлов")
        
        total_words = 0
        
        for html_file in html_files:
            try:
                # Извлекаем текст
                text = self.extract_text_from_html(html_file)
                if text:
                    # Добавляем слова в анализатор
                    self.word_analyzer.add_words_from_text(text)
                    
                    # Подсчитываем слова в этом файле
                    words_in_file = len(text.split())
                    total_words += words_in_file
                    
                    self.analysis_stats['files_processed'] += 1
                    self.logger.info(f"✅ Обработан {html_file.name}: найдено {words_in_file} слов")
                else:
                    self.logger.warning(f"⚠️ Пропущен {html_file.name}: пустой текст")
                    
            except Exception as e:
                self.logger.error(f"❌ Ошибка при анализе {html_file.name}: {e}")
        
        self.analysis_stats['words_found'] = total_words
        
        self.logger.info(f"Анализ завершён. Обработано файлов: {self.analysis_stats['files_processed']}")
        self.logger.info(f"Всего найдено слов: {total_words}")
        
        return {
            'files_processed': self.analysis_stats['files_processed'],
            'words_found': total_words,
            'unique_words': len(self.word_analyzer.word_frequencies)
        }
    
    def generate_filename_with_timestamp(self, prefix: str = "driving_tests_analysis") -> str:
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
            
            if len(excel_files) > self.max_results_files:
                # Сортируем по времени изменения (старые первыми)
                excel_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Удаляем самые старые файлы
                files_to_delete = excel_files[:-self.max_results_files]
                
                for old_file in files_to_delete:
                    old_file.unlink()
                    self.logger.info(f"Удалён старый файл: {old_file.name}")
                
                self.logger.info(f"Удалено {len(files_to_delete)} старых файлов результатов")
            
        except Exception as e:
            self.logger.error(f"Ошибка при очистке старых файлов: {e}")
    
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
            
            self.logger.info(f"Результаты экспортированы в: {filename}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Ошибка при экспорте результатов: {e}")
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
        self.logger.info("Результаты анализа сброшены")
    
    def close(self):
        """Закрывает соединения"""
        if self.anki_integration:
            self.anki_integration.disconnect()
            self.logger.info("Соединение с Anki закрыто")


def main():
    """Основная функция для демонстрации"""
    print("📊 Анализатор билетов по вождению\n")
    
    # Создаём анализатор
    analyzer = DrivingTestsAnalyzer()
    
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
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        return 1
    finally:
        analyzer.close()
    
    return 0


if __name__ == "__main__":
    exit(main())

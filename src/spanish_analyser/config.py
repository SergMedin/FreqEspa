"""
Модуль для работы с конфигурацией проекта

Загружает настройки из config.yaml и .env файлов
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv


class Config:
    """Класс для работы с конфигурацией проекта"""
    
    def __init__(self, config_path: str = None):
        """
        Инициализация конфигурации
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Ищем config.yaml в корне проекта
            current_dir = Path.cwd()
            config_path = current_dir / "config.yaml"
            
            # Если не найден в текущей директории, ищем в родительских
            while not config_path.exists() and current_dir.parent != current_dir:
                current_dir = current_dir.parent
                config_path = current_dir / "config.yaml"
            
            self.config_path = config_path
        
        self.config_data = {}
        self.env_data = {}
        
        # Загружаем конфигурацию
        self._load_config()
        self._load_env()
    
    def _load_config(self):
        """Загружает конфигурацию из YAML файла"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                print(f"✅ Конфигурация загружена из {self.config_path}")
            else:
                print(f"⚠️ Файл конфигурации {self.config_path} не найден, используются значения по умолчанию")
                self.config_data = self._get_default_config()
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            self.config_data = self._get_default_config()
    
    def _load_env(self):
        """Загружает переменные окружения из .env файла"""
        try:
            load_dotenv()
            self.env_data = {
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
                'PRACTICATEST_EMAIL': os.getenv('PRACTICATEST_EMAIL'),
                'PRACTICATEST_PASSWORD': os.getenv('PRACTICATEST_PASSWORD'),
            }
            print("✅ Переменные окружения загружены")
        except Exception as e:
            print(f"❌ Ошибка загрузки переменных окружения: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        return {
            'anki': {
                'collection_path': "~/Library/Application Support/Anki2/User 1/collection.anki2",
                'deck_pattern': "Spanish*",
                'field_names': ["FrontText", "BackText"]
            },
            'text_analysis': {
                'min_word_length': 3,
                'max_words_export': 1000,
                'enable_pos_tagging': True,
                'spacy_model': "es_core_news_md"
            },
            'web_scraper': {
                'base_url': "https://practicatest.com",
                'timeout': 30,
                'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            'files': {
                'downloads_folder': "data/downloads",
                'results_folder': "data/results",
                'max_results_files': 20,
                'results_filename_prefix': "driving_tests_analysis"
            },
            'excel': {
                'frequency_decimal_places': 2,
                'include_headers': True,
                'main_sheet_name': "Word Analysis"
            },
            'logging': {
                'level': "INFO",
                'format': "%(asctime)s - %(levelname)s - %(message)s",
                'log_to_file': False,
                'log_file': "logs/spanish_analyser.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение конфигурации по ключу
        
        Args:
            key: Ключ в формате 'section.subsection.parameter'
            default: Значение по умолчанию
            
        Returns:
            Значение параметра или default
        """
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Получает значение переменной окружения
        
        Args:
            key: Ключ переменной окружения
            default: Значение по умолчанию
            
        Returns:
            Значение переменной окружения или default
        """
        return self.env_data.get(key, default)
    
    def get_anki_config(self) -> Dict[str, Any]:
        """Получает конфигурацию Anki"""
        return self.config_data.get('anki', {})
    
    def get_text_analysis_config(self) -> Dict[str, Any]:
        """Получает конфигурацию анализа текста"""
        return self.config_data.get('text_analysis', {})
    
    def get_web_scraper_config(self) -> Dict[str, Any]:
        """Получает конфигурацию веб-скрапера"""
        return self.config_data.get('web_scraper', {})
    
    def get_files_config(self) -> Dict[str, Any]:
        """Получает конфигурацию файлов"""
        return self.config_data.get('files', {})
    
    def get_excel_config(self) -> Dict[str, Any]:
        """Получает конфигурацию Excel"""
        return self.config_data.get('excel', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получает конфигурацию логирования"""
        return self.config_data.get('logging', {})
    
    def get_collection_path(self) -> str:
        """Получает путь к коллекции Anki"""
        path = self.get('anki.collection_path')
        return os.path.expanduser(path)
    
    def get_deck_pattern(self) -> str:
        """Получает паттерн для поиска колод"""
        return self.get('anki.deck_pattern', "Spanish*")
    
    def get_field_names(self) -> List[str]:
        """Получает названия полей для извлечения слов"""
        return self.get('anki.field_names', ["FrontText", "BackText"])
    
    def get_downloads_folder(self) -> str:
        """Получает папку для загрузок"""
        return self.get('files.downloads_folder', "data/downloads")
    
    def get_results_folder(self) -> str:
        """Получает папку для результатов"""
        return self.get('files.results_folder', "data/results")
    
    def get_max_results_files(self) -> int:
        """Получает максимальное количество файлов результатов"""
        return self.get('files.max_results_files', 20)
    
    def get_results_filename_prefix(self) -> str:
        """Получает префикс для файлов результатов"""
        return self.get('files.results_filename_prefix', "driving_tests_analysis")
    
    def get_frequency_decimal_places(self) -> int:
        """Получает количество знаков после запятой для частоты"""
        return self.get('excel.frequency_decimal_places', 2)
    
    def get_main_sheet_name(self) -> str:
        """Получает название основного листа Excel"""
        return self.get('excel.main_sheet_name', "Word Analysis")
    
    def get_spacy_model(self) -> str:
        """Получает название модели spaCy"""
        return self.get('text_analysis.spacy_model', "es_core_news_md")
    
    def get_min_word_length(self) -> int:
        """Получает минимальную длину слова"""
        return self.get('text_analysis.min_word_length', 3)
    
    def get_web_scraper_timeout(self) -> int:
        """Получает таймаут для веб-скрапера"""
        return self.get('web_scraper.timeout', 30)
    
    def get_web_scraper_base_url(self) -> str:
        """Получает базовый URL для веб-скрапера"""
        return self.get('web_scraper.base_url', "https://practicatest.com")
    
    def get_web_scraper_user_agent(self) -> str:
        """Получает User-Agent для веб-скрапера"""
        return self.get('web_scraper.user_agent', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    def get_logging_level(self) -> str:
        """Получает уровень логирования"""
        return self.get('logging.level', "INFO")
    
    def get_logging_format(self) -> str:
        """Получает формат логов"""
        return self.get('logging.format', "%(asctime)s - %(levelname)s - %(message)s")
    
    def get_logging_file(self) -> str:
        """Получает путь к файлу логов"""
        return self.get('logging.log_file', "logs/spanish_analyser.log")
    
    def is_logging_to_file_enabled(self) -> bool:
        """Проверяет, включено ли логирование в файл"""
        return self.get('logging.log_to_file', False)
    
    def is_pos_tagging_enabled(self) -> bool:
        """Проверяет, включено ли определение частей речи"""
        return self.get('text_analysis.enable_pos_tagging', True)


# Глобальный экземпляр конфигурации
config = Config()

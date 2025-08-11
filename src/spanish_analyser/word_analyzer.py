"""
Модуль для анализа испанских слов

Предоставляет функциональность для:
- Подсчёта частоты слов
- Категоризации слов по темам
- Анализа частей речи
- Создания отчётов
"""

import json
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
from pathlib import Path


class WordAnalyzer:
    """Класс для анализа испанских слов"""
    
    def __init__(self):
        """Инициализация анализатора слов"""
        self.word_frequencies = Counter()
        self.word_categories = defaultdict(list)
        self.known_words = set()
        self.translation_cache = {}
    
    def load_known_words(self, file_path: str) -> bool:
        """
        Загружает список известных слов из файла
        
        Args:
            file_path: Путь к файлу с известными словами
            
        Returns:
            True если загрузка успешна, False в противном случае
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = [line.strip().lower() for line in f if line.strip()]
                self.known_words = set(words)
            print(f"Загружено {len(self.known_words)} известных слов")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке известных слов: {e}")
            return False
    
    def load_translation_cache(self, file_path: str) -> bool:
        """
        Загружает кэш переводов из JSON файла
        
        Args:
            file_path: Путь к JSON файлу с кэшем переводов
            
        Returns:
            True если загрузка успешна, False в противном случае
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translation_cache = json.load(f)
            print(f"Загружен кэш переводов: {len(self.translation_cache)} записей")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке кэша переводов: {e}")
            return False
    
    def add_words_from_text(self, text: str, weight: int = 1):
        """
        Добавляет слова из текста в статистику частот
        
        Args:
            text: Текст для анализа
            weight: Вес для подсчёта (по умолчанию 1)
        """
        if not text:
            return
        
        # Простая токенизация - можно улучшить
        words = text.lower().split()
        for word in words:
            # Очищаем слово от знаков препинания
            clean_word = ''.join(c for c in word if c.isalpha() or c in 'áéíóúüñ')
            if len(clean_word) > 2:  # Игнорируем слишком короткие слова
                self.word_frequencies[clean_word] += weight
    
    def categorize_words_by_frequency(self, min_frequency: int = 1) -> Dict[str, List[str]]:
        """
        Категоризует слова по частоте использования
        
        Args:
            min_frequency: Минимальная частота для включения в категорию
            
        Returns:
            Словарь с категориями и списками слов
        """
        categories = {
            'очень_часто': [],      # > 100 раз
            'часто': [],            # 50-100 раз
            'средне': [],           # 20-49 раз
            'редко': [],            # 5-19 раз
            'очень_редко': []       # 1-4 раза
        }
        
        for word, freq in self.word_frequencies.most_common():
            if freq < min_frequency:
                continue
                
            if freq > 100:
                categories['очень_часто'].append(word)
            elif freq > 50:
                categories['часто'].append(word)
            elif freq > 20:
                categories['средне'].append(word)
            elif freq > 5:
                categories['редко'].append(word)
            else:
                categories['очень_редко'].append(word)
        
        return categories
    
    def get_new_words(self, exclude_known: bool = True) -> List[str]:
        """
        Получает список новых (неизвестных) слов
        
        Args:
            exclude_known: Исключать ли известные слова
            
        Returns:
            Список новых слов, отсортированный по частоте
        """
        if exclude_known:
            new_words = [word for word, freq in self.word_frequencies.most_common() 
                        if word not in self.known_words]
        else:
            new_words = [word for word, freq in self.word_frequencies.most_common()]
        
        return new_words
    
    def get_top_words(self, n: int = 50, exclude_known: bool = True) -> List[Tuple[str, int]]:
        """
        Получает топ N слов по частоте
        
        Args:
            n: Количество слов для возврата
            exclude_known: Исключать ли известные слова
            
        Returns:
            Список кортежей (слово, частота)
        """
        if exclude_known:
            top_words = [(word, freq) for word, freq in self.word_frequencies.most_common() 
                        if word not in self.known_words]
        else:
            top_words = [(word, freq) for word, freq in self.word_frequencies.most_common()]
        
        return top_words[:n]
    
    def export_to_excel(self, file_path: str, include_categories: bool = True):
        """
        Экспортирует статистику слов в Excel файл
        
        Args:
            file_path: Путь для сохранения Excel файла
            include_categories: Включать ли категории по частоте
        """
        try:
            # Создаём DataFrame с основной статистикой
            data = []
            for word, freq in self.word_frequencies.most_common():
                is_known = word in self.known_words
                translation = self.translation_cache.get(word, '')
                
                row = {
                    'Слово': word,
                    'Частота': freq,
                    'Известно': 'Да' if is_known else 'Нет',
                    'Перевод': translation
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Создаём Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Статистика_слов', index=False)
                
                if include_categories:
                    # Добавляем лист с категориями
                    categories = self.categorize_words_by_frequency()
                    category_data = []
                    
                    for category, words in categories.items():
                        for word in words:
                            freq = self.word_frequencies[word]
                            is_known = word in self.known_words
                            translation = self.translation_cache.get(word, '')
                            
                            category_data.append({
                                'Категория': category.replace('_', ' ').title(),
                                'Слово': word,
                                'Частота': freq,
                                'Известно': 'Да' if is_known else 'Нет',
                                'Перевод': translation
                            })
                    
                    category_df = pd.DataFrame(category_data)
                    category_df.to_excel(writer, sheet_name='Категории', index=False)
            
            print(f"Статистика экспортирована в {file_path}")
            
        except Exception as e:
            print(f"Ошибка при экспорте в Excel: {e}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Получает сводную статистику по словам
        
        Returns:
            Словарь со статистикой
        """
        total_words = len(self.word_frequencies)
        total_occurrences = sum(self.word_frequencies.values())
        known_words_count = len(self.known_words.intersection(set(self.word_frequencies.keys())))
        new_words_count = total_words - known_words_count
        
        categories = self.categorize_words_by_frequency()
        
        return {
            'всего_уникальных_слов': total_words,
            'всего_вхождений': total_occurrences,
            'известных_слов': known_words_count,
            'новых_слов': new_words_count,
            'средняя_частота': total_occurrences / total_words if total_words > 0 else 0,
            'категории': {cat: len(words) for cat, words in categories.items()}
        }
    
    def reset(self):
        """Сбрасывает всю статистику"""
        self.word_frequencies.clear()
        self.word_categories.clear()
        print("Статистика слов сброшена")

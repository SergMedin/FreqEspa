"""
Модуль для анализа испанских слов

Предоставляет функциональность для:
- Подсчёта частоты слов
- Категоризации слов по темам
- Анализа частей речи с помощью spaCy
- Создания отчётов
"""

import json
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
from pathlib import Path
import spacy
from .config import config


class WordAnalyzer:
    """Класс для анализа испанских слов с использованием spaCy"""
    
    def __init__(self):
        """Инициализация анализатора слов"""
        self.word_frequencies = Counter()
        self.word_categories = defaultdict(list)
        self.known_words = set()
        self.word_pos_tags = {}  # Словарь для хранения частей речи
        
        # Загружаем модель spaCy для испанского языка из конфигурации
        spacy_model = config.get_spacy_model()
        try:
            self.nlp = spacy.load(spacy_model)
            print(f"✅ Модель spaCy {spacy_model} загружена успешно")
        except OSError:
            print(f"⚠️ Модель spaCy {spacy_model} не найдена. Устанавливаю...")
            try:
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", spacy_model], check=True)
                self.nlp = spacy.load(spacy_model)
                print(f"✅ Модель spaCy {spacy_model} установлена и загружена")
            except Exception as e:
                print(f"❌ Ошибка установки модели spaCy: {e}")
                print("⚠️ Продолжаю без spaCy, используя базовое определение частей речи")
                self.nlp = None
        
        # Названия частей речи на русском языке
        self.POS_NAMES = {
            "ADJ": "прилагательное",
            "ADP": "предлог",
            "ADV": "наречие",
            "AUX": "вспомогательный глагол",
            "CONJ": "союз",
            "CCONJ": "сочинительный союз",
            "DET": "определитель",
            "INTJ": "междометие",
            "NOUN": "существительное",
            "NUM": "числительное",
            "PART": "частица",
            "PRON": "местоимение",
            "PROPN": "собственное имя",
            "PUNCT": "пунктуация",
            "SCONJ": "подчинительный союз",
            "SYM": "символ",
            "VERB": "глагол",
            "X": "неизвестное"
        }
    
    def determine_pos_with_spacy(self, word: str) -> str:
        """
        Определяет часть речи для испанского слова с помощью spaCy
        
        Args:
            word: Слово для анализа
            
        Returns:
            Часть речи на русском языке
        """
        if not self.nlp:
            return self.determine_pos_basic(word)
        
        try:
            # Анализируем слово с помощью spaCy
            doc = self.nlp(word)
            if doc:
                token = doc[0]
                pos_tag = token.pos_
                return self.POS_NAMES.get(pos_tag, "неизвестно")
        except Exception as e:
            print(f"Ошибка при анализе слова '{word}' с spaCy: {e}")
        
        return "неизвестно"
    
    def determine_pos_basic(self, word: str) -> str:
        """
        Базовое определение части речи (fallback если spaCy недоступен)
        
        Args:
            word: Слово для анализа
            
        Returns:
            Часть речи
        """
        word_lower = word.lower()
        
        # Простые паттерны для испанского языка
        if word_lower in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']:
            return "определитель"
        elif word_lower in ['y', 'o', 'pero', 'si', 'que', 'como', 'cuando', 'donde']:
            return "союз"
        elif word_lower in ['yo', 'tú', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ellos', 'ellas']:
            return "местоимение"
        elif word_lower in ['a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'so', 'sobre', 'tras']:
            return "предлог"
        elif word_lower.endswith(('ar', 'er', 'ir')):
            return "глагол"
        elif word_lower.endswith(('ado', 'ido', 'ada', 'ida')):
            return "причастие"
        elif word_lower.endswith(('ando', 'iendo', 'endo')):
            return "герундий"
        elif word_lower.endswith(('oso', 'osa', 'al', 'ar', 'ivo', 'iva', 'able', 'ible')):
            return "прилагательное"
        elif word_lower.endswith(('mente')):
            return "наречие"
        elif word_lower.endswith(('ción', 'sión', 'dad', 'tad', 'tud', 'ez', 'eza', 'ura', 'ía', 'io')):
            return "существительное"
        elif word_lower.isdigit() or word_lower in ['primero', 'segundo', 'tercero', 'cuarto', 'quinto']:
            return "числительное"
        
        return "неизвестно"
    
    def determine_pos(self, word: str) -> str:
        """
        Определяет часть речи для испанского слова
        
        Args:
            word: Слово для анализа
            
        Returns:
            Часть речи на русском языке
        """
        if self.nlp:
            return self.determine_pos_with_spacy(word)
        else:
            return self.determine_pos_basic(word)
    
    def load_known_words_from_anki(self, anki_integration, deck_pattern: str = None, field_names: List[str] = None) -> bool:
        """
        Загружает известные слова из колод Anki
        
        Args:
            anki_integration: Экземпляр AnkiIntegration
            deck_pattern: Паттерн для поиска колод (если не указан, используется из конфигурации)
            field_names: Список названий полей для извлечения слов (если не указан, используется из конфигурации)
            
        Returns:
            True если загрузка успешна, False в противном случае
        """
        # Используем значения по умолчанию из конфигурации
        deck_pattern = deck_pattern or config.get_deck_pattern()
        field_names = field_names or config.get_field_names()
        
        try:
            if not anki_integration.is_connected():
                print("Не подключены к Anki для загрузки известных слов")
                return False
            
            # Находим заметки в испанских колодах
            note_ids = anki_integration.find_notes_by_deck(deck_pattern)
            if not note_ids:
                print(f"Не найдено заметок в колодах по паттерну: {deck_pattern}")
                return False
            
            print(f"Найдено {len(note_ids)} заметок в испанских колодах")
            
            # Извлекаем текст из заметок
            notes_data = anki_integration.extract_text_from_notes(note_ids, field_names)
            
            # Собираем все слова из текста
            all_words = set()
            for note_data in notes_data:
                for text in note_data['texts']:
                    if text:
                        # Очищаем текст от HTML и извлекаем слова
                        from .text_processor import SpanishTextProcessor
                        processor = SpanishTextProcessor()
                        cleaned_text = processor.clean_text(text, remove_prefixes=False)
                        words = processor.extract_spanish_words(cleaned_text)
                        all_words.update(words)
            
            # Устанавливаем известные слова
            self.known_words = all_words
            print(f"Загружено {len(self.known_words)} известных слов из Anki")
            return True
            
        except Exception as e:
            print(f"Ошибка при загрузке известных слов из Anki: {e}")
            return False
    
    def load_known_words(self, file_path: str) -> bool:
        """
        Загружает список известных слов из файла (устаревший метод)
        
        Args:
            file_path: Путь к файлу с известными словами
            
        Returns:
            True если загрузка успешна, False в противном случае
        """
        print("ВНИМАНИЕ: Метод load_known_words() устарел. Используйте load_known_words_from_anki()")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = [line.strip().lower() for line in f if line.strip()]
                self.known_words = set(words)
            print(f"Загружено {len(words)} известных слов из файла")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке известных слов: {e}")
            return False
    
    def add_words_from_text(self, text: str, weight: int = 1):
        """
        Добавляет слова из текста в статистику частот с определением частей речи
        
        Args:
            text: Текст для анализа
            weight: Вес для подсчёта (по умолчанию 1)
        """
        if not text:
            return
        
        # Используем spaCy для анализа текста, если доступен
        if self.nlp:
            try:
                doc = self.nlp(text)
                for token in doc:
                    if token.is_alpha and len(token.text) > 2:
                        # Лемматизируем слово для лучшего анализа
                        lemma = token.lemma_.lower()
                        pos_tag = token.pos_
                        pos_name = self.POS_NAMES.get(pos_tag, "неизвестно")
                        
                        # Создаём слово в формате "слово (часть_речи)" как в оригинальном коде
                        word_with_pos = f"{lemma} ({pos_name})"
                        
                        # Сохраняем частоту и часть речи
                        self.word_frequencies[word_with_pos] += weight
                        self.word_pos_tags[lemma] = pos_name  # Сохраняем для отдельных слов
                        
            except Exception as e:
                print(f"Ошибка при анализе текста с spaCy: {e}")
                # Fallback к базовому методу
                self._add_words_basic(text, weight)
        else:
            # Базовый метод без spaCy
            self._add_words_basic(text, weight)
    
    def _add_words_basic(self, text: str, weight: int = 1):
        """
        Базовый метод добавления слов без spaCy
        
        Args:
            text: Текст для анализа
            weight: Вес для подсчёта
        """
        words = text.lower().split()
        for word in words:
            # Очищаем слово от знаков препинания
            clean_word = ''.join(c for c in word if c.isalpha() or c in 'áéíóúüñ')
            if len(clean_word) > 2:  # Игнорируем слишком короткие слова
                # Определяем часть речи
                pos_tag = self.determine_pos_basic(clean_word)
                
                # Создаём слово в формате "слово (часть_речи)" как в оригинальном коде
                word_with_pos = f"{clean_word} ({pos_tag})"
                
                # Сохраняем частоту и часть речи
                self.word_frequencies[word_with_pos] += weight
                self.word_pos_tags[clean_word] = pos_tag
    
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
        
        for word_with_pos, freq in self.word_frequencies.most_common():
            if freq < min_frequency:
                continue
                
            if freq > 100:
                categories['очень_часто'].append(word_with_pos)
            elif freq > 50:
                categories['часто'].append(word_with_pos)
            elif freq > 20:
                categories['средне'].append(word_with_pos)
            elif freq > 5:
                categories['редко'].append(word_with_pos)
            else:
                categories['очень_редко'].append(word_with_pos)
        
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
            new_words = []
            for word_with_pos, freq in self.word_frequencies.most_common():
                # Извлекаем только слово без части речи
                if ' (' in word_with_pos and word_with_pos.endswith(')'):
                    word = word_with_pos.split(' (')[0]
                else:
                    word = word_with_pos
                
                if word not in self.known_words:
                    new_words.append(word_with_pos)
        else:
            new_words = [word_with_pos for word_with_pos, freq in self.word_frequencies.most_common()]
        
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
            top_words = []
            for word_with_pos, freq in self.word_frequencies.most_common():
                # Извлекаем только слово без части речи
                if ' (' in word_with_pos and word_with_pos.endswith(')'):
                    word = word_with_pos.split(' (')[0]
                else:
                    word = word_with_pos
                
                if word not in self.known_words:
                    top_words.append((word_with_pos, freq))
        else:
            top_words = [(word_with_pos, freq) for word_with_pos, freq in self.word_frequencies.most_common()]
        
        return top_words[:n]
    
    def export_to_excel(self, file_path: str, include_categories: bool = True):
        """
        Экспортирует статистику слов в Excel файл
        
        Args:
            file_path: Путь для сохранения Excel файла
            include_categories: Параметр оставлен для совместимости, но не используется
        """
        try:
            # Вычисляем общее количество всех слов (включая повторения)
            total_words = sum(self.word_frequencies.values())
            
            # Получаем настройки из конфигурации
            decimal_places = config.get_frequency_decimal_places()
            sheet_name = config.get_main_sheet_name()
            
            # Создаём DataFrame с основной статистикой в простом формате
            data = []
            for word_with_pos, freq in self.word_frequencies.most_common():
                # Извлекаем слово и часть речи из формата "слово (часть_речи)"
                if ' (' in word_with_pos and word_with_pos.endswith(')'):
                    word = word_with_pos.split(' (')[0]
                    pos_tag = word_with_pos.split(' (')[1].rstrip(')')
                else:
                    word = word_with_pos
                    pos_tag = 'неизвестно'
                
                # Вычисляем относительную частоту (процент от общего количества слов)
                relative_frequency = (freq / total_words) * 100 if total_words > 0 else 0
                
                row = {
                    'Word': word,
                    'Part of Speech': pos_tag,
                    'Frequency': f"{relative_frequency:.{decimal_places}f}%",  # Относительная частота в процентах
                    'Count': freq  # Абсолютное количество
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Создаём Excel writer с одним листом
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Только основной лист с простой структурой
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
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
        
        # Подсчитываем уникальные слова (без частей речи)
        unique_words = set()
        for word_with_pos in self.word_frequencies.keys():
            if ' (' in word_with_pos and word_with_pos.endswith(')'):
                word = word_with_pos.split(' (')[0]
            else:
                word = word_with_pos
            unique_words.add(word)
        
        known_words_count = len(self.known_words.intersection(unique_words))
        new_words_count = len(unique_words) - known_words_count
        
        categories = self.categorize_words_by_frequency()
        
        return {
            'всего_уникальных_слов': len(unique_words),
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
        self.word_pos_tags.clear()
        print("Статистика слов сброшена")

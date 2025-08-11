"""
Тесты для модуля word_analyzer
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spanish_analyser.word_analyzer import WordAnalyzer


class TestWordAnalyzer(unittest.TestCase):
    """Тесты для класса WordAnalyzer"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.analyzer = WordAnalyzer()
    
    def test_add_words_from_text(self):
        """Тест добавления слов из текста"""
        # Добавляем слова
        self.analyzer.add_words_from_text("hola mundo")
        self.assertEqual(self.analyzer.word_frequencies["hola"], 1)
        self.assertEqual(self.analyzer.word_frequencies["mundo"], 1)
        
        # Добавляем снова
        self.analyzer.add_words_from_text("hola casa")
        self.assertEqual(self.analyzer.word_frequencies["hola"], 2)
        self.assertEqual(self.analyzer.word_frequencies["casa"], 1)
        
        # Тест с весом
        self.analyzer.add_words_from_text("hola", weight=3)
        self.assertEqual(self.analyzer.word_frequencies["hola"], 5)
    
    def test_categorize_words_by_frequency(self):
        """Тест категоризации слов по частоте"""
        # Добавляем слова с разной частотой
        self.analyzer.add_words_from_text("muyfrecuente " * 150)  # > 100
        self.analyzer.add_words_from_text("frecuente " * 75)       # 50-100
        self.analyzer.add_words_from_text("medio " * 35)           # 20-49
        self.analyzer.add_words_from_text("raro " * 10)            # 5-19
        self.analyzer.add_words_from_text("muyraro " * 3)         # 1-4
        
        categories = self.analyzer.categorize_words_by_frequency()
        
        self.assertIn("muyfrecuente", categories["очень_часто"])
        self.assertIn("frecuente", categories["часто"])
        self.assertIn("medio", categories["средне"])
        self.assertIn("raro", categories["редко"])
        self.assertIn("muyraro", categories["очень_редко"])
    
    def test_get_new_words(self):
        """Тест получения новых слов"""
        # Добавляем слова
        self.analyzer.add_words_from_text("nuevo conocido")
        
        # Добавляем известные слова
        self.analyzer.known_words.add("conocido")
        
        # Получаем новые слова
        new_words = self.analyzer.get_new_words(exclude_known=True)
        self.assertIn("nuevo", new_words)
        self.assertNotIn("conocido", new_words)
        
        # Получаем все слова
        all_words = self.analyzer.get_new_words(exclude_known=False)
        self.assertIn("nuevo", all_words)
        self.assertIn("conocido", all_words)
    
    def test_get_top_words(self):
        """Тест получения топ слов"""
        # Добавляем слова
        self.analyzer.add_words_from_text("primero segundo tercero")
        self.analyzer.add_words_from_text("primero segundo")
        self.analyzer.add_words_from_text("primero")
        
        # Получаем топ 2 слова
        top_words = self.analyzer.get_top_words(2)
        self.assertEqual(len(top_words), 2)
        self.assertEqual(top_words[0][0], "primero")  # Самое частое
        self.assertEqual(top_words[0][1], 3)
    
    def test_load_known_words(self):
        """Тест загрузки известных слов"""
        # Создаём временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("hola\nmundo\ncasa\n")
            temp_file = f.name
        
        try:
            # Загружаем слова
            result = self.analyzer.load_known_words(temp_file)
            self.assertTrue(result)
            self.assertEqual(len(self.analyzer.known_words), 3)
            self.assertIn("hola", self.analyzer.known_words)
            self.assertIn("mundo", self.analyzer.known_words)
            self.assertIn("casa", self.analyzer.known_words)
        finally:
            # Удаляем временный файл
            os.unlink(temp_file)
    
    def test_load_translation_cache(self):
        """Тест загрузки кэша переводов"""
        # Создаём временный JSON файл
        cache_data = {"hola": "привет", "mundo": "мир"}
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False)
            temp_file = f.name
        
        try:
            # Загружаем кэш
            result = self.analyzer.load_translation_cache(temp_file)
            self.assertTrue(result)
            self.assertEqual(self.analyzer.translation_cache, cache_data)
        finally:
            # Удаляем временный файл
            os.unlink(temp_file)
    
    def test_get_summary_stats(self):
        """Тест получения сводной статистики"""
        # Добавляем слова
        self.analyzer.add_words_from_text("hola mundo")
        self.analyzer.known_words.add("hola")
        
        stats = self.analyzer.get_summary_stats()
        
        self.assertEqual(stats["всего_уникальных_слов"], 2)
        self.assertEqual(stats["всего_вхождений"], 2)
        self.assertEqual(stats["известных_слов"], 1)
        self.assertEqual(stats["новых_слов"], 1)
        self.assertEqual(stats["средняя_частота"], 1.0)
    
    def test_reset(self):
        """Тест сброса статистики"""
        # Добавляем слова
        self.analyzer.add_words_from_text("hola mundo")
        self.analyzer.known_words.add("test")
        
        # Проверяем, что слова добавлены
        self.assertGreater(len(self.analyzer.word_frequencies), 0)
        
        # Сбрасываем
        self.analyzer.reset()
        
        # Проверяем, что статистика сброшена
        self.assertEqual(len(self.analyzer.word_frequencies), 0)
        self.assertEqual(len(self.analyzer.word_categories), 0)


if __name__ == "__main__":
    unittest.main()
